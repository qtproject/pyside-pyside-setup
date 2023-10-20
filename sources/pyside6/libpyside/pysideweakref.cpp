// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysideweakref.h"

#include <sbkpython.h>
#include <shiboken.h>

struct PySideCallableObject {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PySideWeakRefFunction weakref_func;
    void *user_data;
};

static PyObject *CallableObject_call(PyObject *callable_object, PyObject *args, PyObject *kw);

static PyTypeObject *createCallableObjectType()
{
    PyType_Slot PySideCallableObjectType_slots[] = {
        {Py_tp_call, reinterpret_cast<void *>(CallableObject_call)},
        {Py_tp_dealloc, reinterpret_cast<void *>(Sbk_object_dealloc)},
        {0, nullptr}
    };

    PyType_Spec PySideCallableObjectType_spec = {
        "1:PySide.Callable",
        sizeof(PySideCallableObject),
        0,
        Py_TPFLAGS_DEFAULT,
        PySideCallableObjectType_slots,
    };

    return SbkType_FromSpec(&PySideCallableObjectType_spec);
}

static PyTypeObject *PySideCallableObject_TypeF()
{
    static auto *type = createCallableObjectType();
    return type;
}

static PyObject *CallableObject_call(PyObject *callable_object, PyObject *args, PyObject * /* kw */)
{
    PySideCallableObject *obj = reinterpret_cast<PySideCallableObject *>(callable_object);
    obj->weakref_func(obj->user_data);

    Py_XDECREF(PyTuple_GET_ITEM(args, 0)); //kill weak ref object
    Py_RETURN_NONE;
}

namespace PySide::WeakRef {

PyObject *create(PyObject *obj, PySideWeakRefFunction func, void *userData)
{
    if (obj == Py_None)
        return nullptr;

    auto *callableObject_Type = PySideCallableObject_TypeF();
    auto *callableObject_PyObject = reinterpret_cast<PyObject *>(callableObject_Type);
    if (callableObject_PyObject->ob_type == nullptr) {
        callableObject_PyObject->ob_type = &PyType_Type;
        PyType_Ready(callableObject_Type);
    }

    PyTypeObject *type = PySideCallableObject_TypeF();
    PySideCallableObject *callable = PyObject_New(PySideCallableObject, type);
    if (!callable || PyErr_Occurred())
        return nullptr;

    PyObject *weak = PyWeakref_NewRef(obj, reinterpret_cast<PyObject *>(callable));
    if (!weak || PyErr_Occurred())
        return nullptr;

    callable->weakref_func = func;
    callable->user_data = userData;
    Py_DECREF(callable); // PYSIDE-79: after decref the callable is undefined (theoretically)

    return reinterpret_cast<PyObject *>(weak);
}

} // namespace PySide::WeakRef
