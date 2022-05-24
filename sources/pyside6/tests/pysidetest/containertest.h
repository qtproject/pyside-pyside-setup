// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#pragma once

#include "pysidetest_macros.h"

#include <QtCore/QObject>
#include <QtCore/QList>
#include <QtCore/QMap>
#include <QtCore/QMultiMap>
#include <QtCore/QMultiHash>
#include <QtCore/QSet>
#include <QtCore/QString>

class PYSIDETEST_API ContainerTest
{
public:
    ContainerTest();

    static QMultiMap<int, QString> createMultiMap();

    static QMultiMap<int, QString> passThroughMultiMap(const QMultiMap<int, QString> &in);

    static QMultiHash<int, QString> createMultiHash();

    static QMultiHash<int, QString> passThroughMultiHash(const QMultiHash<int, QString> &in);

    static QList<int> createList();
    static QList<int> passThroughList(const QList<int> &list);

    static QSet<int> createSet();
    static QSet<int> passThroughSet(const QSet<int> &set);
};
