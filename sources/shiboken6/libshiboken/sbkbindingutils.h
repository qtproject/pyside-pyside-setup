// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_BINDINGUTILS
#define SBK_BINDINGUTILS

#include "sbkpython.h"
#include "shibokenmacros.h"

namespace Shiboken {
struct AutoDecRef;

/*!
    \struct Shiboken::ArgumentNameIndexMapping
    \inmodule libshiboken

    \brief Maps a keyword argument by name to its parameter index.
*/
struct ArgumentNameIndexMapping
{
    const char *name;
    int index;
};

LIBSHIBOKEN_API bool
    parseKeywordArguments(PyObject *kwds,
                          const ArgumentNameIndexMapping *mapping, size_t size,
                          Shiboken::AutoDecRef &errInfo, PyObject **pyArgs);

LIBSHIBOKEN_API bool
    parseConstructorKeywordArguments(PyObject *kwds,
                                     const ArgumentNameIndexMapping *mapping, size_t size,
                                     Shiboken::AutoDecRef &errInfo, PyObject **pyArgs);

/*!
    Returns whether we are running in compiled mode (Nuitka).
*/
LIBSHIBOKEN_API bool isCompiled();

} // namespace Shiboken

#endif // SBK_BINDINGUTILS
