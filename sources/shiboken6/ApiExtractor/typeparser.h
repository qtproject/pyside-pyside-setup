// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPEPARSER_H
#define TYPEPARSER_H

#include <QtCore/QString>

class TypeInfo;

class TypeParser
{
public:
    static TypeInfo parse(const QString &str, QString *errorMessage = nullptr);
};

#endif // TYPEPARSER_H
