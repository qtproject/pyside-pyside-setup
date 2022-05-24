// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#ifndef MACROS_H
#define MACROS_H

#include <QtCore/qglobal.h>

// Export symbols when creating .dll and .lib, and import them when using .lib.
#if BINDINGS_BUILD
#    define BINDINGS_API Q_DECL_EXPORT
#else
#    define BINDINGS_API Q_DECL_IMPORT
#endif

#endif // MACROS_H
