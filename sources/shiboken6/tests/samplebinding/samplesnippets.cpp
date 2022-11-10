// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

// @snippet intwrapper_add_ints
extern "C" {
static PyObject *Sbk_IntWrapper_add_ints(PyObject * /* self */, PyObject *args)
{
    PyObject *result = nullptr;
    if (PyTuple_Check(args) != 0 && PyTuple_Size(args) == 2) {
        PyObject *arg1 = PyTuple_GetItem(args, 0);
        PyObject *arg2 = PyTuple_GetItem(args, 1);
        if (PyLong_Check(arg1) != 0 && PyLong_Check(arg2) != 0)
            result = PyLong_FromLong(PyLong_AsLong(arg1) + PyLong_AsLong(arg2));
    }
    if (result == nullptr)
        PyErr_SetString(PyExc_TypeError, "expecting 2 ints");
    return result;
}
}
// @snippet intwrapper_add_ints
