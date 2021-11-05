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
