// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "sbkerrors.h"
#include "helper.h"

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

void setPrivateMethod(const char *name)
{
    PyErr_Format(PyExc_TypeError, "%s is a private method.\", ", name);
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

namespace Warnings
{
void warnInvalidReturnValue(const char *className, const char *functionName,
                            const char *expectedType, const char *actualType)
{
    Shiboken::warning(PyExc_RuntimeWarning, 2,
                      "Invalid return value in function '%s.%s', expected %s, got %s.",
                      className, functionName, expectedType, actualType);
}

} // namespace Warnings
} // namespace Shiboken
