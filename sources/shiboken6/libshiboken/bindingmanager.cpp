// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "autodecref.h"
#include "basewrapper.h"
#include "basewrapper_p.h"
#include "bindingmanager.h"
#include "gilstate.h"
#include "helper.h"
#include "sbkstring.h"
#include "sbkstaticstrings.h"
#include "sbkfeature_base.h"
#include "debugfreehook.h"

#include <cstddef>
#include <cstring>
#include <fstream>
#include <mutex>
#include <unordered_map>

namespace Shiboken
{

using WrapperMap = std::unordered_map<const void *, SbkObject *>;

class Graph
{
public:
    using NodeList = std::vector<PyTypeObject *>;
    using Edges = std::unordered_map<PyTypeObject *, NodeList>;

    Edges m_edges;

    Graph() = default;

    void addEdge(PyTypeObject *from, PyTypeObject *to)
    {
        m_edges[from].push_back(to);
    }

#ifndef NDEBUG
    void dumpDotGraph() const
    {
        std::ofstream file("/tmp/shiboken_graph.dot");

        file << "digraph D {\n";

        for (const auto &p : m_edges) {
            auto *node1 = p.first;
            const NodeList &nodeList = p.second;
            for (const PyTypeObject *o : nodeList) {
                auto *node2 = o;
                file << '"' << node2->tp_name << "\" -> \""
                    << node1->tp_name << "\"\n";
            }
        }
        file << "}\n";
    }
#endif

    PyTypeObject *identifyType(void **cptr, PyTypeObject *type, PyTypeObject *baseType) const
    {
        auto edgesIt = m_edges.find(type);
        if (edgesIt != m_edges.end()) {
            const NodeList &adjNodes = m_edges.find(type)->second;
            for (PyTypeObject *node : adjNodes) {
                PyTypeObject *newType = identifyType(cptr, node, baseType);
                if (newType)
                    return newType;
            }
        }
        void *typeFound = nullptr;
        auto *sotp = PepType_SOTP(type);
        if (sotp->type_discovery)
            typeFound = sotp->type_discovery(*cptr, baseType);
        if (typeFound) {
            // This "typeFound != type" is needed for backwards compatibility with old modules using a newer version of
            // libshiboken because old versions of type_discovery function used to return a PyTypeObject *instead of
            // a possible variation of the C++ instance pointer (*cptr).
            if (typeFound != type)
                *cptr = typeFound;
            return type;
        }
        return nullptr;
    }
};


#ifndef NDEBUG
static void showWrapperMap(const WrapperMap &wrapperMap)
{
    if (Shiboken::pyVerbose() > 0) {
        fprintf(stderr, "-------------------------------\n");
        fprintf(stderr, "WrapperMap: %p (size: %d)\n", &wrapperMap, (int) wrapperMap.size());
        for (auto it = wrapperMap.begin(), end = wrapperMap.end(); it != end; ++it) {
            const SbkObject *sbkObj = it->second;
            fprintf(stderr, "key: %p, value: %p (%s, refcnt: %d)\n", it->first,
                    static_cast<const void *>(sbkObj),
                    (Py_TYPE(sbkObj))->tp_name,
                    int(Py_REFCNT(reinterpret_cast<const PyObject *>(sbkObj))));
        }
        fprintf(stderr, "-------------------------------\n");
    }
}
#endif

struct BindingManager::BindingManagerPrivate {
    using DestructorEntries = std::vector<DestructorEntry>;

    WrapperMap wrapperMapper;
    // Guard wrapperMapper mainly for QML which calls into the generated
    // QObject::metaObject() and elsewhere from threads without GIL, causing
    // crashes for example in retrieveWrapper(). std::shared_mutex was rejected due to:
    // https://stackoverflow.com/questions/50972345/when-is-stdshared-timed-mutex-slower-than-stdmutex-and-when-not-to-use-it
    std::recursive_mutex wrapperMapLock;
    Graph classHierarchy;
    DestructorEntries deleteInMainThread;
    bool destroying;

    BindingManagerPrivate() : destroying(false) {}
    bool releaseWrapper(void *cptr, SbkObject *wrapper);
    void assignWrapper(SbkObject *wrapper, const void *cptr);

};

bool BindingManager::BindingManagerPrivate::releaseWrapper(void *cptr, SbkObject *wrapper)
{
    // The wrapper argument is checked to ensure that the correct wrapper is released.
    // Returns true if the correct wrapper is found and released.
    // If wrapper argument is NULL, no such check is performed.
    std::lock_guard<std::recursive_mutex> guard(wrapperMapLock);
    auto iter = wrapperMapper.find(cptr);
    if (iter != wrapperMapper.end() && (wrapper == nullptr || iter->second == wrapper)) {
        wrapperMapper.erase(iter);
        return true;
    }
    return false;
}

void BindingManager::BindingManagerPrivate::assignWrapper(SbkObject *wrapper, const void *cptr)
{
    assert(cptr);
    std::lock_guard<std::recursive_mutex> guard(wrapperMapLock);
    auto iter = wrapperMapper.find(cptr);
    if (iter == wrapperMapper.end())
        wrapperMapper.insert(std::make_pair(cptr, wrapper));
}

BindingManager::BindingManager()
{
    m_d = new BindingManager::BindingManagerPrivate;

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
    showWrapperMap(m_d->wrapperMapper);
#endif
    /* Cleanup hanging references. We just invalidate them as when
     * the BindingManager is being destroyed the interpreter is alredy
     * shutting down. */
    if (Py_IsInitialized()) {  // ensure the interpreter is still valid
        std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
        while (!m_d->wrapperMapper.empty()) {
            Object::destroy(m_d->wrapperMapper.begin()->second, const_cast<void *>(m_d->wrapperMapper.begin()->first));
        }
        assert(m_d->wrapperMapper.empty());
    }
    delete m_d;
}

BindingManager &BindingManager::instance() {
    static BindingManager singleton;
    return singleton;
}

bool BindingManager::hasWrapper(const void *cptr)
{
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
    return m_d->wrapperMapper.find(cptr) != m_d->wrapperMapper.end();
}

void BindingManager::registerWrapper(SbkObject *pyObj, void *cptr)
{
    auto *instanceType = Py_TYPE(pyObj);
    auto *d = PepType_SOTP(instanceType);

    if (!d)
        return;

    if (d->mi_init && !d->mi_offsets)
        d->mi_offsets = d->mi_init(cptr);
    m_d->assignWrapper(pyObj, cptr);
    if (d->mi_offsets) {
        int *offset = d->mi_offsets;
        while (*offset != -1) {
            if (*offset > 0)
                m_d->assignWrapper(pyObj, reinterpret_cast<void *>(reinterpret_cast<uintptr_t>(cptr) + *offset));
            offset++;
        }
    }
}

void BindingManager::releaseWrapper(SbkObject *sbkObj)
{
    auto *sbkType = Py_TYPE(sbkObj);
    auto *d = PepType_SOTP(sbkType);
    int numBases = ((d && d->is_multicpp) ? getNumberOfCppBaseClasses(Py_TYPE(sbkObj)) : 1);

    void ** cptrs = reinterpret_cast<SbkObject *>(sbkObj)->d->cptr;
    for (int i = 0; i < numBases; ++i) {
        auto *cptr = reinterpret_cast<unsigned char *>(cptrs[i]);
        m_d->releaseWrapper(cptr, sbkObj);
        if (d && d->mi_offsets) {
            int *offset = d->mi_offsets;
            while (*offset != -1) {
                if (*offset > 0)
                    m_d->releaseWrapper(reinterpret_cast<void *>(reinterpret_cast<uintptr_t>(cptr) + *offset), sbkObj);
                offset++;
            }
        }
    }
    sbkObj->d->validCppObject = false;
}

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

SbkObject *BindingManager::retrieveWrapper(const void *cptr)
{
    std::lock_guard<std::recursive_mutex> guard(m_d->wrapperMapLock);
    auto iter = m_d->wrapperMapper.find(cptr);
    if (iter == m_d->wrapperMapper.end())
        return nullptr;
    return iter->second;
}

PyObject *BindingManager::getOverride(const void *cptr,
                                      PyObject *nameCache[],
                                      const char *methodName)
{
    SbkObject *wrapper = retrieveWrapper(cptr);
    // The refcount can be 0 if the object is dieing and someone called
    // a virtual method from the destructor
    if (!wrapper || Py_REFCNT(reinterpret_cast<const PyObject *>(wrapper)) == 0)
        return nullptr;

    // PYSIDE-1626: Touch the type to initiate switching early.
    SbkObjectType_UpdateFeature(Py_TYPE(wrapper));

    int flag = currentSelectId(Py_TYPE(wrapper));
    int propFlag = isdigit(methodName[0]) ? methodName[0] - '0' : 0;
    bool is_snake = flag & 0x01;
    PyObject *pyMethodName = nameCache[is_snake];  // borrowed
    if (pyMethodName == nullptr) {
        if (propFlag)
            methodName += 2;    // skip the propFlag and ':'
        pyMethodName = Shiboken::String::getSnakeCaseName(methodName, is_snake);
        nameCache[is_snake] = pyMethodName;
    }

    auto *obWrapper = reinterpret_cast<PyObject *>(wrapper);
    auto *wrapper_dict = SbkObject_GetDict_NoRef(obWrapper);
    if (PyObject *method = PyDict_GetItem(wrapper_dict, pyMethodName)) {
        // Note: This special case was implemented for duck-punching, which happens
        // in the instance dict. It does not work with properties.
        Py_INCREF(method);
        return method;
    }

    PyObject *method = PyObject_GetAttr(reinterpret_cast<PyObject *>(wrapper), pyMethodName);

    PyObject *function = nullptr;

    // PYSIDE-1523: PyMethod_Check is not accepting compiled methods, we do this rather
    // crude check for them.
    if (method) {
        // PYSIDE-535: This macro is redefined in a compatible way in pep384
        if (PyMethod_Check(method)) {
            if (PyMethod_GET_SELF(method) == reinterpret_cast<PyObject *>(wrapper)) {
                function = PyMethod_GET_FUNCTION(method);
            } else {
                Py_DECREF(method);
                method = nullptr;
            }
        } else if (PyObject_HasAttr(method, PyName::im_self())
                   && PyObject_HasAttr(method, PyName::im_func())
                   && PyObject_HasAttr(method, Shiboken::PyMagicName::code())) {
            PyObject *im_self = PyObject_GetAttr(method, PyName::im_self());
            // Not retaining a reference inline with what PyMethod_GET_SELF does.
            Py_DECREF(im_self);

            if (im_self == reinterpret_cast<PyObject *>(wrapper)) {
                function = PyObject_GetAttr(method, PyName::im_func());
                // Not retaining a reference inline with what PyMethod_GET_FUNCTION does.
                Py_DECREF(function);
            } else {
                Py_DECREF(method);
                method = nullptr;
            }
        } else {
            Py_DECREF(method);
            method = nullptr;
        }
    }

    if (method != nullptr) {
        PyObject *defaultMethod{};
        PyObject *mro = Py_TYPE(wrapper)->tp_mro;

        int size = PyTuple_GET_SIZE(mro);
        bool defaultFound = false;
        // The first class in the mro (index 0) is the class being checked and it should not be tested.
        // The last class in the mro (size - 1) is the base Python object class which should not be tested also.
        for (int idx = 1; idx < size - 1; ++idx) {
            auto *parent = reinterpret_cast<PyTypeObject *>(PyTuple_GET_ITEM(mro, idx));
            AutoDecRef tpDict(PepType_GetDict(parent));
            auto *parentDict = tpDict.object();
            if (parentDict) {
                defaultMethod = PyDict_GetItem(parentDict, pyMethodName);
                if (defaultMethod) {
                    defaultFound = true;
                    if (function != defaultMethod)
                        return method;
                }
            }
        }
        // PYSIDE-2255: If no default method was found, use the method.
        if (!defaultFound)
            return method;
        Py_DECREF(method);
    }

    return nullptr;
}

void BindingManager::addClassInheritance(PyTypeObject *parent, PyTypeObject *child)
{
    m_d->classHierarchy.addEdge(parent, child);
}

PyTypeObject *BindingManager::resolveType(void **cptr, PyTypeObject *type)
{
    PyTypeObject *identifiedType = m_d->classHierarchy.identifyType(cptr, type, type);
    return identifiedType ? identifiedType : type;
}

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

void BindingManager::visitAllPyObjects(ObjectVisitor visitor, void *data)
{
    WrapperMap copy = m_d->wrapperMapper;
    for (const auto &p : copy) {
        if (hasWrapper(p.first))
            visitor(p.second, data);
    }
}

static bool isPythonType(PyTypeObject *type)
{
    // This is a type which should be called by multiple inheritance.
    // It is either a pure Python type or a derived PySide type.
    return !ObjectType::checkType(type) || ObjectType::isUserType(type);
}

bool callInheritedInit(PyObject *self, PyObject *args, PyObject *kwds,
                                       const char *fullName)
{
    using Shiboken::AutoDecRef;

    static PyObject *const _init = String::createStaticString("__init__");

    // A native C++ self cannot have multiple inheritance.
    if (!Object::isUserType(self))
        return false;

    auto *startType = Py_TYPE(self);
    auto *mro = startType->tp_mro;
    Py_ssize_t idx, n = PyTuple_GET_SIZE(mro);
    auto classNameLen = std::strrchr(fullName, '.') - fullName;
    /* No need to check the last one: it's gonna be skipped anyway.  */
    for (idx = 0; idx + 1 < n; ++idx) {
        auto *lookType = reinterpret_cast<PyTypeObject *>(PyTuple_GET_ITEM(mro, idx));
        const char *lookName = lookType->tp_name;
        auto lookLen = long(std::strlen(lookName));
        if (std::strncmp(lookName, fullName, classNameLen) == 0 && lookLen == classNameLen)
            break;
    }
    // We are now at the first non-Python class `QObject`.
    // mro: ('C', 'A', 'QObject', 'Object', 'B', 'object')
    // We want to catch class `B` and call its `__init__`.
    for (idx += 1; idx + 1 < n; ++idx) {
        auto *t = reinterpret_cast<PyTypeObject *>(PyTuple_GET_ITEM(mro, idx));
        if (isPythonType(t))
            break;
    }
    if (idx >= n)
        return false;

    auto *obSubType = PyTuple_GET_ITEM(mro, idx);
    auto *subType = reinterpret_cast<PyTypeObject *>(obSubType);
    if (subType == &PyBaseObject_Type)
        return false;
    AutoDecRef func(PyObject_GetAttr(obSubType, _init));
    // PYSIDE-2294: We need to explicitly ignore positional args in a mixin class.
    SBK_UNUSED(args);
    AutoDecRef newArgs(PyTuple_New(1));
    auto *newArgsOb = newArgs.object();
    Py_INCREF(self);
    PyTuple_SET_ITEM(newArgsOb, 0, self);
    // Note: This can fail, so please always check the error status.
    AutoDecRef result(PyObject_Call(func, newArgs, kwds));
    return true;
}

} // namespace Shiboken

