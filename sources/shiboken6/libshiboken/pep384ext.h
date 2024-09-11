// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PEP384EXT_H
#define PEP384EXT_H

#include "pep384impl.h"

/// Returns the allocator slot of the PyTypeObject.
inline allocfunc PepExt_Type_GetAllocSlot(PyTypeObject *t)
{
    return reinterpret_cast<allocfunc>(PepType_GetSlot(t, Py_tp_alloc));
}

/// Invokes the allocator slot of the PyTypeObject.
template <class Type>
inline Type *PepExt_TypeCallAlloc(PyTypeObject *t, Py_ssize_t nitems)
{
    PyObject *result = PepExt_Type_GetAllocSlot(t)(t, nitems);
    return reinterpret_cast<Type *>(result);
}

/// Returns the getattro slot of the PyTypeObject.
inline getattrofunc PepExt_Type_GetGetAttroSlot(PyTypeObject *t)
{
    return reinterpret_cast<getattrofunc>(PepType_GetSlot(t, Py_tp_getattro));
}

/// Returns the setattro slot of the PyTypeObject.
inline setattrofunc PepExt_Type_GetSetAttroSlot(PyTypeObject *t)
{
    return reinterpret_cast<setattrofunc>(PepType_GetSlot(t, Py_tp_setattro));
}

/// Returns the descr_get slot of the PyTypeObject.
inline descrgetfunc PepExt_Type_GetDescrGetSlot(PyTypeObject *t)
{
    return reinterpret_cast<descrgetfunc>(PepType_GetSlot(t, Py_tp_descr_get));
}

/// Invokes the descr_get slot of the PyTypeObject.
inline PyObject *PepExt_Type_CallDescrGet(PyObject *self, PyObject *obj, PyObject *type)
{
    return PepExt_Type_GetDescrGetSlot(Py_TYPE(self))(self, obj, type);
}

/// Returns the descr_set slot of the PyTypeObject.
inline descrsetfunc PepExt_Type_GetDescrSetSlot(PyTypeObject *t)
{
    return reinterpret_cast<descrsetfunc>(PepType_GetSlot(t, Py_tp_descr_set));
}

/// Returns the call slot of the PyTypeObject.
inline ternaryfunc PepExt_Type_GetCallSlot(PyTypeObject *t)
{
    return reinterpret_cast<ternaryfunc>(PepType_GetSlot(t, Py_tp_call));
}

/// Returns the new slot of the PyTypeObject.
inline newfunc PepExt_Type_GetNewSlot(PyTypeObject *t)
{
    return reinterpret_cast<newfunc>(PepType_GetSlot(t, Py_tp_new));
}

/// Returns the init slot of the PyTypeObject.
inline initproc PepExt_Type_GetInitSlot(PyTypeObject *t)
{
    return reinterpret_cast<initproc>(PepType_GetSlot(t, Py_tp_init));
}

/// Returns the free slot of the PyTypeObject.
inline freefunc PepExt_Type_GetFreeSlot(PyTypeObject *t)
{
    return reinterpret_cast<freefunc>(PepType_GetSlot(t, Py_tp_free));
}

/// Invokes the free slot of the PyTypeObject.
inline void PepExt_TypeCallFree(PyTypeObject *t, void *object)
{
    PepExt_Type_GetFreeSlot(t)(object);
}

/// Invokes the free slot of the PyTypeObject.
inline void PepExt_TypeCallFree(PyObject *object)
{
    PepExt_Type_GetFreeSlot(Py_TYPE(object))(object);
}

LIBSHIBOKEN_API bool PepExt_Weakref_IsAlive(PyObject *weakRef);

#endif // PEP384EXT_H
