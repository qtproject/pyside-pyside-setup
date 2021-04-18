/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "pysideqflags.h"

#include <autodecref.h>
#include <sbkenum.h>

extern "C" {
    struct SbkConverter;

    struct PySideQFlagsTypePrivate
    {
        SbkConverter **converterPtr;
        SbkConverter *converter;
    };
    /**
     * Type of all QFlags
     */
    struct PySideQFlagsType
    {
        PyTypeObject type;
    };

    #define PYSIDE_QFLAGS(X) reinterpret_cast<PySideQFlagsObject *>(X)

    PyObject *PySideQFlagsNew(PyTypeObject *type, PyObject *args, PyObject * /* kwds */)
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

    static PyObject *qflag_int(PyObject *self)
    {
        return PyLong_FromLong(reinterpret_cast<PySideQFlagsObject*>(self)->ob_value);
    }

    PyObject *PySideQFlagsRichCompare(PyObject *self, PyObject *other, int op)
    {
        int result = 0;
        if (!PyNumber_Check(other)) {
            PyErr_BadArgument();
            return nullptr;
        }

        long valA = PYSIDE_QFLAGS(self)->ob_value;
        long valB = getNumberValue(other);

        if (self == other) {
            result = 1;
        } else  {
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

    static void PySideQFlagsDealloc(PyObject *self)
    {
        auto *flagsType = reinterpret_cast<PySideQFlagsType *>(self);
        PepType_PFTP_delete(flagsType);
        Sbk_object_dealloc(self);
    }
}

namespace PySide
{
namespace QFlags
{
    static PyType_Slot SbkNewQFlagsType_slots[] = {
        {Py_nb_bool, nullptr},
        {Py_nb_invert, nullptr},
        {Py_nb_and, nullptr},
        {Py_nb_xor, nullptr},
        {Py_nb_or, nullptr},
        {Py_nb_int, reinterpret_cast<void*>(qflag_int)},
        {Py_nb_index, reinterpret_cast<void*>(qflag_int)},
        {Py_tp_new, reinterpret_cast<void *>(PySideQFlagsNew)},
        {Py_tp_richcompare, reinterpret_cast<void *>(PySideQFlagsRichCompare)},
        {Py_tp_dealloc, reinterpret_cast<void *>(PySideQFlagsDealloc)},
        {0, nullptr}
    };
    static PyType_Spec SbkNewQFlagsType_spec = {
        "missing QFlags name", // to be inserted later
        sizeof(PySideQFlagsObject),
        0,
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_CHECKTYPES,
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
        PyTypeObject *type = (PyTypeObject *)SbkType_FromSpec(&newspec);
        Py_TYPE(type) = &PyType_Type;

        PySideQFlagsType *flagsType = reinterpret_cast<PySideQFlagsType *>(type);
        auto *pftp = PepType_PFTP(flagsType);
        pftp->converterPtr = &pftp->converter;

        if (PyType_Ready(type) < 0)
            return nullptr;

        return type;
    }

    PySideQFlagsObject *newObject(long value, PyTypeObject *type)
    {
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
