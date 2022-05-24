// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef HEADERGENERATOR_H
#define HEADERGENERATOR_H

#include "shibokengenerator.h"
#include "include.h"

#include <QtCore/QSet>

class AbstractMetaFunction;

/**
 *   The HeaderGenerator generate the declarations of C++ bindings classes.
 */
class HeaderGenerator : public ShibokenGenerator
{
public:
    OptionDescriptions options() const override { return OptionDescriptions(); }

    const char *name() const override { return "Header generator"; }

    static QString headerFileNameForContext(const GeneratorContext &context);

protected:
    QString fileNameForContext(const GeneratorContext &context) const override;
    void generateClass(TextStream &s, const GeneratorContext &classContext) override;
    bool finishGeneration() override;

private:
    void writeCopyCtor(TextStream &s, const AbstractMetaClass *metaClass) const;
    void writeFunction(TextStream &s, const AbstractMetaFunctionCPtr &func,
                       FunctionGeneration generation);
    void writeSbkTypeFunction(TextStream &s, const AbstractMetaEnum &cppEnum) const;
    static void writeSbkTypeFunction(TextStream &s, const AbstractMetaClass *cppClass) ;
    static void writeSbkTypeFunction(TextStream &s, const AbstractMetaType &metaType) ;
    void writeTypeIndexValueLine(TextStream &s, const ApiExtractorResult &api,
                                 const TypeEntry *typeEntry);
    void writeTypeIndexValueLines(TextStream &s, const ApiExtractorResult &api,
                                  const AbstractMetaClass *metaClass);
    void writeProtectedEnumSurrogate(TextStream &s, const AbstractMetaEnum &cppEnum) const;
    void writeMemberFunctionWrapper(TextStream &s,
                                    const AbstractMetaFunctionCPtr &func,
                                    const QString &postfix = {}) const;
    void writePrivateHeader(const QString &moduleHeaderDir,
                            const QString &publicIncludeShield,
                            const QSet<Include> &privateIncludes,
                            const QString &privateTypeFunctions);

    QSet<AbstractMetaFunctionCPtr> m_inheritedOverloads;
    AbstractMetaClassCList m_alternateTemplateIndexes;
};

#endif // HEADERGENERATOR_H

