// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick3D
import QtQuick3D.Helpers

import CustomGeometryExample

ApplicationWindow {
    id: window
    width: 1280
    height: 720
    visible: true
    title: "Custom Geometry Example"

    property bool isLandscape: width > height

    View3D {
        id: v3d
        anchors.left: window.isLandscape ? controlsPane.right : parent.left
        anchors.top: window.isLandscape ? parent.top : controlsPane.bottom
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        camera: camera

        environment: SceneEnvironment {
            id: env
            backgroundMode: SceneEnvironment.Color
            clearColor: "#002b36"
        }

        Node {
            id: originNode
            PerspectiveCamera {
                id: cameraNode
                z: 600
            }
        }

        DirectionalLight {
            id: directionalLight
            color: Qt.rgba(0.4, 0.2, 0.6, 1.0)
            ambientColor: Qt.rgba(0.1, 0.1, 0.1, 1.0)
        }

        PointLight {
            id: pointLight
            position: Qt.vector3d(0, 0, 100)
            color: Qt.rgba(0.1, 1.0, 0.1, 1.0)
            ambientColor: Qt.rgba(0.2, 0.2, 0.2, 1.0)
        }

        Model {
            id: gridModel
            visible: false
            scale: Qt.vector3d(100, 100, 100)
            geometry: GridGeometry {
                id: grid
                horizontalLines: 20
                verticalLines: 20
            }
            materials: [
                PrincipledMaterial {
                    lineWidth: sliderLineWidth.value
                }
            ]
        }

        //! [model triangle]
        Model {
            id: triangleModel
            visible: false
            scale: Qt.vector3d(100, 100, 100)
            geometry: ExampleTriangleGeometry {
                normals: cbNorm.checked
                normalXY: sliderNorm.value
                uv: cbUV.checked
                uvAdjust: sliderUV.value
            }
            materials: [
                PrincipledMaterial {
                    Texture {
                        id: baseColorMap
                        source: "qt_logo_rect.png"
                    }
                    cullMode: PrincipledMaterial.NoCulling
                    baseColorMap: cbTexture.checked ? baseColorMap : null
                    specularAmount: 0.5
                }
            ]
        }
        //! [model triangle]

        Model {
            id: pointModel
            visible: false
            scale: Qt.vector3d(100, 100, 100)
            geometry: ExamplePointGeometry { }
            materials: [
                PrincipledMaterial {
                    lighting: PrincipledMaterial.NoLighting
                    cullMode: PrincipledMaterial.NoCulling
                    baseColor: "yellow"
                    pointSize: sliderPointSize.value
                }
            ]
        }

        Model {
            id: torusModel
            visible: false
            geometry: TorusMesh {
                radius: radiusSlider.value
                tubeRadius: tubeRadiusSlider.value
                segments: segmentsSlider.value
                rings: ringsSlider.value
            }
            materials: [
                PrincipledMaterial {
                    id: torusMaterial
                    baseColor: "#dc322f"
                    metalness: 0.0
                    roughness: 0.1
                }
            ]
        }

        OrbitCameraController {
            origin: originNode
            camera: cameraNode
        }
    }

    Pane {
        id: controlsPane
        width: window.isLandscape ? implicitWidth : window.width
        height: window.isLandscape ? window.height : implicitHeight
        ColumnLayout {
            GroupBox {
                title: "Mode"
                ButtonGroup {
                    id: modeGroup
                    buttons: [ radioGridGeom, radioCustGeom, radioPointGeom, radioQMLGeom ]
                }
                ColumnLayout {
                    RadioButton {
                        id: radioGridGeom
                        text: "GridGeometry"
                        checked: true
                    }
                    RadioButton {
                        id: radioCustGeom
                        text: "Custom geometry from application (triangle)"
                        checked: false
                    }
                    RadioButton {
                        id: radioPointGeom
                        text: "Custom geometry from application (points)"
                        checked: false
                    }
                    RadioButton {
                        id: radioQMLGeom
                        text: "Custom geometry from QML"
                        checked: false
                    }
                }
            }

            Pane {
                id: gridSettings
                visible: false
                ColumnLayout {
                    Button {
                        text: "+ Y Cells"
                        onClicked: grid.horizontalLines += 1
                        Layout.alignment: Qt.AlignHCenter

                    }
                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        Button  {
                            text: "- X Cells"
                            onClicked: grid.verticalLines -= 1
                        }
                        Button {
                            text: "+ X Cells"
                            onClicked: grid.verticalLines += 1
                        }
                    }
                    Button  {
                        text: "- Y Cells"
                        onClicked: grid.horizontalLines -= 1
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Label {
                        text: "Line width (if supported)"
                    }
                    Slider {
                        Layout.fillWidth: true
                        id: sliderLineWidth
                        from: 1.0
                        to: 10.0
                        stepSize: 0.5
                        value: 1.0
                    }
                }
            }
            Pane {
                id: triangleSettings
                visible: false
                ColumnLayout {
                    CheckBox {
                        id: cbNorm
                        text: "provide normals in geometry"
                        checked: false
                    }
                    RowLayout {
                        enabled: cbNorm.checked
                        Label {
                            Layout.fillWidth: true
                            text: "Normal adjust: "
                        }
                        Slider {
                            id: sliderNorm

                            from: 0.0
                            to: 1.0
                            stepSize: 0.01
                            value: 0.0
                        }
                    }
                    CheckBox {
                        id: cbTexture
                        text: "enable base color map"
                        checked: false
                    }
                    CheckBox {
                        id: cbUV
                        text: "provide UV in geometry"
                        checked: false
                    }
                    RowLayout {
                        enabled: cbUV.checked
                        Label {
                            Layout.fillWidth: true
                            text: "UV adjust:"
                        }
                        Slider {
                            id: sliderUV
                            from: 0.0
                            to: 1.0
                            stepSize: 0.01
                            value: 0.0
                        }
                    }
                }

            }
            Pane {
                id: pointSettings
                visible: false
                RowLayout {
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
                            }
                        }
                    }
                }
            }
            Pane {
                id: torusSettings
                visible: false
                ColumnLayout {
                    Label {
                        text: "Radius: (" + radiusSlider.value + ")"
                    }
                    Slider {
                        id: radiusSlider
                        from: 1.0
                        to: 1000.0
                        stepSize: 1.0
                        value: 200
                    }
                    Label {
                        text: "Tube Radius: (" + tubeRadiusSlider.value + ")"
                    }
                    Slider {
                        id: tubeRadiusSlider
                        from: 1.0
                        to: 500.0
                        stepSize: 1.0
                        value: 50
                    }
                    Label {
                        text: "Rings: (" + ringsSlider.value + ")"
                    }
                    Slider {
                        id: ringsSlider
                        from: 3
                        to: 35
                        stepSize: 1.0
                        value: 20
                    }
                    Label {
                        text: "Segments: (" + segmentsSlider.value + ")"
                    }
                    Slider {
                        id: segmentsSlider
                        from: 3
                        to: 35
                        stepSize: 1.0
                        value: 20
                    }
                    CheckBox {
                        id: wireFrameCheckbox
                        text: "Wireframe Mode"
                        checked: false
                        onCheckedChanged: {
                            env.debugSettings.wireframeEnabled = checked
                            torusMaterial.cullMode = checked ? Material.NoCulling : Material.BackFaceCulling


                        }
                    }
                }

            }
        }
        states: [
            State {
                name: "gridMode"
                when: radioGridGeom.checked
                PropertyChanges {
                    gridModel.visible: true
                    gridSettings.visible: true
                    env.debugSettings.wireframeEnabled: false
                    originNode.position: Qt.vector3d(0, 0, 0)
                    originNode.rotation: Qt.quaternion(1, 0, 0, 0)
                    cameraNode.z: 600

                }
            },
            State {
                name: "triangleMode"
                when: radioCustGeom.checked
                PropertyChanges {
                    triangleModel.visible: true
                    triangleSettings.visible: true
                    env.debugSettings.wireframeEnabled: false
                    originNode.position: Qt.vector3d(0, 0, 0)
                    originNode.rotation: Qt.quaternion(1, 0, 0, 0)
                    cameraNode.z: 600
                }
            },
            State {
                name: "pointMode"
                when: radioPointGeom.checked
                PropertyChanges {
                    pointModel.visible: true
                    pointSettings.visible: true
                    env.debugSettings.wireframeEnabled: false
                    originNode.position: Qt.vector3d(0, 0, 0)
                    originNode.rotation: Qt.quaternion(1, 0, 0, 0)
                    cameraNode.z: 600
                }
            },
            State {
                name: "qmlMode"
                when: radioQMLGeom.checked
                PropertyChanges {
                    torusModel.visible: true
                    torusSettings.visible: true
                    directionalLight.eulerRotation: Qt.vector3d(-40, 0, 0)
                    directionalLight.color: "white"
                    pointLight.color: "white"
                    pointLight.position: Qt.vector3d(0, 0, 0)
                    originNode.position: Qt.vector3d(0, 0, 0)
                    originNode.eulerRotation: Qt.vector3d(-40, 0, 0)
                    cameraNode.z: 600
                }
            }
        ]
    }
}
