// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CLANGDEBUGUTILS_H
#define CLANGDEBUGUTILS_H

#include <QtCore/qtclasshelpermacros.h>

#include <clang-c/Index.h>

#include <string_view>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QString)

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug debug, const CXString &cs);
QDebug operator<<(QDebug debug, CXCursorKind cursorKind);
QDebug operator<<(QDebug debug, CX_CXXAccessSpecifier ac);
QDebug operator<<(QDebug debug, const CXType &type);
QDebug operator<<(QDebug debug, const CXCursor &cursor);
QDebug operator<<(QDebug debug, const CXSourceLocation &location);
QDebug operator<<(QDebug debug, const std::string_view &v); // for code snippets
#endif // !QT_NO_DEBUG_STREAM

#endif // CLANGDEBUGUTILS_H
