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

#ifndef SHIBOKENMACROS_H
#define SHIBOKENMACROS_H

// LIBSHIBOKEN_API macro is used for the public API symbols.
#if defined _WIN32
#  define LIBSHIBOKEN_EXPORT __declspec(dllexport)
#  ifdef _MSC_VER
#    define LIBSHIBOKEN_IMPORT __declspec(dllimport)
#  else
#    define LIBSHIBOKEN_IMPORT
#  endif
#  define SBK_DEPRECATED(func) __declspec(deprecated) func
#else
#  define LIBSHIBOKEN_EXPORT __attribute__ ((visibility("default")))
#  define LIBSHIBOKEN_IMPORT
#  define SBK_DEPRECATED(func) func __attribute__ ((deprecated))
#endif

#ifdef BUILD_LIBSHIBOKEN
#  define LIBSHIBOKEN_API LIBSHIBOKEN_EXPORT
#else
#  define LIBSHIBOKEN_API LIBSHIBOKEN_IMPORT
#endif

#endif // SHIBOKENMACROS_H
