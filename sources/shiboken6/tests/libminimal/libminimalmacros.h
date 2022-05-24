// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef LIBMINIMALMACROS_H
#define LIBMINIMALMACROS_H

#if defined _WIN32
#  define LIBMINIMAL_EXPORT __declspec(dllexport)
#  ifdef _MSC_VER
#    define LIBMINIMAL_IMPORT __declspec(dllimport)
#  else
#    define LIBMINIMAL_IMPORT
#  endif
#else
#  define LIBMINIMAL_EXPORT __attribute__ ((visibility("default")))
#  define LIBMINIMAL_IMPORT
#endif

#ifdef LIBMINIMAL_BUILD
#  define LIBMINIMAL_API LIBMINIMAL_EXPORT
#else
#  define LIBMINIMAL_API LIBMINIMAL_IMPORT
#endif

#endif // LIBMINIMALMACROS_H
