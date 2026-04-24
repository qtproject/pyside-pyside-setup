// Copyright (C) 2025 Ford Motor Company
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "pysidecapsulemethod_p.h"

#include <string.h>
#include <sbkpep.h>

extern "C"
{

// This struct is used for both CapsuleMethod and CapsuleProperty
struct CapsuleDescriptor
{
    PyTypeObject base;
    PyObject *capsule;
    PyMethodDef methodDef;

    void configure(PyObject *capsule, PyMethodDef *method)
    {
        this->capsule = capsule;
        Py_INCREF(capsule);
        // We make a copy of the input name and doc strings so they can be temporary on
        // the input.
        if (method->ml_name)
            methodDef.ml_name = strdup(method->ml_name);
        if (method->ml_doc)
            methodDef.ml_doc = strdup(method->ml_doc);
        methodDef.ml_meth = method->ml_meth;
        methodDef.ml_flags = method->ml_flags;
    }
};

static PyObject *CapsuleDescriptor_tp_new(PyTypeObject *type, PyObject * /* args */, PyObject * /* kwds */);
static void CapsuleDescriptor_free(PyObject *self);
static PyObject *CapsuleMethod_descr_get(PyObject *self, PyObject *instance, PyObject * /* owner */);
static PyObject *CapsuleProperty_descr_get(PyObject *self, PyObject *instance, PyObject * /* owner */);
static int CapsuleProperty_descr_set(PyObject *self, PyObject *instance, PyObject * /* owner */);

/**
 * We are creating two related types, CapsuleMethod and CapsuleProperty, that are
 * used to enable lambda-like behavior. The difference is in usage, where
 * CapsuleMethod's __get__ function returns a Callable (i.e., method-like usage:
 * obj.capsuleMethodName(args)) and only supports the __get__ method.
 * CapsuleProperty on the other hand is used for properties, and supports both
 * __get__ and __set__ methods (i.e., obj.capsulePropertyName = value or val =
 * obj.capsulePropertyName).
 */
static PyTypeObject *createCapsuleMethodType()
{
    PyType_Slot CapsuleMethodType_slots[] = {
        {Py_tp_new,         reinterpret_cast<void *>(CapsuleDescriptor_tp_new)},
        {Py_tp_descr_get,   reinterpret_cast<void *>(CapsuleMethod_descr_get)},
        {Py_tp_free,        reinterpret_cast<void *>(CapsuleDescriptor_free)},
        {0, nullptr}
    };

    PyType_Spec CapsuleMethodType_spec = {
        "2:PySide6.QtRemoteObjects.CapsuleMethod",
        sizeof(CapsuleDescriptor),
        0,
        Py_TPFLAGS_DEFAULT,
        CapsuleMethodType_slots};

    PyObject *type = PyType_FromSpec(&CapsuleMethodType_spec);
    if (!type) {
        PyErr_Print();
        return nullptr;
    }
    return reinterpret_cast<PyTypeObject*>(type);
}

PyTypeObject *CapsuleMethod_TypeF(void)
{
    static auto *type = createCapsuleMethodType();
    return type;
}

static PyTypeObject *createCapsulePropertyType(bool isWritable)
{
    PyType_Slot WritablePropertyType_slots[] = {
        {Py_tp_new,         reinterpret_cast<void *>(CapsuleDescriptor_tp_new)},
        {Py_tp_descr_get,   reinterpret_cast<void *>(CapsuleProperty_descr_get)},
        {Py_tp_descr_set,   reinterpret_cast<void *>(CapsuleProperty_descr_set)},
        {Py_tp_free,        reinterpret_cast<void *>(CapsuleDescriptor_free)},
        {0, nullptr}
    };

    PyType_Slot ReadOnlyPropertyType_slots[] = {
        {Py_tp_new,         reinterpret_cast<void *>(CapsuleDescriptor_tp_new)},
        {Py_tp_descr_get,   reinterpret_cast<void *>(CapsuleProperty_descr_get)},
        {Py_tp_free,        reinterpret_cast<void *>(CapsuleDescriptor_free)},
        {0, nullptr}
    };

    PyType_Spec CapsulePropertyType_spec = {
        "2:PySide6.QtRemoteObjects.CapsuleProperty",
        sizeof(CapsuleDescriptor),
        0,
        Py_TPFLAGS_DEFAULT,
        isWritable ? WritablePropertyType_slots : ReadOnlyPropertyType_slots};

    PyObject *type = PyType_FromSpec(&CapsulePropertyType_spec);
    if (!type) {
        PyErr_Print();
        return nullptr;
    }
    return reinterpret_cast<PyTypeObject*>(type);
}

PyTypeObject *CapsuleProperty_TypeF(bool isWritable=false)
{
    if (isWritable) {
        static auto *type = createCapsulePropertyType(true);
        return type;
    }
    static auto *type = createCapsulePropertyType(false);
    return type;
}

static PyObject *CapsuleDescriptor_tp_new(PyTypeObject *type, PyObject * /* args */, PyObject * /* kwds */)
{
    auto *self = reinterpret_cast<CapsuleDescriptor *>(PyType_GenericAlloc(type, 0));
    if (self != nullptr) {
        self->capsule = nullptr;
        self->methodDef = {nullptr, nullptr, METH_NOARGS, nullptr}; // Initialize methodDef
    }
    return reinterpret_cast<PyObject *>(self);
}

static void CapsuleDescriptor_free(PyObject *self)
{
    auto *d = reinterpret_cast<CapsuleDescriptor *>(self);
    Py_XDECREF(d->capsule);
    free(const_cast<char*>(d->methodDef.ml_name));
    free(const_cast<char*>(d->methodDef.ml_doc));
}

static PyObject *CapsuleMethod_descr_get(PyObject *self, PyObject *instance, PyObject * /* owner */)
{
    if (instance == nullptr) {
        // Return the descriptor object if accessed from the class
        Py_INCREF(self);
        return self;
    }

    auto *d = reinterpret_cast<CapsuleDescriptor *>(self);
    auto *data = new CapsuleDescriptorData{instance, d->capsule};
    PyObject *payload = PyCapsule_New(data, "Payload", [](PyObject *capsule) {
        delete reinterpret_cast<CapsuleDescriptorData *>(PyCapsule_GetPointer(capsule, "Payload"));
    });
    if (!payload)
        return nullptr;

    Py_INCREF(payload);
    return PyCFunction_New(&d->methodDef, payload);
}

bool add_capsule_method_to_type(PyTypeObject *type, PyMethodDef *method, PyObject *capsule)
{
    if (PyType_Ready(type) < 0) {
        PyErr_Print();
        return false;
    }
    auto *descriptor = reinterpret_cast<CapsuleDescriptor *>(
        PyObject_CallObject(reinterpret_cast<PyObject *>(CapsuleMethod_TypeF()), nullptr));
    if (!descriptor) {
        PyErr_Print();
        return false;
    }
    descriptor->configure(capsule, method);

    auto *descr = reinterpret_cast<PyObject *>(descriptor);
    if (PyObject_SetAttrString(reinterpret_cast<PyObject *>(type), method->ml_name, descr) < 0) {
        PyErr_Print();
        return false;
    }
    return true;
}

static PyObject *CapsuleProperty_descr_get(PyObject *self, PyObject *instance, PyObject * /* owner */)
{
    if (instance == nullptr) {
        // Return the descriptor object if accessed from the class
        Py_INCREF(self);
        return self;
    }

    auto *d = reinterpret_cast<CapsuleDescriptor *>(self);
    auto *data = new CapsuleDescriptorData{instance, d->capsule};
    PyObject *payload = PyCapsule_New(data, "Payload", [](PyObject *capsule) {
        delete reinterpret_cast<CapsuleDescriptorData *>(PyCapsule_GetPointer(capsule, "Payload"));
    });
    if (!payload)
        return nullptr;

    return PyObject_CallFunctionObjArgs(PyCFunction_New(&d->methodDef, payload), nullptr);
}

static int CapsuleProperty_descr_set(PyObject *self, PyObject *instance, PyObject *value)
{
    auto *d = reinterpret_cast<CapsuleDescriptor *>(self);
    auto *data = new CapsuleDescriptorData{instance, d->capsule};
    PyObject *payload = PyCapsule_New(data, "Payload", [](PyObject *capsule) {
        delete reinterpret_cast<CapsuleDescriptorData *>(PyCapsule_GetPointer(capsule, "Payload"));
    });
    if (!payload)
        return -1;

    Py_INCREF(payload);
    PyObject *result = PyObject_CallFunctionObjArgs(PyCFunction_New(&d->methodDef, payload),
                                                    value, nullptr);
    if (!result)
        return -1;

    Py_DECREF(result);
    return 0;
}

// Returns a new CapsuleProperty descriptor object for use with PySideProperty
PyObject *make_capsule_property(PyMethodDef *method, PyObject *capsule, bool isWritable)
{
    auto *type = CapsuleProperty_TypeF(isWritable);
    auto *descriptor = PyObject_CallObject(reinterpret_cast<PyObject *>(type), nullptr);
    if (!descriptor)
        return nullptr;

    reinterpret_cast<CapsuleDescriptor*>(descriptor)->configure(capsule, method);

    return descriptor;
}

} // extern "C"
