// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// There is a bug in Python 3.6 that turned the Index_Check function
// into a macro without taking care of the limited API.
// This leads to the single problem that we don't have
// access to PyLong_Type's nb_index field which is no heap type.
// We cannot easily create this function by inheritance since it is
// not inherited.
//
// Simple solution: Create the structure and write such a function.
// Long term: Submit a patch to python.org .

// This structure comes from Python 3.7, but we have checked that
// it also works for Python 3.8 and 3.9.

typedef struct {
    /* Number implementations must check *both*
       arguments for proper type and implement the necessary conversions
       in the slot functions themselves. */

    binaryfunc nb_add;
    binaryfunc nb_subtract;
    binaryfunc nb_multiply;
    binaryfunc nb_remainder;
    binaryfunc nb_divmod;
    ternaryfunc nb_power;
    unaryfunc nb_negative;
    unaryfunc nb_positive;
    unaryfunc nb_absolute;
    inquiry nb_bool;
    unaryfunc nb_invert;
    binaryfunc nb_lshift;
    binaryfunc nb_rshift;
    binaryfunc nb_and;
    binaryfunc nb_xor;
    binaryfunc nb_or;
    unaryfunc nb_int;
    void *nb_reserved;  /* the slot formerly known as nb_long */
    unaryfunc nb_float;

    binaryfunc nb_inplace_add;
    binaryfunc nb_inplace_subtract;
    binaryfunc nb_inplace_multiply;
    binaryfunc nb_inplace_remainder;
    ternaryfunc nb_inplace_power;
    binaryfunc nb_inplace_lshift;
    binaryfunc nb_inplace_rshift;
    binaryfunc nb_inplace_and;
    binaryfunc nb_inplace_xor;
    binaryfunc nb_inplace_or;

    binaryfunc nb_floor_divide;
    binaryfunc nb_true_divide;
    binaryfunc nb_inplace_floor_divide;
    binaryfunc nb_inplace_true_divide;

    unaryfunc nb_index;

    binaryfunc nb_matrix_multiply;
    binaryfunc nb_inplace_matrix_multiply;
} PyNumberMethods;

// temporary structure until we have a generator for the offsets
typedef struct _oldtypeobject {
    PyVarObject ob_base;
    void *X01; // const char *tp_name;
    void *X02; // Py_ssize_t tp_basicsize;
    void *X03; // Py_ssize_t tp_itemsize;
    void *X04; // destructor tp_dealloc;
    void *X05; // printfunc tp_print;
    void *X06; // getattrfunc tp_getattr;
    void *X07; // setattrfunc tp_setattr;
    void *X08; // PyAsyncMethods *tp_as_async;
    void *X09; // reprfunc tp_repr;
    PyNumberMethods *tp_as_number;

} PyOldTypeObject;

static bool is_compatible_version()
{
    auto number = _PepRuntimeVersion();
    return number < (3 << 16 | 10 << 8 | 0);
}

///////////////////////////////////////////////////////////////////////
//
// PYSIE-1797: The Solution
// ========================
//
// Inspecting the data structures of Python 3.6, 3.7, 3.8 and 3.9
// shows that concerning the here needed offset of nb_index, they
// are all compatible.
// That means: We can use the above definition for all these versions.
//
// From Python 3.10 on, the `PyType_GetSlot` function also works with
// non-heap types. That means this solution will always work.
//
// Note: When we have moved to Python 3.8 as the minimum version,
// this whole nonsense can be trashed.
// There is an automatic warning about this in parser.py .
//

LIBSHIBOKEN_API int PepIndex_Check(PyObject *obj)
{
    static bool old_python_version = is_compatible_version();
    if (old_python_version) {
        auto *type = reinterpret_cast<PyOldTypeObject *>(Py_TYPE(obj));
        return type->tp_as_number != nullptr &&
               type->tp_as_number->nb_index != nullptr;
    }
    // From Python 3.10 on, we can use PyType_GetSlot also with normal types!
    unaryfunc nb_index = reinterpret_cast<unaryfunc>(PyType_GetSlot(Py_TYPE(obj), Py_nb_index));
    return nb_index != nullptr;
}

