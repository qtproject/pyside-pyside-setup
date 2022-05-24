// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef QTCOMPAT_H
#define QTCOMPAT_H

#include <QtCore/QtGlobal>

#if QT_VERSION < 0x060400

// QTBUG-98434, provide literals of Qt 6.4 for compatibility.

#  include <QtCore/QString>

# define QLatin1StringView QLatin1String

namespace Qt {
inline namespace Literals {
inline namespace StringLiterals {

constexpr inline QLatin1String operator"" _L1(const char *str, size_t size) noexcept
{
    return QLatin1String(str, qsizetype(size));
}

inline QString operator"" _s(const char16_t *str, size_t size) noexcept
{
    return QString(QStringPrivate(nullptr, const_cast<char16_t *>(str), qsizetype(size)));
}

} // StringLiterals
} // Literals
} // Qt

#endif // < 6.4

#endif // QTCOMPAT_H
