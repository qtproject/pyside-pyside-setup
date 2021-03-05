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

#include "pysideweakref.h"

#include <sbkpython.h>
#include <shiboken.h>

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PySideWeakRefFunction weakref_func;
    void *user_data;
} PySideCallableObject;

static PyObject *CallableObject_call(PyObject *callable_object, PyObject *args, PyObject *kw);

static PyType_Slot PySideCallableObjectType_slots[] = {
    {Py_tp_call, (void *)CallableObject_call},
    {Py_tp_dealloc, (void *)Sbk_object_dealloc},
    {0, 0}
};
static PyType_Spec PySideCallableObjectType_spec = {
    "1:PySide.Callable",
    sizeof(PySideCallableObject),
    0,
    Py_TPFLAGS_DEFAULT,
    PySideCallableObjectType_slots,
};


static PyTypeObject *PySideCallableObjectTypeF()
{
    static PyTypeObject *type =
        reinterpret_cast<PyTypeObject *>(SbkType_FromSpec(&PySideCallableObjectType_spec));
    return type;
}

static PyObject *CallableObject_call(PyObject *callable_object, PyObject *args, PyObject * /* kw */)
{
    PySideCallableObject *obj = reinterpret_cast<PySideCallableObject *>(callable_object);
    obj->weakref_func(obj->user_data);

    Py_XDECREF(PyTuple_GET_ITEM(args, 0)); //kill weak ref object
    Py_RETURN_NONE;
}

namespace PySide { namespace WeakRef {

PyObject *create(PyObject *obj, PySideWeakRefFunction func, void *userData)
{
    if (obj == Py_None)
        return 0;

    if (Py_TYPE(PySideCallableObjectTypeF()) == 0)
    {
        Py_TYPE(PySideCallableObjectTypeF()) = &PyType_Type;
        PyType_Ready(PySideCallableObjectTypeF());
    }

    PyTypeObject *type = PySideCallableObjectTypeF();
    PySideCallableObject *callable = PyObject_New(PySideCallableObject, type);
    if (!callable || PyErr_Occurred())
        return 0;

    PyObject *weak = PyWeakref_NewRef(obj, reinterpret_cast<PyObject *>(callable));
    if (!weak || PyErr_Occurred())
        return 0;

    callable->weakref_func = func;
    callable->user_data = userData;
    Py_DECREF(callable); // PYSIDE-79: after decref the callable is undefined (theoretically)

    return reinterpret_cast<PyObject *>(weak);
}

} }  //namespace

