/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "sbktypefactory.h"
#include "shiboken.h"

extern "C"
{

PyTypeObject *SbkType_FromSpec(PyType_Spec *spec)
{
    return SbkType_FromSpec_BMDWBD(spec, nullptr, nullptr, 0, 0, nullptr, nullptr);
}

PyTypeObject *SbkType_FromSpecAddDict(PyType_Spec *spec, PyObject *dict_add)
{
    return SbkType_FromSpec_BMDWBD(spec, nullptr, nullptr, 0, 0, nullptr, dict_add);
}

PyTypeObject *SbkType_FromSpecWithMeta(PyType_Spec *spec, PyTypeObject *meta)
{
    return SbkType_FromSpec_BMDWBD(spec, nullptr, meta, 0, 0, nullptr, nullptr);
}

PyTypeObject *SbkType_FromSpecWithBases(PyType_Spec *spec, PyObject *bases)
{
    return SbkType_FromSpec_BMDWBD(spec, bases, nullptr, 0, 0, nullptr, nullptr);
}

PyTypeObject *SbkType_FromSpecBasesMeta(PyType_Spec *spec, PyObject *bases, PyTypeObject *meta)
{
    return SbkType_FromSpec_BMDWBD(spec, bases, meta, 0, 0, nullptr, nullptr);
}

PyTypeObject *SbkType_FromSpec_BMDWBD(PyType_Spec *spec,
                                      PyObject *bases,
                                      PyTypeObject *meta,
                                      int dictoffset,
                                      int weaklistoffset,
                                      PyBufferProcs *bufferprocs,
                                      PyObject *dict_add)
{
    // PYSIDE-1286: Generate correct __module__ and __qualname__
    // The name field can now be extended by an "n:" prefix which is
    // the number of modules in the name. The default is 1.
    //
    // Example:
    //    "2:mainmod.submod.mainclass.subclass"
    // results in
    //    __module__   : "mainmod.submod"
    //    __qualname__ : "mainclass.subclass"
    //    __name__     : "subclass"

    PyType_Spec new_spec = *spec;
    const char *colon = strchr(spec->name, ':');
    assert(colon);
    int package_level = atoi(spec->name);
    const char *mod = new_spec.name = colon + 1;

    PyObject *obType = PyType_FromSpecWithBases(&new_spec, bases);
    if (obType == nullptr)
        return nullptr;

    const char *qual = mod;
    for (int idx = package_level; idx > 0; --idx) {
        const char *dot = strchr(qual, '.');
        if (!dot)
            break;
        qual = dot + 1;
    }
    int mlen = qual - mod - 1;
    Shiboken::AutoDecRef module(Shiboken::String::fromCString(mod, mlen));
    Shiboken::AutoDecRef qualname(Shiboken::String::fromCString(qual));
    if (PyObject_SetAttr(obType, Shiboken::PyMagicName::module(), module) < 0)
        return nullptr;
    if (PyObject_SetAttr(obType, Shiboken::PyMagicName::qualname(), qualname) < 0)
        return nullptr;

    auto *type = reinterpret_cast<PyTypeObject *>(obType);

    if (meta) {
        PyTypeObject *hold = Py_TYPE(type);
        Py_TYPE(type) = meta;
        Py_INCREF(Py_TYPE(type));
        if (hold->tp_flags & Py_TPFLAGS_HEAPTYPE)
            Py_DECREF(hold);
    }

    if (dictoffset)
        type->tp_dictoffset = dictoffset;
    if (weaklistoffset)
        type->tp_weaklistoffset = weaklistoffset;
    if (bufferprocs)
        PepType_AS_BUFFER(type) = bufferprocs;
    if (dict_add)
        PyDict_Update(reinterpret_cast<PyObject *>(type->tp_dict), dict_add);

    PyType_Modified(type);
    return type;
}

} //extern "C"
