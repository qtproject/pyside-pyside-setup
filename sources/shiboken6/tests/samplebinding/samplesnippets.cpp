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

// @snippet stdcomplex_floor
%PYARG_0 = PyFloat_FromDouble(std::floor(%CPPSELF.abs_value()));
// @snippet stdcomplex_floor

// @snippet stdcomplex_ceil
%PYARG_0 = PyFloat_FromDouble(std::ceil(%CPPSELF.abs_value()));
// @snippet stdcomplex_ceil

// @snippet stdcomplex_abs
%PYARG_0 = PyFloat_FromDouble(%CPPSELF.abs_value());
// @snippet stdcomplex_abs

// @snippet stdcomplex_pow
%RETURN_TYPE %0 = %CPPSELF.pow(%1);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet stdcomplex_pow

// @snippet size_char_ct
// Convert a string "{width}x{height}" specification
{
    double width = -1;
    double height = -1;
    const std::string s = %1;
    const auto pos = s.find('x');
    if (pos != std::string::npos) {
        std::istringstream wstr(s.substr(0, pos));
        wstr >> width;
        std::istringstream hstr(s.substr(pos + 1, s.size() - pos - 1));
        hstr >> height;
    }
    %0 = new %TYPE(width, height);
}
// @snippet size_char_ct
