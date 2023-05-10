// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETABUILDER_P_H
#define ABSTRACTMETABUILDER_P_H

#include "abstractmetabuilder.h"
#include "dependency.h"
#include "parser/codemodel_fwd.h"
#include "abstractmetalang.h"
#include "abstractmetatype.h"
#include "include.h"
#include "typeparser.h"
#include "modifications_typedefs.h"
#include "typesystem_typedefs.h"

#include <QtCore/QFileInfo>
#include <QtCore/QList>
#include <QtCore/QMap>
#include <QtCore/QSet>

#include <optional>
#include <set>

class TypeDatabase;

struct RejectEntry
{
    AbstractMetaBuilder::RejectReason reason;
    QString signature;
    QString sortkey;
    QString message;
};

bool operator<(const RejectEntry &re1, const RejectEntry &re2);

class AbstractMetaBuilderPrivate
{
public:
    struct TypeClassEntry
    {
        AbstractMetaType type;
        AbstractMetaClassCPtr klass;
    };

    using TranslateTypeFlags = AbstractMetaBuilder::TranslateTypeFlags;

    Q_DISABLE_COPY(AbstractMetaBuilderPrivate)

    AbstractMetaBuilderPrivate();

    static FileModelItem buildDom(QByteArrayList arguments,
                                  bool addCompilerSupportArguments,
                                  LanguageLevel level,
                                  unsigned clangFlags);
    void traverseDom(const FileModelItem &dom, ApiExtractorFlags flags);

    void dumpLog() const;

    static AbstractMetaClassList
        classesTopologicalSorted(const AbstractMetaClassList &classList,
                                 const Dependencies &additionalDependencies = {});
    static AbstractMetaClassCList
        classesTopologicalSorted(const AbstractMetaClassCList &classList,
                                 const Dependencies &additionalDependencies = {});

    NamespaceModelItem popScope() { return m_scopes.takeLast(); }

    void pushScope(const NamespaceModelItem &item);

    NamespaceModelItem currentScope() const { return m_scopes.constLast(); }

    AbstractMetaClassPtr argumentToClass(const ArgumentModelItem &,
                                       const AbstractMetaClassCPtr &currentClass);

    void addAbstractMetaClass(const AbstractMetaClassPtr &cls, const _CodeModelItem *item);
    AbstractMetaClassPtr traverseTypeDef(const FileModelItem &dom,
                                       const TypeDefModelItem &typeDef,
                                       const AbstractMetaClassPtr &currentClass);
    void traverseTypesystemTypedefs();
    AbstractMetaClassPtr traverseClass(const FileModelItem &dom,
                                     const ClassModelItem &item,
                                     const AbstractMetaClassPtr &currentClass);
    void traverseScopeMembers(const ScopeModelItem &item,
                              const AbstractMetaClassPtr &metaClass);
    void traverseClassMembers(const ClassModelItem &scopeItem);
    void traverseUsingMembers(const AbstractMetaClassPtr &metaClass);
    void traverseNamespaceMembers(const NamespaceModelItem &scopeItem);
    bool setupInheritance(const AbstractMetaClassPtr &metaClass);
    AbstractMetaClassPtr traverseNamespace(const FileModelItem &dom,
                                         const NamespaceModelItem &item);
    std::optional<AbstractMetaEnum> traverseEnum(const EnumModelItem &item,
                                                 const AbstractMetaClassPtr &enclosing,
                                                 const QSet<QString> &enumsDeclarations);
    void traverseEnums(const ScopeModelItem &item, const AbstractMetaClassPtr &parent,
                       const QStringList &enumsDeclarations);
    AbstractMetaFunctionRawPtrList classFunctionList(const ScopeModelItem &scopeItem,
                                                     AbstractMetaClass::Attributes *constructorAttributes,
                                                     const AbstractMetaClassPtr &currentClass);
    void traverseFunctions(ScopeModelItem item, const AbstractMetaClassPtr &parent);
    static void applyFunctionModifications(AbstractMetaFunction *func);
    void traverseFields(const ScopeModelItem &item, const AbstractMetaClassPtr &parent);
    bool traverseStreamOperator(const FunctionModelItem &functionItem,
                                const AbstractMetaClassPtr &currentClass);
    void traverseOperatorFunction(const FunctionModelItem &item,
                                  const AbstractMetaClassPtr &currentClass);
    AbstractMetaFunction *traverseAddedFunctionHelper(const AddedFunctionPtr &addedFunc,
                                                      const AbstractMetaClassPtr &metaClass,
                                                      QString *errorMessage);
    bool traverseAddedGlobalFunction(const AddedFunctionPtr &addedFunc,
                                     QString *errorMessage);
    bool traverseAddedMemberFunction(const AddedFunctionPtr &addedFunc,
                                     const AbstractMetaClassPtr &metaClass,
                                     QString *errorMessage);
    void rejectFunction(const FunctionModelItem &functionItem,
                        const AbstractMetaClassPtr &currentClass,
                        AbstractMetaBuilder::RejectReason reason,
                        const QString &rejectReason);
        AbstractMetaFunction *traverseFunction(const FunctionModelItem &function,
                                           const AbstractMetaClassPtr &currentClass);
    std::optional<AbstractMetaField> traverseField(const VariableModelItem &field,
                                                   const AbstractMetaClassCPtr &cls);
    void checkFunctionModifications();
    void registerHashFunction(const FunctionModelItem &functionItem,
                              const AbstractMetaClassPtr &currentClass);
    void registerToStringCapabilityIn(const NamespaceModelItem &namespaceItem);
    void registerToStringCapability(const FunctionModelItem &functionItem,
                                    const AbstractMetaClassPtr &currentClass);

    /**
     *   A conversion operator function should not have its owner class as
     *   its return type, but unfortunately it does. This function fixes the
     *   return type of operator functions of this kind making the return type
     *   be the same as it is supposed to generate when used in C++.
     *   If the returned type is a wrapped C++ class, this method also adds the
     *   conversion operator to the collection of external conversions of the
     *   said class.
     *   \param metaFunction conversion operator function to be fixed.
     */
    static void fixReturnTypeOfConversionOperator(AbstractMetaFunction *metaFunction);

    void parseQ_Properties(const AbstractMetaClassPtr &metaClass,
                           const QStringList &declarations);
    void setupEquals(const AbstractMetaClassPtr &metaClass);
    void setupComparable(const AbstractMetaClassPtr &metaClass);
    void setupExternalConversion(const AbstractMetaClassCPtr &cls);

    static bool isQualifiedCppIdentifier(QStringView e);
    QString fixDefaultValue(QString expr, const AbstractMetaType &type,
                            const AbstractMetaClassCPtr &) const;
    QString fixSimpleDefaultValue(QStringView expr,
                                  const AbstractMetaClassCPtr &klass) const;

    QString fixEnumDefault(const AbstractMetaType &type, const QString &expr,
                           const AbstractMetaClassCPtr &) const;
    /// Qualify a static field name for default value expressions
    static QString qualifyStaticField(const AbstractMetaClassCPtr &c, QStringView field);

    std::optional<AbstractMetaType>
        translateType(const TypeInfo &type, const AbstractMetaClassCPtr &currentClass,
                      TranslateTypeFlags flags = {}, QString *errorMessage = nullptr);
    static std::optional<AbstractMetaType>
        translateTypeStatic(const TypeInfo &type, const AbstractMetaClassCPtr &current,
                            AbstractMetaBuilderPrivate *d = nullptr, TranslateTypeFlags flags = {},
                            QString *errorMessageIn = nullptr);
    static TypeEntryCList findTypeEntriesHelper(const QString &qualifiedName, const QString &name,
                                                TranslateTypeFlags flags = {},
                                                const AbstractMetaClassCPtr &currentClass = {},
                                                AbstractMetaBuilderPrivate *d = nullptr);
    static TypeEntryCList findTypeEntries(const QString &qualifiedName, const QString &name,
                                          TranslateTypeFlags flags = {},
                                          const AbstractMetaClassCPtr &currentClass = {},
                                          AbstractMetaBuilderPrivate *d = nullptr,
                                          QString *errorMessage = nullptr);

    qint64 findOutValueFromString(const QString &stringValue, bool &ok);

    AbstractMetaClassPtr findTemplateClass(const QString& name, const AbstractMetaClassCPtr &context,
                                         TypeInfo *info = nullptr,
                                         ComplexTypeEntryPtr *baseContainerType = nullptr) const;
    AbstractMetaClassCList getBaseClasses(const AbstractMetaClassCPtr &metaClass) const;

    static bool inheritTemplate(const AbstractMetaClassPtr &subclass,
                                const AbstractMetaClassCPtr &templateClass,
                                const TypeInfo &info);
    static bool inheritTemplate(const AbstractMetaClassPtr &subclass,
                                const AbstractMetaClassCPtr &templateClass,
                                const AbstractMetaTypeList &templateTypes,
                                InheritTemplateFlags flags = {});

    static AbstractMetaFunctionPtr
        inheritTemplateFunction(const AbstractMetaFunctionCPtr &function,
                                const AbstractMetaTypeList &templateTypes);

    static AbstractMetaFunctionPtr
        inheritTemplateMember(const AbstractMetaFunctionCPtr &function,
                              const AbstractMetaTypeList &templateTypes,
                              const AbstractMetaClassCPtr &templateClass,
                              const AbstractMetaClassPtr &subclass);

    static void inheritTemplateFunctions(const AbstractMetaClassPtr &subclass);
    static std::optional<AbstractMetaType>
        inheritTemplateType(const AbstractMetaTypeList &templateTypes,
                            const AbstractMetaType &metaType);

    static bool isQObject(const FileModelItem &dom, const QString &qualifiedName);
    static bool isEnum(const FileModelItem &dom, const QStringList &qualifiedName);

    void sortLists();
    void setInclude(const TypeEntryPtr &te, const QString &path) const;
    static void fixArgumentNames(AbstractMetaFunction *func, const FunctionModificationList &mods);

    void fillAddedFunctions(const AbstractMetaClassPtr &metaClass);
    AbstractMetaClassCPtr resolveTypeSystemTypeDef(const AbstractMetaType &t) const;

    void fixSmartPointers();

    AbstractMetaBuilder *q;
    AbstractMetaClassList m_metaClasses;
    AbstractMetaClassList m_templates;
    AbstractMetaClassList m_smartPointers;
    QHash<const _CodeModelItem *, AbstractMetaClassPtr > m_itemToClass;
    QHash<AbstractMetaClassCPtr, const _CodeModelItem *> m_classToItem;
    AbstractMetaFunctionCList m_globalFunctions;
    AbstractMetaEnumList m_globalEnums;

    using RejectSet = std::set<RejectEntry>;

    RejectSet m_rejectedClasses;
    RejectSet m_rejectedEnums;
    RejectSet m_rejectedFunctions;
    RejectSet m_rejectedFields;

    QHash<TypeEntryCPtr, AbstractMetaEnum> m_enums;

    QList<NamespaceModelItem> m_scopes;

    QString m_logDirectory;
    QFileInfoList m_globalHeaders;
    QStringList m_headerPaths;
    mutable QHash<QString, Include> m_resolveIncludeHash;
    QList<TypeClassEntry> m_typeSystemTypeDefs; // look up metatype->class for type system typedefs
    ApiExtractorFlags m_apiExtractorFlags;
    bool m_skipDeprecated = false;
    static bool m_useGlobalHeader;
    static bool m_codeModelTestMode;
};

#endif // ABSTRACTMETBUILDER_P_H
