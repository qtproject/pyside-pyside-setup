// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CLANGDEBUGUTILS_H
#define CLANGDEBUGUTILS_H

#include <QtCore/QtGlobal>

#include <clang-c/Index.h>

#include <string_view>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QString)

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug s, const CXString &cs);
QDebug operator<<(QDebug s, CXCursorKind cursorKind);
QDebug operator<<(QDebug s, CX_CXXAccessSpecifier ac);
QDebug operator<<(QDebug s, const CXType &t);
QDebug operator<<(QDebug s, const CXCursor &cursor);
QDebug operator<<(QDebug s, const CXSourceLocation &location);
QDebug operator<<(QDebug s, const std::string_view &v); // for code snippets
#endif // !QT_NO_DEBUG_STREAM

#endif // CLANGDEBUGUTILS_H
