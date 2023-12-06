// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick3D
import QtQuick3D.Helpers
import QtQuick.Controls
import QtQuick.Layouts

import ProceduralTextureModule

ApplicationWindow {
    id: window
    width: 480
    height: 320
    visible: true
    title: "Procedural Texture Example"

    QtObject {
        id: applicationState
        property int size: size256.checked ? 256 : 16
        property color startColor: "#00dbde"
        property color endColor: "#fc00ff"
        property int filterMode: size === 256 ? Texture.Linear : Texture.Nearest
        property Texture texture: pythonModeRadio.checked ? textureFromPython : textureFromQML

        function randomColor() : color {
            return Qt.rgba(Math.random(),
                           Math.random(),
                           Math.random(),
                           1.0);
        }
    }

    View3D {
        anchors.fill: parent

        DirectionalLight {
        }

        PerspectiveCamera {
            z: 300
        }

        Texture {
            id: textureFromPython

            minFilter: applicationState.filterMode
            magFilter: applicationState.filterMode
            textureData: gradientTexture

            GradientTexture {
                id: gradientTexture
                startColor: applicationState.startColor
                endColor: applicationState.endColor
                width: applicationState.size
                height: width
            }
        }

        Texture {
            id: textureFromQML
            minFilter: applicationState.filterMode
            magFilter: applicationState.filterMode
            textureData: gradientTextureDataQML

            ProceduralTextureData {
                id: gradientTextureDataQML

                property color startColor: applicationState.startColor
                property color endColor: applicationState.endColor
                width: applicationState.size
                height: width
                textureData: generateTextureData()

                function linearInterpolate(startColor : color, endColor : color, fraction : real) : color{
                    return Qt.rgba(
                                startColor.r + (endColor.r - startColor.r) * fraction,
                                startColor.g + (endColor.g - startColor.g) * fraction,
                                startColor.b + (endColor.b - startColor.b) * fraction,
                                startColor.a + (endColor.a - startColor.a) * fraction
                                );
                }

                function generateTextureData() {
                    let dataBuffer = new ArrayBuffer(width * height * 4)
                    let data = new Uint8Array(dataBuffer)

                    let gradientScanline = new Uint8Array(width * 4);

                    for (let x = 0; x < width; ++x) {
                        let color = linearInterpolate(startColor, endColor, x / width);
                        let offset = x * 4;
                        gradientScanline[offset + 0] = color.r * 255;
                        gradientScanline[offset + 1] = color.g * 255;
                        gradientScanline[offset + 2] = color.b * 255;
                        gradientScanline[offset + 3] = color.a * 255;
                    }

                    for (let y = 0; y < height; ++y) {
                        data.set(gradientScanline, y * width * 4);
                    }

                    return dataBuffer;
                }
            }
        }

        Model {
            source: "#Cube"

            materials: [
                PrincipledMaterial {
                    baseColorMap: applicationState.texture
                }
            ]

            PropertyAnimation on eulerRotation.y {
                from: 0
                to: 360
                duration: 5000
                loops: Animation.Infinite
                running: true
            }
        }
    }

    Pane {
        ColumnLayout {

            GroupBox {
                title: "Size:"

                ButtonGroup  {
                    id: sizeGroup
                }

                ColumnLayout {
                    RadioButton {
                        id: size256
                        text: "256x256"
                        checked: true
                        ButtonGroup.group: sizeGroup
                    }
                    RadioButton {
                        id: size512
                        text: "16x16"
                        checked: false
                        ButtonGroup.group: sizeGroup
                    }
                }
            }

            GroupBox {
                title: "Backend:"

                ButtonGroup {
                    id: backendGroup
                }

                ColumnLayout {
                    RadioButton {
                        id: pythonModeRadio
                        text: "Python"
                        checked: true
                        ButtonGroup.group: backendGroup
                    }
                    RadioButton {
                        id: qmlModeRadio
                        text: "QML"
                        checked: false
                        ButtonGroup.group: backendGroup
                    }
                }

            }

            Button {
                text: "Random Start Color"
                onClicked: applicationState.startColor = applicationState.randomColor();
            }
            Button {
                text: "Random End Color"
                onClicked: applicationState.endColor = applicationState.randomColor();
            }
        }
    }
}
