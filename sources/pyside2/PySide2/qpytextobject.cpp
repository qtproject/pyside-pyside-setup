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

#include "qpytextobject.h"

/*!
    \class QPyTextObject
    \brief Workaround to make possible use QTextObjectInterface on PySide.
    \ingroup richtext-processing
    Due to the technical details of how to bind C++ classes to Python, you need to use this class when you need to implement
    your own QTextObjectInterface rather than create a class inheriting from QObject and QTextObjectInterface.

    \sa QTextObjectInterface
*/
