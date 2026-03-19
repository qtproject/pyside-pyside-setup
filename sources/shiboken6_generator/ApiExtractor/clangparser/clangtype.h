// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CLANGTYPE_H
#define CLANGTYPE_H

#include <QtCore/qstring.h>

#include <optional>

QT_FORWARD_DECLARE_CLASS(QDebug)

namespace clang {

struct TypeName
{
    QString name;
    QString templateParameters;
};

// Split a type name "std::list<int>::value_type<T>" into the canonical name
// "std::list::value_type" and its template parameters "<T>"
std::optional<TypeName> parseTypeName(QString t);

QDebug operator<<(QDebug, const TypeName &ct);
} // namespace clang

#endif // CLANGTYPE_H
