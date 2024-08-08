// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtWebView
import QtQuick.Layouts


ApplicationWindow {
    id: window
    visible: true
    title: webView.title

    menuBar: ToolBar {
        id: navigationBar
        RowLayout {
            anchors.fill: parent
            spacing: 0

            ToolButton {
                id: backButton
                icon.source: "qrc:/left-32.png"
                onClicked: webView.goBack()
                enabled: webView.canGoBack
                Layout.preferredWidth: navigationBar.height
            }

            ToolButton {
                id: forwardButton
                icon.source: "qrc:/right-32.png"
                onClicked: webView.goForward()
                enabled: webView.canGoForward
                Layout.preferredWidth: navigationBar.height
            }

            ToolButton {
                id: reloadButton
                icon.source: webView.loading ? "qrc:/stop-32.png" : "qrc:/refresh-32.png"
                onClicked: webView.loading ? webView.stop() : webView.reload()
                Layout.preferredWidth: navigationBar.height
            }

            Item { Layout.preferredWidth: 5 }

            TextField {
                Layout.fillWidth: true
                id: urlField
                inputMethodHints: Qt.ImhUrlCharactersOnly | Qt.ImhPreferLowercase
                text: webView.url
                onAccepted: webView.url = utils.fromUserInput(text)
             }

            Item { Layout.preferredWidth: 5 }

            ToolButton {
                id: goButton
                text: qsTr("Go")
                onClicked: {
                    Qt.inputMethod.commit()
                    Qt.inputMethod.hide()
                    webView.url = utils.fromUserInput(urlField.text)
                }
            }

            ToolButton {
                id: settingsButton
                icon.source: "qrc:/settings-32.png"
                onClicked: {
                    settingsDrawer.width = (settingsDrawer.width > 0) ? 0 : window.width * 1/4
                }
                Layout.preferredWidth: navigationBar.height
            }

            Item { Layout.preferredWidth: 10 }
         }
         ProgressBar {
             id: progress
             anchors {
                left: parent.left
                top: parent.bottom
                right: parent.right
                leftMargin: parent.leftMargin
                rightMargin: parent.rightMargin
             }
             height:3
             z: Qt.platform.os === "android" ? -1 : -2
             background: Item {}
             visible: Qt.platform.os !== "ios" && Qt.platform.os !== "winrt"
             from: 0
             to: 100
             value: webView.loadProgress < 100 ? webView.loadProgress : 0
        }
    }

    Item {
        id: settingsDrawer
        anchors.right: parent.right
        ColumnLayout {
            Label {
                text: "JavaScript"
            }
            CheckBox {
                id: javaScriptEnabledCheckBox
                text: "enabled"
                onCheckStateChanged: webView.settings.javaScriptEnabled = (checkState == Qt.Checked)
            }
            Label {
                text: "Local storage"
            }
            CheckBox {
                id: localStorageEnabledCheckBox
                text: "enabled"
                onCheckStateChanged: webView.settings.localStorageEnabled = (checkState == Qt.Checked)
            }
            Label {
                text: "Allow file access"
            }
            CheckBox {
                id: allowFileAccessEnabledCheckBox
                text: "enabled"
                onCheckStateChanged: webView.settings.allowFileAccess = (checkState == Qt.Checked)
            }
            Label {
                text: "Local content can access file URLs"
            }
            CheckBox {
                id: localContentCanAccessFileUrlsEnabledCheckBox
                text: "enabled"
                onCheckStateChanged: webView.settings.localContentCanAccessFileUrls = (checkState == Qt.Checked)
            }
        }
    }

    WebView {
        id: webView
        url: initialUrl
        anchors.right: settingsDrawer.left
        anchors.left: parent.left
        height: parent.height
        onLoadingChanged: function(loadRequest) {
            if (loadRequest.errorString)
                console.error(loadRequest.errorString);
        }

        Component.onCompleted: {
            javaScriptEnabledCheckBox.checkState = settings.javaScriptEnabled ? Qt.Checked : Qt.Unchecked
            localStorageEnabledCheckBox.checkState = settings.localStorageEnabled ? Qt.Checked : Qt.Unchecked
            allowFileAccessEnabledCheckBox.checkState = settings.allowFileAccess ? Qt.Checked : Qt.Unchecked
            localContentCanAccessFileUrlsEnabledCheckBox.checkState = settings.localContentCanAccessFileUrls ? Qt.Checked : Qt.Unchecked
        }
    }
}
