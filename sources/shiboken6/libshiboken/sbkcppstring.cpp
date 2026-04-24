// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "sbkcppstring.h"
#include "autodecref.h"
#include "sbkpep.h"

namespace Shiboken::String
{

PyObject *fromCppString(const std::string &value)
{
    return PyUnicode_FromStringAndSize(value.data(), value.size());
}

PyObject *fromCppStringView(std::string_view value)
{
    return PyUnicode_FromStringAndSize(value.data(), value.size());
}

PyObject *fromCppWString(const std::wstring &value)
{
    return PyUnicode_FromWideChar(value.data(), value.size());
}

void toCppString(PyObject *str, std::string *value)
{
    value->clear();

    if (str == Py_None)
        return;

    if (PyUnicode_Check(str)) {
        if (PyUnicode_GetLength(str) > 0) {
            Py_ssize_t size{};
            const char *utf8 = PyUnicode_AsUTF8AndSize(str, &size);
            value->assign(utf8, size_t(size));
        }
        return;
    }

    if (PyBytes_Check(str))
        value->assign(PyBytes_AsString(str));
}

void toCppWString(PyObject *str, std::wstring *value)
{
    value->clear();

    if (str == Py_None || PyUnicode_Check(str) == 0 || PyUnicode_GetLength(str) == 0)
        return;

    wchar_t *w = PyUnicode_AsWideCharString(str, nullptr);
    value->assign(w);
    PyMem_Free(w);
}

} // namespace Shiboken::String
