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
    # Broken in 6.5.0
    #'QtQuickControls2': 'qtquickcontrols-module.html',
    'QtSql': 'qtsql-module.html',
    'QtWidgets': 'qtwidgets-module.html',
    'QtConcurrent': 'qtconcurrent-module.html',
    'QtDBus': 'qtdbus-module.html',
    'QtHelp': 'qthelp-module.html',
    'QtOpenGL': 'qtopengl-module.html',
    'QtPrintSupport': 'qtprintsupport-module.html',
    'QtSvg': 'qtsvg-module.html',
    'QtSvgWidgets': 'qtsvgwidgets-module.html',
    'QtUiTools': 'qtuitools-module.html',
    'QtXml': 'qtxml-module.html',
    'QtTest': 'qttest-module.html',
    'Qt3DCore': 'qt3dcore-module.html',
    'Qt3DInput': 'qt3dinput-module.html',
    'Qt3DLogic': 'qt3dlogic-module.html',
    'Qt3DRender': 'qt3drender-module.html',
    'Qt3DAnimation': 'qt3danimation-module.html',
    'Qt3DExtras': 'qt3dextras-module.html',
    'QtNetworkAuth':  'qtnetworkauth-module.html',
    'QtStateMachine': 'qtstatemachine-module.html',
    # 'QtCoAp' -- TODO
    # 'QtMqtt' -- TODO
    # 'QtOpcUA' -- TODO

    # 6.1
    'QtScxml':  'qtscxml-module.html',
    'QtCharts':  'qtcharts-module.html',
    'QtDataVisualization':  'qtdatavisualization-module.html',

    # 6.2
    'QtBluetooth': 'qtbluetooth-module.html',
    'QtPositioning':  'qtpositioning-module.html',
    'QtMultimedia':  'qtmultimedia-module.html',
    'QtRemoteObjects':  'qtremoteobjects-module.html',
    'QtSensors':  'qtsensors-module.html',
    'QtSerialPort':  'qtserialport-module.html',
    'QtWebChannel':  'qtwebchannel-module.html',
    'QtWebEngineCore':  'qtwebenginecore-module.html',
    'QtWebEngineQuick':  'qtwebenginequick-module.html',
    'QtWebEngineWidgets':  'qtwebenginewidgets-module.html',
    'QtWebSockets':  'qtwebsockets-module.html',
    'QtHttpServer': 'qthttpserver-module.html',

    #  6.3
    #'QtSpeech':  'qtspeech-module.html',
    'QtMultimediaWidgets':  'qtmultimediawidgets-module.html',
    'QtNfc': 'qtnfc-module.html',
    'QtQuick3D': 'qtquick3d-module.html',

    # 6.4
    'QtPdf':  'qtpdf-module.html',  # this include qtpdfwidgets
    'QtSpatialAudio': 'qtspatialaudio-module.html',

    # 6.5
    'QtSerialBus':  'qtserialbus-module.html',
    'QtTextToSpeech': 'qttexttospeech-module.html',
    'QtLocation':  'qtlocation-module.html',

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
