// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef BINDINGMANAGER_H
#define BINDINGMANAGER_H

#include "sbkpython.h"
#include "shibokenclasshelpermacros.h"
#include "shibokenmacros.h"
#include "sbkdestructorentry.h"

#include <set>
#include <utility>

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
    LIBSHIBOKEN_DISABLE_COPY_MOVE(BindingManager)

    static BindingManager &instance();

    bool hasWrapper(const void *cptr, PyTypeObject *typeObject) const;
    bool hasWrapper(const void *cptr) const;

    void registerWrapper(SbkObject *pyObj, void *cptr);
    void unregisterWrapper(SbkObject *sbkObj);
    void releaseWrapper(SbkObject *sbkObj);

    void runDeletionInMainThread();
    void addToDeletionInMainThread(const DestructorEntry &);

    SbkObject *retrieveWrapper(const void *cptr, PyTypeObject *typeObject) const;
    SbkObject *retrieveWrapper(const void *cptr) const;
    static PyObject *getOverride(SbkObject *wrapper, PyObject *pyMethodName);

    void addClassInheritance(Module::TypeInitStruct *parent, Module::TypeInitStruct *child);
    using TypeCptrPair = std::pair<PyTypeObject *, void *>;
    TypeCptrPair findDerivedType(void *cptr, PyTypeObject *type) const;

    static void *runTypeDiscovery(void *cptr, PyTypeObject *probeType, PyTypeObject *type);

    [[deprecated]] PyTypeObject *resolveType(void **cptr, PyTypeObject *type);

    std::set<PyObject *> getAllPyObjects();

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
