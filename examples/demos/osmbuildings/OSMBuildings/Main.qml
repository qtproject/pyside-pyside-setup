// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Window
import QtQuick3D
import QtQuick3D.Helpers

import OSMBuildings

Window {
    width: 1024
    height: 768
    visible: true
    title: qsTr("OSM Buildings")

    OSMManager {
        id: osmManager

        onMapsDataReady: function( mapData, tileX, tileY, zoomLevel ){
            mapModels.addModel(mapData, tileX, tileY, zoomLevel)
        }
    }

    Component {
        id: chunkModelMap
        Node {
            property variant mapData: null
            property int tileX: 0
            property int tileY: 0
            property int zoomLevel: 0
            Model {
                id: basePlane
                position: Qt.vector3d( osmManager.tileSizeX * tileX, osmManager.tileSizeY * -tileY, 0.0 )
                scale: Qt.vector3d( osmManager.tileSizeX / 100., osmManager.tileSizeY / 100., 0.5)
                source: "#Rectangle"
                materials: [
                    CustomMaterial {
                        property TextureInput tileTexture: TextureInput {
                            enabled: true
                            texture: Texture {
                                textureData: CustomTextureData {
                                    Component.onCompleted: setImageData( mapData )
                                } }
                        }
                        shadingMode: CustomMaterial.Shaded
                        cullMode: Material.BackFaceCulling
                        fragmentShader: "customshadertiles.frag"
                    }
                ]
            }
        }
    }


    View3D {
        id: v3d
        anchors.fill: parent

        environment: ExtendedSceneEnvironment {
            id: env
            backgroundMode: SceneEnvironment.Color
            clearColor: "#8099b3"
            fxaaEnabled: true
            fog: Fog {
                id: theFog
                color:"#8099b3"
                enabled: true
                depthEnabled: true
                depthFar: 600
            }
        }

        Node {
            id: originNode
            eulerRotation: Qt.vector3d(50.0, 0.0, 0.0)
            PerspectiveCamera {
                id: cameraNode
                frustumCullingEnabled: true
                clipFar: 600
                clipNear: 100
                fieldOfView: 90
                z: 100

                onZChanged: originNode.updateManagerCamera()

            }
            Component.onCompleted: updateManagerCamera()

            onPositionChanged: updateManagerCamera()

            onRotationChanged: updateManagerCamera()

            function updateManagerCamera(){
                osmManager.setCameraProperties( originNode.position,
                                               originNode.right, cameraNode.z,
                                               cameraController.minimumZoom,
                                               cameraController.maximumZoom,
                                               originNode.eulerRotation.x,
                                               cameraController.minimumTilt,
                                               cameraController.maximumTilt )
            }
        }

        DirectionalLight {
            color: Qt.rgba(1.0, 1.0, 0.95, 1.0)
            ambientColor: Qt.rgba(0.5, 0.45, 0.45, 1.0)
            rotation: Quaternion.fromEulerAngles(-10, -45, 0)
        }

        Node {
            id: mapModels

            function addModel(mapData, tileX, tileY, zoomLevel)
            {
                chunkModelMap.createObject( mapModels, { "mapData": mapData,
                                               "tileX": tileX,
                                               "tileY": tileY,
                                               "zoomLevel": zoomLevel
                                           } )
            }
        }

        OSMCameraController {
            id: cameraController
            origin: originNode
            camera: cameraNode
        }
    }

    Item {
        id: tokenArea
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 10
        Text {
            id: tokenInputArea
            visible: false
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            color: "white"
            styleColor: "black"
            style: Text.Outline
            text: "Open street map tile token: "
            Rectangle {
                border.width: 1
                border.color: "black"
                anchors.fill: tokenTxtInput
                anchors.rightMargin: -30
                Text {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.topMargin: 2
                    anchors.rightMargin: 8
                    color: "blue"
                    styleColor: "white"
                    style: Text.Outline
                    text: "OK"
                    Behavior on scale {
                        NumberAnimation {
                            easing.type: Easing.OutBack
                        }
                    }
                    MouseArea {
                        anchors.fill: parent
                        anchors.margins: -10
                        onPressedChanged: {
                            if (pressed)
                                parent.scale = 0.9
                            else
                                parent.scale = 1.0
                        }
                        onClicked: {
                            tokenInputArea.visible = false
                            osmManager.setToken(tokenTxtInput.text)
                            tokenWarning.demoToken = osmManager.isDemoToken()
                            tokenWarning.visible = true
                        }
                    }
                }
            }
            TextInput {
                id: tokenTxtInput
                clip: true
                anchors.left: parent.right
                anchors.bottom: parent.bottom
                anchors.bottomMargin: -3
                height: tokenTxtInput.contentHeight + 5
                width: 110
                leftPadding: 5
                rightPadding: 5
            }
        }

        Text {
            id: tokenWarning
            property bool demoToken: true
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            color: "white"
            styleColor: "black"
            style: Text.Outline
            text: demoToken ? "You are using the OSM limited demo token " :
                              "You are using a token "
            Text {
                anchors.left: parent.right
                color: "blue"
                styleColor: "white"
                style: Text.Outline
                text: "click here to change"
                Behavior on scale {
                    NumberAnimation {
                        easing.type: Easing.OutBack
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    onPressedChanged: {
                        if (pressed)
                            parent.scale = 0.9
                        else
                            parent.scale = 1.0
                    }
                    onClicked: {
                        tokenWarning.visible = false
                        tokenTxtInput.text = osmManager.token()
                        tokenInputArea.visible = true
                    }
                }
            }
        }
    }
}
