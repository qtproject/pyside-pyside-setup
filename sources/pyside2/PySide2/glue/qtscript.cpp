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

// @snippet qscriptvalue-repr
if (%CPPSELF.isVariant() || %CPPSELF.isString()) {
    QString format = QString::asprintf("%s(\"%s\")",
            Py_TYPE(%PYSELF)->tp_name,
            qPrintable(%CPPSELF.toString()));
    %PYARG_0 = Shiboken::String::fromCString(qPrintable(format));
 } else {
    %PYARG_0 = Shiboken::String::fromCString(Py_TYPE(%PYSELF)->tp_name);
}
// @snippet qscriptvalue-repr

// @snippet qscriptvalue-mgetitem
Shiboken::AutoDecRef key(PyObject_Str(_key));
QVariant res = %CPPSELF.property(Shiboken::String::toCString(key.object())).toVariant();
if (res.isValid()) {
    return %CONVERTTOPYTHON[QVariant](res);
} else {
    PyObject *errorType = PyInt_Check(_key) ? PyExc_IndexError : PyExc_KeyError;
    PyErr_SetString(errorType, "Key not found.");
    return 0;
}
// @snippet qscriptvalue-mgetitem

// @snippet qscriptvalueiterator-next
if (%CPPSELF.hasNext()) {
    %CPPSELF.next();
    QString name = %CPPSELF.name();
    QVariant value = %CPPSELF.value().toVariant();
    %PYARG_0 = PyTuple_New(2);
    PyTuple_SET_ITEM(%PYARG_0, 0, %CONVERTTOPYTHON[QString](name));
    PyTuple_SET_ITEM(%PYARG_0, 1, %CONVERTTOPYTHON[QVariant](value));
} else {
    PyErr_SetNone(PyExc_StopIteration);
}
// @snippet qscriptvalueiterator-next
