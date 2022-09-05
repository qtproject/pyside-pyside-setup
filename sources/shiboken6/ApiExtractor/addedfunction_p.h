// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ADDEDFUNCTION_P_H
#define ADDEDFUNCTION_P_H

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
    bool equals(const Argument &rhs) const;

    QString type;
    QString name;
    QString defaultValue;
};

using Arguments = QList<Argument>;

inline bool operator==(const Argument &a1, const Argument &a2) { return a1.equals(a2); }
inline bool operator!=(const Argument &a1, const Argument &a2) { return !a1.equals(a2); }

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const Argument &a);
#endif

Arguments splitParameters(QStringView paramString, QString *errorMessage = nullptr);

} // namespace AddedFunctionParser

#endif // MODIFICATIONS_P_H
