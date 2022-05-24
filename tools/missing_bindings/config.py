# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


modules_to_test = {
    # 6.0
    'QtCore': 'qtcore-module.html',
    'QtGui': 'qtgui-module.html',
    'QtNetwork': 'qtnetwork-module.html',
    'QtQml': 'qtqml-module.html',
    'QtQuick': 'qtquick-module.html',
    'QtQuickWidgets': 'qtquickwidgets-module.html',
    'QtQuickControls2': 'qtquickcontrols2-module.html',
    # QtQuick3D - no python bindings
    'QtSql': 'qtsql-module.html',
    'QtWidgets': 'qtwidgets-module.html',
    'QtConcurrent': 'qtconcurrent-module.html',
    # QtDBUS - no python bindings
    'QtHelp': 'qthelp-module.html',
    'QtOpenGL': 'qtopengl-module.html',
    'QtPrintSupport': 'qtprintsupport-module.html',
    'QtSvg': 'qtsvg-module.html',
    'QtUiTools': 'qtuitools-module.html',
    'QtXml': 'qtxml-module.html',
    'QtTest': 'qttest-module.html',
    # 'QtXmlPatterns':  'qtxmlpatterns-module.html',  # in Qt5 compat
    'Qt3DCore': 'qt3dcore-module.html',
    'Qt3DInput': 'qt3dinput-module.html',
    'Qt3DLogic': 'qt3dlogic-module.html',
    'Qt3DRender': 'qt3drender-module.html',
    'Qt3DAnimation': 'qt3danimation-module.html',
    'Qt3DExtras': 'qt3dextras-module.html',
    # 'QtNetworkAuth':  'qtnetworkauth-module.html',  # no python bindings
    # 'QtCoAp' -- TODO
    # 'QtMqtt' -- TODO
    # 'QtOpcUA' -- TODO

    # 6.1
    # 'QtScxml':  'qtscxml-module.html',
    # 'QtCharts':  'qtcharts-module.html',
    # 'QtDataVisualization':  'qtdatavisualization-module.html',

    # 6.2
    'QtBluetooth': 'qtbluetooth-module.html',
    # 'QtPositioning':  'qtpositioning-module.html',
    # 'QtMultimedia':  'qtmultimedia-module.html',
    # 'QtRemoteObjects':  'qtremoteobjects-module.html',
    # 'QtSensors':  'qtsensors-module.html',
    # 'QtSerialPort':  'qtserialport-module.html',
    # 'QtWebChannel':  'qtwebchannel-module.html',
    # 'QtWebEngine':  'qtwebengine-module.html',
    # 'QtWebEngineCore':  'qtwebenginecore-module.html',
    # 'QtWebEngineWidgets':  'qtwebenginewidgets-module.html',
    # 'QtWebSockets':  'qtwebsockets-module.html',

    #  6.x
    # 'QtSpeech':  'qtspeech-module.html',
    # 'QtMultimediaWidgets':  'qtmultimediawidgets-module.html',
    # 'QtLocation':  'qtlocation-module.html',

    #  Not in 6
    # 'QtScriptTools':  'qtscripttools-module.html',
    # 'QtMacExtras':  'qtmacextras-module.html',
    # 'QtX11Extras':  'qtx11extras-module.html',
    # 'QtWinExtras':  'qtwinextras-module.html',
}

types_to_ignore = {
    # QtCore
    'QFlag',
    'QFlags',
    'QGlobalStatic',
    'QDebug',
    'QDebugStateSaver',
    'QMetaObject.Connection',
    'QPointer',
    'QAssociativeIterable',
    'QSequentialIterable',
    'QStaticPlugin',
    'QChar',
    'QLatin1Char',
    'QHash',
    'QMultiHash',
    'QLinkedList',
    'QList',
    'QMap',
    'QMultiMap',
    'QMap.key_iterator',
    'QPair',
    'QQueue',
    'QScopedArrayPointer',
    'QScopedPointer',
    'QScopedValueRollback',
    'QMutableSetIterator',
    'QSet',
    'QSet.const_iterator',
    'QSet.iterator',
    'QExplicitlySharedDataPointer',
    'QSharedData',
    'QSharedDataPointer',
    'QEnableSharedFromThis',
    'QSharedPointer',
    'QWeakPointer',
    'QStack',
    'QLatin1String',
    'QString',
    'QStringRef',
    'QStringList',
    'QStringMatcher',
    'QVarLengthArray',
    'QVector',
    'QFutureIterator',
    'QHashIterator',
    'QMutableHashIterator',
    'QLinkedListIterator',
    'QMutableLinkedListIterator',
    'QListIterator',
    'QMutableListIterator',
    'QMapIterator',
    'QMutableMapIterator',
    'QSetIterator',
    'QMutableVectorIterator',
    'QVectorIterator',
    # QtGui
    'QIconEnginePlugin',
    'QImageIOPlugin',
    'QGenericPlugin',
    'QGenericPluginFactory',
    'QGenericMatrix',
    'QOpenGLExtraFunctions',
    # QtWidgets
    'QItemEditorCreator',
    'QStandardItemEditorCreator',
    'QStylePlugin',
    # QtSql
    'QSqlDriverCreator',
    'QSqlDriverPlugin',
}
