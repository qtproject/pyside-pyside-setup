// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBKERRORS_H
#define SBKERRORS_H

#include "sbkpython.h"
#include "shibokenmacros.h"

namespace Shiboken
{
namespace Errors
{

LIBSHIBOKEN_API void setInstantiateAbstractClass(const char *name);
LIBSHIBOKEN_API void setInstantiateAbstractClassDisabledWrapper(const char *name);
LIBSHIBOKEN_API void setInvalidTypeDeletion(const char *name);
LIBSHIBOKEN_API void setOperatorNotImplemented();
LIBSHIBOKEN_API void setPureVirtualMethodError(const char *name);
LIBSHIBOKEN_API void setPrivateMethod(const char *name);
LIBSHIBOKEN_API void setReverseOperatorNotImplemented();
LIBSHIBOKEN_API void setSequenceTypeError(const char *expectedType);
LIBSHIBOKEN_API void setSetterTypeError(const char *name, const char *expectedType);
LIBSHIBOKEN_API void setWrongContainerType();

} // namespace Errors

namespace Warnings
{
/// Warn about invalid return value of overwritten virtual
LIBSHIBOKEN_API void warnInvalidReturnValue(const char *className, const char *functionName,
                                            const char *expectedType, const char *actualType);
LIBSHIBOKEN_API void warnDeprecated(const char *functionName);
LIBSHIBOKEN_API void warnDeprecated(const char *className, const char *functionName);
} // namespace Warnings

} // namespace Shiboken

#endif // SBKERRORS_H
