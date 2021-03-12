/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet qopenglshaderprogram_setuniformvalue_float
float value = %2;
%CPPSELF.setUniformValue(%1, value);
// @snippet qopenglshaderprogram_setuniformvalue_float

// @snippet qopenglshaderprogram_setuniformvalue_int
int value = %2;
%CPPSELF.setUniformValue(%1, value);
// @snippet qopenglshaderprogram_setuniformvalue_int

// @snippet qopenglversionfunctionsfactory-get
QAbstractOpenGLFunctions *af = %CPPSELF.%FUNCTION_NAME(%1, %2);
if (auto *f = dynamic_cast<QOpenGLFunctions_4_5_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_5_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_5_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_5_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_4_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_4_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_4_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_4_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_3_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_3_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_2_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_2_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_1_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_1_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_0_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_0_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_0_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_0_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_3_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_3_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_3_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_3_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_2_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_2_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_2_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_2_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_1 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_1 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_0 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_0 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_2_1 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_2_1 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_2_0 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_2_0 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_5 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_5 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_4 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_4 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_3 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_3 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_2 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_2 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_1 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_1 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_0 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_0 *](f);
} else {
    QString message;
    QDebug(&message) << "No OpenGL functions could be obtained for" << %1;
    PyErr_SetString(PyExc_RuntimeError, message.toUtf8().constData());
    %PYARG_0 = Py_None;
}
// @snippet qopenglversionfunctionsfactory-get

