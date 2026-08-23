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

    void registerWrapper(SbkObject *pyObj, void *cptr);
    /// Take the object out of the wrapper map, leaving its flags alone.
    /// Deallocation uses this to make the wrapper unreachable before it runs
    /// any Python code; releaseWrapper() below is the same plus invalidation.
    void unregisterWrapper(SbkObject *sbkObj);
    void releaseWrapper(SbkObject *sbkObj);

    void runDeletionInMainThread();
    void addToDeletionInMainThread(const DestructorEntry &);

#ifdef Py_GIL_DISABLED
    /// Look up a wrapper and take a reference to it in one step. Returns an
    /// empty AcquiredWrapper when there is no wrapper for cptr, or when the one
    /// there is has already started to be deallocated. This is what call
    /// sites should use; see sbkacquiredwrapper.h for why.
    [[nodiscard]] AcquiredWrapper acquireWrapper(const void *cptr, PyTypeObject *typeObject) const;
    [[nodiscard]] AcquiredWrapper acquireWrapper(const void *cptr) const;

    /// Register \a pyObj for \a cptr unless another thread got there first,
    /// under one hold of the map lock. An empty return means this wrapper is
    /// the registered one; a non-empty return is the wrapper that won, and
    /// the caller has to discard its own.
    ///
    /// Looking up and registering as two steps leaves a gap in which two
    /// threads both find nothing and both register, which gives one C++
    /// object two wrappers - two destructors, and `a is b` false where PySide
    /// promises true.
    [[nodiscard]] AcquiredWrapper registerWrapperUnlessPresent(SbkObject *pyObj, void *cptr,
                                                               PyTypeObject *typeObject);
#endif // Py_GIL_DISABLED

    /// \deprecated Hands out the borrowed reference the map holds, which the
    /// caller cannot safely increment. Being replaced by acquireWrapper() one
    /// call site at a time; this declaration goes away with the last of them.
    SbkObject *retrieveWrapper(const void *cptr, PyTypeObject *typeObject) const;
    SbkObject *retrieveWrapper(const void *cptr) const;
    static PyObject *getOverride(SbkObject *wrapper, PyObject *pyMethodName);

    void addClassInheritance(Module::TypeInitStruct *parent, Module::TypeInitStruct *child);
    /// Try to find the correct type of cptr via type discovery knowing that it's at least
    /// of type \p type. If a derived class is found, it returns a cptr cast to the type
    /// (which may be different in case of  multiple inheritance.
    /// \param cptr a pointer to the instance of type \p type
    /// \param type type of cptr
    using TypeCptrPair = std::pair<PyTypeObject *, void *>;
    TypeCptrPair findDerivedType(void *cptr, PyTypeObject *type) const;

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
                                       Module::TypeInitStruct typeStruct);

} // namespace Shiboken

#endif // BINDINGMANAGER_H
