// Copyright (C) 2025 Ford Motor Company
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "pysidedynamicenum_p.h"
#include "pysidedynamiccommon_p.h"

#include <autodecref.h>
#include <sbkconverter.h>
#include <sbkenum.h>

#include <QtCore/qmetaobject.h>

using namespace Shiboken;

// Remote Objects transfer enums as integers of the underlying type.
#define CREATE_ENUM_CONVERSION_FUNCTIONS(SUFFIX, INT_TYPE, PY_TYPE) \
static void pythonToCpp_PyEnum_QEnum_##SUFFIX(PyObject *pyIn, void *cppOut) \
{ \
    Enum::EnumValueType value = Enum::getValue(pyIn); \
    INT_TYPE val(value); \
    *reinterpret_cast<INT_TYPE *>(cppOut) = val; \
} \
static PythonToCppFunc is_PyEnum_PythonToCpp_QEnum_##SUFFIX##_Convertible(PyObject *pyIn) \
{ \
    if (Enum::check(pyIn)) \
        return pythonToCpp_PyEnum_QEnum_##SUFFIX; \
    return {}; \
} \
static PyObject *cppToPython_QEnum_##SUFFIX##_PyEnum(const void *cppIn) \
{ \
    auto convertedCppIn = *reinterpret_cast<const INT_TYPE *>(cppIn); \
    return PY_TYPE(convertedCppIn); \
}

CREATE_ENUM_CONVERSION_FUNCTIONS(I8, int8_t, PyLong_FromLong)
CREATE_ENUM_CONVERSION_FUNCTIONS(I16, int16_t, PyLong_FromLong)
CREATE_ENUM_CONVERSION_FUNCTIONS(I32, int32_t, PyLong_FromLong)
CREATE_ENUM_CONVERSION_FUNCTIONS(U8, uint8_t, PyLong_FromUnsignedLong)
CREATE_ENUM_CONVERSION_FUNCTIONS(U16, uint16_t, PyLong_FromUnsignedLong)
CREATE_ENUM_CONVERSION_FUNCTIONS(U32, uint32_t, PyLong_FromUnsignedLong)
CREATE_ENUM_CONVERSION_FUNCTIONS(I64, int64_t, PyLong_FromLongLong)
CREATE_ENUM_CONVERSION_FUNCTIONS(U64, uint64_t, PyLong_FromUnsignedLongLong)

PyTypeObject *createEnumType(QMetaEnum *metaEnum)
{
    static const auto namePrefix = QByteArrayLiteral("2:PySide6.QtRemoteObjects.DynamicEnum.");
    auto fullName = namePrefix + metaEnum->scope() + "." + metaEnum->enumName();

    AutoDecRef args(PyList_New(0));
    auto *pyEnumItems = args.object();
    auto metaType = metaEnum->metaType();
    auto underlyingType = metaType.underlyingType();
    bool isUnsigned = underlyingType.flags().testFlag(QMetaType::IsUnsignedEnumeration);
    for (int idx = 0; idx < metaEnum->keyCount(); ++idx) {
        auto *key = PyUnicode_FromString(metaEnum->key(idx));
        auto *key_value = PyTuple_New(2);
        PyTuple_SetItem(key_value, 0, key);
        // Value should only return a nullopt if there is no metaObject or the index is not valid
        auto valueOpt = metaEnum->value64(idx);
        if (!valueOpt) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to get value64 from enum");
            return nullptr;
        }
        if (isUnsigned) {
            auto *value = PyLong_FromUnsignedLongLong(*valueOpt);
            PyTuple_SetItem(key_value, 1, value);
        } else {
            auto *value = PyLong_FromLongLong(*valueOpt);
            PyTuple_SetItem(key_value, 1, value);
        }
        PyList_Append(pyEnumItems, key_value);
    }

    PyTypeObject *newType{};
    if (metaEnum->isFlag())
        newType = Enum::createPythonEnum(fullName.constData(), pyEnumItems, "Flag");
    else
        newType = Enum::createPythonEnum(fullName.constData(), pyEnumItems);

    SbkConverter *converter = nullptr;
    switch (underlyingType.sizeOf()) {
        case 1:
            if (isUnsigned) {
                converter = Conversions::createConverter(newType,
                                                         cppToPython_QEnum_U8_PyEnum);
                Conversions::addPythonToCppValueConversion(converter,
                                                           pythonToCpp_PyEnum_QEnum_U8,
                                                           is_PyEnum_PythonToCpp_QEnum_U8_Convertible);
            } else {
                converter = Conversions::createConverter(newType,
                                                         cppToPython_QEnum_I8_PyEnum);
                Conversions::addPythonToCppValueConversion(converter,
                                                           pythonToCpp_PyEnum_QEnum_I8,
                                                           is_PyEnum_PythonToCpp_QEnum_I8_Convertible);
            }
            break;
        case 2:
            if (isUnsigned) {
                converter = Conversions::createConverter(newType,
                                                         cppToPython_QEnum_U16_PyEnum);
                Conversions::addPythonToCppValueConversion(converter,
                                                           pythonToCpp_PyEnum_QEnum_U16,
                                                           is_PyEnum_PythonToCpp_QEnum_U16_Convertible);
            } else {
                converter = Conversions::createConverter(newType,
                                                         cppToPython_QEnum_I16_PyEnum);
                Conversions::addPythonToCppValueConversion(converter,
                                                           pythonToCpp_PyEnum_QEnum_I16,
                                                           is_PyEnum_PythonToCpp_QEnum_I16_Convertible);
            }
            break;
        case 4:
            if (isUnsigned) {
                converter = Conversions::createConverter(newType,
                                                         cppToPython_QEnum_U32_PyEnum);
                Conversions::addPythonToCppValueConversion(converter,
                                                           pythonToCpp_PyEnum_QEnum_U32,
                                                           is_PyEnum_PythonToCpp_QEnum_U32_Convertible);
            } else {
                converter = Conversions::createConverter(newType,
                                                         cppToPython_QEnum_I32_PyEnum);
                Conversions::addPythonToCppValueConversion(converter,
                                                           pythonToCpp_PyEnum_QEnum_I32,
                                                           is_PyEnum_PythonToCpp_QEnum_I32_Convertible);
            }
            break;
        case 8:
            if (isUnsigned) {
                converter = Conversions::createConverter(newType,
                                                         cppToPython_QEnum_U64_PyEnum);
                Conversions::addPythonToCppValueConversion(converter,
                                                           pythonToCpp_PyEnum_QEnum_U64,
                                                           is_PyEnum_PythonToCpp_QEnum_U64_Convertible);
            } else {
                converter = Conversions::createConverter(newType,
                                                         cppToPython_QEnum_I64_PyEnum);
                Conversions::addPythonToCppValueConversion(converter,
                                                           pythonToCpp_PyEnum_QEnum_I64,
                                                           is_PyEnum_PythonToCpp_QEnum_I64_Convertible);
            }
            break;
        default:
            PyErr_SetString(PyExc_RuntimeError, "Unsupported enum underlying type");
            return nullptr;
    }
    auto scopedName = QByteArray(metaEnum->scope()) + "::" + metaEnum->enumName();
    Conversions::registerConverterName(converter, scopedName.constData());
    Conversions::registerConverterName(converter, metaEnum->enumName());
    // createConverter increases the ref count of type, but that will create a
    // circular reference when we add the capsule with the converter's pointer
    // to the type's attributes. So we need to decrease the ref count on the
    // type after calling createConverter.
    Py_DECREF(newType);
    if (set_cleanup_capsule_attr_for_pointer(newType, "_converter_capsule", converter) < 0)
        return nullptr;

    return newType;
}
