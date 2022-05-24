// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testtoposort.h"
#include "graph.h"

#include <QtTest/QTest>
#include <QtCore/QDebug>

using IntGraph = Graph<int>;

Q_DECLARE_METATYPE(IntGraph)

using IntList = QList<int>;

void TestTopoSort::testTopoSort_data()
{
    QTest::addColumn<IntGraph>("graph");
    QTest::addColumn<bool>("expectedValid");
    QTest::addColumn<IntList>("expectedOrder");

    const int nodes1[] = {0, 1, 2};
    IntGraph g(std::begin(nodes1), std::end(nodes1));
    g.addEdge(1, 2);
    g.addEdge(0, 1);
    IntList expected = {0, 1, 2};
    QTest::newRow("DAG") << g << true << expected;

    const int nodes2[] = {0, 1};
    g.clear();
    g.setNodes(std::begin(nodes2), std::end(nodes2));
    expected = {1, 0};
    QTest::newRow("No edges") << g << true << expected;

    g.clear();
    g.setNodes(std::begin(nodes1), std::end(nodes1));
    g.addEdge(0, 1);
    g.addEdge(1, 2);
    g.addEdge(2, 0);
    expected.clear();
    QTest::newRow("Cyclic") << g << false << expected;
}

void TestTopoSort::testTopoSort()
{
    QFETCH(IntGraph, graph);
    QFETCH(bool, expectedValid);
    QFETCH(IntList, expectedOrder);

    const auto result = graph.topologicalSort();
    QCOMPARE(result.isValid(), expectedValid);
    if (expectedValid) {
        QCOMPARE(result.result, expectedOrder);
        QVERIFY(result.cyclic.isEmpty());
    } else {
        QVERIFY(!result.cyclic.isEmpty());
    }
}

QTEST_APPLESS_MAIN(TestTopoSort)

