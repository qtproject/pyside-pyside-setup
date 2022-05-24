// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef LIBOTHERMACROS_H
#define LIBOTHERMACROS_H

#include "../libminimal/libminimalmacros.h"

#define LIBOTHER_EXPORT LIBMINIMAL_EXPORT
#define LIBOTHER_IMPORT LIBMINIMAL_IMPORT

#ifdef LIBOTHER_BUILD
#  define LIBOTHER_API LIBOTHER_EXPORT
#else
#  define LIBOTHER_API LIBOTHER_IMPORT
#endif

#endif // LIBOTHERMACROS_H
