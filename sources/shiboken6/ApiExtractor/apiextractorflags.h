// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef APIEXTRACTORFLAGS_H
#define APIEXTRACTORFLAGS_H

#include <QtCore/QFlags>

enum class ApiExtractorFlag
{
    UsePySideExtensions = 0x1,
    AvoidProtectedHack = 0x2
};

Q_DECLARE_FLAGS(ApiExtractorFlags, ApiExtractorFlag)
Q_DECLARE_OPERATORS_FOR_FLAGS(ApiExtractorFlags)

enum class InheritTemplateFlag
{
    SetEnclosingClass = 0x1
};

Q_DECLARE_FLAGS(InheritTemplateFlags, InheritTemplateFlag)
Q_DECLARE_OPERATORS_FOR_FLAGS(InheritTemplateFlags)

#endif // APIEXTRACTORFLAGS_H
