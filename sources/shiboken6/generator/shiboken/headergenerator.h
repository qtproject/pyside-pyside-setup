// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef HEADERGENERATOR_H
#define HEADERGENERATOR_H

#include "shibokengenerator.h"
#include "include.h"
#include "modifications_typedefs.h"

#include <QtCore/QList>
#include <QtCore/QSet>

struct IndexValue;
class AbstractMetaFunction;
struct ModuleHeaderParameters;

/**
 *   The HeaderGenerator generate the declarations of C++ bindings classes.
 */
class HeaderGenerator : public ShibokenGenerator
{
public:
    const char *name() const override { return "Header generator"; }

    static const char *protectedHackDefine;

protected:
    QString fileNameForContext(const GeneratorContext &context) const override;
    void generateClass(TextStream &s, const GeneratorContext &classContext) override;
    bool finishGeneration() override;

private:
    using InheritedOverloadSet = QSet<AbstractMetaFunctionCPtr>;
    using IndexValues = QList<IndexValue>;

    IndexValues collectTypeIndexes(const AbstractMetaClassCList &classList);
    IndexValues collectConverterIndexes() const;

    static void writeCopyCtor(TextStream &s, const AbstractMetaClassCPtr &metaClass);
    void writeFunction(TextStream &s,
                       const AbstractMetaFunctionCPtr &func,
                       InheritedOverloadSet *inheritedOverloads,
                       FunctionGeneration generation) const;
    static void writeSbkTypeFunction(TextStream &s, const AbstractMetaEnum &cppEnum);
    static void writeSbkTypeFunction(TextStream &s, const AbstractMetaClassCPtr &cppClass);
    static void writeSbkTypeFunction(TextStream &s, const AbstractMetaType &metaType);
    void collectTypeEntryTypeIndexes(const ApiExtractorResult &api,
                                     const TypeEntryCPtr &typeEntry,
                                     IndexValues *indexValues);
    void collectClassTypeIndexes(const ApiExtractorResult &api,
                                 const AbstractMetaClassCPtr &metaClass,
                                 IndexValues *indexValues);
    static void writeProtectedEnumSurrogate(TextStream &s, const AbstractMetaEnum &cppEnum);
    void writeMemberFunctionWrapper(TextStream &s,
                                    const AbstractMetaFunctionCPtr &func,
                                    const QString &postfix = {}) const;
    void writePrivateHeader(const QString &moduleHeaderDir,
                            const QString &publicIncludeShield,
                            const ModuleHeaderParameters &parameters);
    static void writeTypeFunctions(TextStream &s, const QString &typeFunctions);
    void writeWrapperClassDeclaration(TextStream &s,
                                      const QString &wrapperName,
                                      const GeneratorContext &classContext) const;
    void writeWrapperClass(TextStream &s, const QString &wrapperName, const GeneratorContext &classContext) const;
    void writeInheritedWrapperClassDeclaration(TextStream &s,
                                               const GeneratorContext &classContext) const;
    void writeModuleCodeSnips(TextStream &s, const CodeSnipList &codeSnips,
                              TypeSystem::CodeSnipPosition position,
                              TypeSystem::Language language) const;

    AbstractMetaClassCList m_alternateTemplateIndexes;
};

#endif // HEADERGENERATOR_H

