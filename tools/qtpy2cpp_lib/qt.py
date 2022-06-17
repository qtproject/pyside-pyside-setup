#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python project.
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

"""Provides some type information on Qt classes"""


from enum import Flag


class ClassFlag(Flag):
    PASS_BY_CONSTREF = 1
    PASS_BY_REF = 2
    PASS_BY_VALUE = 4
    PASS_ON_STACK_MASK = PASS_BY_CONSTREF | PASS_BY_REF | PASS_BY_VALUE
    INSTANTIATE_ON_STACK = 8


_QT_CLASS_FLAGS = {
    "QBrush": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QGradient": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QIcon": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QLine": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QLineF": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QPixmap": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QPointF": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QRect": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QRectF": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QSizeF": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QString": ClassFlag.PASS_BY_CONSTREF | ClassFlag.INSTANTIATE_ON_STACK,
    "QFile": ClassFlag.PASS_BY_REF | ClassFlag.INSTANTIATE_ON_STACK,
    "QSettings": ClassFlag.PASS_BY_REF | ClassFlag.INSTANTIATE_ON_STACK,
    "QTextStream": ClassFlag.PASS_BY_REF | ClassFlag.INSTANTIATE_ON_STACK,
    "QColor": ClassFlag.PASS_BY_VALUE | ClassFlag.INSTANTIATE_ON_STACK,
    "QPoint": ClassFlag.PASS_BY_VALUE | ClassFlag.INSTANTIATE_ON_STACK,
    "QSize": ClassFlag.PASS_BY_VALUE | ClassFlag.INSTANTIATE_ON_STACK,
    "QApplication": ClassFlag.INSTANTIATE_ON_STACK,
    "QColorDialog": ClassFlag.INSTANTIATE_ON_STACK,
    "QCoreApplication": ClassFlag.INSTANTIATE_ON_STACK,
    "QFileDialog": ClassFlag.INSTANTIATE_ON_STACK,
    "QFileInfo": ClassFlag.INSTANTIATE_ON_STACK,
    "QFontDialog": ClassFlag.INSTANTIATE_ON_STACK,
    "QGuiApplication": ClassFlag.INSTANTIATE_ON_STACK,
    "QMessageBox": ClassFlag.INSTANTIATE_ON_STACK,
    "QPainter": ClassFlag.INSTANTIATE_ON_STACK,
    "QPen": ClassFlag.INSTANTIATE_ON_STACK,
    "QQmlApplicationEngine": ClassFlag.INSTANTIATE_ON_STACK,
    "QQmlComponent": ClassFlag.INSTANTIATE_ON_STACK,
    "QQmlEngine": ClassFlag.INSTANTIATE_ON_STACK,
    "QQuickView": ClassFlag.INSTANTIATE_ON_STACK,
    "QSaveFile": ClassFlag.INSTANTIATE_ON_STACK
}


def qt_class_flags(type):
    f = _QT_CLASS_FLAGS.get(type)
    return f if f else ClassFlag(0)
