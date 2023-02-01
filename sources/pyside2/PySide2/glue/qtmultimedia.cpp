/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

// @snippet upcast
%BEGIN_ALLOW_THREADS
QObject * upcastedArg = %CONVERTTOCPP[QObject *](%PYARG_1);
//XXX   /|\ omitting this space crashes shiboken!
%CPPSELF.%FUNCTION_NAME(reinterpret_cast< %ARG1_TYPE >(upcastedArg));
%END_ALLOW_THREADS
// @snippet upcast

// @snippet qvideoframe-bits
%BEGIN_ALLOW_THREADS
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME();
%END_ALLOW_THREADS
%PYARG_0 = Shiboken::Buffer::newObject(%0, %CPPSELF.bytesPerLine() * %CPPSELF.height(), Shiboken::Buffer::ReadWrite);
// @snippet qvideoframe-bits
