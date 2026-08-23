// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "bindingmanager.h"

#include "autodecref.h"
#include "basewrapper.h"
#include "basewrapper_p.h"
#include "helper.h"
#include "sbkfeature_base.h"
#include "sbkmodule.h"
#include "sbkpep.h"
#include "sbkstaticstrings.h"
#include "sbkstring.h"

#include <cstddef>
#include <cstring>
#include <fstream>
#include <iostream>
#include <mutex>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#ifdef Py_GIL_DISABLED
#  include <cassert>
#  include <utility>

// Taking a reference needs an attached thread state: PyUnstable_TryIncRef
// touches the interpreter's refcount bookkeeping. The precondition used to be
// documentation only, which is how it got broken once already. PyGILState_Check
// is not in the limited API, so the check only exists where we develop.
#  if !defined(Py_LIMITED_API) && !defined(NDEBUG)
#    define SBK_ASSERT_ATTACHED() assert(PyGILState_Check())
#  else
#    define SBK_ASSERT_ATTACHED() ((void)0)
#  endif
#endif // Py_GIL_DISABLED

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
    SbkObject *acquire() const
    {
        if (PyUnstable_TryIncRef(reinterpret_cast<PyObject *>(m_obj)) == 0)
            return nullptr;
        return m_obj;
    }

    /// Identity check that does not acquire, for findSbkObject().
    bool refersTo(SbkObject *obj) const { return m_obj == obj; }

private:
    SbkObject *m_obj = nullptr;   // borrowed, as before
};

// Mapping of C++ address to wrapper. We use a multimap to allow for co-located
// objects, which happens for example for the first field of a struct.
using WrapperMap = std::unordered_multimap<const void *, WrapperEntry>;
#else // Py_GIL_DISABLED
// Mapping of C++ address to wrapper. We use a multimap to allow for co-located
// objects, which happens for example for the first field of a struct.
using WrapperMap = std::unordered_multimap<const void *, SbkObject *>;
#endif // Py_GIL_DISABLED

template <class NodeType>
class BaseGraph
{
public:
    using NodeList = std::vector<NodeType>;
    using NodeSet = std::unordered_set<NodeType>;

    using Edges = std::unordered_map<NodeType, NodeList>;

    Edges m_edges;

    BaseGraph() = default;

    void addEdge(NodeType from, NodeType to)
    {
        m_edges[from].push_back(to);
    }

    NodeSet nodeSet() const
    {
        NodeSet result;
        for (const auto &p : m_edges) {
            result.insert(p.first);
            for (const auto node2 : p.second)
                result.insert(node2);
        }
        return result;
    }
};

class Graph : public BaseGraph<GraphNode>
{
public:
    using TypeCptrPair = BindingManager::TypeCptrPair;

    TypeCptrPair identifyType(void *cptr, PyTypeObject *type, PyTypeObject *baseType) const
    {
        return identifyType(cptr, GraphNode(type->tp_name), type, baseType);
    }

    bool dumpTypeGraph(const char *fileName) const;

private:
    TypeCptrPair identifyType(void *cptr, const GraphNode &typeNode, PyTypeObject *type,
                              PyTypeObject *baseType) const;
};

Graph::TypeCptrPair Graph::identifyType(void *cptr,
                                        const GraphNode &typeNode, PyTypeObject *type,
                                        PyTypeObject *baseType) const
{
    assert(typeNode.initStruct != nullptr || type != nullptr);
    auto edgesIt = m_edges.find(typeNode);
    if (edgesIt != m_edges.end()) {
        const NodeList &adjNodes = edgesIt->second;
        for (const auto &node : adjNodes) {
            auto newType = identifyType(cptr, node, nullptr, baseType);
            if (newType.first != nullptr)
                return newType;
        }
    }

    if (type == nullptr) {
        if (typeNode.initStruct->type == nullptr) // Layzily create type
            type = Shiboken::Module::get(*typeNode.initStruct);
        else
            type = typeNode.initStruct->type;
    }

    auto *sotp = PepType_SOTP(type);
    if (sotp->type_discovery != nullptr) {
        if (void *derivedCPtr = sotp->type_discovery(cptr, baseType))
            return {type, derivedCPtr};
    }
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
    std::ofstream file(fileName);
    if (!file.good())
        return false;

    file << "digraph D {\n";

    // Define nodes with short names
    for (const auto &node : nodeSet())
        formatDotNode(node.name, file);

    // Write edges
    for (const auto &p : m_edges) {
        const auto &node1 = p.first;
        const NodeList &nodeList = p.second;
        for (const auto &node2 : nodeList)
            file << "    \"" << node2.name << "\" -> \"" << node1.name << "\"\n";
    }
    file << "}\n";
    return true;
}

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

    WrapperMap::const_iterator findSbkObject(const void *cptr, SbkObject *wrapper) const;
    WrapperMap::const_iterator findByType(const void *cptr, PyTypeObject *desiredType) const;

    bool releaseWrapper(void *cptr, SbkObject *wrapper, const int *bases = nullptr);
    bool releaseWrapperHelper(void *cptr, SbkObject *wrapper);

    void assignWrapper(SbkObject *wrapper, const void *cptr, const int *bases = nullptr);
    void assignWrapperHelper(SbkObject *wrapper, const void *cptr);
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
        auto *foundType = Py_TYPE(reinterpret_cast<PyObject *>(it->second.borrowed()));
#else
        auto *foundType = Py_TYPE(reinterpret_cast<PyObject *>(it->second));
#endif
        if (foundType == desiredType || PyType_IsSubtype(foundType, desiredType) != 0)
            return it;
    }
    return end;
}

bool BindingManager::BindingManagerPrivate::releaseWrapperHelper(void *cptr, SbkObject *wrapper)
{
    // The wrapper argument is checked to ensure that the correct wrapper is released.
    // Returns true if the correct wrapper is found and released.
    // If wrapper argument is NULL, no such check is performed.
    const auto it = wrapper != nullptr ? findSbkObject(cptr, wrapper) : wrapperMapper.find(cptr);
    if (it != wrapperMapper.cend()) {
        wrapperMapper.erase(it);
        return true;
    }
    return false;
}

bool BindingManager::BindingManagerPrivate::releaseWrapper(void *cptr, SbkObject *wrapper,
                                                           const int *bases)
{
    assert(cptr);
    std::lock_guard<std::recursive_mutex> guard(wrapperMapLock);
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
    std::lock_guard<std::recursive_mutex> guard(wrapperMapLock);
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
#ifndef NDEBUG
    if (Shiboken::pyVerbose() > 0)
        dumpWrapperMap();
#endif
    /* Cleanup hanging references. We just invalidate them as when
     * the BindingManager is being destroyed the interpreter is alredy
     * shutting down. */
    if (Py_IsInitialized()) {  // ensure the interpreter is still valid
#ifdef Py_GIL_DISABLED
        // One entry at a time, and destroy() outside the lock - the same rule
        // visitAllPyObjects() follows: destroy() runs Python and C++
        // destructors, which take this lock again, and a decref underneath a
        // non-detaching mutex can stall a stop-the-world pause.
        while (true) {
            AcquiredWrapper wrapper;
            const void *key = nullptr;
            {
                std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
                if (m_d->wrapperMapper.empty())
                    break;
                const auto it = m_d->wrapperMapper.begin();
                key = it->first;
                wrapper = AcquiredWrapper::fromOwned(it->second.acquire());
                if (wrapper.isNull()) {
                    // Being deallocated elsewhere; destroy() would not reach
                    // it and the loop would never end.
                    m_d->wrapperMapper.erase(it);
                    continue;
                }
            }
            Object::destroy(wrapper.object(), const_cast<void *>(key));
        }
#else // Py_GIL_DISABLED
        std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
        while (!m_d->wrapperMapper.empty()) {
            Object::destroy(m_d->wrapperMapper.begin()->second, const_cast<void *>(m_d->wrapperMapper.begin()->first));
        }
#endif // Py_GIL_DISABLED
        assert(m_d->wrapperMapper.empty());
    }
    delete m_d;
}

BindingManager &BindingManager::instance() {
    static BindingManager singleton;
    return singleton;
}

bool BindingManager::hasWrapper(const void *cptr) const
{
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
    return m_d->wrapperMapper.find(cptr) != m_d->wrapperMapper.end();
}

bool BindingManager::hasWrapper(const void *cptr, PyTypeObject *typeObject) const
{
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
    return m_d->findByType(cptr, typeObject) != m_d->wrapperMapper.cend();
}

void BindingManager::registerWrapper(SbkObject *pyObj, void *cptr)
{
    auto *instanceType = Shiboken::pyType(pyObj);
    auto *d = PepType_SOTP(instanceType);

    if (!d)
        return;

    if (d->mi_init && !d->mi_offsets)
        d->mi_offsets = d->mi_init(cptr);
    m_d->assignWrapper(pyObj, cptr, d->mi_offsets);
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

    const int *mi_offsets = d != nullptr ? d->mi_offsets : nullptr;
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

void BindingManager::runDeletionInMainThread()
{
    for (const DestructorEntry &e : m_d->deleteInMainThread)
        e.destructor(e.cppInstance);
    m_d->deleteInMainThread.clear();
}

void BindingManager::addToDeletionInMainThread(const DestructorEntry &e)
{
    m_d->deleteInMainThread.push_back(e);
}

#ifdef Py_GIL_DISABLED
AcquiredWrapper BindingManager::acquireWrapper(const void *cptr) const
{
    SBK_ASSERT_ATTACHED();
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
    // The map is a multimap for co-located objects, so a key can carry more
    // than one entry. Stopping at the first one that fails to acquire would
    // report "no wrapper" while a live sibling sits right behind it - and the
    // callers answer that by registering yet another wrapper for the same
    // pointer.
    const auto range = m_d->wrapperMapper.equal_range(cptr);
    for (auto it = range.first; it != range.second; ++it) {
        if (auto *wrapper = it->second.acquire())
            return AcquiredWrapper::fromOwned(wrapper);
    }
    return {};
}

AcquiredWrapper BindingManager::acquireWrapper(const void *cptr, PyTypeObject *typeObject) const
{
    SBK_ASSERT_ATTACHED();
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
    // Same as above: keep looking past an entry that cannot be acquired.
    // Reading the type through the borrowed pointer is sound here: taking an
    // entry out of the map is the first thing deallocation does, and it needs
    // this very lock, so nothing in the map has been freed yet.
    const auto range = m_d->wrapperMapper.equal_range(cptr);
    for (auto it = range.first; it != range.second; ++it) {
        auto *found = reinterpret_cast<PyObject *>(it->second.borrowed());
        auto *foundType = Py_TYPE(found);
        if (foundType != typeObject && PyType_IsSubtype(foundType, typeObject) == 0)
            continue;
        if (auto *wrapper = it->second.acquire())
            return AcquiredWrapper::fromOwned(wrapper);
    }
    return {};
}

AcquiredWrapper BindingManager::registerWrapperUnlessPresent(SbkObject *pyObj, void *cptr,
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
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);

    if (auto winner = acquireWrapper(cptr, typeObject))
        return winner;

    // The registration registerWrapper() does. mi_init() computes offsets
    // from the C++ pointer and runs no Python, so it may run under the lock.
    if (d->mi_init && !d->mi_offsets)
        d->mi_offsets = d->mi_init(cptr);
    m_d->assignWrapper(pyObj, cptr, d->mi_offsets);
    return {};
}
#else // Py_GIL_DISABLED
SbkObject *BindingManager::retrieveWrapper(const void *cptr) const
{
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
    auto iter = m_d->wrapperMapper.find(cptr);
    if (iter == m_d->wrapperMapper.end())
        return nullptr;
    return iter->second;
}

SbkObject *BindingManager::retrieveWrapper(const void *cptr, PyTypeObject *typeObject) const
{
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
    const auto it = m_d->findByType(cptr, typeObject);
    return it != m_d->wrapperMapper.cend() ? it->second : nullptr;
}
#endif // Py_GIL_DISABLED

PyObject *BindingManager::getOverride(SbkObject *wrapper, PyObject *pyMethodName)
{
    auto *obWrapper = reinterpret_cast<PyObject *>(wrapper);

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
    } else if (isCompiledMethod(method)) {
        Shiboken::AutoDecRef im_self(PyObject_GetAttr(method, PyName::im_self()));
        // Not retaining a reference inline with what PyMethod_GET_SELF does.
        if (im_self.object() != obWrapper)
            return nullptr;
        function = PyObject_GetAttr(method, PyName::im_func());
        // Not retaining a reference inline with what PyMethod_GET_FUNCTION does.
        Py_DECREF(function);
    } else {
        return nullptr;
    }

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
    // PYSIDE-2255: If no default method was found, use the method.
    if (!defaultFound)
        return function;
    return nullptr;
}

void BindingManager::addClassInheritance(Module::TypeInitStruct *parent,
                                         Module::TypeInitStruct *child)
{
    m_d->classHierarchy.addEdge(GraphNode(parent), GraphNode(child));
}

BindingManager::TypeCptrPair BindingManager::findDerivedType(void *cptr, PyTypeObject *type) const
{
    return m_d->classHierarchy.identifyType(cptr, type, type);
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
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
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
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
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
    for (const auto &wrapper : wrappers)
        visitor(wrapper.object(), data);
#else
    // The map has its own lock because C++ reaches it without a thread state -
    // releaseWrapper() runs from destructors. The visitor stays outside it: it
    // runs Python and C++ destructors, which take it again and mutate the map.
    WrapperMap copy;
    {
        std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
        copy = m_d->wrapperMapper;
    }
    for (const auto &p : copy) {
        auto *o = p.second;
        bool present = false;
        {
            std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
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
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
    const auto &wrapperMap = m_d->wrapperMapper;
    std::cerr <<  "-------------------------------\n"
        << "WrapperMap size: " << wrapperMap.size() << " Types: "
        << m_d->classHierarchy.nodeSet().size() << '\n';
    for (auto it : wrapperMap) {
#ifdef Py_GIL_DISABLED
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
                       Module::TypeInitStruct typeStruct)
{
    using Shiboken::AutoDecRef;

    static PyObject *const _init = String::createStaticString("__init__");
    static PyObject *objectInit =
        PyObject_GetAttr(reinterpret_cast<PyObject *>(&PyBaseObject_Type), _init);

    // A native C++ self cannot have multiple inheritance.
    if (!Object::isUserType(self))
        return false;

    auto *startType = Py_TYPE(self);
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
