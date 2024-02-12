// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBKCPPSTRING_H
#define SBKCPPSTRING_H

#include "sbkpython.h"
#include "shibokenmacros.h"

#include <string>
#include <string_view>

namespace Shiboken::String
{
    LIBSHIBOKEN_API PyObject *fromCppString(const std::string &value);
    LIBSHIBOKEN_API PyObject *fromCppStringView(std::string_view value);
    LIBSHIBOKEN_API PyObject *fromCppWString(const std::wstring &value);
    LIBSHIBOKEN_API void toCppString(PyObject *str, std::string *value);
    LIBSHIBOKEN_API void toCppWString(PyObject *str, std::wstring *value);
} // namespace Shiboken::String

#endif // SBKCPPSTRING_H
