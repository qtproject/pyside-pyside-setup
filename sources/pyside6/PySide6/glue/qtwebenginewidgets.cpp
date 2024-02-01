// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qwebenginepage-findtext
auto callable = %PYARG_3;
auto callback = [callable](const QWebEngineFindTextResult &result)
{
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 3 of %FUNCTION_NAME must be a callable.");
        return;
    }
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QWebEngineFindTextResult](result));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);

};
Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(%1, %2, callback);
// @snippet qwebenginepage-findtext

// @snippet qwebenginepage-print
auto printer = %PYARG_1;
auto callable = %PYARG_2;
auto callback = [printer, callable](bool succeeded)
{
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 2 of %FUNCTION_NAME must be a callable.");
        return;
    }
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[bool](succeeded));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
    Py_DECREF(printer);

};
Py_INCREF(printer); // Add a reference to the printer until asynchronous printing has finished
Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(%1, callback);
// @snippet qwebenginepage-print

// @snippet qwebenginepage-convertto
auto callable = %PYARG_1;
auto callback = [callable](const QString &text)
{
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 1 of %FUNCTION_NAME must be a callable.");
        return;
    }
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QString](text));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};

Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(callback);
// @snippet qwebenginepage-convertto

// @snippet qwebenginepage-runjavascript
auto callable = %PYARG_3;
auto callback = [callable](const QVariant &result)
{
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 3 of %FUNCTION_NAME must be a callable.");
        return;
    }
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    switch (result.type()) {
    case QVariant::Bool: {
        const bool value = result.toBool();
        PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QString](value));
    }
        break;
     case QVariant::Int:
     case QVariant::UInt:
     case QVariant::LongLong:
     case QVariant::ULongLong:
     case QVariant::Double: {
        const double number = result.toDouble();
        PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[double](number));
    }
        break;
    default: {
        const QString value = result.toString();
        PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QString](value));
    }
        break;
    }
   // PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[bool](found));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};

Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(%1, %2, callback);
// @snippet qwebenginepage-runjavascript

// @snippet qwebenginepage-printtopdf
auto callable = %PYARG_1;
auto callback = [callable](const QByteArray &pdf)
{
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 1 of %FUNCTION_NAME must be a callable.");
        return;
    }
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QByteArray](pdf));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};

Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(callback, %2);
// @snippet qwebenginepage-printtopdf
