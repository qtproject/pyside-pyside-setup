// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef COMPLEXTYPEENTRY_H
#define COMPLEXTYPEENTRY_H

#include "configurabletypeentry.h"
#include "typesystem_enums.h"
#include "modifications_typedefs.h"
#include "pymethoddefentry.h"

#include <QtCore/QSet>

class ComplexTypeEntryPrivate;

struct TypeSystemPyMethodDefEntry : public PyMethodDefEntry
{
    QStringList signatures;
};

struct TypeSystemProperty
{
    bool isValid() const { return !name.isEmpty() && !read.isEmpty() && !type.isEmpty(); }

    QString type;
    QString name;
    QString read;
    QString write;
    QString reset;
    QString designable;
    QString notify; // Q_PROPERTY/C++ only
    // Indicates whether actual code is generated instead of relying on libpyside.
    bool generateGetSetDef = false;
};

class ComplexTypeEntry : public ConfigurableTypeEntry
{
public:
    enum TypeFlag {
        DisableWrapper     = 0x1,
        Deprecated         = 0x4,
        ForceAbstract      = 0x8,
        // Indicates that the instances are used to create hierarchies
        // like widgets; parent ownership heuristics are enabled for them.
        ParentManagement   = 0x10
    };
    Q_DECLARE_FLAGS(TypeFlags, TypeFlag)

    enum CopyableFlag {
        CopyableSet,
        NonCopyableSet,
        Unknown
    };

    explicit ComplexTypeEntry(const QString &entryName, Type t, const QVersionNumber &vr,
                              const TypeEntryCPtr &parent);

    bool isComplex() const override;

    TypeFlags typeFlags() const;
    void setTypeFlags(TypeFlags flags);

    // Override command line options to generate nb_bool from
    // operator bool or method isNull().
    TypeSystem::BoolCast operatorBoolMode() const;
    void setOperatorBoolMode(TypeSystem::BoolCast b);
    TypeSystem::BoolCast isNullMode() const;
    void setIsNullMode(TypeSystem::BoolCast b);

    FunctionModificationList functionModifications() const;
    void setFunctionModifications(const FunctionModificationList &functionModifications);
    void addFunctionModification(const FunctionModification &functionModification);
    FunctionModificationList functionModifications(const QStringList &signatures) const;

    const CodeSnipList &codeSnips() const;
    CodeSnipList &codeSnips();
    void setCodeSnips(const CodeSnipList &codeSnips);
    void addCodeSnip(const CodeSnip &codeSnip);

    void setDocModification(const DocModificationList& docMods);
    /// Class documentation modifications
    DocModificationList docModifications() const;
    /// Function documentation modifications (matching signature)
    DocModificationList functionDocModifications() const;

    /// Extra includes for function arguments determined by the meta builder.
    const IncludeList &argumentIncludes() const;
    void addArgumentInclude(const Include &newInclude);

    AddedFunctionList addedFunctions() const;
    void setAddedFunctions(const AddedFunctionList &addedFunctions);
    void addNewFunction(const AddedFunctionPtr &addedFunction);

    const QList<TypeSystemPyMethodDefEntry> &addedPyMethodDefEntrys() const;
    void addPyMethodDef(const TypeSystemPyMethodDefEntry &p);

    // Functions specified in the "generate-functions" attribute
    const QSet<QString> &generateFunctions() const;
    void setGenerateFunctions(const QSet<QString> &f);

    void setFieldModifications(const FieldModificationList &mods);
    FieldModificationList fieldModifications() const;

    const QList<TypeSystemProperty> &properties() const;
    void addProperty(const TypeSystemProperty &p);

    QString defaultSuperclass() const;
    void setDefaultSuperclass(const QString &sc);

    QString qualifiedCppName() const override;

    void setIsPolymorphicBase(bool on);
    bool isPolymorphicBase() const;

    void setPolymorphicIdValue(const QString &value);
    QString polymorphicIdValue() const;

    QString polymorphicNameFunction() const;
    void setPolymorphicNameFunction(const QString &n);

    QString targetType() const;
    void setTargetType(const QString &code);

    bool isGenericClass() const;
    void setGenericClass(bool isGeneric);

    bool deleteInMainThread() const;
    void setDeleteInMainThread(bool d);

    CopyableFlag copyable() const;
    void setCopyable(CopyableFlag flag);

    TypeSystem::QtMetaTypeRegistration qtMetaTypeRegistration() const;
    void setQtMetaTypeRegistration(TypeSystem::QtMetaTypeRegistration r);

    QString hashFunction() const;
    void setHashFunction(const QString &hashFunction);

    void setBaseContainerType(const ComplexTypeEntryCPtr &baseContainer);

    ComplexTypeEntryCPtr baseContainerType() const;

    TypeSystem::ExceptionHandling exceptionHandling() const;
    void setExceptionHandling(TypeSystem::ExceptionHandling e);

    TypeSystem::AllowThread allowThread() const;
    void setAllowThread(TypeSystem::AllowThread allowThread);

    QString defaultConstructor() const;
    void setDefaultConstructor(const QString& defaultConstructor);
    bool hasDefaultConstructor() const;

    TypeEntry *clone() const override;

    void useAsTypedef(const ComplexTypeEntryCPtr &source);

    TypeSystem::SnakeCase snakeCase() const;
    void setSnakeCase(TypeSystem::SnakeCase sc);

    // Determined by AbstractMetaBuilder from the code model.
    bool isValueTypeWithCopyConstructorOnly() const;
    void setValueTypeWithCopyConstructorOnly(bool v);

    // FIXME PYSIDE 7: Remove this
    static bool isParentManagementEnabled();
    static void setParentManagementEnabled(bool e);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &debug) const override;
#endif
protected:
    explicit ComplexTypeEntry(ComplexTypeEntryPrivate *d);
};

Q_DECLARE_OPERATORS_FOR_FLAGS(ComplexTypeEntry::TypeFlags)

#endif // COMPLEXTYPEENTRY_H
