// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <Python.h>

#if defined _WIN32
#  define MODULE_EXPORT __declspec(dllexport)
#else
#  define MODULE_EXPORT __attribute__ ((visibility("default")))
#endif

static PyMethodDef QtExampleIconsMethods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduleDef = {
    /* m_base     */ PyModuleDef_HEAD_INIT,
    /* m_name     */ "QtExampleIcons",
    /* m_doc      */ NULL,
    /* m_size     */ -1,
    /* m_methods  */ QtExampleIconsMethods,
    /* m_reload   */ NULL,
    /* m_traverse */ NULL,
    /* m_clear    */ NULL,
    /* m_free     */ NULL
};

MODULE_EXPORT PyObject *PyInit_QtExampleIcons(void)
{
    return PyModule_Create(&moduleDef);
}

int main(int argc, char *argv[])
{
#ifndef PYPY_VERSION
    Py_SetProgramName(L"module-test");
    Py_Initialize();
#endif
    PyInit_QtExampleIcons();
    return 0;
}
