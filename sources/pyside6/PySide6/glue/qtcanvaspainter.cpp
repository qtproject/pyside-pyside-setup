// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

// @snippet qcpainterwidget-grabcanvas
auto callable = %PYARG_2;
auto callback = [callable](const QImage &result)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SetItem(arglist, 0, %CONVERTTOPYTHON[QImage](result));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);

};
Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(%1, callback);
// @snippet qcpainterwidget-grabcanvas
