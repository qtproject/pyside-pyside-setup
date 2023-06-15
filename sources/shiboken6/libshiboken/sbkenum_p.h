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
};

extern "C" {

/// PYSIDE-1735: Pass on the Python enum/flag information.
LIBSHIBOKEN_API void initEnumFlagsDict(PyTypeObject *type);

/// PYSIDE-1735: Patching the Enum / Flags implementation. Remove in 6.4
LIBSHIBOKEN_API PyTypeObject *morphLastEnumToPython();
LIBSHIBOKEN_API PyTypeObject *mapFlagsToSameEnum(PyTypeObject *FType, PyTypeObject *EType);

/// PYSIDE-1735: Make sure that we can import the Python enum implementation.
LIBSHIBOKEN_API PyTypeObject *getPyEnumMeta();
/// PYSIDE-1735: Helper function supporting QEnum
LIBSHIBOKEN_API int enumIsFlag(PyObject *ob_enum);
/// PYSIDE-1735: Helper function to ask what enum we are using
LIBSHIBOKEN_API bool usingNewEnum();

}

namespace Shiboken { namespace Enum {

enum : int {
    ENOPT_OLD_ENUM        = 0x00,
    ENOPT_NEW_ENUM        = 0x01,
    ENOPT_INHERIT_INT     = 0x02,
    ENOPT_GLOBAL_SHORTCUT = 0x04,
    ENOPT_SCOPED_SHORTCUT = 0x08,
    ENOPT_NO_FAKESHORTCUT = 0x10,
    ENOPT_NO_FAKERENAMES  = 0x20,
    ENOPT_NO_ZERODEFAULT  = 0x40,
    ENOPT_NO_MISSING      = 0x80,
};

LIBSHIBOKEN_API extern int enumOption;

}}

#endif // SBKENUM_P_H
