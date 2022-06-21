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
#include "sbkenum_p.h"
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

static PyObject *cached_globals{};
static PyObject *last_select_id{};

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
    static getattrofunc const type_getattro = PyType_Type.tp_getattro;
    static PyObject *const ignAttr1 = PyName::qtStaticMetaObject();
    static PyObject *const ignAttr2 = PyMagicName::get();
    static PyTypeObject *const EnumMeta = getPyEnumMeta();
    static PyObject *const _member_map_ = String::createStaticString("_member_map_");

    if (SelectFeatureSet != nullptr)
        type->tp_dict = SelectFeatureSet(type);
    auto *ret = type_getattro(reinterpret_cast<PyObject *>(type), name);

    // PYSIDE-1735: Be forgiving with strict enums and fetch the enum, silently.
    //              The PYI files now look correct, but the old duplication is
    //              emulated here. This should be removed in Qt 7, see `parser.py`.
    //
    // FIXME PYSIDE7 should remove this forgivingness:
    //
    //      The duplication of enum values into the enclosing scope, allowing to write
    //      Qt.AlignLeft instead of Qt.Alignment.AlignLeft, is still implemented but
    //      no longer advertized in PYI files or line completion.

    if (!ret && name != ignAttr1 && name != ignAttr2) {
        PyObject *error_type, *error_value, *error_traceback;
        PyErr_Fetch(&error_type, &error_value, &error_traceback);

        // This is similar to `find_name_in_mro`, but instead of looking directly into
        // tp_dict, we search for the attribute in local classes of that dict.
        PyObject *mro = type->tp_mro;
        assert(PyTuple_Check(mro));
        size_t idx, n = PyTuple_GET_SIZE(mro);
        for (idx = 0; idx < n; ++idx) {
            // FIXME This loop should further be optimized by installing an extra
            //       <classname>_EnumInfo structure. This comes with the next compatibility patch.
            auto *base = PyTuple_GET_ITEM(mro, idx);
            auto *type_base = reinterpret_cast<PyTypeObject *>(base);
            auto *dict = type_base->tp_dict;
            PyObject *key, *value;
            Py_ssize_t pos = 0;
            while (PyDict_Next(dict, &pos, &key, &value)) {
                if (Py_TYPE(value) == EnumMeta) {
                    auto *valtype = reinterpret_cast<PyTypeObject *>(value);
                    auto *member_map = PyDict_GetItem(valtype->tp_dict, _member_map_);
                    if (member_map && PyDict_Check(member_map)) {
                        auto *result = PyDict_GetItem(member_map, name);
                        if (result) {
                            Py_INCREF(result);
                            return result;
                        }
                    }
                }
            }
        }
        PyErr_Restore(error_type, error_value, error_traceback);
    }
    return ret;
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
    return PepType_SOTP(type)->pyside_reserved_bits;
}

void SbkObjectType_SetReserved(PyTypeObject *type, int value)
{
    PepType_SOTP(type)->pyside_reserved_bits = value;
}

const char **SbkObjectType_GetPropertyStrings(PyTypeObject *type)
{
    return PepType_SOTP(type)->propertyStrings;
}

void SbkObjectType_SetPropertyStrings(PyTypeObject *type, const char **strings)
{
    PepType_SOTP(type)->propertyStrings = strings;
}

// PYSIDE-1626: Enforcing a context switch without further action.
void SbkObjectType_UpdateFeature(PyTypeObject *type)
{
    if (SelectFeatureSet != nullptr)
        type->tp_dict = SelectFeatureSet(type);
}

} // extern "C"
