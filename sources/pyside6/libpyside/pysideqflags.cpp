// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysideqflags.h"

#include <autodecref.h>
#include <sbkenum.h>
#include <sbkconverter.h>
#include <sbkenum_p.h>

extern "C" {
    struct SbkConverter;

    struct PySideQFlagsTypePrivate : public SbkQFlagsTypePrivate
    {
        // PYSIDE-1735: These fields are just there for comatibility with the enumstructure.
        //              We need to switch between flags and enum at runtine.
        //              This will vanish completely when we no longer support two implementations.
        const char *_cppName;
        PyTypeObject *_replacementType;
    };
    /**
     * Type of all QFlags
     */
    struct PySideQFlagsType
    {
        PyTypeObject type;
    };

    #define PYSIDE_QFLAGS(X) reinterpret_cast<PySideQFlagsObject *>(X)

    PyObject *PySideQFlags_tp_new(PyTypeObject *type, PyObject *args, PyObject * /* kwds */)
    {
        long val = 0;
        if (PyTuple_GET_SIZE(args)) {
            PyObject *arg = PyTuple_GET_ITEM(args, 0);
            if (Shiboken::isShibokenEnum(arg)) {// faster call
                val = Shiboken::Enum::getValue(arg);
            } else if (PyNumber_Check(arg)) {
                Shiboken::AutoDecRef number(PyNumber_Long(arg));
                val = PyLong_AsLong(number);
            } else {
                PyErr_SetString(PyExc_TypeError,"QFlags must be created using enums or numbers.");
                return nullptr;
            }
        }
        PySideQFlagsObject *self = PyObject_New(PySideQFlagsObject, type);
        self->ob_value = val;
        return reinterpret_cast<PyObject *>(self);
    }

    static long getNumberValue(PyObject *v)
    {
        Shiboken::AutoDecRef number(PyNumber_Long(v));
        return PyLong_AsLong(number);
    }

    static PyObject *qflag_nb_int(PyObject *self)
    {
        return PyLong_FromLong(reinterpret_cast<PySideQFlagsObject*>(self)->ob_value);
    }

    PyObject *PySideQFlags_tp_richcompare(PyObject *self, PyObject *other, int op)
    {
        int result = 0;
        if (!PyNumber_Check(other)) {
            switch (op) {
            case Py_EQ:
                Py_RETURN_FALSE;
            case Py_NE:
                Py_RETURN_TRUE;
            default:
                Py_RETURN_NOTIMPLEMENTED;
            }
        }

        if (self == other) {
            switch (op) {
            case Py_EQ:
            case Py_LE:
            case Py_GE:
                result = 1;
                break;
            }
        } else  {
            const long valA = PYSIDE_QFLAGS(self)->ob_value;
            const long valB = getNumberValue(other);
            switch (op) {
            case Py_EQ:
                result = (valA == valB);
                break;
            case Py_NE:
                result = (valA != valB);
                break;
            case Py_LE:
                result = (valA <= valB);
                break;
            case Py_GE:
                result = (valA >= valB);
                break;
            case Py_LT:
                result = (valA < valB);
                break;
            case Py_GT:
                result = (valA > valB);
                break;
            default:
                PyErr_BadArgument();
                return nullptr;
            }
        }
        if (result)
            Py_RETURN_TRUE;
        Py_RETURN_FALSE;
    }

    static void PySideQFlags_tp_dealloc(PyObject *self)
    {
        auto *flagsType = reinterpret_cast<PySideQFlagsType *>(self);
        PepType_PFTP_delete(flagsType);
        Sbk_object_dealloc(self);
    }

    /// PYSIDE-1735: Support for redirection to the new Python enum.Flag .
    static PyTypeObject *getEnumMeta()
    {
        static auto *mod = PyImport_ImportModule("enum");
        if (mod) {
            static auto *EnumMeta = PyObject_GetAttrString(mod, "EnumMeta");
            if (EnumMeta)
                return reinterpret_cast<PyTypeObject *>(EnumMeta);
        }
        Py_FatalError("Python module 'enum' not found");
        return nullptr;
    }
}

namespace PySide
{
namespace QFlagsSupport
{
    static PyType_Slot SbkNewQFlagsType_slots[] = {
        {Py_nb_bool, nullptr},
        {Py_nb_invert, nullptr},
        {Py_nb_and, nullptr},
        {Py_nb_xor, nullptr},
        {Py_nb_or, nullptr},
        {Py_nb_int, reinterpret_cast<void*>(qflag_nb_int)},
        {Py_nb_index, reinterpret_cast<void*>(qflag_nb_int)},   // same as nb_int
        {Py_tp_new, reinterpret_cast<void *>(PySideQFlags_tp_new)},
        {Py_tp_richcompare, reinterpret_cast<void *>(PySideQFlags_tp_richcompare)},
        {Py_tp_dealloc, reinterpret_cast<void *>(PySideQFlags_tp_dealloc)},
        {0, nullptr}
    };
    static PyType_Spec SbkNewQFlagsType_spec = {
        "missing QFlags name", // to be inserted later
        sizeof(PySideQFlagsObject),
        0,
        Py_TPFLAGS_DEFAULT,
        SbkNewQFlagsType_slots,
    };

    PyTypeObject *create(const char *name, PyType_Slot numberMethods[])
    {
        char qualname[200];
        // PYSIDE-747: Here we insert now the full class name.
        strcpy(qualname, name);
        // Careful: SbkType_FromSpec does not allocate the string.
        PyType_Spec newspec;
        newspec.name = strdup(qualname);
        newspec.basicsize = SbkNewQFlagsType_spec.basicsize;
        newspec.itemsize = SbkNewQFlagsType_spec.itemsize;
        newspec.flags = SbkNewQFlagsType_spec.flags;
        int idx = -1;
        while (numberMethods[++idx].slot) {
            assert(SbkNewQFlagsType_slots[idx].slot == numberMethods[idx].slot);
            SbkNewQFlagsType_slots[idx].pfunc = numberMethods[idx].pfunc;
        }
        newspec.slots = SbkNewQFlagsType_spec.slots;
        return SbkType_FromSpec(&newspec);
    }

    PySideQFlagsObject *newObject(long value, PyTypeObject *type)
    {
        // PYSIDE-1735: In case of a new Python enum, we must redirect to the
        //              enum.Flag implementation.
        static PyTypeObject *enumMeta = getEnumMeta();
        if (Py_TYPE(type) == enumMeta) {
            // We are cheating: This is an enum type.
            auto *flag_enum = PyObject_CallFunction(reinterpret_cast<PyObject *>(type), "i", value);
            return reinterpret_cast<PySideQFlagsObject *>(flag_enum);
        }
        PySideQFlagsObject *qflags = PyObject_New(PySideQFlagsObject, type);
        qflags->ob_value = value;
        return qflags;
    }

    long getValue(PySideQFlagsObject *self)
    {
        return self->ob_value;
    }
}
}
