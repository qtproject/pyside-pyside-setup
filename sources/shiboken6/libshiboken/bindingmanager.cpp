// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "bindingmanager.h"
#include "sbkfailpoint.h"
#include "sbkftoptions.h"
#include "sbkheldlocks.h"

#include "autodecref.h"
#include "basewrapper.h"
#include "basewrapper_p.h"
#include "helper.h"
#include "sbkfeature_base.h"
#include "sbkmodule.h"
#include "sbkpep.h"
#include "sbkstaticstrings.h"
#include "sbkstring.h"

#include <atomic>
#include <cassert>
#include <cstddef>
#include <cstring>
#include <fstream>
#include <iostream>
#include <memory>
#include <mutex>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <utility>

// Taking a reference, or reading type state, needs an attached thread state.
// The precondition used to be documentation only, which is how it got broken
// once already. PyGILState_Check is not in the limited API, so the check only
// exists where we develop. Defined in both builds: the typed lookups it
// guards are compiled in both.
#if !defined(Py_LIMITED_API) && !defined(NDEBUG)
#  define SBK_ASSERT_ATTACHED() assert(PyGILState_Check())
#else
#  define SBK_ASSERT_ATTACHED() ((void)0)
#endif

// GraphNode for the dependency graph. It keeps a pointer to
// the TypeInitStruct to be able to lazily create the type and hashes
// by the full type name.
struct GraphNode
{
    explicit GraphNode(Shiboken::Module::TypeInitStruct *i) : name(i->fullName), initStruct(i) {}
    explicit GraphNode(const char *n) : name(n), initStruct(nullptr) {} // Only for searching

    std::string_view name;
    Shiboken::Module::TypeInitStruct *initStruct;

    friend bool operator==(const GraphNode &n1, const GraphNode &n2) { return n1.name == n2.name; }
    friend bool operator!=(const GraphNode &n1, const GraphNode &n2) { return n1.name != n2.name; }
};

template <>
struct std::hash<GraphNode> {
    size_t operator()(const GraphNode &n) const noexcept
    {
        return std::hash<std::string_view>{}(n.name);
    }
};

namespace Shiboken
{

#ifdef Py_GIL_DISABLED
// What the wrapper map stores.
//
// The map is weak on purpose: strong references would make every wrapper
// immortal, because for a Python-owned object the entry is only dropped once
// the C++ object goes away, and that happens when the wrapper dies. So a
// lookup has to upgrade a weak reference to a strong one, and "increment, but
// only if the count is not zero" cannot be assembled from two steps - under
// free threading Py_REFCNT() is computed from ob_ref_local / ob_ref_shared /
// ob_tid rather than being a field to compare-and-swap, and the decref that
// reaches zero happens inside CPython, out of reach of any lock of ours.
//
// PyUnstable_TryIncRef() is that upgrade. It is not in the limited API, so
// an abi3t build will have to do it with a weakref instead.
class WrapperEntry
{
public:
    explicit WrapperEntry(SbkObject *obj) : m_obj(obj)
    {
        // Without this, TryIncRef fails for every object no other thread has
        // touched yet, which looks just like "already dying".
        PyUnstable_EnableTryIncRef(reinterpret_cast<PyObject *>(obj));
    }

    /// The borrowed reference the map holds. Unsafe by nature; only read
    /// under the wrapper map lock, never handed out.
    SbkObject *borrowed() const { return m_obj; }

    /// A *new* reference, or nullptr when the wrapper is already on its way
    /// out - "the entry exists" and "the object is alive" in one statement.
    ///
    /// A tombstone answers nullptr without touching m_obj, and that is not a
    /// convenience: the wrapper is freed while the tombstone still stands, so
    /// even asking TryIncRef would read freed memory - and if the block has
    /// been recycled into another object, it would succeed and hand out a
    /// stranger. The guard belongs here rather than in the callers, because
    /// every caller needs it and two of them did not have it.
    SbkObject *acquire() const
    {
        if (m_dying)
            return nullptr;
        if (PyUnstable_TryIncRef(reinterpret_cast<PyObject *>(m_obj)) == 0)
            return nullptr;
        return m_obj;
    }

    /// Identity check that does not acquire, for findSbkObject().
    bool refersTo(SbkObject *obj) const { return m_obj == obj; }

    /// The type a tombstone stands for, null while the entry is live.
    PyTypeObject *typeKey() const { return m_typeKey; }

    /// Whether the C++ object behind this entry is on its way out. A
    /// tombstone answers "not absent" without exposing a wrapper: publishing
    /// a replacement here would hand out a pointer the destructor is about
    /// to invalidate.
    bool isDying() const { return m_dying; }

    /// Become a tombstone, and take a reference to the type while doing so:
    /// the wrapper is about to be freed, and the type is what a later lookup
    /// classifies against. Only a tombstone holds one - a live entry can read
    /// Py_TYPE() off the wrapper, and a reference here would outlive every
    /// removal path that does not go through retirement. The increment may
    /// happen under the lock; the decref may not, and it happens where the
    /// tombstone falls.
    void markDying()
    {
        if (m_dying)
            return;
        m_dying = true;
        m_typeKey = Py_TYPE(reinterpret_cast<PyObject *>(m_obj));
        Py_INCREF(reinterpret_cast<PyObject *>(m_typeKey));
    }

    /// The type reference the entry holds, handed over so the caller can
    /// drop it outside the lock.
    PyTypeObject *takeTypeKey()
    {
        auto *type = m_typeKey;
        m_typeKey = nullptr;
        return type;
    }

    /// Take in a wrapper the dying-conversion exception let through. It is
    /// deliberately not in the map - a lookup must not find it - so the
    /// tombstone is the only thing that still knows about it, and holds a
    /// reference for as long as it does.
    void addStray(SbkObject *obj)
    {
        Py_INCREF(reinterpret_cast<PyObject *>(obj));
        m_strays.push_back(obj);
    }

    /// A stray of this identity that fits \a typeObject, with a reference
    /// taken, or nullptr. Two conversions inside one destruction window used
    /// to meet in the map and come back with the same wrapper; they still do.
    /// Plain Py_INCREF: this entry holds a reference, so the object cannot be
    /// in deallocation.
    SbkObject *acquireStray(PyTypeObject *typeObject) const
    {
        for (SbkObject *stray : m_strays) {
            auto *found = reinterpret_cast<PyObject *>(stray);
            auto *foundType = Py_TYPE(found);
            if (foundType != typeObject) {
                // The contract's type-state exception, as in acquireWrapper().
                Shiboken::noteContractException(Shiboken::RawLock::WrapperMap);
                if (PyType_IsSubtype(foundType, typeObject) == 0)
                    continue;
            }
            Py_INCREF(found);
            return stray;
        }
        return nullptr;
    }

    /// How many wrappers this tombstone is holding, for the map dump.
    std::size_t strayCount() const { return m_strays.size(); }

    /// The strays, handed over so the caller can invalidate them outside the
    /// lock - that walks the object graph and takes the state lock - and drop
    /// the references there as well.
    std::vector<SbkObject *> takeStrays()
    {
        auto result = std::move(m_strays);
        m_strays.clear();
        return result;
    }

private:
    SbkObject *m_obj = nullptr;   // borrowed, as before
    PyTypeObject *m_typeKey = nullptr;  // owned
    std::vector<SbkObject *> m_strays;  // owned; only a tombstone has any
    bool m_dying = false;
};

// Mapping of C++ address to wrapper. We use a multimap to allow for co-located
// objects, which happens for example for the first field of a struct.
using WrapperMap = std::unordered_multimap<const void *, WrapperEntry>;
#else // Py_GIL_DISABLED
// Mapping of C++ address to wrapper. We use a multimap to allow for co-located
// objects, which happens for example for the first field of a struct.
using WrapperMap = std::unordered_multimap<const void *, SbkObject *>;
#endif // Py_GIL_DISABLED

using ClassHierarchyGuard =
    Shiboken::TrackedGuard<std::mutex, Shiboken::RawLock::ClassHierarchy>;

// The class hierarchy: modules add edges, conversions read them. A reader
// cannot hold a lock - identifyType() creates types and calls discovery
// functions - so the edges are immutable and a writer publishes a new map.
template <class NodeType>
class BaseGraph
{
public:
    using NodeList = std::vector<NodeType>;
    using NodeSet = std::unordered_set<NodeType>;

    using Edges = std::unordered_map<NodeType, NodeList>;
    using EdgesPtr = std::shared_ptr<const Edges>;

    BaseGraph() : m_edges(std::make_shared<const Edges>()) {}

    using Edge = std::pair<NodeType, NodeType>;

    /// A module's edges, in one publication. Publishing means copying the
    /// map, so one call per edge copies it once per edge - a full build has
    /// 436 of them, and the graph grows by a module at a time, never by an
    /// edge at a time.
    void addEdges(const std::vector<Edge> &edges)
    {
        if (edges.empty())
            return;
        // The copy under the lock as well: two modules publishing at once
        // would otherwise start from the same map and one would lose its
        // edges. Module initialization is the only writer.
        ClassHierarchyGuard guard(m_mutex);
        auto next = std::make_shared<Edges>(*m_edges);
        for (const auto &[from, to] : edges)
            (*next)[from].push_back(to);
        m_edges = std::move(next);
    }

    // The edges as they are now. Held by the caller for as long as it walks
    // them, which is why the lock is not.
    EdgesPtr edges() const
    {
        ClassHierarchyGuard guard(m_mutex);
        return m_edges;
    }

    static NodeSet nodeSet(const Edges &snapshot)
    {
        NodeSet result;
        for (const auto &p : snapshot) {
            result.insert(p.first);
            for (const auto node2 : p.second)
                result.insert(node2);
        }
        return result;
    }

private:
    EdgesPtr m_edges;
    mutable std::mutex m_mutex;
};

class Graph : public BaseGraph<GraphNode>
{
public:
    using TypeCptrPair = BindingManager::TypeCptrPair;

    // Find derived class by trying to find a child node that accepts the base class in
    // its type discovery function, return type and cptr cast to derived class.
    TypeCptrPair identifyType(void *cptr, PyTypeObject *type, PyTypeObject *baseType) const
    {
        // One snapshot for the whole traversal: a later round must not see a
        // different graph from the one it started on.
        const auto snapshot = edges();
        return identifyType(*snapshot, cptr, GraphNode(type->tp_name), type,
                            baseType);
    }

    bool dumpTypeGraph(const char *fileName) const;

private:
    TypeCptrPair identifyType(const Edges &snapshot, void *cptr,
                              GraphNode typeNode, PyTypeObject *type,
                              PyTypeObject *baseType) const;
};

Graph::TypeCptrPair Graph::identifyType(const Edges &snapshot, void *cptr,
                                        GraphNode typeNode, PyTypeObject *type,
                                        PyTypeObject *baseType) const
{
    assert(typeNode.initStruct != nullptr || type != nullptr);
    auto edgesIt = snapshot.find(typeNode);
    if (edgesIt != snapshot.end()) {
        typeNode = edgesIt->first;
        const NodeList &adjNodes = edgesIt->second;
        for (const auto &node : adjNodes) {
            auto newType = identifyType(snapshot, cptr, node, nullptr, baseType);
            if (newType.first != nullptr)
                return newType;
        }
    }

    if (type == nullptr) // Lazily create the type
        type = Shiboken::Module::get(*typeNode.initStruct);

    if (void *derivedCPtr = BindingManager::runTypeDiscovery(cptr, type, baseType))
        return {type, derivedCPtr};
    return {nullptr, nullptr};
}

static void formatDotNode(std::string_view name, std::ostream &file)
{
    auto lastDot = name.rfind('.');
    file << "    \"" << name << "\" [ label=";
    if (lastDot != std::string::npos) {
        file << '"' << name.substr(lastDot + 1) << "\" tooltip=\""
             << name.substr(0, lastDot) << '"';
    } else {
        file << '"' << name << '"';
    }
    file << " ]\n";
}

bool Graph::dumpTypeGraph(const char *fileName) const
{
    // Snapshot first: the file is written with no lock held, and the writer
    // must not see the graph change halfway through.
    const auto snapshot = edges();

    std::ofstream file(fileName);
    if (!file.good())
        return false;

    file << "digraph D {\n";

    // Define nodes with short names
    for (const auto &node : nodeSet(*snapshot))
        formatDotNode(node.name, file);

    // Write edges. One iterator alive across the failpoint: a test stops here
    // and lets a module publish, which is the race made deterministic.
    auto it = snapshot->cbegin();
    SBK_FAILPOINT("hierarchy-mid-traversal");
    for (; it != snapshot->cend(); ++it) {
        const auto &node1 = it->first;
        for (const auto &node2 : it->second)
            file << "    \"" << node2.name << "\" -> \"" << node1.name << "\"\n";
    }
    file << "}\n";
    return true;
}

// Tracked guards: the held-lock set the contract asserts against is complete
// only if every acquisition notes itself, so the plain lock_guard is not
// used here.
using WrapperMapGuard =
    Shiboken::TrackedGuard<std::recursive_mutex, Shiboken::RawLock::WrapperMap>;
using MainThreadDeleteGuard =
    Shiboken::TrackedGuard<std::mutex, Shiboken::RawLock::MainThreadDelete>;

struct BindingManager::BindingManagerPrivate {
    using DestructorEntries = std::vector<DestructorEntry>;

    WrapperMap wrapperMapper;
    // Guard wrapperMapper mainly for QML which calls into the generated
    // QObject::metaObject() and elsewhere from threads without GIL, causing
    // crashes for example in acquireWrapper(). std::shared_mutex was rejected due to:
    // https://stackoverflow.com/questions/50972345/when-is-stdshared-timed-mutex-slower-than-stdmutex-and-when-not-to-use-it
    std::recursive_mutex wrapperMapLock;
    Graph classHierarchy;
    DestructorEntries deleteInMainThread;
#ifdef Py_GIL_DISABLED
    // Nothing serializes the two users of the list above once the GIL is gone:
    // it is filled from every thread that deallocates a delete-in-main-thread
    // wrapper - QWidget, QWindow, QQuickItem and everything below them.
    std::mutex deleteInMainThreadLock;
#endif

#ifdef Py_GIL_DISABLED
    /// What retirement needs for a destruction C++ started, kept because the
    /// object it would have been read from is gone by then. Keyed by the
    /// primary C++ address, which is all operator delete knows.
    struct ExternalDestruction
    {
        SbkObject *wrapper;      ///< a key, never dereferenced
        void **cptrs;            ///< owned
        PyTypeObject *type;      ///< owned reference
    };
    std::unordered_map<const void *, ExternalDestruction> externalDying;
#endif

    WrapperMap::const_iterator findSbkObject(const void *cptr, SbkObject *wrapper) const;
    WrapperMap::const_iterator findByType(const void *cptr, PyTypeObject *desiredType) const;

    bool releaseWrapper(void *cptr, SbkObject *wrapper, const int *bases);
    bool releaseWrapperHelper(void *cptr, SbkObject *wrapper);

    void assignWrapper(SbkObject *wrapper, const void *cptr, const int *bases = nullptr);
    void assignWrapperHelper(SbkObject *wrapper, const void *cptr);
#ifdef Py_GIL_DISABLED
    /// What a registration meets at an address: nothing that is dying, a
    /// dying identity that refuses to be replaced, or one that lets the
    /// conversion through because it invalidates the result itself.
    enum class DyingIdentity { None, Refuse, Exempt };
    DyingIdentity classifyDyingIdentity(const void *cptr, PyTypeObject *typeObject,
                                        WrapperMap::iterator *exempt);
    void markDying(void *cptr, SbkObject *wrapper, const int *bases);
    void markDyingHelper(void *cptr, SbkObject *wrapper);
    /// Type references taken from the tombstones this retires, dropped by the
    /// caller once the lock is gone. Per call, never a member: two threads
    /// retire entries at the same time.
    using TypeRefs = std::vector<PyTypeObject *>;
    /// The wrappers the tombstones handed out while they stood, for the same
    /// reason and with the same rule: taken out under the lock, invalidated
    /// and dropped outside it.
    using StrayList = std::vector<SbkObject *>;
    void retire(void *cptr, SbkObject *wrapper, const int *bases, TypeRefs &types,
                StrayList &strays);
    void retireHelper(void *cptr, SbkObject *wrapper, TypeRefs &types, StrayList &strays);
#endif
};

// Find wrapper map entry by Python instance
WrapperMap::const_iterator
    BindingManager::BindingManagerPrivate::findSbkObject(const void *cptr,
                                                         SbkObject *wrapper) const
{
    const auto end = wrapperMapper.cend();
    auto it = wrapperMapper.find(cptr);
    for (; it != end && it->first == cptr; ++it) {
#ifdef Py_GIL_DISABLED
        if (it->second.refersTo(wrapper))
#else
        if (it->second == wrapper)
#endif
            return it;
    }
    return end;
}

// Find wrapper map entry by Python type
WrapperMap::const_iterator
    BindingManager::BindingManagerPrivate::findByType(const void *cptr,
                                                      PyTypeObject *desiredType) const
{
    const auto end = wrapperMapper.cend();
    auto it = wrapperMapper.find(cptr);
    for (; it != end && it->first == cptr; ++it) {
#ifdef Py_GIL_DISABLED
        // Same as in acquireWrapper(): a dying identity is not offered, and
        // its wrapper may already be freed, so Py_TYPE() must not touch it.
        if (it->second.isDying())
            continue;
        auto *foundType = Py_TYPE(reinterpret_cast<PyObject *>(it->second.borrowed()));
#else
        auto *foundType = Py_TYPE(reinterpret_cast<PyObject *>(it->second));
#endif
        if (foundType == desiredType)
            return it;
        // Same exception as in acquireWrapper(): Python-owned type state read
        // under the map lock, counted where it is taken.
        Shiboken::noteContractException(Shiboken::RawLock::WrapperMap);
        if (PyType_IsSubtype(foundType, desiredType) != 0)
            return it;
    }
    return end;
}

bool BindingManager::BindingManagerPrivate::releaseWrapperHelper(void *cptr, SbkObject *wrapper)
{
    // The wrapper argument is checked to ensure that the correct wrapper is released.
    // Returns true if the correct wrapper is found and released.
    // If wrapper argument is NULL, no such check is performed.
    const auto cit = wrapper != nullptr ? findSbkObject(cptr, wrapper) : wrapperMapper.find(cptr);
    if (cit != wrapperMapper.cend()) {
#ifdef Py_GIL_DISABLED
        // A tombstone is not released here. deallocData() comes through on
        // its way to the C++ destructor, and removing the entry there would
        // reopen exactly the window the tombstone exists for: between that
        // point and the destructor a lookup would see true absence. It falls
        // in retireWrapper(), once the destruction can no longer reach the
        // address - and with it the type reference, which is why nothing is
        // handed back here: the only entry that holds one is a tombstone, and
        // a tombstone never gets past the line above.
        if (cit->second.isDying())
            return false;
#endif
        wrapperMapper.erase(cit);
        return true;
    }
    return false;
}

#ifdef Py_GIL_DISABLED
// Installed by PySide for QObject; see the declaration for why. Atomic for
// the memory model rather than for the machine: the write happens in QtCore's
// module init, the reads happen under the wrapper map lock on other threads,
// and nothing makes those two agree. Relaxed is enough - the value points at
// code, so there is no data behind it that would need ordering.
static std::atomic<DyingConversionPredicate> dyingConversionPredicate{nullptr};

void setDyingConversionPredicate(DyingConversionPredicate predicate)
{
    dyingConversionPredicate.store(predicate, std::memory_order_relaxed);
}

// Invalidate and let go of the wrappers a falling tombstone kept. No lock may
// be held here: invalidate() walks the object graph and takes the state lock,
// and the last reference can run a destructor.
static void invalidateStrays(const std::vector<SbkObject *> &strays)
{
    for (SbkObject *stray : strays) {
        Object::invalidate(stray);
        Py_DECREF(reinterpret_cast<PyObject *>(stray));
    }
}

// Whether a compatible identity at cptr is being destroyed, and if so on
// which terms. Called with the lock held, from the registration that would
// otherwise publish a wrapper for it. \a exempt is written only for the
// Exempt answer, and names the tombstone that gave it.
BindingManager::BindingManagerPrivate::DyingIdentity
    BindingManager::BindingManagerPrivate::classifyDyingIdentity(const void *cptr,
                                                                 PyTypeObject *typeObject,
                                                                 WrapperMap::iterator *exempt)
{
    // Asked of the dying type, not of the one being published: what decides
    // is whether the destruction that is running invalidates what a
    // conversion hands out.
    const auto predicate =
        Shiboken::FreeThreading::optionEnabled(
            Shiboken::FreeThreading::DyingConversionException)
        ? dyingConversionPredicate.load(std::memory_order_relaxed) : nullptr;
    auto answer = DyingIdentity::None;
    const auto range = wrapperMapper.equal_range(cptr);
    for (auto it = range.first; it != range.second; ++it) {
        if (!it->second.isDying())
            continue;
        auto *key = it->second.typeKey();
        if (key != nullptr && key != typeObject) {
            // The same question acquireWrapper() asks, from the type the
            // entry kept rather than from the wrapper, which may be gone.
            Shiboken::noteContractException(Shiboken::RawLock::WrapperMap);
            if (PyType_IsSubtype(key, typeObject) == 0)
                continue;
        }
        if (key != nullptr && predicate != nullptr) {
            Shiboken::noteContractException(Shiboken::RawLock::WrapperMap);
            if (predicate(key)) {
                // Remember the first one, but keep looking: a co-located
                // identity that refuses outweighs one that does not.
                if (answer == DyingIdentity::None) {
                    answer = DyingIdentity::Exempt;
                    *exempt = it;
                }
                continue;
            }
        }
        return DyingIdentity::Refuse;
    }
    return answer;
}

void BindingManager::BindingManagerPrivate::markDyingHelper(void *cptr, SbkObject *wrapper)
{
    const auto range = wrapperMapper.equal_range(cptr);
    for (auto it = range.first; it != range.second; ++it) {
        if (it->second.refersTo(wrapper))
            it->second.markDying();
    }
}

void BindingManager::BindingManagerPrivate::markDying(void *cptr, SbkObject *wrapper,
                                                      const int *bases)
{
    assert(cptr);
    markDyingHelper(cptr, wrapper);
    if (bases != nullptr) {
        auto *base = static_cast<uint8_t *>(cptr);
        for (const auto *offset = bases; *offset != -1; ++offset)
            markDyingHelper(base + *offset, wrapper);
    }
}

// The wrapper is a key here and nothing else: it is freed by the time this
// runs. Filtering by it matters because the map is a multimap for co-located
// objects - two identities can share an address, and only the tombstones this
// destruction laid down may fall with it.
void BindingManager::BindingManagerPrivate::retireHelper(void *cptr, SbkObject *wrapper,
                                                         TypeRefs &types, StrayList &strays)
{
    const auto range = wrapperMapper.equal_range(cptr);
    for (auto it = range.first; it != range.second; ) {
        if (it->second.isDying() && it->second.refersTo(wrapper)) {
            types.push_back(it->second.takeTypeKey());
            const auto entryStrays = it->second.takeStrays();
            strays.insert(strays.end(), entryStrays.cbegin(), entryStrays.cend());
            it = wrapperMapper.erase(it);
        } else {
            ++it;
        }
    }
}

void BindingManager::BindingManagerPrivate::retire(void *cptr, SbkObject *wrapper,
                                                   const int *bases, TypeRefs &types,
                                                   StrayList &strays)
{
    assert(cptr);
    retireHelper(cptr, wrapper, types, strays);
    if (bases != nullptr) {
        auto *base = static_cast<uint8_t *>(cptr);
        for (const auto *offset = bases; *offset != -1; ++offset)
            retireHelper(base + *offset, wrapper, types, strays);
    }
}
#endif // Py_GIL_DISABLED

bool BindingManager::BindingManagerPrivate::releaseWrapper(void *cptr, SbkObject *wrapper,
                                                           const int *bases)
{
    assert(cptr);
    WrapperMapGuard guard(wrapperMapLock);
    const bool result = releaseWrapperHelper(cptr, wrapper);
    if (bases != nullptr) {
        auto *base = static_cast<uint8_t *>(cptr);
        for (const auto *offset = bases; *offset != -1; ++offset)
            releaseWrapperHelper(base + *offset, wrapper);
    }
    return result;
}

inline void BindingManager::BindingManagerPrivate::assignWrapperHelper(SbkObject *wrapper,
                                                                       const void *cptr)
{
    const auto it = findSbkObject(cptr, wrapper);
    if (it == wrapperMapper.cend())
#ifdef Py_GIL_DISABLED
        wrapperMapper.insert(std::make_pair(cptr, WrapperEntry(wrapper)));
#else
        wrapperMapper.insert(std::make_pair(cptr, wrapper));
#endif
}

void BindingManager::BindingManagerPrivate::assignWrapper(SbkObject *wrapper, const void *cptr,
                                                          const int *bases)
{
    assert(cptr);
    WrapperMapGuard guard(wrapperMapLock);
    assignWrapperHelper(wrapper, cptr);
    if (bases != nullptr) {
        const auto *base = static_cast<const uint8_t *>(cptr);
        for (const auto *offset = bases; *offset != -1; ++offset)
            assignWrapperHelper(wrapper, base + *offset);
    }
}

BindingManager::BindingManager() :
    m_d(new BindingManager::BindingManagerPrivate)
{
#ifdef SHIBOKEN_INSTALL_FREE_DEBUG_HOOK
    debugInstallFreeHook();
#endif
}

BindingManager::~BindingManager()
{
#ifdef SHIBOKEN_INSTALL_FREE_DEBUG_HOOK
    debugRemoveFreeHook();
#endif
#ifdef Py_GIL_DISABLED
    // No Python work here: a static destructor may run on any thread after
    // finalization has begun. Entries still in the map are abandoned.
    // See "A retired identity leaves a tombstone" in the free-threading notes.
#else
#ifndef NDEBUG
    if (Shiboken::pyVerbose() > 0)
        dumpWrapperMap();
#endif
    /* Cleanup hanging references. We just invalidate them as when
     * the BindingManager is being destroyed the interpreter is alredy
     * shutting down. */
    if (Py_IsInitialized()) {  // ensure the interpreter is still valid
        // Destroying under the lock, as this branch always did: with a GIL
        // nothing else reaches the map, and this runs at interpreter
        // shutdown. The branch above may not do it, and that difference is
        // what the contract buys.
        WrapperMapGuard guard(m_d->wrapperMapLock);
        while (!m_d->wrapperMapper.empty()) {
            Object::destroy(m_d->wrapperMapper.begin()->second, const_cast<void *>(m_d->wrapperMapper.begin()->first));
        }
        assert(m_d->wrapperMapper.empty());
    }
#endif
    delete m_d;
}

BindingManager &BindingManager::instance() {
    static BindingManager singleton;
    return singleton;
}

bool BindingManager::hasWrapper(const void *cptr) const
{
    WrapperMapGuard guard(m_d->wrapperMapLock);
#ifdef Py_GIL_DISABLED
    // A tombstone is not a wrapper. The question every caller asks is whether
    // Python holds an identity for this address that it may still use, and
    // for an identity on its way out the answer is no - the conversion that
    // follows a true here would build a wrapper for an address the destructor
    // is about to invalidate. Only a bool is read, so this stays usable from
    // a thread with no thread state.
    const auto range = m_d->wrapperMapper.equal_range(cptr);
    for (auto it = range.first; it != range.second; ++it) {
        if (!it->second.isDying())
            return true;
    }
    return false;
#else
    return m_d->wrapperMapper.find(cptr) != m_d->wrapperMapper.end();
#endif
}

bool BindingManager::hasWrapper(const void *cptr, PyTypeObject *typeObject) const
{
    // Narrowing by type reads Py_TYPE and walks tp_mro, so it needs the
    // thread attached. The untyped overload above is the one an unattached
    // caller may use: it compares addresses and nothing else.
    SBK_ASSERT_ATTACHED();
    WrapperMapGuard guard(m_d->wrapperMapLock);
    return m_d->findByType(cptr, typeObject) != m_d->wrapperMapper.cend();
}

// The MI aliases of one identity. Asked of the generated mi_init() every
// time rather than cached in the type: the function computes the offsets on
// its first call and hands out the same array afterwards, so there is
// nothing to save, and the three writers that used to fill and copy
// SbkObjectTypePrivate::mi_offsets - here, in the constructor and in type
// creation - wrote it while other threads were reading it.
static const int *miOffsets(SbkObjectTypePrivate *d, const void *cptr)
{
    return (d != nullptr && d->mi_init != nullptr && cptr != nullptr)
        ? d->mi_init(cptr) : nullptr;
}

void BindingManager::registerWrapper(SbkObject *pyObj, void *cptr)
{
    auto *instanceType = Shiboken::pyType(pyObj);
    auto *d = PepType_SOTP(instanceType);

    if (!d)
        return;

#ifdef Py_GIL_DISABLED
    // The second ending an external tombstone can get, and the only one that
    // reaches a placement-constructed object: this is the publication of a
    // *newly built* object at that address, which the allocator cannot hand
    // out before the previous destruction is over. Conversions do not count
    // and do not come through here - they go through
    // registerWrapperUnlessPresent(), where meeting a tombstone is exactly
    // what has to be refused.
    retireExternallyDying(cptr);
#endif
    m_d->assignWrapper(pyObj, cptr, miOffsets(d, cptr));
}

#ifdef Py_GIL_DISABLED
void BindingManager::unregisterWrapper(SbkObject *sbkObj, void * const *cptrs)
{
    if (cptrs == nullptr)
        cptrs = sbkObj->d->cptr;
    // The pointers may already be detached: invalidate() runs after the
    // destruction transaction has taken them out of the object. Nothing is
    // left to look up then.
    if (cptrs == nullptr)
        return;
#else
void BindingManager::unregisterWrapper(SbkObject *sbkObj)
{
    void **cptrs = sbkObj->d->cptr;
    if (cptrs == nullptr)
        return;
#endif // Py_GIL_DISABLED
    auto *sbkType = Shiboken::pyType(sbkObj);
    auto *d = PepType_SOTP(sbkType);
    int numBases = ((d && d->is_multicpp) ? getNumberOfCppBaseClasses(sbkType) : 1);

    const int *mi_offsets = miOffsets(d, cptrs[0]);
    for (int i = 0; i < numBases; ++i) {
        if (cptrs[i] != nullptr)
            m_d->releaseWrapper(cptrs[i], sbkObj, mi_offsets);
    }
}

#ifdef Py_GIL_DISABLED
// The flag is cleared without the state lock on purpose. This runs from
// runInvalidationPlan(), which asserts the state lock is *not* held: it takes
// the wrapper map lock, and a transaction must not take another lock. The
// write therefore travels with that step rather than with the transaction
// that decided it.
void BindingManager::releaseWrapper(SbkObject *sbkObj, void * const *cptrs)
{
    unregisterWrapper(sbkObj, cptrs);
    sbkObj->d->validCppObject = false;
}
#else
void BindingManager::releaseWrapper(SbkObject *sbkObj)
{
    unregisterWrapper(sbkObj);
    sbkObj->d->validCppObject = false;
}
#endif // Py_GIL_DISABLED

#ifdef Py_GIL_DISABLED
void BindingManager::runDeletionInMainThread()
{
    BindingManagerPrivate::DestructorEntries pending;
    {
        MainThreadDeleteGuard guard(m_d->deleteInMainThreadLock);
        pending.swap(m_d->deleteInMainThread);
    }
    SBK_ASSERT_NO_RAW_LOCK();
    // With the list taken over, not iterated in place: a destructor can
    // deallocate further wrappers and queue them here.
    for (const DestructorEntry &e : pending)
        e.destructor(e.cppInstance);
}

void BindingManager::addToDeletionInMainThread(const DestructorEntry &e)
{
    MainThreadDeleteGuard guard(m_d->deleteInMainThreadLock);
    m_d->deleteInMainThread.push_back(e);
}

// A retirement travels in the destructor queue rather than beside it, so that
// it keeps its place: the entries run in order, and the tombstone has to fall
// after the destructor it was waiting for.
namespace {
struct PendingRetirement
{
    SbkObject *wrapper;
    std::vector<void *> cptrs;
    PyTypeObject *type;
};

void runPendingRetirement(void *data)
{
    auto *pending = static_cast<PendingRetirement *>(data);
    BindingManager::instance().retireWrapper(pending->wrapper,
                                             pending->cptrs.data(), pending->type);
    Py_DECREF(reinterpret_cast<PyObject *>(pending->type));
    delete pending;
}
} // namespace

void BindingManager::retireAfterDeletionInMainThread(SbkObject *sbkObj,
                                                     const std::vector<void *> &cptrs,
                                                     PyTypeObject *type)
{
    // Its own reference on the type: retireWrapper() reads the type layout,
    // and the tombstone that would otherwise be holding it is not something
    // this can check - markDying() takes one only for an entry that is in
    // the map, and the caller does not know that it was.
    Py_INCREF(reinterpret_cast<PyObject *>(type));
    addToDeletionInMainThread({runPendingRetirement,
                               new PendingRetirement{sbkObj, cptrs, type}});
}
#else // Py_GIL_DISABLED
void BindingManager::runDeletionInMainThread()
{
    SBK_ASSERT_NO_RAW_LOCK();
    for (const DestructorEntry &e : m_d->deleteInMainThread)
        e.destructor(e.cppInstance);
    m_d->deleteInMainThread.clear();
}

void BindingManager::addToDeletionInMainThread(const DestructorEntry &e)
{
    m_d->deleteInMainThread.push_back(e);
}
#endif // Py_GIL_DISABLED

#ifdef Py_GIL_DISABLED
AcquiredWrapper BindingManager::acquireWrapper(const void *cptr) const
{
    SBK_ASSERT_ATTACHED();
    WrapperMapGuard guard(m_d->wrapperMapLock);
    // The map is a multimap for co-located objects, so a key can carry more
    // than one entry. Stopping at the first one that fails to acquire would
    // report "no wrapper" while a live sibling sits right behind it - and the
    // callers answer that by registering yet another wrapper for the same
    // pointer.
    const auto range = m_d->wrapperMapper.equal_range(cptr);
    for (auto it = range.first; it != range.second; ++it) {
        if (it->second.isDying())
            continue;
        if (auto *wrapper = it->second.acquire())
            return AcquiredWrapper::fromOwned(wrapper);
    }
    return {};
}

AcquiredWrapper BindingManager::acquireWrapper(const void *cptr, PyTypeObject *typeObject) const
{
    SBK_ASSERT_ATTACHED();
    WrapperMapGuard guard(m_d->wrapperMapLock);
    // Same as above: keep looking past an entry that cannot be acquired.
    // Reading the type through the borrowed pointer is sound here: taking an
    // entry out of the map is the first thing deallocation does, and it needs
    // this very lock, so nothing in the map has been freed yet.
    const auto range = m_d->wrapperMapper.equal_range(cptr);
    for (auto it = range.first; it != range.second; ++it) {
        if (it->second.isDying())
            continue;
        auto *found = reinterpret_cast<PyObject *>(it->second.borrowed());
        auto *foundType = Py_TYPE(found);
        if (foundType == typeObject) {
            if (auto *wrapper = it->second.acquire())
                return AcquiredWrapper::fromOwned(wrapper);
            continue;
        }
        // Reading Python-owned type state under the lock: the contract's
        // second exception, counted like the first one and where it is
        // really taken, not once per call.
        Shiboken::noteContractException(Shiboken::RawLock::WrapperMap);
        if (PyType_IsSubtype(foundType, typeObject) == 0)
            continue;
        if (auto *wrapper = it->second.acquire())
            return AcquiredWrapper::fromOwned(wrapper);
    }
    return {};
}

BindingManager::Registration
    BindingManager::registerWrapperUnlessPresent(SbkObject *pyObj, void *cptr,
                                                 PyTypeObject *typeObject)
{
    SBK_ASSERT_ATTACHED();
    auto *instanceType = Shiboken::pyType(pyObj);
    auto *d = PepType_SOTP(instanceType);
    if (d == nullptr)
        return {};

    // The lookup and the insertion have to be one hold of the lock. It is
    // recursive, so the two steps below may take it again; what matters is
    // that nothing between them can slip in and register the same pointer.
    WrapperMapGuard guard(m_d->wrapperMapLock);

    if (auto winner = acquireWrapper(cptr, typeObject))
        return {std::move(winner), false};

    // A tombstone for a compatible identity: the C++ object is still there,
    // but its destructor is going to run, and a wrapper published now would
    // outlive it. This is the half that removing the entry early does not
    // fix - the window between the removal and the destructor.
    WrapperMap::iterator exempt;
    switch (m_d->classifyDyingIdentity(cptr, typeObject, &exempt)) {
    case BindingManagerPrivate::DyingIdentity::None:
        break;
    case BindingManagerPrivate::DyingIdentity::Refuse:
        return {{}, true};
    case BindingManagerPrivate::DyingIdentity::Exempt:
        // The exception destroyed(QObject *) needs. The wrapper is handed out
        // but stays out of the map: an entry here would survive the tombstone
        // and become the canonical wrapper for whatever the allocator puts at
        // this address next. The tombstone keeps it instead, and invalidates
        // it when it falls, so the conversion is usable exactly as long as
        // the destruction it belongs to is running.
        if (Shiboken::FreeThreading::optionEnabled(Shiboken::FreeThreading::DyingStrays)) {
            if (auto *stray = exempt->second.acquireStray(typeObject))
                return {AcquiredWrapper::fromOwned(stray), false};
            exempt->second.addStray(pyObj);
            return {};
        }
        break;
    }

    // The registration registerWrapper() does. mi_init() computes offsets
    // from the C++ pointer and runs no Python, so it may run under the lock.
    m_d->assignWrapper(pyObj, cptr, miOffsets(d, cptr));
    return {};
}

void BindingManager::markWrapperDying(SbkObject *sbkObj, void * const *cptrs)
{
    if (cptrs == nullptr)
        cptrs = sbkObj->d->cptr;
    if (cptrs == nullptr)
        return;
    auto *sbkType = Shiboken::pyType(sbkObj);
    auto *d = PepType_SOTP(sbkType);
    const int numBases = ((d && d->is_multicpp) ? getNumberOfCppBaseClasses(sbkType) : 1);
    const int *mi_offsets = miOffsets(d, cptrs[0]);

    // One hold for every alias of the identity, so no reader can see half of
    // it converted.
    WrapperMapGuard guard(m_d->wrapperMapLock);
    for (int i = 0; i < numBases; ++i) {
        if (cptrs[i] != nullptr)
            m_d->markDying(cptrs[i], sbkObj, mi_offsets);
    }
}

// A destruction C++ started. The binding hears it begin, in the generated
// wrapper destructor, and is never called again - so nothing can take the
// tombstone away the way the deallocator does, and everything retirement
// needs has to be kept here instead of read off an object that is gone.
void BindingManager::markExternallyDying(SbkObject *sbkObj, void **cptrs,
                                         PyTypeObject *type)
{
    if (cptrs == nullptr)
        return;
    if (cptrs[0] == nullptr) {
        delete[] cptrs;
        return;
    }
    // An address that already carries one: the previous destruction never
    // got either of its two endings. Retire it now - a second destruction at
    // the same address is proof that the first one is over.
    retireExternallyDying(cptrs[0]);

    markWrapperDying(sbkObj, cptrs);
    Py_INCREF(reinterpret_cast<PyObject *>(type));
    WrapperMapGuard guard(m_d->wrapperMapLock);
    m_d->externalDying.insert({cptrs[0], {sbkObj, cptrs, type}});
}

bool BindingManager::hasExternallyDying(const void *cptr) const
{
    WrapperMapGuard guard(m_d->wrapperMapLock);
    return m_d->externalDying.find(cptr) != m_d->externalDying.end();
}

void BindingManager::retireExternallyDying(void *cptr)
{
    if (cptr == nullptr)
        return;
    BindingManagerPrivate::ExternalDestruction pending{};
    {
        WrapperMapGuard guard(m_d->wrapperMapLock);
        const auto it = m_d->externalDying.find(cptr);
        if (it == m_d->externalDying.end())
            return;
        pending = it->second;
        m_d->externalDying.erase(it);
    }
    // Outside that hold, because retireWrapper() takes the lock itself and
    // invalidates strays with none held.
    retireWrapper(pending.wrapper, pending.cptrs, pending.type);
    delete[] pending.cptrs;
    Py_DECREF(reinterpret_cast<PyObject *>(pending.type));
}

void BindingManager::retireWrapper(SbkObject *sbkObj, void * const *cptrs,
                                   PyTypeObject *type)
{
    if (cptrs == nullptr)
        return;
    auto *d = PepType_SOTP(type);
    const int numBases = ((d && d->is_multicpp) ? getNumberOfCppBaseClasses(type) : 1);
    // cptrs[0] may point at freed memory by now - that is the whole point of
    // retirement. mi_init() does not read it: it computed the offsets once,
    // at registration, and every call after that returns the same array. The
    // pointer is passed, never dereferenced.
    const int *mi_offsets = miOffsets(d, cptrs[0]);

    // The entries hold a reference to their type, and a tombstone also holds
    // the wrappers it let through. Collected under the lock, dealt with after
    // it: invalidation walks the object graph and takes the state lock, and a
    // decref can run a destructor.
    BindingManagerPrivate::TypeRefs types;
    BindingManagerPrivate::StrayList strays;
    {
        WrapperMapGuard guard(m_d->wrapperMapLock);
        for (int i = 0; i < numBases; ++i) {
            if (cptrs[i] != nullptr)
                m_d->retire(cptrs[i], sbkObj, mi_offsets, types, strays);
        }
    }
    // This is the other end of the dying-conversion exception: the address is
    // out of reach for good now, so what was handed out over it may no longer
    // claim to be valid. Nothing else can do it - a stray was never in the
    // map, which is where every other invalidation path looks.
    invalidateStrays(strays);
    for (auto *t : types)
        Py_XDECREF(reinterpret_cast<PyObject *>(t));
}
#else // Py_GIL_DISABLED
SbkObject *BindingManager::retrieveWrapper(const void *cptr) const
{
    WrapperMapGuard guard(m_d->wrapperMapLock);
    auto iter = m_d->wrapperMapper.find(cptr);
    if (iter == m_d->wrapperMapper.end())
        return nullptr;
    return iter->second;
}

SbkObject *BindingManager::retrieveWrapper(const void *cptr, PyTypeObject *typeObject) const
{
    WrapperMapGuard guard(m_d->wrapperMapLock);
    const auto it = m_d->findByType(cptr, typeObject);
    return it != m_d->wrapperMapper.cend() ? it->second : nullptr;
}
#endif // Py_GIL_DISABLED

PyObject *BindingManager::getOverride(SbkObject *wrapper, PyObject *pyMethodName)
{
    auto *obWrapper = reinterpret_cast<PyObject *>(wrapper);

    // Two PyObject_GetAttr() calls below, plus an mro walk: attribute access
    // runs descriptors and can re-enter the bindings, and none of it may be
    // reached from a thread that has no thread state.
    SBK_ASSERT_ATTACHED();
    SBK_ASSERT_NO_RAW_LOCK();
    Shiboken::AutoDecRef method(PyObject_GetAttr(obWrapper, pyMethodName));
    if (method.isNull())
        return nullptr;

    PyObject *function = nullptr;

    // PYSIDE-1523: PyMethod_Check is not accepting compiled methods, we do this rather
    // crude check for them.
    // PYSIDE-535: This macro is redefined in a compatible way in pep384
    if (PyMethod_Check(method) != 0) {
        if (PyMethod_Self(method) != obWrapper)
            return nullptr;
        function = PyMethod_Function(method);
#ifdef Py_GIL_DISABLED
        Py_INCREF(function);
#endif
    } else if (isCompiledMethod(method)) {
        Shiboken::AutoDecRef im_self(PyObject_GetAttr(method, PyName::im_self()));
        // Not retaining a reference inline with what PyMethod_GET_SELF does.
        if (im_self.object() != obWrapper)
            return nullptr;
        function = PyObject_GetAttr(method, PyName::im_func());
#ifdef Py_GIL_DISABLED
        // Owned; functionRef below releases it.
#else
        // Not retaining a reference inline with what PyMethod_GET_FUNCTION does.
        Py_DECREF(function);
#endif
    } else {
        return nullptr;
    }

#ifdef Py_GIL_DISABLED
    // Owned across the walk, which runs Python; each return hands it over.
    // See "A virtual dispatch owns the override it found" in the free-threading notes.
    AutoDecRef functionRef(function);
    // A snapshot: the loop runs Python code (PepType_GetDict(), key
    // comparisons), where another thread can assign __bases__.
    PepMroRef mro(Py_TYPE(obWrapper));
    if (mro.isNull())
        return nullptr;
    // A test assigns __bases__ here from another thread.
    SBK_FAILPOINT("mro-after-snapshot");
    bool defaultFound = false;
    // The first class in the mro (index 0) is the class being checked and it should not be tested.
    // The last class in the mro (size - 1) is the base Python object class which should not be tested also.
    for (Py_ssize_t idx = 1, size = PyTuple_Size(mro.object()); idx < size - 1; ++idx) {
        auto *parent = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(mro.object(), idx));
        AutoDecRef parentDict(PepType_GetDict(parent));
        if (parentDict) {
            AutoDecRef defaultMethod(PepDict_GetItemOwned(parentDict.object(), pyMethodName));
            if (!defaultMethod.isNull()) {
                defaultFound = true;
                if (function != defaultMethod.object())
                    return functionRef.release();
            }
        }
    }
#else
    PyObject *mro = Py_TYPE(obWrapper)->tp_mro;
    bool defaultFound = false;
    // The first class in the mro (index 0) is the class being checked and it should not be tested.
    // The last class in the mro (size - 1) is the base Python object class which should not be tested also.
    for (Py_ssize_t idx = 1, size = PyTuple_Size(mro); idx < size - 1; ++idx) {
        auto *parent = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(mro, idx));
        AutoDecRef parentDict(PepType_GetDict(parent));
        if (parentDict) {
            if (PyObject *defaultMethod = PyDict_GetItem(parentDict.object(), pyMethodName)) {
                defaultFound = true;
                if (function != defaultMethod)
                    return function;
            }
        }
    }
#endif
    // PYSIDE-2255: If no default method was found, use the method.
    if (!defaultFound)
#ifdef Py_GIL_DISABLED
        return functionRef.release();
#else
        return function;
#endif
    return nullptr;
}

void BindingManager::addClassInheritance(const InheritanceEdge *edges, std::size_t count)
{
    std::vector<Graph::Edge> graphEdges;
    graphEdges.reserve(count);
    for (std::size_t i = 0; i < count; ++i)
        graphEdges.emplace_back(GraphNode(edges[i].parent), GraphNode(edges[i].child));
    m_d->classHierarchy.addEdges(graphEdges);
}

BindingManager::TypeCptrPair BindingManager::findDerivedType(void *cptr, PyTypeObject *type) const
{
    return m_d->classHierarchy.identifyType(cptr, type, type);
}

void *BindingManager::runTypeDiscovery(void *cptr, PyTypeObject *probeType, PyTypeObject *type)
{
    auto *sotp = PepType_SOTP(probeType);
    assert(sotp != nullptr);
    return sotp->type_discovery != nullptr ? sotp->type_discovery(cptr, type) : nullptr;
}

// FIXME PYSIDE7: remove, just for compatibility
PyTypeObject *BindingManager::resolveType(void **cptr, PyTypeObject *type)
{
    auto result = findDerivedType(*cptr, type);
    if (result.second != nullptr)
        *cptr = result.second;
    return result.first != nullptr ? result.first : type;
}

#ifdef Py_GIL_DISABLED
std::vector<AcquiredWrapper> BindingManager::getAllPyObjects()
{
    std::vector<AcquiredWrapper> result;
    // Multiple inheritance registers one wrapper under several C++ pointers,
    // so the same wrapper can be met more than once. The set the build with a
    // GIL returns does that for free.
    std::set<const SbkObject *> seen;
    WrapperMapGuard guard(m_d->wrapperMapLock);
    for (const auto &entry : m_d->wrapperMapper) {
        // Taking a reference under the lock is allowed - it runs no Python.
        auto ref = AcquiredWrapper::fromOwned(entry.second.acquire());
        if (ref.isNull() || !seen.insert(ref.object()).second)
            continue;   // already deallocating, or already collected
        result.push_back(std::move(ref));
    }
    return result;
}
#else // Py_GIL_DISABLED
std::set<PyObject *> BindingManager::getAllPyObjects()
{
    std::set<PyObject *> pyObjects;
    WrapperMapGuard guard(m_d->wrapperMapLock);
    const WrapperMap &wrappersMap = m_d->wrapperMapper;
    auto it = wrappersMap.begin();
    for (; it != wrappersMap.end(); ++it)
        pyObjects.insert(reinterpret_cast<PyObject *>(it->second));

    return pyObjects;
}
#endif // Py_GIL_DISABLED

void BindingManager::visitAllPyObjects(ObjectVisitor visitor, void *data)
{
#ifdef Py_GIL_DISABLED
    // Collect first, visit afterwards. The visitor runs Python and C++
    // destructors, which take this lock again and mutate the map, so it must
    // not run underneath it - and the references taken here are what keeps
    // the collected wrappers alive until their turn comes.
    std::vector<AcquiredWrapper> wrappers = getAllPyObjects();
    SBK_ASSERT_NO_RAW_LOCK();
    for (const auto &wrapper : wrappers)
        visitor(wrapper.object(), data);
#else
    // The map has its own lock because C++ reaches it without a thread state -
    // releaseWrapper() runs from destructors. The visitor stays outside it: it
    // runs Python and C++ destructors, which take it again and mutate the map.
    WrapperMap copy;
    {
        WrapperMapGuard guard(m_d->wrapperMapLock);
        copy = m_d->wrapperMapper;
    }
    for (const auto &p : copy) {
        auto *o = p.second;
        bool present = false;
        SBK_ASSERT_NO_RAW_LOCK();
        {
            WrapperMapGuard guard(m_d->wrapperMapLock);
            present = m_d->findSbkObject(p.first, o) != m_d->wrapperMapper.cend();
        }
        if (present)
            visitor(o, data);
    }
#endif // Py_GIL_DISABLED
}

bool BindingManager::dumpTypeGraph(const char *fileName) const
{
    return m_d->classHierarchy.dumpTypeGraph(fileName);
}

void BindingManager::dumpWrapperMap()
{
    // The hierarchy before the map lock: the two locks have a rank each, and
    // taking the lower-ranked one underneath would be the inversion the rank
    // exists to prevent.
    const auto typeCount = Graph::nodeSet(*m_d->classHierarchy.edges()).size();

    WrapperMapGuard guard(m_d->wrapperMapLock);
    const auto &wrapperMap = m_d->wrapperMapper;
    std::cerr <<  "-------------------------------\n"
        << "WrapperMap size: " << wrapperMap.size() << " Types: "
        << typeCount << '\n';
    for (auto it : wrapperMap) {
#ifdef Py_GIL_DISABLED
        // A tombstone is printed from what the entry kept, never from the
        // wrapper: that one is freed while the entry still stands.
        if (it.second.isDying()) {
            auto *key = it.second.typeKey();
            std::cerr << "key: " << it.first << ", tombstone ("
                << (key != nullptr ? PepType_GetFullyQualifiedNameStr(key)
                                   : "<no type>") << ')';
            if (const auto strays = it.second.strayCount())
                std::cerr << ", " << strays << " stray(s)";
            std::cerr << '\n';
            continue;
        }
        // Borrowed, but under the lock and only read - see acquireWrapper().
        auto *ob = reinterpret_cast<PyObject *>(it.second.borrowed());
#else
        auto *ob = reinterpret_cast<PyObject *>(it.second);
#endif
        std::cerr << "key: " << it.first << ", value: "
            << static_cast<const void *>(ob) << " ("
            << PepType_GetFullyQualifiedNameStr(Py_TYPE(ob)) << ", refcnt: "
            << Py_REFCNT(ob) << ")\n";
    }
    std::cerr << "-------------------------------\n";
}

static bool isPythonType(PyTypeObject *type)
{
    // This is a type which should be called by multiple inheritance.
    // It is either a pure Python type or a derived PySide type.
    return !ObjectType::checkType(type) || ObjectType::isUserType(type);
}

bool callInheritedInit(PyObject *self, PyObject *args, PyObject *kwds,
                       const Module::TypeInitStruct &typeStruct)
{
    using Shiboken::AutoDecRef;

    static PyObject *const _init = String::createStaticString("__init__");
    static PyObject *objectInit =
        PyObject_GetAttr(reinterpret_cast<PyObject *>(&PyBaseObject_Type), _init);

    // A native C++ self cannot have multiple inheritance.
    if (!Object::isUserType(self))
        return false;

    auto *startType = Py_TYPE(self);
#ifdef Py_GIL_DISABLED
    // Held past the loops: the type they stop at goes to PyObject_GetAttr().
    PepMroRef mro(startType);
    if (mro.isNull())
        return false;
    Py_ssize_t idx = 0;
    const Py_ssize_t n = PyTuple_Size(mro.object());
    /* No need to check the last one: it's gonna be skipped anyway.  */
    const char *className = typeStruct.fullName;
    for ( ; idx + 1 < n; ++idx) {
        auto *lookType = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(mro.object(), idx));
        if (std::strcmp(className, PepType_GetFullyQualifiedNameStr(lookType)) == 0)
            break;
    }
    // We are now at the first non-Python class `QObject`.
    // mro: ('C', 'A', 'QObject', 'Object', 'B', 'object')
    // We want to catch class `B` and call its `__init__`.
    for (idx += 1; idx + 1 < n; ++idx) {
        auto *t = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(mro.object(), idx));
        if (isPythonType(t))
            break;
    }
    if (idx >= n)
        return false;

    auto *obSubType = PyTuple_GetItem(mro.object(), idx);
#else
    auto *mro = startType->tp_mro;
    Py_ssize_t idx = 0;
    const Py_ssize_t n = PyTuple_Size(mro);
    /* No need to check the last one: it's gonna be skipped anyway.  */
    const char *className = typeStruct.fullName;
    for ( ; idx + 1 < n; ++idx) {
        auto *lookType = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(mro, idx));
        if (std::strcmp(className, PepType_GetFullyQualifiedNameStr(lookType)) == 0)
            break;
    }
    // We are now at the first non-Python class `QObject`.
    // mro: ('C', 'A', 'QObject', 'Object', 'B', 'object')
    // We want to catch class `B` and call its `__init__`.
    for (idx += 1; idx + 1 < n; ++idx) {
        auto *t = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(mro, idx));
        if (isPythonType(t))
            break;
    }
    if (idx >= n)
        return false;

    auto *obSubType = PyTuple_GetItem(mro, idx);
#endif
    auto *subType = reinterpret_cast<PyTypeObject *>(obSubType);
    if (subType == &PyBaseObject_Type)
        return false;
    AutoDecRef func(PyObject_GetAttr(obSubType, _init));
    // PYSIDE-2654: If this has no implementation then we get object.__init__
    //              but that is the same case like above.
    if (func == objectInit)
        return false;
    // PYSIDE-2294: We need to explicitly ignore positional args in a mixin class.
    SBK_UNUSED(args);
    AutoDecRef newArgs(PyTuple_New(1));
    auto *newArgsOb = newArgs.object();
    Py_INCREF(self);
    PyTuple_SetItem(newArgsOb, 0, self);
    // Note: This can fail, so please always check the error status.
    AutoDecRef result(PyObject_Call(func, newArgs, kwds));
    return true;
}

} // namespace Shiboken
