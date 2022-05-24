// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef LIBSAMPLEMACROS_H
#define LIBSAMPLEMACROS_H

#include "../libminimal/libminimalmacros.h"

#define LIBSAMPLE_EXPORT LIBMINIMAL_EXPORT
#define LIBSAMPLE_IMPORT LIBMINIMAL_IMPORT

#ifdef LIBSAMPLE_BUILD
#  define LIBSAMPLE_API LIBSAMPLE_EXPORT
#else
#  define LIBSAMPLE_API LIBSAMPLE_IMPORT
#endif

#endif // LIBSAMPLEMACROS_H
