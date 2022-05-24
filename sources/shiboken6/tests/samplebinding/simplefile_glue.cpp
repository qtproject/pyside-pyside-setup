// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

if (!%CPPSELF.%FUNCTION_NAME()) {
    PyObject* error_msg = PyBytes_FromFormat(
            "Could not open file: \"%s\"", %CPPSELF->filename());
    PyErr_SetObject(PyExc_IOError, error_msg);
    return 0;
}
