// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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
