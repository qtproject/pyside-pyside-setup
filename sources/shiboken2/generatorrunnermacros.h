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

#ifndef GENERATORRUNNERMACROS_H
#define GENERATORRUNNERMACROS_H

// GENRUNNER_API is used for the public API symbols.
#if defined _WIN32
    #define GENRUNNER_EXPORT __declspec(dllexport)
    #if GENRUNNER_EXPORTS
        #define GENRUNNER_API GENRUNNER_EXPORT
    #endif
#elif __GNUC__ >= 4
    #define GENRUNNER_EXPORT __attribute__ ((visibility("default")))
    #define GENRUNNER_API GENRUNNER_EXPORT
#elif __GNUC__ < 4
    #define GENRUNNER_EXPORT
#endif

#ifndef GENRUNNER_API
    #define GENRUNNER_API
#endif
#endif
