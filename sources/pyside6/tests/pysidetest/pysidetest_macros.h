// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PYSIDETEST_MACROS_H
#define PYSIDETEST_MACROS_H

#include <pysidemacros.h>

#define PYSIDETEST_EXPORT PYSIDE_EXPORT
#define PYSIDETEST_IMPORT PYSIDE_IMPORT

#ifdef BUILD_PYSIDETEST
#  define PYSIDETEST_API PYSIDETEST_EXPORT
#else
#  define PYSIDETEST_API PYSIDETEST_IMPORT
#endif

#endif // PYSIDETEST_MACROS_H
