/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef COMPLEXTYPEENTRY_H
#define COMPLEXTYPEENTRY_H

#include "typesystem.h"

#include <QtCore/QSet>

class ComplexTypeEntryPrivate;

struct TypeSystemProperty
{
    bool isValid() const { return !name.isEmpty() && !read.isEmpty() && !type.isEmpty(); }

    QString type;
    QString name;
    QString read;
    QString write;
    QString reset;
    QString designable;
    // Indicates whether actual code is generated instead of relying on libpyside.
    bool generateGetSetDef = false;
};

class ComplexTypeEntry : public TypeEntry
{
public:
    enum TypeFlag {
        DisableWrapper     = 0x1,
        Deprecated         = 0x4,
        ForceAbstract      = 0x8
    };
    Q_DECLARE_FLAGS(TypeFlags, TypeFlag)

    enum CopyableFlag {
        CopyableSet,
        NonCopyableSet,
        Unknown
    };

    explicit ComplexTypeEntry(const QString &entryName, Type t, const QVersionNumber &vr,
                              const TypeEntry *parent);

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
    FunctionModificationList functionModifications(const QString &signature) const;

    AddedFunctionList addedFunctions() const;
    void setAddedFunctions(const AddedFunctionList &addedFunctions);
    void addNewFunction(const AddedFunctionPtr &addedFunction);

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

    void setBaseContainerType(const ComplexTypeEntry *baseContainer);

    const ComplexTypeEntry *baseContainerType() const;

    TypeSystem::ExceptionHandling exceptionHandling() const;
    void setExceptionHandling(TypeSystem::ExceptionHandling e);

    TypeSystem::AllowThread allowThread() const;
    void setAllowThread(TypeSystem::AllowThread allowThread);

    QString defaultConstructor() const;
    void setDefaultConstructor(const QString& defaultConstructor);
    bool hasDefaultConstructor() const;

    TypeEntry *clone() const override;

    void useAsTypedef(const ComplexTypeEntry *source);

    TypeSystem::SnakeCase snakeCase() const;
    void setSnakeCase(TypeSystem::SnakeCase sc);

    // Determined by AbstractMetaBuilder from the code model.
    bool isValueTypeWithCopyConstructorOnly() const;
    void setValueTypeWithCopyConstructorOnly(bool v);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &debug) const override;
#endif
protected:
    explicit ComplexTypeEntry(ComplexTypeEntryPrivate *d);
};

Q_DECLARE_OPERATORS_FOR_FLAGS(ComplexTypeEntry::TypeFlags)

#endif // COMPLEXTYPEENTRY_H
