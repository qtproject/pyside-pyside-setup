#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################


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
