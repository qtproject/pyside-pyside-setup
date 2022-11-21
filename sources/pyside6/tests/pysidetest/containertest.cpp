// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "containertest.h"

using namespace Qt::StringLiterals;

ContainerTest::ContainerTest() = default;

QMultiMap<int, QString> ContainerTest::createMultiMap()
{
    static const QMultiMap<int, QString>
        result{{1, u"v1"_s},
                {2, u"v2_1"_s}, {2, u"v2_2"_s},
                {3, u"v3"_s},
                {4, u"v4_1"_s}, {4, u"v4_2"_s}};
    return result;
}

QMultiMap<int, QString> ContainerTest::passThroughMultiMap(const QMultiMap<int, QString> &in)
{
    return in;
}

QMultiHash<int, QString> ContainerTest::createMultiHash()
{
    static const QMultiHash<int, QString>
        result{{1, u"v1"_s},
               {2, u"v2_1"_s}, {2, u"v2_2"_s},
               {3, u"v3"_s},
               {4, u"v4_1"_s}, {4, u"v4_2"_s}};
    return result;

}

QMultiHash<int, QString> ContainerTest::passThroughMultiHash(const QMultiHash<int, QString> &in)
{
    return in;
}

QList<int> ContainerTest::createList()
{
    return {1, 2};
}

QList<int> ContainerTest::passThroughList(const QList<int> &list)
{
    return list;
}

QSet<int> ContainerTest::createSet()
{
    return {1, 2};
}

QSet<int> ContainerTest::passThroughSet(const QSet<int> &set)
{
    return set;
}
