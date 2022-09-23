// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "sbkmodule.h"
#include "basewrapper.h"
#include "bindingmanager.h"
#include <unordered_map>

/// This hash maps module objects to arrays of Python types.
using ModuleTypesMap = std::unordered_map<PyObject *, PyTypeObject **> ;

/// This hash maps module objects to arrays of converters.
using ModuleConvertersMap = std::unordered_map<PyObject *, SbkConverter **>;

/// All types produced in imported modules are mapped here.
static ModuleTypesMap moduleTypes;
static ModuleConvertersMap moduleConverters;

namespace Shiboken
{
namespace Module
{

PyObject *import(const char *moduleName)
{
    PyObject *sysModules = PyImport_GetModuleDict();
    PyObject *module = PyDict_GetItemString(sysModules, moduleName);
    if (module)
        Py_INCREF(module);
    else
        module = PyImport_ImportModule(moduleName);

    if (!module)
        PyErr_Format(PyExc_ImportError,"could not import module '%s'", moduleName);

    return module;
}

PyObject *create(const char * /* moduleName */, void *moduleData)
{
    Shiboken::init();
    return PyModule_Create(reinterpret_cast<PyModuleDef *>(moduleData));
}

void registerTypes(PyObject *module, PyTypeObject **types)
{
    auto iter = moduleTypes.find(module);
    if (iter == moduleTypes.end())
        moduleTypes.insert(std::make_pair(module, types));
}

PyTypeObject **getTypes(PyObject *module)
{
    auto iter = moduleTypes.find(module);
    return (iter == moduleTypes.end()) ? 0 : iter->second;
}

void registerTypeConverters(PyObject *module, SbkConverter **converters)
{
    auto iter = moduleConverters.find(module);
    if (iter == moduleConverters.end())
        moduleConverters.insert(std::make_pair(module, converters));
}

SbkConverter **getTypeConverters(PyObject *module)
{
    auto iter = moduleConverters.find(module);
    return (iter == moduleConverters.end()) ? 0 : iter->second;
}

} } // namespace Shiboken::Module
