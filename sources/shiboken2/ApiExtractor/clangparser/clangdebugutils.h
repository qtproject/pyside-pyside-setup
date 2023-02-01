/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef CLANGDEBUGUTILS_H
#define CLANGDEBUGUTILS_H

#include <QtCore/QtGlobal>

#include <clang-c/Index.h>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QString)

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug s, const CXString &cs);
QDebug operator<<(QDebug s, CXCursorKind cursorKind);
QDebug operator<<(QDebug s, CX_CXXAccessSpecifier ac);
QDebug operator<<(QDebug s, const CXType &t);
QDebug operator<<(QDebug s, const CXCursor &cursor);
QDebug operator<<(QDebug s, const CXSourceLocation &location);
#endif // !QT_NO_DEBUG_STREAM

#endif // CLANGDEBUGUTILS_H
