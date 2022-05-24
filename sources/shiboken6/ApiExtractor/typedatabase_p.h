// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPEDATABASE_P_H
#define TYPEDATABASE_P_H

#include <QtCore/QHash>
#include <QtCore/QString>

class TypeDatabase;
class SmartPointerTypeEntry;

struct TypeDatabaseParserContext
{
    using SmartPointerInstantiations = QHash<SmartPointerTypeEntry *, QString>;

    TypeDatabase *db;
    SmartPointerInstantiations smartPointerInstantiations;
};

#endif // TYPEDATABASE_P_H
