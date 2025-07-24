// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtWebEngine

QtObject {
    id: root

    property QtObject defaultProfilePrototype : WebEngineProfilePrototype {
        storageName: "Profile"
        Component.onCompleted: {
            let fullVersionList = defaultProfilePrototype.instance().clientHints.fullVersionList;
            fullVersionList["QuickNanoBrowser"] = "1.0";
            defaultProfilePrototype.instance().clientHints.fullVersionList = fullVersionList;
        }
    }

    property QtObject otrPrototype : WebEngineProfilePrototype {
    }

    property Component browserWindowComponent: BrowserWindow {
        applicationRoot: root
    }
    property Component browserDialogComponent: BrowserDialog {
        onClosing: destroy()
    }
    function createWindow(profile) {
        var newWindow = browserWindowComponent.createObject(root);
        newWindow.currentWebView.profile = profile;
        profile.downloadRequested.connect(newWindow.onDownloadRequested);
        return newWindow;
    }
    function createDialog(profile) {
        var newDialog = browserDialogComponent.createObject(root);
        newDialog.currentWebView.profile = profile;
        return newDialog;
    }
    function load(url) {
        var browserWindow = createWindow(defaultProfilePrototype.instance());
        browserWindow.currentWebView.url = url;
    }
}
