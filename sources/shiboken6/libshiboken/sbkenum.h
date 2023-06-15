// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBKENUM_H
#define SBKENUM_H

#include "sbkpython.h"
#include "shibokenmacros.h"

extern "C"
{

LIBSHIBOKEN_API bool PyEnumMeta_Check(PyObject *ob);

/// exposed for the signature module
LIBSHIBOKEN_API void init_enum();

struct SbkConverter;
struct SbkEnumType;

struct SbkEnumTypePrivate
{
    SbkConverter *converter;
};

/// PYSIDE-1735: Pass on the Python enum/flag information.
LIBSHIBOKEN_API void initEnumFlagsDict(PyTypeObject *type);

/// PYSIDE-1735: Make sure that we can import the Python enum implementation.
LIBSHIBOKEN_API PyTypeObject *getPyEnumMeta();
/// PYSIDE-1735: Helper function supporting QEnum
LIBSHIBOKEN_API int enumIsFlag(PyObject *ob_enum);

}

namespace Shiboken { namespace Enum {

enum : int {
    ENOPT_OLD_ENUM        = 0x00,   // PySide 6.6: no longer supported
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

using EnumValueType = long long;

LIBSHIBOKEN_API bool check(PyObject *obj);

LIBSHIBOKEN_API PyObject *newItem(PyTypeObject *enumType, EnumValueType itemValue,
                                  const char *itemName = nullptr);

LIBSHIBOKEN_API EnumValueType getValue(PyObject *enumItem);
LIBSHIBOKEN_API PyObject *getEnumItemFromValue(PyTypeObject *enumType,
                                               EnumValueType itemValue);

/// Sets the enum/flag's type converter.
LIBSHIBOKEN_API void setTypeConverter(PyTypeObject *type, SbkConverter *converter, bool isFlag);

/// Creating Python enums for different types.
LIBSHIBOKEN_API PyTypeObject *createPythonEnum(PyObject *module,
    const char *fullName, const char *enumItemStrings[], int64_t enumValues[]);

LIBSHIBOKEN_API PyTypeObject *createPythonEnum(PyObject *module,
    const char *fullName, const char *enumItemStrings[], uint64_t enumValues[]);

LIBSHIBOKEN_API PyTypeObject *createPythonEnum(PyObject *module,
    const char *fullName, const char *enumItemStrings[], int32_t enumValues[]);

LIBSHIBOKEN_API PyTypeObject *createPythonEnum(PyObject *module,
    const char *fullName, const char *enumItemStrings[], uint32_t enumValues[]);

LIBSHIBOKEN_API PyTypeObject *createPythonEnum(PyObject *module,
    const char *fullName, const char *enumItemStrings[], int16_t enumValues[]);

LIBSHIBOKEN_API PyTypeObject *createPythonEnum(PyObject *module,
    const char *fullName, const char *enumItemStrings[], uint16_t enumValues[]);

LIBSHIBOKEN_API PyTypeObject *createPythonEnum(PyObject *module,
    const char *fullName, const char *enumItemStrings[], int8_t enumValues[]);

LIBSHIBOKEN_API PyTypeObject *createPythonEnum(PyObject *module,
    const char *fullName, const char *enumItemStrings[], uint8_t enumValues[]);

/// This template removes duplication by inlining necessary type casts.
template <typename IntT>
inline PyTypeObject *createPythonEnum(PyTypeObject *scope,
    const char *fullName, const char *enumItemStrings[], IntT enumValues[])
{
    auto *obScope = reinterpret_cast<PyObject *>(scope);
    return createPythonEnum(obScope, fullName, enumItemStrings, enumValues);
}

} // namespace Enum
} // namespace Shiboken

#endif // SKB_PYENUM_H
