// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "pysidechange.h"

#include <sbkpython.h>

extern "C" {

static int exec_QtQmlFeatures(PyObject *module)
{
    PySide::Change::init(module);
    return 0;
}

} // extern "C"

static PyModuleDef_Slot PySideQtQmlFeatures_Slots[] = {
    {Py_mod_exec, reinterpret_cast<void *>(exec_QtQmlFeatures)},
#if !defined(PYPY_VERSION) && ((!defined(Py_LIMITED_API) && PY_VERSION_HEX >= 0x030C0000) || (defined(Py_LIMITED_API) && Py_LIMITED_API >= 0x030C0000))
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
#endif
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_USED},
#endif
    {0, nullptr}
};

static struct PyModuleDef PySideQtQmlFeatures_ModuleDef = {
    /* m_base     */ PyModuleDef_HEAD_INIT,
    /* m_name     */ "PySide6.QtQmlFeatures",
    /* m_doc      */ nullptr,
    /* m_size     */ 0,
    /* m_methods  */ nullptr,
    /* m_slots    */ PySideQtQmlFeatures_Slots,
    /* m_traverse */ nullptr,
    /* m_clear    */ nullptr,
    /* m_free     */ nullptr
};

extern "C" PYSIDEQML_EXPORT PyObject *PyInit_QtQmlFeatures()
{
    return PyModuleDef_Init(&PySideQtQmlFeatures_ModuleDef);
}
