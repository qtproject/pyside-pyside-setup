// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ADDEDFUNCTION_P_H
#define ADDEDFUNCTION_P_H

#include <QtCore/QtCompare>
#include <QtCore/QList>
#include <QtCore/QString>
#include <QtCore/QStringView>

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

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const Argument &a);
#endif

Arguments splitParameters(QStringView paramString, QString *errorMessage = nullptr);

} // namespace AddedFunctionParser

#endif // MODIFICATIONS_P_H
