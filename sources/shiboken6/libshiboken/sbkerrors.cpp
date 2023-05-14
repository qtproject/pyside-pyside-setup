// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "sbkerrors.h"
#include "sbkstring.h"
#include "helper.h"
#include "gilstate.h"

namespace Shiboken
{

// PYSIDE-2335: Track down if we can reach a Python error handler.
//              _pythonContextStack has always the current state of handler status
//              in its lowest bit.
//              Blocking calls like exec or run need to use `setBlocking`.
static thread_local std::size_t _pythonContextStack{};

PythonContextMarker::PythonContextMarker()
{
    // Shift history up and set lowest bit.
    _pythonContextStack = (_pythonContextStack * 2) + 1;
}

PythonContextMarker::~PythonContextMarker()
{
    // Shift history down.
    _pythonContextStack /= 2;
}

void PythonContextMarker::setBlocking()
{
    // Clear lowest bit.
    _pythonContextStack = _pythonContextStack / 2 * 2;
}

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

struct ErrorStore {
    PyObject *type;
    PyObject *exc;
    PyObject *traceback;
};

static thread_local ErrorStore savedError{};

void storeErrorOrPrint()
{
    // This error happened in a function with no way to return an error state.
    // Therefore, we handle the error when we are error checking, anyway.
    // But we do that only when we know that an error handler can pick it up.
    if (_pythonContextStack & 1)
        PyErr_Fetch(&savedError.type, &savedError.exc, &savedError.traceback);
    else
        PyErr_Print();
}

PyObject *occurred()
{
    if (savedError.type) {
        PyErr_Restore(savedError.type, savedError.exc, savedError.traceback);
        savedError.type = nullptr;
    }
    return PyErr_Occurred();
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

void warnDeprecated(const char *functionName)
{
    Shiboken::warning(PyExc_DeprecationWarning, 1,
                      "Function: '%s' is marked as deprecated, please check "
                      "the documentation for more information.",
                      functionName);
}

void warnDeprecated(const char *className, const char *functionName)
{
    Shiboken::warning(PyExc_DeprecationWarning, 1,
                      "Function: '%s.%s' is marked as deprecated, please check "
                      "the documentation for more information.",
                      className, functionName);
}

void warnDeprecatedEnum(const char *enumName)
{
    Shiboken::warning(PyExc_DeprecationWarning, 1,
                      "Enum: '%s' is marked as deprecated, please check "
                      "the documentation for more information.",
                      enumName);
}

void warnDeprecatedEnumValue(const char *enumName, const char *valueName)
{
    Shiboken::warning(PyExc_DeprecationWarning, 1,
                      "Enum value '%s.%s' is marked as deprecated, please check "
                      "the documentation for more information.",
                      enumName, valueName);

}

} // namespace Warnings
} // namespace Shiboken
