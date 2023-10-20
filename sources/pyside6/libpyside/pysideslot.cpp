// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysidesignal_p.h"
#include "pysideslot_p.h"
#include "pysidestaticstrings.h"

#include <shiboken.h>

#include <QtCore/QMetaObject>
#include <QtCore/QString>
#include <signature.h>

using namespace Shiboken;

struct SlotData
{
    QByteArray name;
    QByteArray args;
    QByteArray resultType;
    QByteArray tag; // QMetaMethod::tag()
};

struct PySideSlot
{
    PyObject_HEAD
    SlotData *slotData;
};

extern "C"
{

static void slotDataListDestructor(PyObject *o)
{
    delete PySide::Slot::dataListFromCapsule(o);
}

static int slotTpInit(PyObject *, PyObject *, PyObject *);
static PyObject *slotCall(PyObject *, PyObject *, PyObject *);

// Class Definition -----------------------------------------------

static PyTypeObject *createSlotType()
{
    PyType_Slot PySideSlotType_slots[] = {
        {Py_tp_call, reinterpret_cast<void *>(slotCall)},
        {Py_tp_init, reinterpret_cast<void *>(slotTpInit)},
        {Py_tp_new, reinterpret_cast<void *>(PyType_GenericNew)},
        {Py_tp_dealloc, reinterpret_cast<void *>(Sbk_object_dealloc)},
        {0, nullptr}
    };

    PyType_Spec PySideSlotType_spec = {
        "2:PySide6.QtCore.Slot",
        sizeof(PySideSlot),
        0,
        Py_TPFLAGS_DEFAULT,
        PySideSlotType_slots,
    };

    return SbkType_FromSpec(&PySideSlotType_spec);
}

static PyTypeObject *PySideSlot_TypeF()
{
    static auto *type = createSlotType();
    return type;
}

int slotTpInit(PyObject *self, PyObject *args, PyObject *kw)
{
    static PyObject *emptyTuple = nullptr;
    static const char *kwlist[] = {"name", "result", "tag", nullptr};
    char *argName = nullptr;
    PyObject *argResult = nullptr;
    char *tag = nullptr;

    if (emptyTuple == nullptr)
        emptyTuple = PyTuple_New(0);

    if (!PyArg_ParseTupleAndKeywords(emptyTuple, kw, "|sOs:QtCore.Slot",
                                     const_cast<char **>(kwlist),
                                     &argName, &argResult, &tag)) {
        return -1;
    }

    PySideSlot *data = reinterpret_cast<PySideSlot *>(self);
    if (!data->slotData)
        data->slotData = new SlotData;
    for(Py_ssize_t i = 0, i_max = PyTuple_Size(args); i < i_max; i++) {
        PyObject *argType = PyTuple_GET_ITEM(args, i);
        const auto typeName = PySide::Signal::getTypeName(argType);
        if (typeName.isEmpty()) {
            PyErr_Format(PyExc_TypeError, "Unknown signal argument type: %s", Py_TYPE(argType)->tp_name);
            return -1;
        }
        if (!data->slotData->args.isEmpty())
            data->slotData->args += ',';
        data->slotData->args += typeName;
    }

    if (argName)
        data->slotData->name = argName;

    if (tag)
        data->slotData->tag = tag;

    data->slotData->resultType = argResult
        ? PySide::Signal::getTypeName(argResult) : PySide::Signal::voidType();

    return 0;
}

PyObject *slotCall(PyObject *self, PyObject *args, PyObject * /* kw */)
{
    PyObject *callback = nullptr;

    if (!PyArg_UnpackTuple(args, "Slot.__call__", 1, 1, &callback))
        return nullptr;
    Py_INCREF(callback);

    if (PyCallable_Check(callback)) {
        PySideSlot *data = reinterpret_cast<PySideSlot *>(self);

        if (!data->slotData)
            data->slotData = new SlotData;

        if (data->slotData->name.isEmpty()) {
            // PYSIDE-198: Use PyObject_GetAttr instead of PepFunction_GetName to support Nuitka.
            AutoDecRef funcName(PyObject_GetAttr(callback, PyMagicName::name()));
            data->slotData->name = funcName.isNull() ? "<no name>" : String::toCString(funcName);
        }
        const QByteArray returnType = QMetaObject::normalizedType(data->slotData->resultType);
        const QByteArray signature = data->slotData->name + '(' + data->slotData->args + ')';

        PyObject *pySlotName = PySide::PySideMagicName::slot_list_attr();
        PySide::Slot::DataList *entryList = nullptr;
        if (PyObject_HasAttr(callback, pySlotName)) {
            auto *capsule = PyObject_GetAttr(callback, pySlotName);
            entryList = PySide::Slot::dataListFromCapsule(capsule);
        } else {
            entryList = new PySide::Slot::DataList{};
            auto *capsule = PyCapsule_New(entryList, nullptr /* name */, slotDataListDestructor);
            Py_INCREF(capsule);
            PyObject_SetAttr(callback, pySlotName, capsule);
        }
        entryList->append({signature, returnType, data->slotData->tag});

        //clear data
        delete data->slotData;
        data->slotData = nullptr;
    }
    return callback;
}

} // extern "C"

namespace PySide::Slot {

DataList *dataListFromCapsule(PyObject *capsule)
{
    if (capsule != nullptr && PyCapsule_CheckExact(capsule) != 0) {
        if (void *v = PyCapsule_GetPointer(capsule, nullptr))
            return reinterpret_cast<DataList *>(v);
    }
    return nullptr;
}

static const char *Slot_SignatureStrings[] = {
    "PySide6.QtCore.Slot(self,*types:type,name:str=nullptr,result:type=nullptr)",
    "PySide6.QtCore.Slot.__call__(self,function:typing.Callable)->typing.Any",
    nullptr}; // Sentinel

void init(PyObject *module)
{
    if (InitSignatureStrings(PySideSlot_TypeF(), Slot_SignatureStrings) < 0)
        return;

    Py_INCREF(PySideSlot_TypeF());
    PyModule_AddObject(module, "Slot", reinterpret_cast<PyObject *>(PySideSlot_TypeF()));
}

} // namespace PySide::Slot
