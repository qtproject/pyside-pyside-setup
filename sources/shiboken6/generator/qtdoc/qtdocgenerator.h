// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
#ifndef DOCGENERATOR_H
#define DOCGENERATOR_H

#include <QtCore/QStringList>
#include <QtCore/QMap>
#include <QtCore/QScopedPointer>

#include "generator.h"
#include "documentation.h"
#include "typesystem_enums.h"
#include "modifications_typedefs.h"
#include "qtxmltosphinxinterface.h"

class DocParser;

struct GeneratorDocumentation;

/**
*   The DocGenerator generates documentation from library being binded.
*/
class QtDocGenerator : public Generator, public QtXmlToSphinxDocGeneratorInterface
{
public:
    QtDocGenerator();
    ~QtDocGenerator();

    bool doSetup() override;

    const char* name() const override
    {
        return "QtDocGenerator";
    }

    OptionDescriptions options() const override;
    bool handleOption(const QString &key, const QString &value) override;

    // QtXmlToSphinxDocGeneratorInterface
    QString expandFunction(const QString &function) const override;
    QString expandClass(const QString &context,
                        const QString &name) const override;
    QString resolveContextForMethod(const QString &context,
                                    const QString &methodName) const override;
    const QLoggingCategory &loggingCategory() const override;
    QtXmlToSphinxLink resolveLink(const QtXmlToSphinxLink &) const override;

    static QString getFuncName(const AbstractMetaFunctionCPtr &cppFunc);
    static QString formatArgs(const AbstractMetaFunctionCPtr &func);

protected:
    bool shouldGenerate(const TypeEntryCPtr &) const override;
    static QString fileNameSuffix();
    QString fileNameForContext(const GeneratorContext &context) const override;
    void generateClass(TextStream &ts, const GeneratorContext &classContext) override;
    bool finishGeneration() override;

private:
    void writeEnums(TextStream &s, const AbstractMetaClass *cppClass) const;

    void writeFields(TextStream &s, const AbstractMetaClass *cppClass) const;
    static QString functionSignature(const AbstractMetaClass *cppClass,
                                     const AbstractMetaFunctionCPtr &func);
    void writeFunction(TextStream &s, const AbstractMetaClass *cppClass,
                       const AbstractMetaFunctionCPtr &func, bool indexed = true);
    void writeFunctionParametersType(TextStream &s, const AbstractMetaClass *cppClass,
                                     const AbstractMetaFunctionCPtr &func) const;
    static void writeFunctionToc(TextStream &s, const QString &title,
                                 const AbstractMetaClass *cppClass,
                                 const AbstractMetaFunctionCList &functions);
    void writeParameterType(TextStream &s, const AbstractMetaClass *cppClass,
                            const AbstractMetaArgument &arg) const;

    void writeConstructors(TextStream &s,
                           const AbstractMetaClass *cppClass,
                           const AbstractMetaFunctionCList &constructors) const;

    void writeFormattedText(TextStream &s, const QString &doc,
                            Documentation::Format format,
                            const AbstractMetaClass *metaClass = nullptr) const;
    void writeFormattedBriefText(TextStream &s, const Documentation &doc,
                                 const AbstractMetaClass *metaclass = nullptr) const;
    void writeFormattedDetailedText(TextStream &s, const Documentation &doc,
                                    const AbstractMetaClass *metaclass = nullptr) const;

    bool writeInjectDocumentation(TextStream &s, TypeSystem::DocModificationMode mode,
                                  const AbstractMetaClass *cppClass,
                                  const AbstractMetaFunctionCPtr &func);
    static void writeDocSnips(TextStream &s, const CodeSnipList &codeSnips,
                              TypeSystem::CodeSnipPosition position, TypeSystem::Language language);

    void writeModuleDocumentation();
    void writeAdditionalDocumentation() const;
    bool writeInheritanceFile();

    QString translateToPythonType(const AbstractMetaType &type, const AbstractMetaClass *cppClass) const;

    bool convertToRst(const QString &sourceFileName,
                      const QString &targetFileName,
                      const QString &context = QString(),
                      QString *errorMessage = nullptr) const;

    GeneratorDocumentation generatorDocumentation(const AbstractMetaClass *cppClass) const;

    QString m_extraSectionDir;
    QStringList m_functionList;
    QMap<QString, QStringList> m_packages;
    QScopedPointer<DocParser> m_docParser;
    QtXmlToSphinxParameters m_parameters;
    QString m_additionalDocumentationList;
    QString m_inheritanceFile;
};

#endif // DOCGENERATOR_H
