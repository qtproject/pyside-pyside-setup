// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef QTDOCPARSER_H
#define QTDOCPARSER_H

#include "docparser.h"

struct ClassDocumentation;

class QtDocParser : public DocParser
{
public:
    QtDocParser() = default;
    void fillDocumentation(const AbstractMetaClassPtr &metaClass) override;
    Documentation retrieveModuleDocumentation() override;
    Documentation retrieveModuleDocumentation(const QString& name) override;

private:
    static QString functionDocumentation(const QString &sourceFileName,
                                         const ClassDocumentation &classDocumentation,
                                         const AbstractMetaClassCPtr &metaClass,
                                         const AbstractMetaFunctionCPtr &func,
                                         QString *errorMessage);

    static QString queryFunctionDocumentation(const QString &sourceFileName,
                                              const ClassDocumentation &classDocumentation,
                                              const AbstractMetaClassCPtr &metaClass,
                                              const AbstractMetaFunctionCPtr &func,
                                              QString *errorMessage);
};

#endif // QTDOCPARSER_H

