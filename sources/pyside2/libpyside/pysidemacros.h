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

#ifndef PYSIDEMACROS_H
#define PYSIDEMACROS_H

#include <shibokenmacros.h>

#define PYSIDE_EXPORT LIBSHIBOKEN_EXPORT
#define PYSIDE_IMPORT LIBSHIBOKEN_IMPORT
#define PYSIDE_DEPRECATED(func) SBK_DEPRECATED(func)

#ifdef BUILD_LIBPYSIDE
#  define PYSIDE_API PYSIDE_EXPORT
#else
#  define PYSIDE_API PYSIDE_IMPORT
#endif

#endif // PYSIDEMACROS_H
