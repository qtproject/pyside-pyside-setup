// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:build-tool

#ifndef ADDEDFUNCTIONPARSER_H
#define ADDEDFUNCTIONPARSER_H

#include <QtCore/qcompare.h>
#include <QtCore/qlist.h>
#include <QtCore/qstring.h>
#include <QtCore/qstringview.h>

#include <optional>

QT_BEGIN_NAMESPACE
class QDebug;
QT_END_NAMESPACE

// Helpers to split a parameter list of <add-function>, <declare-function>
// in a separate header for testing purposes

namespace AddedFunctionParser {

struct Argument
{
    QString type;
    QString name;
    QString defaultValue;

    friend bool comparesEqual(const Argument &lhs, const Argument &rhs) noexcept
    {
        return lhs.type == rhs.type && lhs.name == rhs.name
               && lhs.defaultValue == rhs.defaultValue;
    }
    Q_DECLARE_EQUALITY_COMPARABLE(Argument)
};

using Arguments = QList<Argument>;

struct ParsedFunction
{
    QString name;
    Arguments arguments;
    bool constant{false};
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const Argument &a);
QDebug operator<<(QDebug d, const ParsedFunction &f);
#endif

Arguments splitParameters(QStringView paramString, QString *errorMessage = nullptr);

std::optional<ParsedFunction> parse(QStringView signature, QString *errorMessage);

} // namespace AddedFunctionParser

#endif // ADDEDFUNCTIONPARSER_H
