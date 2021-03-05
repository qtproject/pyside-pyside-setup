/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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

PyObject *create(const char *moduleName, void *moduleData)
{
    Shiboken::init();
#ifndef IS_PY3K
    return Py_InitModule(moduleName, reinterpret_cast<PyMethodDef *>(moduleData));
#else
    return PyModule_Create(reinterpret_cast<PyModuleDef *>(moduleData));
#endif
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
