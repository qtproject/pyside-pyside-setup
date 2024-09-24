# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import math
import sys
from dataclasses import dataclass
from functools import partial

from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtCore import (QByteArray, QTimer, QFile, QFileInfo,
                            QObject, QUrl, Signal, Slot)

# %1 = zoom level(is dynamic), %2 = x tile number, %3 = y tile number
URL_OSMB_MAP = "https://tile-a.openstreetmap.fr/hot/{}/{}/{}.png"


@dataclass
class OSMTileData:
    TileX: int = 0
    TileY: int = 0
    ZoomLevel: int = 1

    def distanceTo(self, x, y):
        deltaX = float(self.TileX) - float(x)
        deltaY = float(self.TileY) - float(y)
        return math.sqrt(deltaX * deltaX + deltaY * deltaY)

    def __eq__(self, rhs):
        return self._equals(rhs)

    def __ne__(self, rhs):
        return not self._equals(rhs)

    def __hash__(self):
        return hash((self.TileX, self.TileY, self.ZoomLevel))

    def _equals(self, rhs):
        return (self.TileX == rhs.TileX and self.TileY == rhs.TileY
                and self.ZoomLevel == rhs.ZoomLevel)


def tileKey(tile):
    return f"{tile.ZoomLevel},{tile.TileX},{tile.TileY}"


class OSMRequest(QObject):

    mapsDataReady = Signal(QByteArray, int, int, int)

    def __init__(self, parent):
        super().__init__(parent)

        self.m_mapsNumberOfRequestsInFlight = 0
        self.m_queuesTimer = QTimer()
        self.m_queuesTimer.setInterval(0)
        self.m_buildingsQueue = []
        self.m_mapsQueue = []
        self.m_networkAccessManager = QNetworkAccessManager()
        self.m_token = ""

        self.m_queuesTimer.timeout.connect(self._slotTimeOut)
        self.m_queuesTimer.setInterval(0)
        self.m_lastBuildingsDataError = ""
        self.m_lastMapsDataError = ""

    @Slot()
    def _slotTimeOut(self):
        if not self.m_buildingsQueue and not self.m_mapsQueue:
            self.m_queuesTimer.stop()
        else:
            numConcurrentRequests = 6
            if self.m_mapsQueue and self.m_mapsNumberOfRequestsInFlight < numConcurrentRequests:
                self.getMapsDataRequest(self.m_mapsQueue[0])
                del self.m_mapsQueue[0]

                self.m_mapsNumberOfRequestsInFlight += 1

    def isDemoToken(self):
        return not self.m_token

    def token(self):
        return self.m_token

    def setToken(self, token):
        self.m_token = token

    def getBuildingsData(self, buildingsQueue):
        if not buildingsQueue:
            return
        self.m_buildingsQueue = buildingsQueue
        if not self.m_queuesTimer.isActive():
            self.m_queuesTimer.start()

    def getMapsData(self, mapsQueue):
        if not mapsQueue:
            return
        self.m_mapsQueue = mapsQueue
        if not self.m_queuesTimer.isActive():
            self.m_queuesTimer.start()

    def getMapsDataRequest(self, tile):
        fileName = "data/" + tileKey(tile) + ".png"
        if QFileInfo.exists(fileName):
            file = QFile(fileName)
            if file.open(QFile.ReadOnly):
                data = file.readAll()
                file.close()
                self.mapsDataReady.emit(data, tile.TileX, tile.TileY, tile.ZoomLevel)
                self.m_mapsNumberOfRequestsInFlight -= 1
                return

        url = QUrl(URL_OSMB_MAP.format(tile.ZoomLevel, tile.TileX, tile.TileY))
        reply = self.m_networkAccessManager.get(QNetworkRequest(url))
        reply.finished.connect(partial(self._mapsDataReceived, reply, tile))

    @Slot(OSMTileData)
    def _mapsDataReceived(self, reply, tile):
        reply.deleteLater()
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            self.mapsDataReady.emit(data, tile.TileX, tile.TileY, tile.ZoomLevel)
        else:
            message = reply.readAll().data().decode('utf-8')
            if message != self.m_lastMapsDataError:
                self.m_lastMapsDataError = message
                print("OSMRequest.getMapsDataRequest", reply.error(),
                      reply.url(), message, file=sys.stderr)
        self.m_mapsNumberOfRequestsInFlight -= 1
