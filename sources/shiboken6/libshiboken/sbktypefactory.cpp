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
    return SbkType_FromSpec_BMDWB(spec, nullptr, nullptr, 0, 0, nullptr);
}

PyTypeObject *SbkType_FromSpecWithMeta(PyType_Spec *spec, PyTypeObject *meta)
{
    return SbkType_FromSpec_BMDWB(spec, nullptr, meta, 0, 0, nullptr);
}

PyTypeObject *SbkType_FromSpecWithBases(PyType_Spec *spec, PyObject *bases)
{
    return SbkType_FromSpec_BMDWB(spec, bases, nullptr, 0, 0, nullptr);
}

PyTypeObject *SbkType_FromSpecBasesMeta(PyType_Spec *spec, PyObject *bases, PyTypeObject *meta)
{
    return SbkType_FromSpec_BMDWB(spec, bases, meta, 0, 0, nullptr);
}

#ifdef PYPY_VERSION

static PyObject *_PyType_FromSpecWithBases(PyType_Spec *, PyObject *);

#else

#define _PyType_FromSpecWithBases PyType_FromSpecWithBases

#endif // PYPY_VERSION

PyTypeObject *SbkType_FromSpec_BMDWB(PyType_Spec *spec,
                                     PyObject *bases,
                                     PyTypeObject *meta,
                                     int dictoffset,
                                     int weaklistoffset,
                                     PyBufferProcs *bufferprocs)
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

    PyObject *obType = _PyType_FromSpecWithBases(&new_spec, bases);
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

#ifdef PYPY_VERSION
    // PYSIDE-535: Careful: Using PyObject_SetAttr would have the side-effect of calling
    // PyType_Ready too early. (at least in PyPy, which caused pretty long debugging.)
    auto *ht = reinterpret_cast<PyHeapTypeObject *>(type);
    ht->ht_qualname = qualname;
    if (PyDict_SetItem(type->tp_dict, Shiboken::PyMagicName::qualname(), qualname))
        return nullptr;
    if (PyDict_SetItem(type->tp_dict, Shiboken::PyMagicName::module(), module))
        return nullptr;
    PyType_Ready(type);
#else
    if (PyObject_SetAttr(obType, Shiboken::PyMagicName::module(), module) < 0)
        return nullptr;
    if (PyObject_SetAttr(obType, Shiboken::PyMagicName::qualname(), qualname) < 0)
        return nullptr;
    PyType_Modified(type);
#endif
    return type;
}

#ifdef PYPY_VERSION

/////////////////////////////////////////////////////////////////////////////
//
// Reimplementation of `PyType_FromSpecWithBases`
//
// This is almost the original code from Python 3.7 with a few changes.
// Especially the call to `PyType_Ready` is deferred until the needed
// post-actions are carried out in `SbkType_FromSpec_BMDWBD`.
//
// FIXME remove ASAP.
// Version is not clear, yet. Current version == 7.3.6
//

static const short slotoffsets[] = {
    -1, /* invalid slot */
/* Generated by typeslots.py */
0,
0,
offsetof(PyHeapTypeObject, as_mapping.mp_ass_subscript),
offsetof(PyHeapTypeObject, as_mapping.mp_length),
offsetof(PyHeapTypeObject, as_mapping.mp_subscript),
offsetof(PyHeapTypeObject, as_number.nb_absolute),
offsetof(PyHeapTypeObject, as_number.nb_add),
offsetof(PyHeapTypeObject, as_number.nb_and),
offsetof(PyHeapTypeObject, as_number.nb_bool),
offsetof(PyHeapTypeObject, as_number.nb_divmod),
offsetof(PyHeapTypeObject, as_number.nb_float),
offsetof(PyHeapTypeObject, as_number.nb_floor_divide),
offsetof(PyHeapTypeObject, as_number.nb_index),
offsetof(PyHeapTypeObject, as_number.nb_inplace_add),
offsetof(PyHeapTypeObject, as_number.nb_inplace_and),
offsetof(PyHeapTypeObject, as_number.nb_inplace_floor_divide),
offsetof(PyHeapTypeObject, as_number.nb_inplace_lshift),
offsetof(PyHeapTypeObject, as_number.nb_inplace_multiply),
offsetof(PyHeapTypeObject, as_number.nb_inplace_or),
offsetof(PyHeapTypeObject, as_number.nb_inplace_power),
offsetof(PyHeapTypeObject, as_number.nb_inplace_remainder),
offsetof(PyHeapTypeObject, as_number.nb_inplace_rshift),
offsetof(PyHeapTypeObject, as_number.nb_inplace_subtract),
offsetof(PyHeapTypeObject, as_number.nb_inplace_true_divide),
offsetof(PyHeapTypeObject, as_number.nb_inplace_xor),
offsetof(PyHeapTypeObject, as_number.nb_int),
offsetof(PyHeapTypeObject, as_number.nb_invert),
offsetof(PyHeapTypeObject, as_number.nb_lshift),
offsetof(PyHeapTypeObject, as_number.nb_multiply),
offsetof(PyHeapTypeObject, as_number.nb_negative),
offsetof(PyHeapTypeObject, as_number.nb_or),
offsetof(PyHeapTypeObject, as_number.nb_positive),
offsetof(PyHeapTypeObject, as_number.nb_power),
offsetof(PyHeapTypeObject, as_number.nb_remainder),
offsetof(PyHeapTypeObject, as_number.nb_rshift),
offsetof(PyHeapTypeObject, as_number.nb_subtract),
offsetof(PyHeapTypeObject, as_number.nb_true_divide),
offsetof(PyHeapTypeObject, as_number.nb_xor),
offsetof(PyHeapTypeObject, as_sequence.sq_ass_item),
offsetof(PyHeapTypeObject, as_sequence.sq_concat),
offsetof(PyHeapTypeObject, as_sequence.sq_contains),
offsetof(PyHeapTypeObject, as_sequence.sq_inplace_concat),
offsetof(PyHeapTypeObject, as_sequence.sq_inplace_repeat),
offsetof(PyHeapTypeObject, as_sequence.sq_item),
offsetof(PyHeapTypeObject, as_sequence.sq_length),
offsetof(PyHeapTypeObject, as_sequence.sq_repeat),
offsetof(PyHeapTypeObject, ht_type.tp_alloc),
offsetof(PyHeapTypeObject, ht_type.tp_base),
offsetof(PyHeapTypeObject, ht_type.tp_bases),
offsetof(PyHeapTypeObject, ht_type.tp_call),
offsetof(PyHeapTypeObject, ht_type.tp_clear),
offsetof(PyHeapTypeObject, ht_type.tp_dealloc),
offsetof(PyHeapTypeObject, ht_type.tp_del),
offsetof(PyHeapTypeObject, ht_type.tp_descr_get),
offsetof(PyHeapTypeObject, ht_type.tp_descr_set),
offsetof(PyHeapTypeObject, ht_type.tp_doc),
offsetof(PyHeapTypeObject, ht_type.tp_getattr),
offsetof(PyHeapTypeObject, ht_type.tp_getattro),
offsetof(PyHeapTypeObject, ht_type.tp_hash),
offsetof(PyHeapTypeObject, ht_type.tp_init),
offsetof(PyHeapTypeObject, ht_type.tp_is_gc),
offsetof(PyHeapTypeObject, ht_type.tp_iter),
offsetof(PyHeapTypeObject, ht_type.tp_iternext),
offsetof(PyHeapTypeObject, ht_type.tp_methods),
offsetof(PyHeapTypeObject, ht_type.tp_new),
offsetof(PyHeapTypeObject, ht_type.tp_repr),
offsetof(PyHeapTypeObject, ht_type.tp_richcompare),
offsetof(PyHeapTypeObject, ht_type.tp_setattr),
offsetof(PyHeapTypeObject, ht_type.tp_setattro),
offsetof(PyHeapTypeObject, ht_type.tp_str),
offsetof(PyHeapTypeObject, ht_type.tp_traverse),
offsetof(PyHeapTypeObject, ht_type.tp_members),
offsetof(PyHeapTypeObject, ht_type.tp_getset),
offsetof(PyHeapTypeObject, ht_type.tp_free),
offsetof(PyHeapTypeObject, as_number.nb_matrix_multiply),
offsetof(PyHeapTypeObject, as_number.nb_inplace_matrix_multiply),
offsetof(PyHeapTypeObject, as_async.am_await),
offsetof(PyHeapTypeObject, as_async.am_aiter),
offsetof(PyHeapTypeObject, as_async.am_anext),
offsetof(PyHeapTypeObject, ht_type.tp_finalize),
};

static PyTypeObject *
best_base(PyObject *bases)
{
    // We always have only one base
    return reinterpret_cast<PyTypeObject *>(PyTuple_GET_ITEM(bases, 0));
}

static PyObject *
_PyType_FromSpecWithBases(PyType_Spec *spec, PyObject *bases)
{
    PyHeapTypeObject *res = reinterpret_cast<PyHeapTypeObject *>(
                                PyType_GenericAlloc(&PyType_Type, 0));
    PyTypeObject *type, *base;
    PyObject *modname;
    char *s;
    char *res_start = reinterpret_cast<char *>(res);
    PyType_Slot *slot;

    if (res == nullptr)
        return nullptr;

    if (spec->name == nullptr) {
        PyErr_SetString(PyExc_SystemError,
                        "Type spec does not define the name field.");
        goto fail;
    }

    /* Set the type name and qualname */
    s = strrchr(const_cast<char *>(spec->name), '.');
    if (s == nullptr)
        s = (char*)spec->name;
    else
        s++;

    type = &res->ht_type;
    /* The flags must be initialized early, before the GC traverses us */
    type->tp_flags = spec->flags | Py_TPFLAGS_HEAPTYPE;
    res->ht_name = PyUnicode_FromString(s);
    if (!res->ht_name)
        goto fail;
    res->ht_qualname = res->ht_name;
    Py_INCREF(res->ht_qualname);
    type->tp_name = spec->name;

    /* Adjust for empty tuple bases */
    if (!bases) {
        base = &PyBaseObject_Type;
        /* See whether Py_tp_base(s) was specified */
        for (slot = spec->slots; slot->slot; slot++) {
            if (slot->slot == Py_tp_base)
                base = reinterpret_cast<PyTypeObject *>(slot->pfunc);
            else if (slot->slot == Py_tp_bases) {
                bases = reinterpret_cast<PyObject *>(slot->pfunc);
                Py_INCREF(bases);
            }
        }
        if (!bases)
            bases = PyTuple_Pack(1, base);
        if (!bases)
            goto fail;
    }
    else
        Py_INCREF(bases);

    /* Calculate best base, and check that all bases are type objects */
    base = best_base(bases);
    if (base == nullptr) {
        goto fail;
    }

    /* Initialize essential fields */
    type->tp_as_async = &res->as_async;
    type->tp_as_number = &res->as_number;
    type->tp_as_sequence = &res->as_sequence;
    type->tp_as_mapping = &res->as_mapping;
    type->tp_as_buffer = &res->as_buffer;
    /* Set tp_base and tp_bases */
    type->tp_bases = bases;
    bases = nullptr;
    Py_INCREF(base);
    type->tp_base = base;

    type->tp_basicsize = spec->basicsize;
    type->tp_itemsize = spec->itemsize;

    for (slot = spec->slots; slot->slot; slot++) {
        if (slot->slot == Py_tp_base || slot->slot == Py_tp_bases)
            /* Processed above */
            continue;
        *reinterpret_cast<void **>(res_start + slotoffsets[slot->slot]) = slot->pfunc;

        /* need to make a copy of the docstring slot, which usually
           points to a static string literal */
        if (slot->slot == Py_tp_doc) {
            const char *old_doc = reinterpret_cast<char *>(slot->pfunc);
            //_PyType_DocWithoutSignature(type->tp_name, slot->pfunc);
            size_t len = strlen(old_doc)+1;
            char *tp_doc = reinterpret_cast<char *>(PyObject_MALLOC(len));
            if (tp_doc == nullptr) {
                type->tp_doc = nullptr;
                PyErr_NoMemory();
                goto fail;
            }
            memcpy(tp_doc, old_doc, len);
            type->tp_doc = tp_doc;
        }
    }
    if (type->tp_dealloc == nullptr) {
        /* It's a heap type, so needs the heap types' dealloc.
           subtype_dealloc will call the base type's tp_dealloc, if
           necessary. */
        type->tp_dealloc = _PyPy_subtype_dealloc;
    }

    /// Here is the only change needed: Do not finalize type creation.
    // if (PyType_Ready(type) < 0)
    //     goto fail;
    type->tp_dict = PyDict_New();
    /// This is not found in PyPy:
    // if (type->tp_dictoffset) {
    //     res->ht_cached_keys = _PyDict_NewKeysForClass();
    // }

    /* Set type.__module__ */
    /// Removed __module__ handling, already implemented.

    return (PyObject*)res;

 fail:
    Py_DECREF(res);
    return nullptr;
}

#endif // PYPY_VERSION

} //extern "C"
