# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import math
import sys
from dataclasses import dataclass
from enum import IntEnum
from functools import partial

from PySide6.QtPositioning import QGeoCoordinate, QGeoPolygon
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtCore import (QByteArray, QTimer, QFile, QFileInfo, QJsonDocument,
                            QObject, QUrl, Signal, Slot)

# %1 = zoom level(15 the default and only one here that seems working),
# %2 = x tile number, %3 = y tile number
URL_OSMB_JSON = ("https://983wdxn2c2.execute-api.eu-north-1.amazonaws.com/production/"
                 "osmbuildingstile?z={}&x={}&y={}&token={}")

# %1 = zoom level(is dynamic), %2 = x tile number, %3 = y tile number
URL_OSMB_MAP = "https://tile-a.openstreetmap.fr/hot/{}/{}/{}.png"


class GeoTypeSwitch(IntEnum):
    Polygon = 0
    Feature = 1
    FeatureCollection = 2


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


def importPosition(position):
    returnedCoordinates = QGeoCoordinate()
    if position:
        returnedCoordinates.setLongitude(position[0])
        if len(position) > 1:
            returnedCoordinates.setLatitude(position[1])
            if len(position) > 2:
                returnedCoordinates.setAltitude(position[2])
    return returnedCoordinates


def importArrayOfPositions(arrayOfPositions):
    returnedCoordinates = []
    for position in arrayOfPositions:
        coordinate = importPosition(position)
        if coordinate.isValid():
            returnedCoordinates.append(coordinate)  # Populating the QList of coordinates
    return returnedCoordinates


def importArrayOfArrayOfPositions(arrayOfArrayofPositions):
    returnedCoordinates = []
    for position in arrayOfArrayofPositions:
        returnedCoordinates.append(importArrayOfPositions(position))
    return returnedCoordinates


def importPolygon(inputMap):
    returnedObject = QGeoPolygon()
    valueCoordinates = inputMap.get("coordinates")
    for i, p in enumerate(importArrayOfArrayOfPositions(valueCoordinates)):
        if i == 0:
            returnedObject.setPerimeter(p)  # External perimeter
        else:
            returnedObject.addHole(p)  # Inner perimeters
    return returnedObject


def importGeometry(inputMap):
    returnedObject = {}
    geometryTypes = ["Polygon"]
    for i in range(len(geometryTypes)):
        if inputMap.get("type") == geometryTypes[i]:
            if i == 0:
                returnedObject["type"] = "Polygon"
                returnedObject["data"] = importPolygon(inputMap)
    return returnedObject


def importFeatureCollection(inputMap):
    returnedObject = []
    featuresList = inputMap.get("features")
    for inputfeature in featuresList:
        inputFeatureMap = inputfeature
        singleFeatureMap = importGeometry(inputFeatureMap.get("geometry"))
        importedProperties = inputFeatureMap.get("properties")
        singleFeatureMap["properties"] = importedProperties
        if "id" in inputFeatureMap:
            importedId = inputFeatureMap.get("id")
            singleFeatureMap["id"] = importedId

        returnedObject.append(singleFeatureMap)
    return returnedObject


def importGeoJson(geoJson):
    returnedList = []
    rootGeoJsonObject = geoJson.object()  # Read json object from imported doc

    geoType = ["Polygon", "Feature", "FeatureCollection"]
    geometryTypesLen = len(geoType)

    parsedGeoJsonMap = {}

    # Checking whether the JSON object has a "type" member
    valueType = rootGeoJsonObject.get("type")

    # Checking whether the "type" member has a GeoJSON admitted value
    for i in range(geometryTypesLen):
        if valueType == geoType[i]:
            if i == GeoTypeSwitch.Polygon:
                poly = importPolygon(rootGeoJsonObject)
                parsedGeoJsonMap.insert("type", "Polygon")
                parsedGeoJsonMap.insert("data", poly)

            # Single GeoJson geometry object with properties
            elif i == GeoTypeSwitch.Feature:
                parsedGeoJsonMap = importGeometry(rootGeoJsonObject.get("geometry"))
                importedProperties = rootGeoJsonObject.get("properties")
                parsedGeoJsonMap.insert("properties", importedProperties)
                id_value = rootGeoJsonObject.get("id")
                if id_value:
                    parsedGeoJsonMap.insert("id", id_value)
            # Heterogeneous list of GeoJSON geometries with properties
            elif i == GeoTypeSwitch.FeatureCollection:
                featCollection = importFeatureCollection(rootGeoJsonObject)
                parsedGeoJsonMap["type"] = "FeatureCollection"
                parsedGeoJsonMap["data"] = featCollection

            bboxNodeValue = rootGeoJsonObject.get("bbox")
            if bboxNodeValue is not None:
                parsedGeoJsonMap["bbox"] = bboxNodeValue
            returnedList.append(parsedGeoJsonMap)

        elif i >= 9:
            # Error
            break
    return returnedList


class OSMRequest(QObject):

    buildingsDataReady = Signal(list, int, int, int)
    mapsDataReady = Signal(QByteArray, int, int, int)

    def __init__(self, parent):
        super().__init__(parent)

        self.m_buildingsNumberOfRequestsInFlight = 0
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
    def stop(self):
        if self.m_queuesTimer.isActive():
            self.m_queuesTimer.stop()

    @Slot()
    def _slotTimeOut(self):
        if not self.m_buildingsQueue and not self.m_mapsQueue:
            self.m_queuesTimer.stop()
        else:
            numConcurrentRequests = 6
            if (self.m_buildingsQueue
                    and self.m_buildingsNumberOfRequestsInFlight < numConcurrentRequests):
                self.getBuildingsDataRequest(self.m_buildingsQueue[0])
                del self.m_buildingsQueue[0]
                self.m_buildingsNumberOfRequestsInFlight += 1
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

    def getBuildingsDataRequest(self, tile):
        fileName = "data/" + tileKey(tile) + ".json"
        if QFileInfo.exists(fileName):
            file = QFile(fileName)
            if file.open(QFile.ReadOnly):
                data = file.readAll()
                file.close()
                doc = QJsonDocument.fromJson(data)
                self.buildingsDataReady.emit(importGeoJson(doc),
                                             tile.TileX, tile.TileY, tile.ZoomLevel)
                self.m_buildingsNumberOfRequestsInFlight -= 1
                return

        url = QUrl(URL_OSMB_JSON.format(tile.ZoomLevel, tile.TileX, tile.TileY, self.m_token))
        reply = self.m_networkAccessManager.get(QNetworkRequest(url))
        reply.finished.connect(partial(self._buildingsDataReceived, reply, tile))

    @Slot(OSMTileData)
    def _buildingsDataReceived(self, reply, tile):
        reply.deleteLater()
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            self.buildingsDataReady.emit(importGeoJson(QJsonDocument.fromJson(data)),
                                         tile.TileX, tile.TileY, tile.ZoomLevel)
        else:
            message = reply.readAll().data().decode('utf-8')
            if message != self.m_lastBuildingsDataError:
                self.m_lastBuildingsDataError = message
                print("OSMRequest.getBuildingsData ", reply.error(),
                      reply.url(), message, file=sys.stderr)
        self.m_buildingsNumberOfRequestsInFlight -= 1

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
            if file.open(QFile.OpenModeFlag.ReadOnly):
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
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            self.mapsDataReady.emit(data, tile.TileX, tile.TileY, tile.ZoomLevel)
        else:
            message = reply.readAll().data().decode('utf-8')
            if message != self.m_lastMapsDataError:
                self.m_lastMapsDataError = message
                print("OSMRequest.getMapsDataRequest", reply.error(),
                      reply.url(), message, file=sys.stderr)
        self.m_mapsNumberOfRequestsInFlight -= 1
