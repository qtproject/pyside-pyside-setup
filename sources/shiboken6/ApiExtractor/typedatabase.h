// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPEDATABASE_H
#define TYPEDATABASE_H

#include "include.h"
#include "modifications_typedefs.h"
#include "typedatabase_typedefs.h"

#include <QtCore/QRegularExpression>
#include <QtCore/QStringList>
#include <QtCore/QVersionNumber>

#include <memory>

QT_FORWARD_DECLARE_CLASS(QIODevice)

struct TypeDatabasePrivate;
struct TypeDatabaseParserContext;

QT_FORWARD_DECLARE_CLASS(QDebug)

int getMaxTypeIndex();

struct VersionRange
{
    bool isNull() const
    {
        return since.majorVersion() == 0 && since.minorVersion() == 0
            && until.majorVersion() == 9999 && until.minorVersion() == 9999;
    }

    QVersionNumber since{0, 0};
    QVersionNumber until{9999, 9999};
};

struct TypeRejection
{
    enum MatchType
    {
        ExcludeClass,                // Match className only
        Function,                    // Match className and function name
        Field,                       // Match className and field name
        Enum,                        // Match className and enum name
        ArgumentType,                // Match className and argument type
        ReturnType                   // Match className and return type
    };

    QRegularExpression className;
    QRegularExpression pattern;
    MatchType matchType;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const TypeRejection &r);
#endif

class TypeDatabase
{
    TypeDatabase();
    Q_DISABLE_COPY(TypeDatabase)
public:
    ~TypeDatabase();

    /**
    * Return the type system instance.
    * \param newInstance This parameter is useful just for unit testing, because singletons causes
    *                    too many side effects on unit testing.
    */
    static TypeDatabase *instance(bool newInstance = false);

    static QString normalizedSignature(const QString &signature);
    static QString normalizedAddedFunctionSignature(const QString &signature);

    QStringList requiredTargetImports() const;

    void addRequiredTargetImport(const QString &moduleName);

    void addTypesystemPath(const QString &typesystem_paths);

    void setTypesystemKeywords(const QStringList &keywords);
    QStringList typesystemKeywords() const;

    IncludeList extraIncludes(const QString &className) const;

    const QStringList &systemIncludes() const;
    void addSystemInclude(const QString &name);

    void addInlineNamespaceLookups(const NamespaceTypeEntryCPtr &n);

    PrimitiveTypeEntryPtr findPrimitiveType(const QString &name) const;
    ComplexTypeEntryPtr findComplexType(const QString &name) const;
    ObjectTypeEntryPtr findObjectType(const QString &name) const;
    NamespaceTypeEntryList findNamespaceTypes(const QString &name) const;
    NamespaceTypeEntryPtr findNamespaceType(const QString &name, const QString &fileName = QString()) const;
    ContainerTypeEntryPtr findContainerType(const QString &name) const;
    FunctionTypeEntryPtr findFunctionType(const QString &name) const;
    TypeSystemTypeEntryCPtr findTypeSystemType(const QString &name) const;
    TypeSystemTypeEntryCPtr defaultTypeSystemType() const;
    QString loadedTypeSystemNames() const;
    QString defaultPackageName() const;

    TypeEntryPtr findType(const QString &name) const;
    TypeEntryCList findTypes(const QString &name) const;
    TypeEntryCList findCppTypes(const QString &name) const;

    const TypeEntryMultiMap &entries() const;
    const TypedefEntryMap  &typedefEntries() const;

    PrimitiveTypeEntryCList primitiveTypes() const;

    ContainerTypeEntryCList containerTypes() const;

    SmartPointerTypeEntryList smartPointerTypes() const;

    void addRejection(const TypeRejection &);
    bool isClassRejected(const QString &className, QString *reason = nullptr) const;
    bool isFunctionRejected(const QString &className, const QString &functionName,
                            QString *reason = nullptr) const;
    bool isFieldRejected(const QString &className, const QString &fieldName,
                         QString *reason = nullptr) const;
    bool isEnumRejected(const QString &className, const QString &enumName,
                        QString *reason = nullptr) const;
    bool isArgumentTypeRejected(const QString &className, const QString &typeName,
                                QString *reason = nullptr) const;
    bool isReturnTypeRejected(const QString &className, const QString &typeName,
                              QString *reason = nullptr) const;

    bool addType(const TypeEntryPtr &e, QString *errorMessage = nullptr);
    ConstantValueTypeEntryPtr addConstantValueTypeEntry(const QString &value,
                                                      const TypeEntryCPtr &parent);
    void addTypeSystemType(const TypeSystemTypeEntryCPtr &e);

    static ComplexTypeEntryPtr
        initializeTypeDefEntry(const TypedefEntryPtr &typedefEntry,
                               const ComplexTypeEntryCPtr &source);

    FlagsTypeEntryPtr findFlagsType(const QString &name) const;
    void addFlagsType(FlagsTypeEntryPtr fte);

    TemplateEntryPtr findTemplate(const QString &name) const;

    void addTemplate(const TemplateEntryPtr &t);
    void addTemplate(const QString &name, const QString &code);

    AddedFunctionList globalUserFunctions() const;

    void addGlobalUserFunctions(const AddedFunctionList &functions);

    AddedFunctionList findGlobalUserFunctions(const QString &name) const;

    void addGlobalUserFunctionModifications(const FunctionModificationList &functionModifications);

    FunctionModificationList
        globalFunctionModifications(const QStringList &signatures) const;

    void setSuppressWarnings(bool on);

    bool addSuppressedWarning(const QString &warning, QString *errorMessage);

    bool isSuppressedWarning(QStringView s) const;

    static QString globalNamespaceClassName(const TypeEntryCPtr &te);

    // Top level file parsing
    bool parseFile(const QString &filename, bool generate = true);
    bool parseFile(const std::shared_ptr<TypeDatabaseParserContext> &context,
                   const QString &filename, const QString &currentPath, bool generate);

    // Top level QIODevice parsing for tests.
    bool parseFile(QIODevice *device, bool generate = true);
    bool parseFile(const std::shared_ptr<TypeDatabaseParserContext> &context,
                   QIODevice *device, bool generate = true);

    static bool setApiVersion(const QString &package, const QString &version);
    static void clearApiVersions();

    static bool checkApiVersion(const QString &package, const VersionRange &vr);

    bool hasDroppedTypeEntries() const;

    bool shouldDropTypeEntry(const QString &fullTypeName) const;

    void setDropTypeEntries(QStringList dropTypeEntries);

    QString modifiedTypesystemFilepath(const QString &tsFile, const QString &currentPath = QString()) const;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const;
#endif
    void formatBuiltinTypes(QDebug debug) const;

private:
    TypeDatabasePrivate *d;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const TypeEntryCPtr &te);
QDebug operator<<(QDebug d, const TypeEntry *te);
QDebug operator<<(QDebug d, const TypeDatabase &db);
#endif
#endif // TYPEDATABASE_H
