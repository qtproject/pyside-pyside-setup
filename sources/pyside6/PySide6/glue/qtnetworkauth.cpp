// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qabstractoauth-setmodifyparametersfunction
auto callable = %PYARG_1;
auto callback = [callable](QAbstractOAuth::Stage stage, QMultiMap<QString, QVariant>* dictPointer) -> void
{
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 1 of %FUNCTION_NAME must be a callable.");
        return;
    }
    Shiboken::GilState state;
    QMultiMap<QString, QVariant> dict = *dictPointer;
    Shiboken::AutoDecRef arglist(PyTuple_New(2));
    PyTuple_SET_ITEM(arglist, 0, %CONVERTTOPYTHON[QAbstractOAuth::Stage](stage));
    PyTuple_SET_ITEM(arglist, 1, %CONVERTTOPYTHON[QMultiMap<QString, QVariant>](dict));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));

    PyObject *key;
    PyObject *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(ret, &pos, &key, &value)) {
        QString cppKey = %CONVERTTOCPP[QString](key);
        QVariant cppValue = %CONVERTTOCPP[QVariant](value);
        dictPointer->replace(cppKey, cppValue);
    }

    Py_DECREF(callable);
    return;

};
Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(callback);
// @snippet qabstractoauth-setmodifyparametersfunction

