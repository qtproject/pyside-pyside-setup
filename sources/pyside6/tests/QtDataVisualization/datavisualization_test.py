#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QtDataVisualization'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QTimer
from PySide6.QtDataVisualization import (Q3DBars, QBar3DSeries, QBarDataItem,
                                         QBarDataProxy, QCategory3DAxis,
                                         QValue3DAxis, QValue3DAxisFormatter,
                                         qDefaultSurfaceFormat)


def dataToBarDataRow(data):
    result = []
    for d in data:
        result.append(QBarDataItem(d))
    return result


def dataToBarDataArray(data):
    result = []
    for row in data:
        result.append(dataToBarDataRow(row))
    return result


class QtDataVisualizationTestCase(UsesQApplication):
    '''Tests related to QtDataVisualization'''

    def testBars(self):
        self.bars = Q3DBars()
        self.columnAxis = QCategory3DAxis()
        self.columnAxis.setTitle('Columns')
        self.columnAxis.setTitleVisible(True)
        self.columnAxis.setLabels(['Column1', 'Column2'])

        self.rowAxis = QCategory3DAxis()
        self.rowAxis.setTitle('Rows')
        self.rowAxis.setTitleVisible(True)
        self.rowAxis.setLabels(['Row1', 'Row2'])

        self.valueAxis = QValue3DAxis()
        self.valueAxis.setTitle('Values')
        self.valueAxis.setTitleVisible(True)
        self.valueAxis.setRange(0, 5)

        self.bars.setRowAxis(self.rowAxis)
        self.bars.setColumnAxis(self.columnAxis)
        self.bars.setValueAxis(self.valueAxis)

        self.series = QBar3DSeries()
        self.arrayData = [[1, 2], [3, 4]]
        self.series.dataProxy().addRows(dataToBarDataArray(self.arrayData))

        self.bars.setPrimarySeries(self.series)

        self.bars.show()
        QTimer.singleShot(500, self.app.quit)
        self.app.exec()

    def testBarDataProxy(self):
        '''PSYSIDE-1438, crashes in QBarDataProxy.addRow()'''
        items = [QBarDataItem(v) for v in [1.0, 2.0]]
        data_proxy = QBarDataProxy()
        data_proxy.addRow(items)
        data_proxy.addRow(items, 'bla')
        data_proxy.insertRow(0, items)
        data_proxy.insertRow(0, items, 'bla')
        data_proxy.setRow(0, items)
        data_proxy.setRow(0, items, 'bla')
        self.assertTrue(data_proxy.rowCount(), 4)

    def testDefaultSurfaceFormat(self):
         format = qDefaultSurfaceFormat(True)
         print(format)

    def testQValue3DAxisFormatter(self):
        """PYSIDE-2025: Test the added setters of QValue3DAxisFormatter."""
        formatter = QValue3DAxisFormatter()
        float_values = [float(10)]
        formatter.setGridPositions(float_values)
        self.assertEqual(formatter.gridPositions(), float_values)

        formatter.setLabelPositions(float_values)
        self.assertEqual(formatter.labelPositions(), float_values)

        label_strings = ["bla"]
        formatter.setLabelStrings(label_strings)
        self.assertEqual(formatter.labelStrings(), label_strings)


if __name__ == '__main__':
    unittest.main()
