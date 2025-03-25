// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DOCUMENTATION_ENUMS_H
#define DOCUMENTATION_ENUMS_H

#include <QtCore/qtypes.h>

enum class DocumentationTarget : uint8_t
{
    Documentation, // Documentation
    DocString // Python doc string (binding code)
};

enum class DocumentationFormat : uint8_t
{
    Native, // XML
    Target  // RST
};

enum class DocumentationEmphasis : uint8_t
{
    None,
    LanguageNote
};

enum class DocumentationType : uint8_t
{
    Detailed,
    Brief
};

#endif // DOCUMENTATION_ENUMS_H
