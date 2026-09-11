// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef BINDINGMANAGER_H
#define BINDINGMANAGER_H

#include "sbkpython.h"
#include "shibokenmacros.h"
#include "sbkdestructorentry.h"
#ifdef Py_GIL_DISABLED
#  include "sbkacquiredwrapper.h"
#endif

#include <set>
#include <utility>
#include <vector>

struct SbkObject;

namespace Shiboken
{

namespace Module {
struct TypeInitStruct;
}

using ObjectVisitor = void (*)(SbkObject *, void *);

#ifdef Py_GIL_DISABLED
/// Whether a type invalidates its instances' wrappers itself and may
/// therefore be converted while one of them is dying. Qt emits
/// `destroyed(QObject *)` from `~QObject` and PySide invalidates the wrapper
/// right after the signal, so a tombstone must not refuse that conversion; a
/// type with no such mechanism keeps it. libshiboken does not know what a
/// QObject is, so PySide installs the predicate with QtCore.
using DyingConversionPredicate = bool (*)(PyTypeObject *);
LIBSHIBOKEN_API void setDyingConversionPredicate(DyingConversionPredicate predicate);
#endif

class LIBSHIBOKEN_API BindingManager
{
public:
    BindingManager(const BindingManager &) = delete;
    BindingManager(BindingManager &&) = delete;
    BindingManager &operator=(const BindingManager &) = delete;
    BindingManager &operator=(BindingManager &&) = delete;

    static BindingManager &instance();

    bool hasWrapper(const void *cptr, PyTypeObject *typeObject) const;
    bool hasWrapper(const void *cptr) const;

    /// Enter a wrapper in the map. One step of a publication: generated code
    /// goes through Shiboken::Object::commitConstruction(), which takes the
    /// slot and enters the map as one operation.
    void registerWrapper(SbkObject *pyObj, void *cptr);
    /// Take the object out of the wrapper map, leaving its flags alone.
    /// Deallocation uses this to make the wrapper unreachable before it runs
    /// any Python code; releaseWrapper() below is the same plus invalidation.
#ifdef Py_GIL_DISABLED
    /// Pass cptrs when the caller has already detached the pointer array from
    /// the object (see extractDestructionLocked()); nullptr means read it
    /// from sbkObj.
    void unregisterWrapper(SbkObject *sbkObj, void * const *cptrs = nullptr);
    void releaseWrapper(SbkObject *sbkObj, void * const *cptrs = nullptr);
#else
    void unregisterWrapper(SbkObject *sbkObj);
    void releaseWrapper(SbkObject *sbkObj);
#endif

    void runDeletionInMainThread();
    void addToDeletionInMainThread(const DestructorEntry &);

#ifdef Py_GIL_DISABLED
    /// Look up a wrapper and take a reference to it in one step. Empty when
    /// there is no wrapper for cptr, or when it is already being deallocated.
    /// This is what call sites should use; see sbkacquiredwrapper.h.
    [[nodiscard]] AcquiredWrapper acquireWrapper(const void *cptr, PyTypeObject *typeObject) const;
    [[nodiscard]] AcquiredWrapper acquireWrapper(const void *cptr) const;

    /// What a registration attempt found at the address: a live wrapper
    /// another thread registered, or a compatible identity that is being
    /// destroyed. Both mean "do not publish this one"; only the first one
    /// has something to hand back.
    struct Registration
    {
        AcquiredWrapper winner;
        bool dying = false;

        explicit operator bool() const { return bool(winner) || dying; }
    };

    /// Register \a pyObj for \a cptr unless another thread got there first,
    /// under one hold of the map lock. An empty return means the caller keeps
    /// this wrapper and hands it out; a non-empty return is the wrapper that
    /// won, and the caller has to discard its own.
    ///
    /// "Keeps it" is not always "registered it": a conversion that meets a
    /// dying identity of a type that invalidates its own wrappers gets its
    /// wrapper, but the map does not carry it - the tombstone holds it and
    /// invalidates it when it falls. See markWrapperDying() below.
    ///
    /// Looking up and registering as two steps leaves a gap in which two
    /// threads both find nothing and both register, which gives one C++
    /// object two wrappers - two destructors, and `a is b` false where PySide
    /// promises true.
    [[nodiscard]] Registration registerWrapperUnlessPresent(SbkObject *pyObj, void *cptr,
                                                            PyTypeObject *typeObject);

    /// Turn every entry of \a sbkObj into a tombstone: the identity stays in
    /// the map, marked as dying, so a lookup in the window that follows
    /// answers "being destroyed" rather than "absent". Called where the entry
    /// used to be removed. A tombstone also keeps the wrappers it let through
    /// under the dying-conversion exception, and invalidates them below.
    void markWrapperDying(SbkObject *sbkObj, void * const *cptrs = nullptr);

    /// Drop the tombstones \a sbkObj left at \a cptrs. Called once the
    /// retiring lifecycle can no longer destroy anything at those addresses -
    /// after the C++ destructor for an owning wrapper, after deallocation
    /// otherwise. \a sbkObj is a key here and is not dereferenced: by this
    /// point the wrapper is freed.
    void retireWrapper(SbkObject *sbkObj, void * const *cptrs, PyTypeObject *type);
    /// Retire after a destruction that was handed to the main thread: the
    /// tombstone may only fall once that destructor has run, which is later
    /// than the deallocation that queued it.
    void retireAfterDeletionInMainThread(SbkObject *sbkObj,
                                         const std::vector<void *> &cptrs,
                                         PyTypeObject *type);

    /// Lay a tombstone for a destruction the binding did not start and will
    /// not be told the end of: C++ deletes an object Python knows, the
    /// generated wrapper destructor reports it through Object::destroy(),
    /// and after that nothing calls us again. The binding therefore keeps
    /// what retirement needs - \a cptrs (taken over, freed here) and a
    /// reference on \a type - and waits for one of the two moments that do
    /// come back: the wrapper's operator delete, or a construction
    /// publishing a new object at the same address.
    void markExternallyDying(SbkObject *sbkObj, void **cptrs, PyTypeObject *type);

    /// Whether an external tombstone stands at \a cptr. Address comparison
    /// and nothing else, so the generated operator delete can ask before it
    /// takes a thread state - it runs on whatever thread C++ deleted on.
    bool hasExternallyDying(const void *cptr) const;

    /// The memory at \a cptr is being handed back. Drops the tombstone
    /// markExternallyDying() left there, if any; harmless otherwise, which
    /// is what lets the generated operator delete call it unconditionally.
    void retireExternallyDying(void *cptr);
#else // Py_GIL_DISABLED
    /// \deprecated Hands out the borrowed reference the map holds, which the
    /// caller cannot safely increment. Gone under free threading. What is
    /// left are the two Qt callbacks, metaObject() and qt_metacast(), that
    /// PYSIDE-803 keeps out of the GIL on a build that has one - where the
    /// borrow is no worse than it always was.
    SbkObject *retrieveWrapper(const void *cptr, PyTypeObject *typeObject) const;
    SbkObject *retrieveWrapper(const void *cptr) const;
#endif // Py_GIL_DISABLED

    static PyObject *getOverride(SbkObject *wrapper, PyObject *pyMethodName);

    /// One edge of the class hierarchy, the way a module's generated
    /// initInheritance() lists them.
    struct InheritanceEdge
    {
        Module::TypeInitStruct *parent;
        Module::TypeInitStruct *child;
    };

    /// Publish a module's inheritance edges, all of them in one step. The
    /// graph is immutable, so publishing copies it; one call per edge copied
    /// it once per edge.
    void addClassInheritance(const InheritanceEdge *edges, std::size_t count);
    /// Try to find the correct type of cptr via type discovery knowing that it's at least
    /// of type \p type. If a derived class is found, it returns a cptr cast to the type
    /// (which may be different in case of  multiple inheritance.
    /// \param cptr a pointer to the instance of type \p type
    /// \param type type of cptr
    using TypeCptrPair = std::pair<PyTypeObject *, void *>;
    TypeCptrPair findDerivedType(void *cptr, PyTypeObject *type) const;

    /// If \p probeType has a type discovery function, run it passing \p type
    /// and return the (cast'ed) pointer or nullptr.
    /// \param cptr a pointer to the instance of type \p type
    /// \param probeType type to run the check with
    /// \param type type of cptr
    static void *runTypeDiscovery(void *cptr, PyTypeObject *probeType, PyTypeObject *type);

    /**
     * Try to find the correct type of *cptr knowing that it's at least of type \p type.
     * In case of multiple inheritance this function may change the contents of cptr.
     * \param cptr a pointer to a pointer to the instance of type \p type
     * \param type type of *cptr
     * \warning This function is slow, use it only as last resort.
     */
    [[deprecated]] PyTypeObject *resolveType(void **cptr, PyTypeObject *type);

#ifdef Py_GIL_DISABLED
    /// Every live wrapper, each with a reference taken. Wrappers that are
    /// already being deallocated are left out rather than handed over: the
    /// caller could not tell them apart, and incrementing one afterwards is
    /// the resurrection this class exists to prevent.
    std::vector<AcquiredWrapper> getAllPyObjects();
#else
    std::set<PyObject *> getAllPyObjects();
#endif

    /**
     * Calls the function \p visitor for each object registered on binding manager.
     * \note As various C++ pointers can point to the same PyObject due to multiple inheritance
     *       a PyObject can be called more than one time for each PyObject.
     * \param visitor function called for each object.
     * \param data user data passed as second argument to the visitor function.
     */
    void visitAllPyObjects(ObjectVisitor visitor, void *data);

    bool dumpTypeGraph(const char *fileName) const;
    void dumpWrapperMap();

private:
    ~BindingManager();
    BindingManager();

    struct BindingManagerPrivate;
    BindingManagerPrivate *m_d;
};

LIBSHIBOKEN_API bool callInheritedInit(PyObject *self, PyObject *args, PyObject *kwds,
                                       const Module::TypeInitStruct &typeStruct);

} // namespace Shiboken

#endif // BINDINGMANAGER_H
