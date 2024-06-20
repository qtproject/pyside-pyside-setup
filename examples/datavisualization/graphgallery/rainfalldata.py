# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from pathlib import Path

from PySide6.QtCore import QFile, QIODevice, QObject
from PySide6.QtDataVisualization import (QBar3DSeries, QCategory3DAxis, QValue3DAxis)

from variantbardataproxy import VariantBarDataProxy
from variantbardatamapping import VariantBarDataMapping
from variantdataset import VariantDataSet


MONTHS = ["January", "February", "March", "April",
          "May", "June", "July", "August", "September", "October",
          "November", "December"]


class RainfallData(QObject):

    def __init__(self):
        super().__init__()
        self._columnCount = 0
        self._rowCount = 0
        self._years = []
        self._numericMonths = []
        self._proxy = VariantBarDataProxy()
        self._mapping = None
        self._dataSet = None
        self._series = QBar3DSeries()
        self._valueAxis = QValue3DAxis()
        self._rowAxis = QCategory3DAxis()
        self._colAxis = QCategory3DAxis()

        # In data file the months are in numeric format, so create custom list
        for i in range(1, 13):
            self._numericMonths.append(str(i))

        self._columnCount = len(self._numericMonths)

        self.updateYearsList(2010, 2022)

        # Create proxy and series
        self._proxy = VariantBarDataProxy()
        self._series = QBar3DSeries(self._proxy)

        self._series.setItemLabelFormat("%.1f mm")

        # Create the axes
        self._rowAxis = QCategory3DAxis(self)
        self._colAxis = QCategory3DAxis(self)
        self._valueAxis = QValue3DAxis(self)
        self._rowAxis.setAutoAdjustRange(True)
        self._colAxis.setAutoAdjustRange(True)
        self._valueAxis.setAutoAdjustRange(True)

        # Set axis labels and titles
        self._rowAxis.setTitle("Year")
        self._colAxis.setTitle("Month")
        self._valueAxis.setTitle("rainfall (mm)")
        self._valueAxis.setSegmentCount(5)
        self._rowAxis.setLabels(self._years)
        self._colAxis.setLabels(MONTHS)
        self._rowAxis.setTitleVisible(True)
        self._colAxis.setTitleVisible(True)
        self._valueAxis.setTitleVisible(True)

        self.addDataSet()

    def customSeries(self):
        return self._series

    def valueAxis(self):
        return self._valueAxis

    def rowAxis(self):
        return self._rowAxis

    def colAxis(self):
        return self._colAxis

    def updateYearsList(self, start, end):
        self._years.clear()
        for i in range(start, end + 1):
            self._years.append(str(i))
        self._rowCount = len(self._years)

    def addDataSet(self):
        # Create a new variant data set and data item list
        self._dataSet = VariantDataSet()
        itemList = []

        # Read data from a data file into the data item list
        file_path = Path(__file__).resolve().parent / "data" / "raindata.txt"
        dataFile = QFile(file_path)
        if dataFile.open(QIODevice.ReadOnly | QIODevice.Text):
            data = dataFile.readAll().data().decode("utf8")
            for line in data.split("\n"):
                if line and not line.startswith("#"):  # Ignore comments
                    tokens = line.split(",")
                    # Each line has three data items: Year, month, and
                    # rainfall value
                    if len(tokens) >= 3:
                        # Store year and month as strings, and rainfall value
                        # as double into a variant data item and add the item to
                        # the item list.
                        newItem = []
                        newItem.append(tokens[0].strip())
                        newItem.append(tokens[1].strip())
                        newItem.append(float(tokens[2].strip()))
                        itemList.append(newItem)
        else:
            print("Unable to open data file:", dataFile.fileName(),
                  file=sys.stderr)

        # Add items to the data set and set it to the proxy
        self._dataSet.addItems(itemList)
        self._proxy.setDataSet(self._dataSet)

        # Create new mapping for the data and set it to the proxy
        self._mapping = VariantBarDataMapping(0, 1, 2,
                                              self._years, self._numericMonths)
        self._proxy.setMapping(self._mapping)
