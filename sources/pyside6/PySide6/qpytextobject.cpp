// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "qpytextobject.h"

/*!
    \class QPyTextObject
    \brief Workaround to make possible use QTextObjectInterface on PySide.
    \ingroup richtext-processing
    Due to the technical details of how to bind C++ classes to Python, you need to use this class when you need to implement
    your own QTextObjectInterface rather than create a class inheriting from QObject and QTextObjectInterface.

    \sa QTextObjectInterface
*/
