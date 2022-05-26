// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBKENUM_P_H
#define SBKENUM_P_H

#include "sbkpython.h"
#include "shibokenmacros.h"

struct SbkEnumTypePrivate
{
    SbkConverter *converter;
    const char *cppName;
    PyTypeObject *replacementType;
};

extern "C" {

/// PYSIDE-1735: Patching the Enum / Flags implementation. Remove in 6.4
LIBSHIBOKEN_API PyTypeObject *morphLastEnumToPython();
LIBSHIBOKEN_API PyTypeObject *mapFlagsToSameEnum(PyTypeObject *FType, PyTypeObject *EType);

/// PYSIDE-1735: Make sure that we can import the Python enum implementation.
LIBSHIBOKEN_API PyTypeObject *getPyEnumMeta();
/// PYSIDE-1735: Helper function supporting QEnum
LIBSHIBOKEN_API int enumIsFlag(PyObject *ob_enum);

}

#endif // SBKENUM_P_H
