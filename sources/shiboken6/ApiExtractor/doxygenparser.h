// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DOXYGENPARSER_H
#define DOXYGENPARSER_H

#include "docparser.h"

class DoxygenParser : public DocParser
{
public:
    DoxygenParser() = default;
    void fillDocumentation(const AbstractMetaClassPtr &metaClass) override;
    Documentation retrieveModuleDocumentation() override;
    Documentation retrieveModuleDocumentation(const QString& name) override;
};

#endif // DOXYGENPARSER_H
