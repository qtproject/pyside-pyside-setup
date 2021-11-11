/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the Qt for Python examples of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:BSD$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** BSD License Usage
** Alternatively, you may use this file under the terms of the BSD license
** as follows:
**
** "Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are
** met:
**   * Redistributions of source code must retain the above copyright
**     notice, this list of conditions and the following disclaimer.
**   * Redistributions in binary form must reproduce the above copyright
**     notice, this list of conditions and the following disclaimer in
**     the documentation and/or other materials provided with the
**     distribution.
**   * Neither the name of The Qt Company Ltd nor the names of its
**     contributors may be used to endorse or promote products derived
**     from this software without specific prior written permission.
**
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
** "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
** LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
** A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
** OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
** SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
** LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
** DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
** THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
** (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
** OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
**
** $QT_END_LICENSE$
**
****************************************************************************/

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick3D
import QtQuick3D.Helpers
import ExamplePointGeometry
import ExampleTriangleGeometry


Window {
    id: window
    width: 1280
    height: 720
    visible: true
    color: "#848895"

    View3D {
        id: v3d
        anchors.fill: parent
        camera: camera

        PerspectiveCamera {
            id: camera
            position: Qt.vector3d(0, 0, 600)
        }

        DirectionalLight {
            position: Qt.vector3d(-500, 500, -100)
            color: Qt.rgba(0.4, 0.2, 0.6, 1.0)
            ambientColor: Qt.rgba(0.1, 0.1, 0.1, 1.0)
        }

        PointLight {
            position: Qt.vector3d(0, 0, 100)
            color: Qt.rgba(0.1, 1.0, 0.1, 1.0)
            ambientColor: Qt.rgba(0.2, 0.2, 0.2, 1.0)
        }

        Model {
            visible: radioGridGeom.checked
            scale: Qt.vector3d(100, 100, 100)
            geometry: GridGeometry {
                id: grid
                horizontalLines: 20
                verticalLines: 20
            }
            materials: [
                DefaultMaterial {
                    lineWidth: sliderLineWidth.value
                }
            ]
        }

        //! [model triangle]
        Model {
            visible: radioCustGeom.checked
            scale: Qt.vector3d(100, 100, 100)
            geometry: ExampleTriangleGeometry {
                normals: cbNorm.checked
                normalXY: sliderNorm.value
                uv: cbUV.checked
                uvAdjust: sliderUV.value
            }
            materials: [
                DefaultMaterial {
                    Texture {
                        id: baseColorMap
                        source: "qt_logo_rect.png"
                    }
                    cullMode: DefaultMaterial.NoCulling
                    diffuseMap: cbTexture.checked ? baseColorMap : null
                    specularAmount: 0.5
                }
            ]
        }
        //! [model triangle]

        Model {
            visible: radioPointGeom.checked
            scale: Qt.vector3d(100, 100, 100)
            geometry: ExamplePointGeometry { }
            materials: [
                DefaultMaterial {
                    lighting: DefaultMaterial.NoLighting
                    cullMode: DefaultMaterial.NoCulling
                    diffuseColor: "yellow"
                    pointSize: sliderPointSize.value
                }
            ]
        }
    }

    WasdController {
        controlledObject: camera
    }

    ColumnLayout {
        Label {
            text: "Use WASD and mouse to navigate"
            font.bold: true
        }
        ButtonGroup {
            buttons: [ radioGridGeom, radioCustGeom, radioPointGeom ]
        }
        RadioButton {
            id: radioGridGeom
            text: "GridGeometry"
            checked: true
            focusPolicy: Qt.NoFocus
        }
        RadioButton {
            id: radioCustGeom
            text: "Custom geometry from application (triangle)"
            checked: false
            focusPolicy: Qt.NoFocus
        }
        RadioButton {
            id: radioPointGeom
            text: "Custom geometry from application (points)"
            checked: false
            focusPolicy: Qt.NoFocus
        }
        RowLayout {
            visible: radioGridGeom.checked
            ColumnLayout {
                Button {
                    text: "More X cells"
                    onClicked: grid.verticalLines += 1
                    focusPolicy: Qt.NoFocus
                }
                Button  {
                    text: "Fewer X cells"
                    onClicked: grid.verticalLines -= 1
                    focusPolicy: Qt.NoFocus
                }
            }
            ColumnLayout {
                Button {
                    text: "More Y cells"
                    onClicked: grid.horizontalLines += 1
                    focusPolicy: Qt.NoFocus
                }
                Button  {
                    text: "Fewer Y cells"
                    onClicked: grid.horizontalLines -= 1
                    focusPolicy: Qt.NoFocus
                }
            }
        }
        RowLayout {
            visible: radioGridGeom.checked
            Label {
                text: "Line width (if supported)"
            }
            Slider {
                id: sliderLineWidth
                from: 1.0
                to: 10.0
                stepSize: 0.5
                value: 1.0
                focusPolicy: Qt.NoFocus
            }
        }
        RowLayout {
            visible: radioCustGeom.checked
            CheckBox {
                id: cbNorm
                text: "provide normals in geometry"
                checked: false
                focusPolicy: Qt.NoFocus
            }
            RowLayout {
                Label {
                    text: "manual adjust"
                }
                Slider {
                    id: sliderNorm
                    from: 0.0
                    to: 1.0
                    stepSize: 0.01
                    value: 0.0
                    focusPolicy: Qt.NoFocus
                }
            }
        }
        RowLayout {
            visible: radioCustGeom.checked
            CheckBox {
                id: cbTexture
                text: "enable base color map"
                checked: false
                focusPolicy: Qt.NoFocus
            }
            CheckBox {
                id: cbUV
                text: "provide UV in geometry"
                checked: false
                focusPolicy: Qt.NoFocus
            }
            RowLayout {
                Label {
                    text: "UV adjust"
                }
                Slider {
                    id: sliderUV
                    from: 0.0
                    to: 1.0
                    stepSize: 0.01
                    value: 0.0
                    focusPolicy: Qt.NoFocus
                }
            }
        }
        RowLayout {
            visible: radioPointGeom.checked
            ColumnLayout {
                RowLayout {
                    Label {
                        text: "Point size (if supported)"
                    }
                    Slider {
                        id: sliderPointSize
                        from: 1.0
                        to: 16.0
                        stepSize: 1.0
                        value: 1.0
                        focusPolicy: Qt.NoFocus
                    }
                }
            }
        }
        TextArea {
            id: infoText
            readOnly: true
        }
    }
}
