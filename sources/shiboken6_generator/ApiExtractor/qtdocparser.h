// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef QTDOCPARSER_H
#define QTDOCPARSER_H

#include "docparser.h"
#include <optional>

struct ClassDocumentation;
struct FunctionDocumentation;

class QtDocParser : public DocParser
{
public:
    QtDocParser() = default;
    QString fillDocumentation(const AbstractMetaClassPtr &metaClass) override;
    void fillGlobalFunctionDocumentation(const AbstractMetaFunctionPtr &f) override;
    void fillGlobalEnumDocumentation(AbstractMetaEnum &e) override;

    ModuleDocumentation retrieveModuleDocumentation(const QString &name) override;

    static QString qdocModuleDir(const QString &pythonType);

private:
    using FunctionDocumentationOpt = std::optional<FunctionDocumentation>;

    static FunctionDocumentationOpt
         functionDocumentation(const QString &sourceFileName,
                               const ClassDocumentation &classDocumentation,
                               const AbstractMetaClassCPtr &metaClass,
                               const AbstractMetaFunctionCPtr &func, QString *errorMessage);
    static FunctionDocumentationOpt
        queryFunctionDocumentation(const QString &sourceFileName,
                                   const ClassDocumentation &classDocumentation,
                                   const AbstractMetaClassCPtr &metaClass,
                                   const AbstractMetaFunctionCPtr &func, QString *errorMessage);
    static bool extractEnumDocumentation(const ClassDocumentation &classDocumentation,
                                         const QString &sourceFileName,
                                         AbstractMetaEnum &meta_enum);

};

#endif // QTDOCPARSER_H
