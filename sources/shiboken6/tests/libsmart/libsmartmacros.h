// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef LIB_SMART_MACROS_H
#define LIB_SMART_MACROS_H

#include "../libminimal/libminimalmacros.h"

#define LIB_SMART_EXPORT LIBMINIMAL_EXPORT
#define LIB_SMART_IMPORT LIBMINIMAL_IMPORT

#ifdef LIBSMART_BUILD
#  define LIB_SMART_API LIB_SMART_EXPORT
#else
#  define LIB_SMART_API LIB_SMART_IMPORT
#endif

#endif // LIB_SMART_MACROS_H
