# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import ctypes
import math
import mapbox_earcut
import numpy
from functools import partial

from PySide6.QtQuick3D import QQuick3DGeometry
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QVector3D, QColor
from PySide6.QtCore import QByteArray, QThreadPool, Qt, Signal, Slot

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "OSMBuildings"
QML_IMPORT_MAJOR_VERSION = 1


FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
FLOAT_MAX = 3.40282e+38
FLOAT_MIN = 1.17549e-38


UINT32_SIZE = 4

STRIDE_VERTEX_LEN = 20
# 3 Position + 3 Normal + 3 Tangent + 3 Binormal + 4 Color + 2 Texcoord0 + 2 Texcoord1
# as Number of Levels and Is Rooftop.
STRIDE_PRIMITIVE = 3


SPHERE_SECTOR_COUNT = 10
SPHERE_STACK_COUNT = 10


def convertGeoCoordToVertexPosition(lat, lon):
    scale = 1.212
    geoToPositionScale = 1000000 * scale
    XOffsetFromCenter = 537277 * scale
    YOffsetFromCenter = 327957 * scale
    x = (lon / 360.0 + 0.5) * geoToPositionScale
    y = ((1.0 - math.log(math.tan(math.radians(lat)) + 1.0 / math.cos(math.radians(lat))) / math.pi)
         * 0.5 * geoToPositionScale)
    return QVector3D(x - XOffsetFromCenter, YOffsetFromCenter - y, 0.0)


def readColorProperty(properties, name, defaultColor):
    if colorName := properties.get("color"):
        color = QColor.fromString(colorName)
        if color.isValid() and color != QColor(Qt.GlobalColor.black):
            return color
    return defaultColor


class VertexData:
    """A data buffer for the vertexes consisting of STRIDE_VERTEX_LEN * float32
       entries. It can be converted to QByteArray for
       QQuick3DGeometry.setVertexData()."""
    def __init__(self):
        self._vertexData: numpy.ndarray = None
        self._index = 0

    def vertexCount(self):
        return self._vertexData.shape[0] if self._vertexData is not None else 0

    def toByteArray(self):
        return (QByteArray(self._vertexData.tobytes()) if self._vertexData is not None
                else QByteArray())

    def growBy(self, count):
        if count > 0:
            if self._vertexData is None:
                self._vertexData = numpy.ndarray(shape=(count, STRIDE_VERTEX_LEN),
                                                 dtype=numpy.float32)
            else:
                oldSize = self.vertexCount()
                self._vertexData.resize((oldSize + count, STRIDE_VERTEX_LEN), refcheck=False)

    def append(self, pos, normal, tangent, binormal, color, alpha,
               texCoordX, texCoordY, levels, isRoofTop):
        self.set(self._index, pos, normal, tangent, binormal, color, alpha,
                 texCoordX, texCoordY, levels, isRoofTop)
        self._index += 1

    def set(self, index, pos, normal, tangent, binormal, color, alpha,
            texCoordX, texCoordY, levels, isRoofTop):
        self._vertexData[index][0] = pos.x()
        self._vertexData[index][1] = pos.y()
        self._vertexData[index][2] = pos.z()

        self._vertexData[index][3] = normal.x()
        self._vertexData[index][4] = normal.y()
        self._vertexData[index][5] = normal.z()

        self._vertexData[index][6] = tangent.x()
        self._vertexData[index][7] = tangent.y()
        self._vertexData[index][8] = tangent.z()

        self._vertexData[index][9] = binormal.x()
        self._vertexData[index][10] = binormal.y()
        self._vertexData[index][11] = binormal.z()

        self._vertexData[index][12] = color.redF()
        self._vertexData[index][13] = color.greenF()
        self._vertexData[index][14] = color.blueF()
        self._vertexData[index][15] = alpha

        self._vertexData[index][16] = texCoordX
        self._vertexData[index][17] = texCoordY

        self._vertexData[index][18] = levels
        self._vertexData[index][19] = isRoofTop


class IndexData:
    """A data buffer for the vertex indexes consisting uint32 entries. It can be
       converted to QByteArray for QQuick3DGeometry.setIndexData()."""
    def __init__(self):
        self._indexData: numpy.ndarray = None
        self._index = 0

    def indexCount(self):
        return self._indexData.shape[0] if self._indexData is not None else 0

    def toByteArray(self):
        return (QByteArray(self._indexData.tobytes()) if self._indexData is not None
                else QByteArray())

    def growBy(self, count):
        if count > 0:
            if self._indexData is None:
                self._indexData = numpy.ndarray(shape=(count),
                                                dtype=numpy.uint32)
            else:
                oldSize = self.indexCount()
                self._indexData.resize((oldSize + count), refcheck=False)

    def append(self, v):
        self._indexData[self._index] = v
        self._index += 1

    def append3(self, v1, v2, v3):
        self._indexData[self._index] = v1
        self._index += 1
        self._indexData[self._index] = v2
        self._index += 1
        self._indexData[self._index] = v3
        self._index += 1


@QmlElement
class OSMGeometry(QQuick3DGeometry):
    geometryReady = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot("QVariantList")
    def updateData(self, geoVariantsList):
        QThreadPool.globalInstance().start(partial(self.loadGeometryFromData, geoVariantsList))

    def loadGeometryFromData(self, geoVariantsList):

        meshMinBound = QVector3D(FLOAT_MAX, FLOAT_MAX, FLOAT_MAX)
        meshMaxBound = QVector3D(FLOAT_MIN, FLOAT_MIN, FLOAT_MIN)

        globalVertexCounter = 0
        globalPrimitiveCounter = 0

        vertexData = VertexData()
        indexData = IndexData()

        for baseData in geoVariantsList:
            for featureMap in baseData["data"]:
                properties = featureMap["properties"]
                buildingCoords = featureMap["data"].perimeter()
                height = 0.15 * properties["height"]
                levels = float(properties.get("levels", 0))
                color = readColorProperty(properties, "color", QColor(Qt.GlobalColor.white))
                roofColor = readColorProperty(properties, "roofColor", color)
                subsetMinBound = QVector3D(FLOAT_MAX, FLOAT_MAX, FLOAT_MAX)
                subsetMaxBound = QVector3D(FLOAT_MIN, FLOAT_MIN, FLOAT_MIN)

                numSubsetVertices = len(buildingCoords) * 2

                vertexData.growBy(numSubsetVertices)
                indexData.growBy((numSubsetVertices - 2) * STRIDE_PRIMITIVE)

                subsetVertexCounter = 0

                lastBaseVertexPos = QVector3D()
                lastExtrudedVertexPos = QVector3D()
                currentBaseVertexPos = QVector3D()
                currentExtrudedVertexPos = QVector3D()
                subsetPolygonCenter = QVector3D()

                roofPolygonVertices = numpy.ndarray(shape=(len(buildingCoords), 2),
                                                    dtype=numpy.float32)
                for b, buildingPoint in enumerate(buildingCoords):
                    lastBaseVertexPos = currentBaseVertexPos
                    lastExtrudedVertexPos = currentExtrudedVertexPos

                    currentBaseVertexPos = convertGeoCoordToVertexPosition(buildingPoint.latitude(),  # noqa: E501
                                                                           buildingPoint.longitude())  # noqa: E501
                    currentExtrudedVertexPos = QVector3D(currentBaseVertexPos.x(),
                                                         currentBaseVertexPos.y(),
                                                         height)

                    roofPolygonVertices[b][0] = currentBaseVertexPos.x()
                    roofPolygonVertices[b][1] = currentBaseVertexPos.y()

                    subsetPolygonCenter.setX(subsetPolygonCenter.x() + currentBaseVertexPos.x())
                    subsetPolygonCenter.setY(subsetPolygonCenter.y() + currentBaseVertexPos.y())

                    meshMinBound.setX(min(meshMinBound.x(), currentBaseVertexPos.x()))
                    meshMinBound.setY(min(meshMinBound.y(), currentBaseVertexPos.y()))
                    meshMinBound.setZ(min(meshMinBound.z(), currentBaseVertexPos.z()))

                    meshMaxBound.setX(max(meshMaxBound.x(), currentExtrudedVertexPos.x()))
                    meshMaxBound.setY(max(meshMaxBound.y(), currentExtrudedVertexPos.y()))
                    meshMaxBound.setZ(max(meshMaxBound.z(), currentExtrudedVertexPos.z()))

                    subsetMinBound.setX(min(subsetMinBound.x(), currentBaseVertexPos.x()))
                    subsetMinBound.setY(min(subsetMinBound.y(), currentBaseVertexPos.y()))
                    subsetMinBound.setZ(min(subsetMinBound.z(), currentBaseVertexPos.z()))

                    subsetMaxBound.setX(max(subsetMaxBound.x(), currentExtrudedVertexPos.x()))
                    subsetMaxBound.setY(max(subsetMaxBound.y(), currentExtrudedVertexPos.y()))
                    subsetMaxBound.setZ(max(subsetMaxBound.z(), currentExtrudedVertexPos.z()))

                    if subsetVertexCounter < numSubsetVertices - 2:
                        indexData.append3(globalVertexCounter + 3, globalVertexCounter + 2,
                                          globalVertexCounter + 0)
                        indexData.append3(globalVertexCounter + 1, globalVertexCounter + 3,
                                          globalVertexCounter + 0)

                        globalPrimitiveCounter += 2

                    if subsetVertexCounter == 2:
                        tangent = (currentExtrudedVertexPos - currentBaseVertexPos).normalized()
                        binormal = (lastBaseVertexPos - currentBaseVertexPos).normalized()
                        normal = QVector3D.crossProduct(binormal, tangent).normalized()

                        vertexData.append(lastBaseVertexPos, normal, tangent,
                                          binormal, color, 1, 0, 0, levels, 0.0)

                        vertexData.append(lastExtrudedVertexPos, normal,
                                          tangent, binormal, color, 1, 0, 0, levels, 0.0)

                    if subsetVertexCounter >= 2:
                        tangent = (currentExtrudedVertexPos - currentBaseVertexPos).normalized()
                        binormal = (lastBaseVertexPos - currentBaseVertexPos).normalized()
                        normal = QVector3D.crossProduct(binormal, tangent).normalized()

                        xCoord = 1.0 if subsetVertexCounter % 4 != 0 else 0.0
                        vertexData.append(currentBaseVertexPos, normal, tangent,
                                          binormal, color, 1, xCoord, 0, levels, 0.0)

                        vertexData.append(currentExtrudedVertexPos, normal,
                                          tangent, binormal, color, 1, xCoord, 0, levels, 0.0)

                    subsetVertexCounter += 2
                    globalVertexCounter += 2

                if properties.get("shape", "") == "sphere":
                    subsetPolygonCenter = QVector3D(subsetPolygonCenter.x()
                                                    / len(roofPolygonVertices),
                                                    subsetPolygonCenter.y()
                                                    / len(roofPolygonVertices),
                                                    height)

                    sphereRadius = 2.0 * abs(roofPolygonVertices[0][0] - subsetPolygonCenter.x())

                    sphereRadius = max(sphereRadius, 1.0)
                    sphereRadiuslengthInv = 1.0 / sphereRadius

                    sphereSectorStep = 2.0 * math.pi / SPHERE_SECTOR_COUNT
                    sphereStackStep = math.pi / SPHERE_STACK_COUNT

                    sphereVertexCount = (SPHERE_STACK_COUNT + 1) * (SPHERE_SECTOR_COUNT + 1)
                    vertexData.growBy(sphereVertexCount)
                    indexData.growBy(sphereVertexCount * 2 * STRIDE_PRIMITIVE)

                    for stackIndex in range(0, SPHERE_STACK_COUNT + 1):
                        k1 = stackIndex * (SPHERE_SECTOR_COUNT + 1)
                        k2 = k1 + SPHERE_SECTOR_COUNT + 1

                        sphereStackAngle = math.pi / 2.0 - stackIndex * sphereStackStep
                        xy = sphereRadius * math.cos(sphereStackAngle)
                        z = sphereRadius * math.sin(sphereStackAngle)

                        for sectorIndex in range(0, SPHERE_SECTOR_COUNT + 1):
                            if stackIndex != SPHERE_STACK_COUNT:
                                if stackIndex != 0:
                                    indexData.append3(k1 + globalVertexCounter,
                                                      k2 + globalVertexCounter,
                                                      k1 + 1 + globalVertexCounter)
                                    globalPrimitiveCounter += 1

                                if stackIndex != (SPHERE_STACK_COUNT - 1):
                                    indexData.append3(k1 + 1 + globalVertexCounter,
                                                      k2 + globalVertexCounter,
                                                      k2 + 1 + globalVertexCounter)
                                    globalPrimitiveCounter += 1

                            sphereSectorAngle = sectorIndex * sphereSectorStep

                            x = xy * math.cos(sphereSectorAngle)
                            y = xy * math.sin(sphereSectorAngle)

                            position = QVector3D(x + subsetPolygonCenter.x(),
                                                 y + subsetPolygonCenter.y(),
                                                 z + subsetPolygonCenter.z())
                            normal = QVector3D(x * sphereRadiuslengthInv,
                                               y * sphereRadiuslengthInv,
                                               z * sphereRadiuslengthInv)

                            vertexData.append(position, normal,
                                              QVector3D(0, 0, 0), QVector3D(0, 0, 0),
                                              roofColor, 1, 1.0, 1.0, 0.0, 1.0)

                            k1 += 1
                            k2 += 1

                    subsetVertexCounter += sphereVertexCount
                    globalVertexCounter += sphereVertexCount

                rings = numpy.array([len(roofPolygonVertices)], dtype=numpy.uint32)
                roofIndices = mapbox_earcut.triangulate_float32(roofPolygonVertices, rings)

                vertexData.growBy(len(roofPolygonVertices))
                indexData.growBy(len(roofIndices))

                for roofIndex in roofIndices:
                    indexData.append(roofIndex + globalVertexCounter)

                roofPrimitiveCount = int(len(roofIndices) / 3)
                globalPrimitiveCounter += roofPrimitiveCount

                for polygonVertex in roofPolygonVertices:
                    position = QVector3D(polygonVertex[0], polygonVertex[1], height)
                    normal = QVector3D(0.0, 0.0, 1.0)
                    tangent = QVector3D(1.0, 0.0, 0.0)
                    binormal = QVector3D(0.0, 1.0, 0.0)
                    vertexData.append(position, normal, tangent,
                                      binormal, roofColor, 1.0, 1.0, 1.0, 0.0, 1.0)

                    subsetVertexCounter += 1
                    globalVertexCounter += 1

        self.clear()

        self.setIndexData(indexData.toByteArray())
        self.setVertexData(vertexData.toByteArray())
        self.setStride(STRIDE_VERTEX_LEN * FLOAT_SIZE)

        self.setBounds(meshMinBound, meshMaxBound)

        self.setPrimitiveType(QQuick3DGeometry.PrimitiveType.Triangles)
        self.addAttribute(QQuick3DGeometry.Attribute.IndexSemantic, 0,
                          QQuick3DGeometry.Attribute.U32Type)
        self.addAttribute(QQuick3DGeometry.Attribute.PositionSemantic, 0,
                          QQuick3DGeometry.Attribute.F32Type)
        self.addAttribute(QQuick3DGeometry.Attribute.NormalSemantic, 3 * FLOAT_SIZE,
                          QQuick3DGeometry.Attribute.F32Type)
        self.addAttribute(QQuick3DGeometry.Attribute.TangentSemantic, 6 * FLOAT_SIZE,
                          QQuick3DGeometry.Attribute.F32Type)
        self.addAttribute(QQuick3DGeometry.Attribute.BinormalSemantic, 9 * FLOAT_SIZE,
                          QQuick3DGeometry.Attribute.F32Type)
        self.addAttribute(QQuick3DGeometry.Attribute.ColorSemantic, 12 * FLOAT_SIZE,
                          QQuick3DGeometry.Attribute.F32Type)
        self.addAttribute(QQuick3DGeometry.Attribute.TexCoord0Semantic, 16 * FLOAT_SIZE,
                          QQuick3DGeometry.Attribute.F32Type)
        self.addAttribute(QQuick3DGeometry.Attribute.TexCoord1Semantic, 18 * FLOAT_SIZE,
                          QQuick3DGeometry.Attribute.F32Type)
        self.update()
        self.geometryReady.emit()
