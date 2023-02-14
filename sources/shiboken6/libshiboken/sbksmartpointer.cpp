// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "sbksmartpointer.h"
#include "sbkstring.h"
#include "autodecref.h"

#include <unordered_set>

namespace Shiboken::SmartPointer
{

PyObject *repr(PyObject *pointer, PyObject *pointee)
{
    Shiboken::AutoDecRef pointerRepr(Shiboken::String::repr(pointer));
    if (pointer == nullptr)
        return pointerRepr.release();

    Shiboken::AutoDecRef pointeeRepr(pointee != nullptr
                                     ? PyObject_Repr(pointee)
                                     : Shiboken::String::repr(pointee));

    return PyUnicode_FromFormat("%U (%U)", pointerRepr.object(), pointeeRepr.object());
}

// __dir__ for a smart pointer. Add the __dir__ entries of the pointee to the list.
PyObject *dir(PyObject *pointer, PyObject *pointee)
{
    if (pointer == nullptr)
        return PyList_New(0);
    // Get the pointer's dir entries. Note: PyObject_Dir() cannot be called on
    // self, will crash. Work around by using the type dict keys.
    AutoDecRef tpDict(PepType_GetDict(Py_TYPE(pointer)));
    auto *result = PyMapping_Keys(tpDict);

    if (pointee != nullptr && pointee != Py_None) {
        // Add the entries of the pointee that do not exist in the pointer's list.
        // Since Python internally caches strings; we can use a set of PyObject *.
        std::unordered_set<PyObject *> knownStrings;
        for (Py_ssize_t i = 0, size = PySequence_Size(result); i < size; ++i) {
            Shiboken::AutoDecRef item(PySequence_GetItem(result, i));
            knownStrings.insert(item.object());
        }
        const auto knownEnd = knownStrings.end();

        Shiboken::AutoDecRef pointeeDir(PyObject_Dir(pointee));
        for (Py_ssize_t i = 0, size = PySequence_Size(pointeeDir.object()); i < size; ++i) {
            Shiboken::AutoDecRef item(PySequence_GetItem(pointeeDir, i));
            if (knownStrings.find(item.object()) == knownEnd)
                PyList_Append(result, item.object());
        }
    }

    PyList_Sort(result);
    return result;
}

} // namespace Shiboken::SmartPointer
