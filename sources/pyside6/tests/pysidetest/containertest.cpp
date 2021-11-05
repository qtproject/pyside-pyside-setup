/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the test suite of Qt for Python.
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

#include "containertest.h"

ContainerTest::ContainerTest() = default;

QMultiMap<int, QString> ContainerTest::createMultiMap()
{
    static const QMultiMap<int, QString>
        result{{1, u"v1"_qs},
                {2, u"v2_1"_qs}, {2, u"v2_2"_qs},
                {3, u"v3"_qs},
                {4, u"v4_1"_qs}, {4, u"v4_2"_qs}};
    return result;
}

QMultiMap<int, QString> ContainerTest::passThroughMultiMap(const QMultiMap<int, QString> &in)
{
    return in;
}

QMultiHash<int, QString> ContainerTest::createMultiHash()
{
    static const QMultiHash<int, QString>
        result{{1, u"v1"_qs},
               {2, u"v2_1"_qs}, {2, u"v2_2"_qs},
               {3, u"v3"_qs},
               {4, u"v4_1"_qs}, {4, u"v4_2"_qs}};
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
