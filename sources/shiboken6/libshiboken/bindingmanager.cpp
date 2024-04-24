// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "autodecref.h"
#include "basewrapper.h"
#include "basewrapper_p.h"
#include "bindingmanager.h"
#include "gilstate.h"
#include "helper.h"
#include "sbkmodule.h"
#include "sbkstring.h"
#include "sbkstaticstrings.h"
#include "sbkfeature_base.h"
#include "debugfreehook.h"

#include <cstddef>
#include <cstring>
#include <fstream>
#include <iostream>
#include <mutex>
#include <string_view>
#include <unordered_map>
#include <unordered_set>

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

using WrapperMap = std::unordered_map<const void *, SbkObject *>;

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
    // crashes for example in retrieveWrapper(). std::shared_mutex was rejected due to:
    // https://stackoverflow.com/questions/50972345/when-is-stdshared-timed-mutex-slower-than-stdmutex-and-when-not-to-use-it
    std::recursive_mutex wrapperMapLock;
    Graph classHierarchy;
    DestructorEntries deleteInMainThread;

    bool releaseWrapper(void *cptr, SbkObject *wrapper, const int *bases = nullptr);
    bool releaseWrapperHelper(void *cptr, SbkObject *wrapper);

    void assignWrapper(SbkObject *wrapper, const void *cptr, const int *bases = nullptr);
    void assignWrapperHelper(SbkObject *wrapper, const void *cptr);
};

inline bool BindingManager::BindingManagerPrivate::releaseWrapperHelper(void *cptr, SbkObject *wrapper)
{
    // The wrapper argument is checked to ensure that the correct wrapper is released.
    // Returns true if the correct wrapper is found and released.
    // If wrapper argument is NULL, no such check is performed.
    auto iter = wrapperMapper.find(cptr);
    if (iter != wrapperMapper.end() && (wrapper == nullptr || iter->second == wrapper)) {
        wrapperMapper.erase(iter);
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
    auto iter = wrapperMapper.find(cptr);
    if (iter == wrapperMapper.end())
        wrapperMapper.insert(std::make_pair(cptr, wrapper));
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
    if (Shiboken::pyVerbose() > 0)
        dumpWrapperMap();
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
    m_d->assignWrapper(pyObj, cptr, d->mi_offsets);
}

void BindingManager::releaseWrapper(SbkObject *sbkObj)
{
    auto *sbkType = Py_TYPE(sbkObj);
    auto *d = PepType_SOTP(sbkType);
    int numBases = ((d && d->is_multicpp) ? getNumberOfCppBaseClasses(Py_TYPE(sbkObj)) : 1);

    void ** cptrs = reinterpret_cast<SbkObject *>(sbkObj)->d->cptr;
    const int *mi_offsets = d != nullptr ? d->mi_offsets : nullptr;
    for (int i = 0; i < numBases; ++i) {
        if (cptrs[i] != nullptr)
            m_d->releaseWrapper(cptrs[i], sbkObj, mi_offsets);
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

bool BindingManager::dumpTypeGraph(const char *fileName) const
{
    return m_d->classHierarchy.dumpTypeGraph(fileName);
}

void BindingManager::dumpWrapperMap()
{
    const auto &wrapperMap = m_d->wrapperMapper;
    std::cerr <<  "-------------------------------\n"
        << "WrapperMap size: " << wrapperMap.size() << " Types: "
        << m_d->classHierarchy.nodeSet().size() << '\n';
    for (auto it = wrapperMap.begin(), end = wrapperMap.end(); it != end; ++it) {
        const SbkObject *sbkObj = it->second;
        std::cerr << "key: " << it->first << ", value: "
            << static_cast<const void *>(sbkObj) << " ("
            << (Py_TYPE(sbkObj))->tp_name << ", refcnt: "
            << Py_REFCNT(reinterpret_cast<const PyObject *>(sbkObj)) << ")\n";
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
                                       const char *fullName)
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
    // PYSIDE-2654: If this has no implementation then we get object.__init__
    //              but that is the same case like above.
    if (func == objectInit)
        return false;
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

