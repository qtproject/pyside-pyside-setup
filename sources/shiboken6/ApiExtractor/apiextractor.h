// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef APIEXTRACTOR_H
#define APIEXTRACTOR_H

#include "abstractmetalang_typedefs.h"
#include "apiextractorflags.h"
#include "header_paths.h"
#include "clangparser/compilersupport.h"
#include "typesystem_typedefs.h"

#include <QtCore/QFileInfoList>
#include <QtCore/QStringList>

#include <optional>

class ApiExtractorResult;
class AbstractMetaClass;
class AbstractMetaEnum;
class AbstractMetaFunction;
class ComplexTypeEntry;
struct OptionDescription;
class OptionsParser;

QT_BEGIN_NAMESPACE
class QDebug;
class QIODevice;
QT_END_NAMESPACE

struct ApiExtractorPrivate;

class ApiExtractor
{
public:
    Q_DISABLE_COPY_MOVE(ApiExtractor)

    ApiExtractor();
    ~ApiExtractor();

    static QList<OptionDescription> options();
    std::shared_ptr<OptionsParser> createOptionsParser();

    void setTypeSystem(const QString& typeSystemFileName);
    QString typeSystem() const;
    void setCppFileNames(const QFileInfoList &cppFileNames);
    QFileInfoList cppFileNames() const;
    HeaderPaths includePaths() const;
    void setLogDirectory(const QString& logDir);
    LanguageLevel languageLevel() const;
    QStringList clangOptions() const;

    const AbstractMetaEnumList &globalEnums() const;
    const AbstractMetaFunctionCList &globalFunctions() const;
    const AbstractMetaClassList &classes() const;
    const AbstractMetaClassList &smartPointers() const;

    std::optional<ApiExtractorResult> run(ApiExtractorFlags flags);

    /// Forwards to AbstractMetaBuilder::inheritTemplateFunction()
    static AbstractMetaFunctionPtr
        inheritTemplateFunction(const AbstractMetaFunctionCPtr &function,
                                const AbstractMetaTypeList &templateTypes);

    /// Forwards to AbstractMetaBuilder::inheritTemplateMember()
    static AbstractMetaFunctionPtr
        inheritTemplateMember(const AbstractMetaFunctionCPtr &function,
                              const AbstractMetaTypeList &templateTypes,
                              const AbstractMetaClassCPtr &templateClass,
                              const AbstractMetaClassPtr &subclass);

    /// Forwards to AbstractMetaBuilder::inheritTemplateClass()
    static AbstractMetaClassPtr
        inheritTemplateClass(const ComplexTypeEntryPtr &te,
                             const AbstractMetaClassCPtr &templateClass,
                             const AbstractMetaTypeList &templateTypes);

private:
    ApiExtractorPrivate *d;

#ifndef QT_NO_DEBUG_STREAM
    friend QDebug operator<<(QDebug d, const ApiExtractor &ae);
#endif
};

#endif // APIEXTRACTOR_H

