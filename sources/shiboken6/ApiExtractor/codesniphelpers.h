// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CODESNIPHELPERS_H
#define CODESNIPHELPERS_H

#include <QtCore/QString>

class CodeSnipHelpers
{
public:
    static QString fixSpaces(QString code);
    static QString dedent(const QString &code);
    static void prependCode(QString *code, QString firstLine);
};

#endif // CODESNIPHELPERS_H
