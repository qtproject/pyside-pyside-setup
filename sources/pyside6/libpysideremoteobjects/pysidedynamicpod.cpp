// Copyright (C) 2025 Ford Motor Company
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "pysidedynamicpod_p.h"
#include "pysidecapsulemethod_p.h"
#include "pysidedynamiccommon_p.h"

#include <autodecref.h>
#include <helper.h>
#include <pep384ext.h>
#include <sbkconverter.h>
#include <sbkstaticstrings.h>
#include <sbkstring.h>

#include <pysidestaticstrings.h>

#include <QtCore/qmetaobject.h>

using namespace Shiboken;

extern "C"
{

struct PodDefs
{
    static PyObject *tp_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
    {
        SBK_UNUSED(kwds);
        AutoDecRef param_types(PyObject_GetAttrString(reinterpret_cast<PyObject *>(type),
                                                      "__param_types__"));
        if (!param_types) {
            PyErr_Format(PyExc_RuntimeError, "Failed to get POD attributes for type %s",
                         type->tp_name);
            return nullptr;
        }

        // param_types is a tuple of PyTypeObject pointers
        Py_ssize_t size = PyTuple_Size(param_types);
        if (size != PyTuple_Size(args)) {
            PyErr_Format(PyExc_TypeError,
                         "Incorrect number of arguments for type %s.  Expected %zd.",
                         type->tp_name, size);
            return nullptr;
        }

        PyObject *self = PepExt_Type_GetAllocSlot(type)(type, size);

        if (!self)
            return nullptr;

        for (Py_ssize_t i = 0; i < size; ++i) {
            PyObject *expected_type = PyTuple_GetItem(param_types, i);
            PyObject *item = PyTuple_GetItem(args, i);
            // Check if the item is an instance of the expected type
            if (PyObject_IsInstance(item, expected_type)) {
                Py_INCREF(item);
                PyTuple_SetItem(self, i, item);
            } else {
                // Try to convert the item to the expected type
                PyObject *converted_item = PyObject_CallFunctionObjArgs(expected_type, item, nullptr);
                if (!converted_item) {
                    Py_DECREF(self);
                    PyErr_Format(PyExc_TypeError, "Argument %zd must be convertible to type %s", i,
                                 reinterpret_cast<PyTypeObject *>(expected_type)->tp_name);
                    return nullptr;
                }
                PyTuple_SetItem(self, i, converted_item);
            }
        }

        return self;
    }

    static PyObject *tp_repr(PyObject *self)
    {
        auto *type = Py_TYPE(self);
        std::string repr(PepType_GetFullyQualifiedNameStr(type));
        repr += "(";
        for (Py_ssize_t i = 0; i < PyTuple_Size(self); ++i) {
            if (i > 0)
                repr += ", ";

            PyObject *item_repr = PyObject_Repr(PyTuple_GetItem(self, i));
            repr += String::toCString(item_repr);
        }
        repr += ")";
        return PyUnicode_FromString(repr.c_str());
    }

    static PyObject *CapsuleMethod_handler(PyObject *payload, PyObject * /* args */)
    {
        auto *methodData = reinterpret_cast<CapsuleDescriptorData *>(
            PyCapsule_GetPointer(payload, "Payload"));
        if (!methodData) {
            PyErr_SetString(PyExc_RuntimeError, "Invalid call to dynamic method.  Missing payload.");
            return nullptr;
        }
        PyObject *self = methodData->self;
        if (PyCapsule_IsValid(methodData->payload, "PropertyCapsule")) {
            // Handle property getter/setter against our hidden properties attribute
            auto *capsule = PyCapsule_GetPointer(methodData->payload, "PropertyCapsule");
            if (capsule) {
                auto *callData = reinterpret_cast<PropertyCapsule *>(capsule);
                if (callData->indexInObject < 0 || callData->indexInObject >= PyTuple_Size(self)) {
                    PyErr_Format(PyExc_RuntimeError, "Unknown property method: %s",
                                 callData->name.constData());
                    return nullptr;
                }
                auto *val = PyTuple_GetItem(self, callData->indexInObject);
                Py_INCREF(val);
                return val;
            }
        }

        PyErr_SetString(PyExc_RuntimeError, "Unknown capsule type");
        return nullptr;
    }
};

static PyMethodDef DynamicPod_tp_methods[] = {
    {"get_enum", reinterpret_cast<PyCFunction>(DynamicType_get_enum), METH_O | METH_CLASS,
                 "Get enum type by name"},
    {nullptr, nullptr, 0, nullptr}
};

static PyType_Slot DynamicPod_slots[] = {
    {Py_tp_base,        reinterpret_cast<void *>(&PyTuple_Type)},
    {Py_tp_new,         reinterpret_cast<void *>(PodDefs::tp_new)},
    {Py_tp_repr,        reinterpret_cast<void *>(PodDefs::tp_repr)},
    {Py_tp_methods,     reinterpret_cast<void *>(DynamicPod_tp_methods)},
    {0, nullptr}
};

// C++ to Python conversion for POD types.
static PyObject *cppToPython_POD_Tuple(const void *cppIn)
{
    const auto &cppInRef = *reinterpret_cast<const QVariantList *>(cppIn);
    PyObject *pyOut = PyTuple_New(Py_ssize_t(cppInRef.size()));
    Py_ssize_t idx = 0;
    for (auto it = std::cbegin(cppInRef), end = std::cend(cppInRef); it != end; ++it, ++idx) {
        static const Conversions::SpecificConverter argConverter("QVariant");
        const auto &cppItem = *it;
        PyTuple_SetItem(pyOut, idx, Shiboken::Conversions::copyToPython(argConverter, &cppItem));
    }
    return pyOut;
}
static void pythonToCpp_Tuple_POD(PyObject *pyIn, void *cppOut)
{
    auto &cppOutRef = *reinterpret_cast<QVariantList *>(cppOut);

    Py_ssize_t tupleSize = PyTuple_Size(pyIn);
    if (tupleSize != cppOutRef.size()) {
        PyErr_Format(PyExc_ValueError,
                     "Size mismatch: tuple has %zd elements, but POD expects %d elements",
                     tupleSize, cppOutRef.size());
        return;
    }

    for (Py_ssize_t i = 0; i < tupleSize; ++i) {
        static const Conversions::SpecificConverter argConverter("QVariant");
        PyObject *item = PyTuple_GetItem(pyIn, i);
        QVariant &variant = cppOutRef[i];
        Conversions::SpecificConverter converter(variant.metaType().name());
        Shiboken::Conversions::pythonToCppCopy(converter, item, variant.data());
    }
}
static PythonToCppFunc is_Tuple_PythonToCpp_POD_Convertible(PyObject *pyIn)
{
    if (PyTuple_Check(pyIn))
        return pythonToCpp_Tuple_POD;

    return {};
}

} // extern "C"

PyTypeObject *createPodType(QMetaObject *meta)
{
    auto qualname = QByteArrayLiteral("DynamicPod.") + meta->className();
    PyType_Spec spec = {
        qualname.constData(),
        0,
        0,
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_TYPE_SUBCLASS,
        DynamicPod_slots
    };

    PyObject *obType = PyType_FromSpec(&spec);
    if (!obType)
        return nullptr;

    if (create_managed_py_enums(obType, meta) < 0)
        return nullptr;

    Py_ssize_t size = meta->propertyCount() - meta->propertyOffset();
    AutoDecRef pyParamTypes(PyTuple_New(size));
    for (int i = 0; i < size; ++i) {
        auto metaProperty = meta->property(i + meta->propertyOffset());
        auto metaType = metaProperty.metaType();
        if (!metaType.isValid()) {
            PyErr_Format(PyExc_RuntimeError, "Failed to get meta type for property %s",
                         metaProperty.name());
            return nullptr;
        }
        auto *pyType = Conversions::getPythonTypeObject(metaType.name());
        auto *obPyType = reinterpret_cast<PyObject *>(pyType);
        Py_INCREF(obPyType);
        PyTuple_SetItem(pyParamTypes, i, obPyType);
    }

    auto *type = reinterpret_cast<PyTypeObject *>(obType);
    PyMethodDef method = {
        nullptr,
        reinterpret_cast<PyCFunction>(PodDefs::CapsuleMethod_handler),
        METH_VARARGS,
        nullptr
    };
    for (int i = meta->propertyOffset(); i < meta->propertyCount(); ++i) {
        // Create a PropertyCapsule for each property to store the info needed
        // for the handler.
        auto metaProperty = meta->property(i);

        method.ml_name = metaProperty.name();
        auto *capsule = PyCapsule_New(new PropertyCapsule{metaProperty.name(),
                                                          i,
                                                          i - meta->propertyOffset()},
                                      "PropertyCapsule",
                                      [](PyObject *capsule) {
                                          delete static_cast<PropertyCapsule *>(
                                              PyCapsule_GetPointer(capsule, "PropertyCapsule"));
                                      });
        auto *capsulePropObject = make_capsule_property(&method, capsule);
        if (PyObject_SetAttrString(obType, metaProperty.name(), capsulePropObject) < 0)
            return nullptr;

        Py_DECREF(capsulePropObject);
    }

    // createConverter increases the ref count of type, but that will create
    // a circular reference. When we add the capsule with the converter's pointer
    // to the type's attributes. So we need to decrease the ref count on the type
    // after calling createConverter.
    auto *converter = Shiboken::Conversions::createConverter(type, cppToPython_POD_Tuple);
    Py_DECREF(obType);
    if (set_cleanup_capsule_attr_for_pointer(type, "_converter_capsule", converter) < 0)
        return nullptr;
    Shiboken::Conversions::registerConverterName(converter, meta->className());
    Shiboken::Conversions::registerConverterName(converter,
                                                 PepType_GetFullyQualifiedNameStr(type));
    Shiboken::Conversions::addPythonToCppValueConversion(converter, pythonToCpp_Tuple_POD,
                                                         is_Tuple_PythonToCpp_POD_Convertible);

    static PyObject *const module = String::createStaticString("PySide6.QtRemoteObjects");
    AutoDecRef pyQualname(String::fromCString(qualname.constData()));
    PyObject_SetAttr(obType, PyMagicName::qualname(), pyQualname);
    PyObject_SetAttr(obType, PyMagicName::module(), module);
    PyObject_SetAttrString(obType, "__param_types__", pyParamTypes);

    return type;
}
