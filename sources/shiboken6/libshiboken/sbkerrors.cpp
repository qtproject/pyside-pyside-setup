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

#include "sbkerrors.h"

namespace Shiboken
{
namespace Errors
{

void setInstantiateAbstractClass(const char *name)
{
    PyErr_Format(PyExc_NotImplementedError,
                 "'%s' represents a C++ abstract class and cannot be instantiated", name);
}

void setInstantiateAbstractClassDisabledWrapper(const char *name)
{
    PyErr_Format(PyExc_NotImplementedError,
                 "Abstract class '%s' cannot be instantiated since the wrapper has been disabled.",
                 name);
}

void setInvalidTypeDeletion(const char *name)
{
    PyErr_Format(PyExc_TypeError, "'%s' may not be deleted", name);
}

void setOperatorNotImplemented()
{
    PyErr_SetString(PyExc_NotImplementedError, "operator not implemented.");
}

void setPureVirtualMethodError(const char *name)
{
    PyErr_Format(PyExc_NotImplementedError, "pure virtual method '%s' not implemented.", name);
}


void setReverseOperatorNotImplemented()
{
    PyErr_SetString(PyExc_NotImplementedError, "reverse operator not implemented.");
}

void setSequenceTypeError(const char *expectedType)
{
    PyErr_Format(PyExc_TypeError,
                 "attributed value with wrong type, '%s' or other convertible type expected",
                 expectedType);
}

void setSetterTypeError(const char *name, const char *expectedType)
{
    PyErr_Format(PyExc_TypeError,
                 "wrong type attributed to '%s', '%s' or convertible type expected",
                 name, expectedType);
}

void setWrongContainerType()
{
    PyErr_SetString(PyExc_TypeError, "Wrong type passed to container conversion.");
}

} // namespace Errors
} // namespace Shiboken
