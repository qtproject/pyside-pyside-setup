# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import numpy

from PySide6.QtCore import (QFile, QIODevice)
from PySide6.QtGui import (QColor, QMatrix4x4)
from PySide6.QtGui import (QRhiBuffer,
                           QRhiDepthStencilClearValue,
                           QRhiShaderResourceBinding,
                           QRhiShaderStage,
                           QRhiVertexInputAttribute, QRhiVertexInputBinding,
                           QRhiVertexInputLayout, QRhiViewport,
                           QShader)
from PySide6.QtWidgets import QRhiWidget
from PySide6.support import VoidPtr

VERTEX_DATA = numpy.array([ 0.0,  0.5, 1.0, 0.0, 0.0,  # noqa E:201
                           -0.5, -0.5, 0.0, 1.0, 0.0,  # noqa E:241
                            0.5, -0.5, 0.0, 0.0, 1.0],
                          dtype=numpy.float32)


def getShader(name):
    f = QFile(name)
    if f.open(QIODevice.ReadOnly):
        return QShader.fromSerialized(f.readAll())
    return QShader()


class ExampleRhiWidget(QRhiWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_rhi = None
        self.m_vbuf = None
        self.m_ubuf = None
        self.m_srb = None
        self.m_pipeline = None
        self.m_viewProjection = QMatrix4x4()
        self.m_rotation = 0.0

    def releaseResources(self):
        self.m_pipeline.destroy()
        del self.m_pipeline
        self.m_pipeline = None
        self.m_srb.destroy()
        del self.m_srb
        self.m_srb = None
        self.m_ubuf.destroy()
        del self.m_ubuf
        self.m_ubuf = None
        self.m_vbuf.destroy()
        del self.m_vbuf
        self.m_buf = None

    def initialize(self, cb):
        if self.m_rhi != self.rhi():
            self.m_pipeline = None
            self.m_rhi = self.rhi()

        if not self.m_pipeline:
            vertex_size = 4 * VERTEX_DATA.size
            self.m_vbuf = self.m_rhi.newBuffer(QRhiBuffer.Immutable,
                                               QRhiBuffer.VertexBuffer, vertex_size)
            self.m_vbuf.create()

            self.m_ubuf = self.m_rhi.newBuffer(QRhiBuffer.Dynamic,
                                               QRhiBuffer.UniformBuffer, 64)
            self.m_ubuf.create()

            self.m_srb = self.m_rhi.newShaderResourceBindings()
            bindings = [
                QRhiShaderResourceBinding.uniformBuffer(0, QRhiShaderResourceBinding.VertexStage,
                                                        self.m_ubuf)
            ]
            self.m_srb.setBindings(bindings)
            self.m_srb.create()

            self.m_pipeline = self.m_rhi.newGraphicsPipeline()
            stages = [
                QRhiShaderStage(QRhiShaderStage.Vertex,
                                getShader(":/shader_assets/color.vert.qsb")),
                QRhiShaderStage(QRhiShaderStage.Fragment,
                                getShader(":/shader_assets/color.frag.qsb"))
            ]
            self.m_pipeline.setShaderStages(stages)
            inputLayout = QRhiVertexInputLayout()
            input_bindings = [QRhiVertexInputBinding(5 * 4)]  # sizeof(float)
            inputLayout.setBindings(input_bindings)
            attributes = [  # 4: sizeof(float)
                QRhiVertexInputAttribute(0, 0, QRhiVertexInputAttribute.Float2, 0),
                QRhiVertexInputAttribute(0, 1, QRhiVertexInputAttribute.Float3, 2 * 4)
            ]
            inputLayout.setAttributes(attributes)
            self.m_pipeline.setVertexInputLayout(inputLayout)
            self.m_pipeline.setShaderResourceBindings(self.m_srb)
            self.m_pipeline.setRenderPassDescriptor(self.renderTarget().renderPassDescriptor())
            self.m_pipeline.create()

            resourceUpdates = self.m_rhi.nextResourceUpdateBatch()
            resourceUpdates.uploadStaticBuffer(self.m_vbuf, VoidPtr(VERTEX_DATA.tobytes(),
                                                                    vertex_size))
            cb.resourceUpdate(resourceUpdates)

        outputSize = self.renderTarget().pixelSize()
        self.m_viewProjection = self.m_rhi.clipSpaceCorrMatrix()
        r = float(outputSize.width()) / float(outputSize.height())
        self.m_viewProjection.perspective(45.0, r, 0.01, 1000.0)
        self.m_viewProjection.translate(0, 0, -4)

    def render(self, cb):
        resourceUpdates = self.m_rhi.nextResourceUpdateBatch()
        self.m_rotation += 1.0
        modelViewProjection = self.m_viewProjection
        modelViewProjection.rotate(self.m_rotation, 0, 1, 0)
        projection = numpy.array(modelViewProjection.data(),
                                 dtype=numpy.float32)
        resourceUpdates.updateDynamicBuffer(self.m_ubuf, 0, 64,
                                            projection.tobytes())
        clearColor = QColor.fromRgbF(0.4, 0.7, 0.0, 1.0)
        cv = QRhiDepthStencilClearValue(1.0, 0)
        cb.beginPass(self.renderTarget(), clearColor, cv, resourceUpdates)

        cb.setGraphicsPipeline(self.m_pipeline)
        outputSize = self.renderTarget().pixelSize()
        cb.setViewport(QRhiViewport(0, 0, outputSize.width(),
                                    outputSize.height()))
        cb.setShaderResources()
        vbufBinding = (self.m_vbuf, 0)
        cb.setVertexInput(0, [vbufBinding])
        cb.draw(3)
        cb.endPass()

        self.update()
