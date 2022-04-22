/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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
