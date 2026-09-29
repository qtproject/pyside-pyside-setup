// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBKERRORS_H
#define SBKERRORS_H

#include "sbkpython.h"
#include "shibokenmacros.h"
#include "shibokenclasshelpermacros.h"

#include <memory>

// Craving for C++20 and std::source_location::current()
#if defined(_MSC_VER)
#  define SBK_FUNC_INFO     __FUNCSIG__
#elif defined(__GNUC__)
#  define SBK_FUNC_INFO     __PRETTY_FUNCTION__
#else
#  define SBK_FUNC_INFO     __FUNCTION__
#endif

namespace Shiboken
{

struct LIBSHIBOKEN_API PythonContextMarker
{
public:
    LIBSHIBOKEN_DISABLE_COPY_MOVE(PythonContextMarker)

    explicit PythonContextMarker();
    ~PythonContextMarker();
    void setBlocking();
};

namespace Errors
{

struct ErrorStore;

class Stash
{
public:
    LIBSHIBOKEN_DISABLE_COPY_MOVE(Stash)

    LIBSHIBOKEN_API Stash();
    LIBSHIBOKEN_API ~Stash();

    LIBSHIBOKEN_API operator bool() const { return getException() != nullptr; }
    [[nodiscard]] LIBSHIBOKEN_API PyObject *getException() const;

    LIBSHIBOKEN_API void restore();
    LIBSHIBOKEN_API void release();

private:
    std::unique_ptr<ErrorStore> m_store;
};

LIBSHIBOKEN_API void setIndexOutOfBounds(Py_ssize_t value, Py_ssize_t minValue,
                                         Py_ssize_t maxValue);
LIBSHIBOKEN_API void setInstantiateAbstractClass(const char *name);
LIBSHIBOKEN_API void setInstantiateAbstractClassDisabledWrapper(const char *name);
LIBSHIBOKEN_API void setInstantiateNamespace(const char *name);
LIBSHIBOKEN_API void setInstantiateNonConstructible(const char *name);
LIBSHIBOKEN_API void setInvalidTypeDeletion(const char *name);
LIBSHIBOKEN_API void setOperatorNotImplemented();
LIBSHIBOKEN_API void setPureVirtualMethodError(const char *name);
LIBSHIBOKEN_API void setPrivateMethod(const char *name);
LIBSHIBOKEN_API void setReverseOperatorNotImplemented();
LIBSHIBOKEN_API void setSequenceTypeError(const char *expectedType);
LIBSHIBOKEN_API void setSetterTypeError(const char *name, const char *expectedType);
LIBSHIBOKEN_API void setWrongContainerType();

/*!
    Reports an error ASAP: Instead of printing, store for later re-raise.
    This replaces \c PyErr_Print, which cannot report errors as exception.
    To be used in contexts where raising errors is impossible.
*/
LIBSHIBOKEN_API void storeErrorOrPrint();

/*!
    Calls storeErrorOrPrint() and prints the context (\a className,
    \a funcName) to report errors when calling Python overrides of
    virtual functions.
*/
LIBSHIBOKEN_API void storePythonOverrideErrorOrPrint(const char *className, const char *funcName);

/*!
    Handles an error as in \c PyErr_Occurred(), but also checks for errors
    which were captured by storeErrorOrPrint().
    To be used in normal error checks.
*/
LIBSHIBOKEN_API PyObject *occurred();

} // namespace Errors

namespace Warnings
{
/*!
    Warns about an invalid return value of the overridden virtual function
    \a functionName of class \a className (\a actualType returned instead
    of \a expectedType).
*/
LIBSHIBOKEN_API void warnInvalidReturnValue(const char *className, const char *functionName,
                                            const char *expectedType, const char *actualType);
LIBSHIBOKEN_API void warnDeprecated(const char *functionName);
LIBSHIBOKEN_API void warnDeprecated(const char *className, const char *functionName);
LIBSHIBOKEN_API void warnDeprecatedEnum(const char *enumName);
LIBSHIBOKEN_API void warnDeprecatedEnumValue(const char *enumName, const char *valueName);
} // namespace Warnings

} // namespace Shiboken

#endif // SBKERRORS_H
