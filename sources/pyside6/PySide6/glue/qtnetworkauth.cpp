/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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

