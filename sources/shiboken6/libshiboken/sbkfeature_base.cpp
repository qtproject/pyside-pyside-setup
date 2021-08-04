/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
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

#include "basewrapper.h"
#include "basewrapper_p.h"
#include "autodecref.h"
#include "sbkstring.h"
#include "sbkstaticstrings.h"
#include "sbkstaticstrings_p.h"
#include "signature.h"
#include "sbkfeature_base.h"

using namespace Shiboken;

extern "C"
{

////////////////////////////////////////////////////////////////////////////
//
// getFeatureSelectId
//
// This function is needed here already for signature handling.
// Maybe the same function from feature_select.cpp will be replaced.
//

static PyObject *cached_globals = nullptr;
static PyObject *last_select_id = nullptr;

PyObject *getFeatureSelectId()
{
    static PyObject *undef = PyLong_FromLong(-1);
    static PyObject *feature_dict = GetFeatureDict();
    // these things are all borrowed
    PyObject *globals = PyEval_GetGlobals();
    if (globals == nullptr
        || globals == cached_globals)
        return last_select_id;

    PyObject *modname = PyDict_GetItem(globals, PyMagicName::name());
    if (modname == nullptr)
        return last_select_id;

    PyObject *select_id = PyDict_GetItem(feature_dict, modname);
    if (select_id == nullptr
        || !PyLong_Check(select_id)  // int/long cheating
        || select_id == undef)
        return last_select_id;

    cached_globals = globals;
    last_select_id = select_id;
    assert(PyLong_AsSsize_t(select_id) >= 0);
    return select_id;
}

int currentSelectId(PyTypeObject *type)
{
    int sel = SbkObjectType_GetReserved(type);
    // This could theoretically be -1 if used too early.
    assert(sel >= 0);
    return sel;
}

void initFeatureShibokenPart()
{
    static PyObject *no_sel = PyLong_FromLong(0);
    last_select_id = no_sel;
    // Reset the cache. This is called at any "from __feature__ import".
    cached_globals = nullptr;
}

static SelectableFeatureHook SelectFeatureSet = nullptr;

SelectableFeatureHook initSelectableFeature(SelectableFeatureHook func)
{
    auto ret = SelectFeatureSet;
    SelectFeatureSet = func;
    return ret;
}

PyObject *mangled_type_getattro(PyTypeObject *type, PyObject *name)
{
    /*
     * Note: This `type_getattro` version is only the default that comes
     * from `PyType_Type.tp_getattro`. This does *not* interfere in any way
     * with the complex `tp_getattro` of `QObject` and other instances.
     * What we change here is the meta class of `QObject`.
     */
    static getattrofunc type_getattro = PyType_Type.tp_getattro;
    if (SelectFeatureSet != nullptr)
        type->tp_dict = SelectFeatureSet(type);
    return type_getattro(reinterpret_cast<PyObject *>(type), name);
}

PyObject *Sbk_TypeGet___dict__(PyTypeObject *type, void *context)
{
    /*
     * This is the override for getting a dict.
     */
    auto dict = type->tp_dict;
    if (dict == nullptr)
        Py_RETURN_NONE;
    if (SelectFeatureSet != nullptr)
        dict = SelectFeatureSet(type);
    return PyDictProxy_New(dict);
}

// These functions replace the standard PyObject_Generic(Get|Set)Attr functions.
// They provide the default that "object" inherits.
// Everything else is directly handled by cppgenerator that calls `Feature::Select`.
PyObject *SbkObject_GenericGetAttr(PyObject *obj, PyObject *name)
{
    auto type = Py_TYPE(obj);
    if (SelectFeatureSet != nullptr)
        type->tp_dict = SelectFeatureSet(type);
    return PyObject_GenericGetAttr(obj, name);
}

int SbkObject_GenericSetAttr(PyObject *obj, PyObject *name, PyObject *value)
{
    auto type = Py_TYPE(obj);
    if (SelectFeatureSet != nullptr)
        type->tp_dict = SelectFeatureSet(type);
    return PyObject_GenericSetAttr(obj, name, value);
}

// Caching the select Id.
int SbkObjectType_GetReserved(PyTypeObject *type)
{
    auto ptr = PepType_SOTP(reinterpret_cast<SbkObjectType *>(type));
    // PYSIDE-1019: During import PepType_SOTP is still zero.
    if (ptr == nullptr)
        return -1;
    return ptr->pyside_reserved_bits;
}

void SbkObjectType_SetReserved(PyTypeObject *type, int value)
{
    auto ptr = PepType_SOTP(reinterpret_cast<SbkObjectType *>(type));
    // PYSIDE-1019: During import PepType_SOTP is still zero.
    if (ptr == nullptr)
        return;
    ptr->pyside_reserved_bits = value;
}

const char **SbkObjectType_GetPropertyStrings(PyTypeObject *type)
{
    auto ptr = PepType_SOTP(reinterpret_cast<SbkObjectType *>(type));
    // PYSIDE-1019: During import PepType_SOTP is still zero.
    if (ptr == nullptr)
        return nullptr;
    return ptr->propertyStrings;
}

void SbkObjectType_SetPropertyStrings(PyTypeObject *type, const char **strings)
{
    auto ptr = PepType_SOTP(reinterpret_cast<SbkObjectType *>(type));
    // PYSIDE-1019: During import PepType_SOTP is still zero.
    if (ptr == nullptr)
        return;
    ptr->propertyStrings = strings;
}

// PYSIDE-1626: Enforcing a context switch without further action.
void SbkObjectType_UpdateFeature(PyTypeObject *type)
{
    if (SelectFeatureSet != nullptr)
        type->tp_dict = SelectFeatureSet(type);
}

} // extern "C"
