// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef HEADERGENERATOR_H
#define HEADERGENERATOR_H

#include "shibokengenerator.h"
#include "include.h"

#include <QtCore/QSet>

class AbstractMetaFunction;
struct ModuleHeaderParameters;

/**
 *   The HeaderGenerator generate the declarations of C++ bindings classes.
 */
class HeaderGenerator : public ShibokenGenerator
{
public:
    OptionDescriptions options() const override { return OptionDescriptions(); }

    const char *name() const override { return "Header generator"; }

    static const char *protectedHackDefine;

protected:
    QString fileNameForContext(const GeneratorContext &context) const override;
    void generateClass(TextStream &s, const GeneratorContext &classContext) override;
    bool finishGeneration() override;

private:
    using InheritedOverloadSet = QSet<AbstractMetaFunctionCPtr>;

    void writeCopyCtor(TextStream &s, const AbstractMetaClassCPtr &metaClass) const;
    void writeFunction(TextStream &s, const AbstractMetaFunctionCPtr &func,
                       InheritedOverloadSet *inheritedOverloads,
                       FunctionGeneration generation) const;
    void writeSbkTypeFunction(TextStream &s, const AbstractMetaEnum &cppEnum) const;
    static void writeSbkTypeFunction(TextStream &s, const AbstractMetaClassCPtr &cppClass);
    static void writeSbkTypeFunction(TextStream &s, const AbstractMetaType &metaType);
    void writeTypeIndexValueLine(TextStream &s, const ApiExtractorResult &api,
                                 const TypeEntryCPtr &typeEntry);
    void writeTypeIndexValueLines(TextStream &s, const ApiExtractorResult &api,
                                  const AbstractMetaClassCPtr &metaClass);
    void writeProtectedEnumSurrogate(TextStream &s, const AbstractMetaEnum &cppEnum) const;
    void writeMemberFunctionWrapper(TextStream &s,
                                    const AbstractMetaFunctionCPtr &func,
                                    const QString &postfix = {}) const;
    void writePrivateHeader(const QString &moduleHeaderDir,
                            const QString &publicIncludeShield,
                            const ModuleHeaderParameters &parameters);
    void writeTypeFunctions(TextStream &s, const QString &typeFunctions);
    void writeWrapperClassDeclaration(TextStream &s,
                                      const QString &wrapperName,
                                      const GeneratorContext &classContext) const;
    void writeWrapperClass(TextStream &s, const QString &wrapperName, const GeneratorContext &classContext) const;
    void writeInheritedWrapperClassDeclaration(TextStream &s,
                                               const GeneratorContext &classContext) const;

    AbstractMetaClassCList m_alternateTemplateIndexes;
};

#endif // HEADERGENERATOR_H

