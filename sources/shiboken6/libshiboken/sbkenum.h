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

extern LIBSHIBOKEN_API PyTypeObject *SbkEnumType_TypeF(void);
struct SbkConverter;
struct SbkEnumType;
struct SbkEnumTypePrivate;

} // extern "C"

namespace Shiboken
{

inline bool isShibokenEnum(PyObject *pyObj)
{
    return Py_TYPE(Py_TYPE(pyObj)) == SbkEnumType_TypeF();
}

namespace Enum
{
    using EnumValueType = long long;

    LIBSHIBOKEN_API bool check(PyObject *obj);
    /**
     *  Creates a new enum type (and its flags type, if any is given)
     *  and registers it to Python and adds it to \p module.
     *  \param module       Module to where the new enum type will be added.
     *  \param name         Name of the enum.
     *  \param fullName     Name of the enum that includes all scope information (e.g.: "module.Enum").
     *  \param cppName      Full qualified C++ name of the enum.
     *  \param flagsType    Optional Python type for the flags associated with the enum.
     *  \return The new enum type or NULL if it fails.
     */
    LIBSHIBOKEN_API PyTypeObject *createGlobalEnum(PyObject *module,
                                                   const char *name,
                                                   const char *fullName,
                                                   const char *cppName,
                                                   PyTypeObject *flagsType = nullptr);
    /// This function does the same as createGlobalEnum, but adds the enum to a Shiboken type or namespace.
    LIBSHIBOKEN_API PyTypeObject *createScopedEnum(PyTypeObject *scope,
                                                   const char *name,
                                                   const char *fullName,
                                                   const char *cppName,
                                                   PyTypeObject *flagsType = nullptr);

    /**
     *  Creates a new enum item for a given enum type and adds it to \p module.
     *  \param enumType  Enum type to where the new enum item will be added.
     *  \param module    Module to where the enum type of the new enum item belongs.
     *  \param itemName  Name of the enum item.
     *  \param itemValue Numerical value of the enum item.
     *  \return true if everything goes fine, false if it fails.
     */
    LIBSHIBOKEN_API bool createGlobalEnumItem(PyTypeObject *enumType, PyObject *module,
                                              const char *itemName,
                                              EnumValueType itemValue);
    /// This function does the same as createGlobalEnumItem, but adds the enum to a Shiboken type or namespace.
    LIBSHIBOKEN_API bool createScopedEnumItem(PyTypeObject *enumType, PyTypeObject *scope,
                                              const char *itemName, EnumValueType itemValue);

    LIBSHIBOKEN_API PyObject *newItem(PyTypeObject *enumType, EnumValueType itemValue,
                                      const char *itemName = nullptr);

    LIBSHIBOKEN_API PyTypeObject *newTypeWithName(const char *name, const char *cppName,
                                                  PyTypeObject *numbers_fromFlag=nullptr);
    LIBSHIBOKEN_API const char *getCppName(PyTypeObject *type);
    LIBSHIBOKEN_API PyObject *getCppNameNew(PyTypeObject *type);

    LIBSHIBOKEN_API EnumValueType getValue(PyObject *enumItem);
    LIBSHIBOKEN_API PyObject *getEnumItemFromValue(PyTypeObject *enumType,
                                                   EnumValueType itemValue);

    /// Sets the enum/flag's type converter.
    LIBSHIBOKEN_API void setTypeConverter(PyTypeObject *type, SbkConverter *converter, bool isFlag);

    LIBSHIBOKEN_API PyObject *unpickleEnum(PyObject *, PyObject *);
}

} // namespace Shiboken

#endif // SKB_PYENUM_H
