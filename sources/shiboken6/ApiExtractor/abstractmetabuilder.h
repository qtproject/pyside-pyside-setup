// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETABUILDER_H
#define ABSTRACTMETABUILDER_H

#include "abstractmetalang_typedefs.h"
#include "apiextractorflags.h"
#include "header_paths.h"
#include "typesystem_enums.h"
#include "typesystem_typedefs.h"

#include "clangparser/compilersupport.h"

#include <QtCore/QFileInfoList>

#include <optional>

QT_FORWARD_DECLARE_CLASS(QIODevice)

class AbstractMetaBuilderPrivate;
class AbstractMetaClass;
class AbstractMetaType;
class AbstractMetaEnumValue;
class ComplexTypeEntry;
class TypeInfo;
class TypeEntry;

class AbstractMetaBuilder
{
public:
    enum RejectReason {
        NotInTypeSystem,
        GenerationDisabled,
        RedefinedToNotClass,
        UnmatchedArgumentType,
        UnmatchedReturnType,
        ApiIncompatible,
        Deprecated,
        NoReason
    };

    AbstractMetaBuilder();
    virtual ~AbstractMetaBuilder();

    const AbstractMetaClassList &classes() const;
    AbstractMetaClassList takeClasses();
    const AbstractMetaClassList &templates() const;
    AbstractMetaClassList takeTemplates();
    const AbstractMetaClassList &smartPointers() const;
    AbstractMetaClassList takeSmartPointers();
    const AbstractMetaFunctionCList &globalFunctions() const;
    const AbstractMetaEnumList &globalEnums() const;
    const QHash<TypeEntryCPtr, AbstractMetaEnum> &typeEntryToEnumsHash() const;

    bool build(const QByteArrayList &arguments,
               ApiExtractorFlags apiExtractorFlags = {},
               bool addCompilerSupportArguments = true,
               LanguageLevel level = LanguageLevel::Default,
               unsigned clangFlags = 0);
    void setLogDirectory(const QString& logDir);

    /**
    *   AbstractMetaBuilder should know what's the global header being used,
    *   so any class declared under this header wont have the include file
    *   filled.
    */
    void setGlobalHeaders(const QFileInfoList& globalHeaders);
    void setHeaderPaths(const HeaderPaths &h);

    static void setUseGlobalHeader(bool h);

    void setSkipDeprecated(bool value);

    void setApiExtractorFlags(ApiExtractorFlags flags);

    enum TranslateTypeFlag {
        DontResolveType = 0x1,
        TemplateArgument = 0x2,
        NoClassScopeLookup = 0x4
    };
    Q_DECLARE_FLAGS(TranslateTypeFlags, TranslateTypeFlag);

    static std::optional<AbstractMetaType>
        translateType(const TypeInfo &_typei, const AbstractMetaClassPtr &currentClass = {},
                      TranslateTypeFlags flags = {}, QString *errorMessage = nullptr);
    static std::optional<AbstractMetaType>
        translateType(const QString &t, const AbstractMetaClassPtr &currentClass = {},
                      TranslateTypeFlags flags = {}, QString *errorMessage = nullptr);

    /// Performs a template specialization of the function.
    /// \param function Function
    /// \param templateTypes Instantiation types
    /// \return Specialized copy of the function
    static AbstractMetaFunctionPtr
        inheritTemplateFunction(const AbstractMetaFunctionCPtr &function,
                                const AbstractMetaTypeList &templateTypes);

    static AbstractMetaClassPtr
        inheritTemplateClass(const ComplexTypeEntryPtr &te,
                             const AbstractMetaClassCPtr &templateClass,
                             const AbstractMetaTypeList &templateTypes,
                             InheritTemplateFlags flags = {});

    /// Performs a template specialization of the member function.
    /// \param function Member function
    /// \param templateTypes Instantiation types
    /// \param templateClass Template class
    /// \param subclass Specialized class
    /// \return Specialized copy of the function
    static AbstractMetaFunctionPtr
        inheritTemplateMember(const AbstractMetaFunctionCPtr &function,
                              const AbstractMetaTypeList &templateTypes,
                              const AbstractMetaClassCPtr &templateClass,
                              const AbstractMetaClassPtr &subclass);

    static QString getSnakeCaseName(const QString &name);
    // Names under which an item will be registered to Python depending on snakeCase
    static QStringList definitionNames(const QString &name,
                                       TypeSystem::SnakeCase snakeCase);

    static QString resolveScopePrefix(const AbstractMetaClassCPtr &scope,
                                      QStringView value);

    static bool dontFixDefaultValue(QStringView expr);

    // For testing purposes
    QString fixDefaultValue(const QString &expr, const AbstractMetaType &type,
                            const AbstractMetaClassCPtr &) const;
    QString fixEnumDefault(const AbstractMetaType &type, const QString &expr,
                           const AbstractMetaClassCPtr & = {}) const;

    static void setCodeModelTestMode(bool b);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const;
#endif

private:
    friend class AbstractMetaBuilderPrivate;
    AbstractMetaBuilderPrivate *d;
};

Q_DECLARE_OPERATORS_FOR_FLAGS(AbstractMetaBuilder::TranslateTypeFlags);

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const AbstractMetaBuilder &ab);
#endif

#endif // ABSTRACTMETBUILDER_H
