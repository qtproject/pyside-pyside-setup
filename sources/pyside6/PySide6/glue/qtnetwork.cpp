// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qudpsocket-readdatagram
Shiboken::AutoArrayPointer<char> data(%ARGUMENT_NAMES);
QHostAddress ha;
quint16 port;
%BEGIN_ALLOW_THREADS
%RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(data, %ARGUMENT_NAMES, &ha, &port);
%END_ALLOW_THREADS
QByteArray ba(data, retval);
%PYARG_0 = PyTuple_New(3);
PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[QByteArray](ba));
PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[QHostAddress](ha));
PyTuple_SET_ITEM(%PYARG_0, 2, %CONVERTTOPYTHON[quint16](port));
// @snippet qudpsocket-readdatagram

// @snippet qhostinfo-lookuphost-callable
auto *callable = %PYARG_2;
auto cppCallback = [callable](const QHostInfo &hostInfo)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    auto *pyHostInfo = %CONVERTTOPYTHON[QHostInfo](hostInfo);
    PyTuple_SET_ITEM(arglist.object(), 0, pyHostInfo);
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};

Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(%1, cppCallback);
// @snippet qhostinfo-lookuphost-callable

// @snippet qipv6address-len
return 16;
// @snippet qipv6address-len

// @snippet qipv6address-getitem
if (_i >= 16) {
    PyErr_SetString(PyExc_IndexError, "index out of bounds");
    return 0;
}
if (_i < 0)
    _i = 16 - qAbs(_i);

uint item = %CPPSELF.c[_i];
return %CONVERTTOPYTHON[uint](item);
// @snippet qipv6address-getitem

// @snippet qipv6address-setitem
if (_i >= 16) {
    PyErr_SetString(PyExc_IndexError, "index out of bounds");
    return -1;
}
if (_i < 0)
    _i = 16 - qAbs(_i);
quint8 item = %CONVERTTOCPP[quint8](_value);
%CPPSELF.c[_i] = item;
return 0;
// @snippet qipv6address-setitem
