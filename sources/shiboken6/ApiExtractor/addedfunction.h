// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ADDEDFUNCTION_H
#define ADDEDFUNCTION_H

#include "modifications.h"
#include "parser/typeinfo.h"

#include <QtCore/QList>
#include <QtCore/QString>

#include <memory>

QT_FORWARD_DECLARE_CLASS(QDebug)

/// \internal
/// Struct used to store information about functions added by the typesystem.
/// This info will be used later to create a fake AbstractMetaFunction which
/// will be inserted into the right AbstractMetaClass.
struct AddedFunction
{
    using AddedFunctionPtr = std::shared_ptr<AddedFunction>;

    /// Function access types.
    enum Access {
        Protected = 0x1,
        Public =    0x2
    };

    struct Argument
    {
        TypeInfo typeInfo;
        QString name;
        QString defaultValue;
    };

    /// Creates a new AddedFunction with a signature and a return type.
    explicit AddedFunction(const QString &name, const QList<Argument> &arguments,
                           const TypeInfo &returnType);

    static AddedFunctionPtr createAddedFunction(const QString &signatureIn,
                                                const QString &returnTypeIn,
                                                QString *errorMessage);

    AddedFunction() = default;

    /// Returns the function name.
    QString name() const { return m_name; }

    /// Set the function access type.
    void setAccess(Access access) { m_access = access; }

    /// Returns the function access type.
    Access access() const { return m_access; }

    /// Returns the function return type.
    const TypeInfo &returnType() const { return m_returnType; }

    /// Returns a list of argument type infos.
    const QList<Argument> &arguments() const { return m_arguments; }

    /// Returns true if this is a constant method.
    bool isConstant() const { return m_isConst; }
    void setConstant(bool c) { m_isConst = c; };

    /// Set this method static.
    void setStatic(bool value) { m_isStatic = value; }

    /// Set this method as a classmethod.
    void setClassMethod(bool value) { m_isClassMethod = value; }

    /// Returns true if this is a static method.
    bool isStatic() const { return m_isStatic; }

    /// Returns true if this is a class method.
    bool isClassMethod() const { return m_isClassMethod; }

    bool isDeclaration() const { return m_isDeclaration; } // <declare-function>
    void setDeclaration(bool value) { m_isDeclaration = value; }

    const FunctionModificationList &modifications() const { return m_modifications; }
    FunctionModificationList &modifications() { return m_modifications; }

    const DocModificationList &docModifications() const { return m_docModifications; }
    DocModificationList &docModifications() { return m_docModifications; }
    void addDocModification(const DocModification &m) { m_docModifications.append(m); }

private:
    QString m_name;
    QList<Argument> m_arguments;
    TypeInfo m_returnType;
    FunctionModificationList m_modifications;
    DocModificationList m_docModifications;
    Access m_access = Public;
    bool m_isConst = false;
    bool m_isClassMethod = false;
    bool m_isStatic = false;
    bool m_isDeclaration = false;
};

QDebug operator<<(QDebug d, const AddedFunction::Argument &a);
QDebug operator<<(QDebug d, const AddedFunction &af);

#endif // ADDEDFUNCTION_H
