// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CLANG_TYPEDEFS_H
#define CLANG_TYPEDEFS_H

#include <clang-c/Index.h>

namespace clang {

#if LLVM_VERSION >= 22
using PrintingPolicy = CXPrintingPolicy;
#else
using PrintingPolicy = void *;
#endif

} // namespace clang

#endif // CLANG_TYPEDEFS_H
