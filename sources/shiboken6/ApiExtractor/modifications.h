// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef MODIFICATIONS_H
#define MODIFICATIONS_H

#include "typesystem_enums.h"
#include "modifications_typedefs.h"

#include <QtCore/QList>
#include <QtCore/QSharedDataPointer>
#include <QtCore/QString>

class ArgumentModificationData;
class CodeSnip;
class FunctionModificationData;
class ModificationData;
class FieldModificationData;

QT_BEGIN_NAMESPACE
class QDebug;
QT_END_NAMESPACE

struct ReferenceCount
{
    enum Action { // 0x01 - 0xff
        Add         = 0x01,
        AddAll      = 0x02,
        Remove      = 0x04,
        Set         = 0x08,
        Ignore      = 0x10,

        ActionsMask = 0xff,

        Padding     = 0xffffffff
    };

    QString varName;
    Action action;
};

struct ArgumentOwner
{
    enum Action {
        Invalid     = 0x00,
        Add         = 0x01,
        Remove      = 0x02
    };
    enum {
        InvalidIndex = -2,
        ThisIndex = -1,
        ReturnIndex = 0,
        FirstArgumentIndex = 1
    };

    Action action = Invalid;
    int index = InvalidIndex;
};

class ArgumentModification
{
public:
    ArgumentModification();
    explicit ArgumentModification(int idx);
    ArgumentModification(const ArgumentModification &);
    ArgumentModification &operator=(const ArgumentModification &);
    ArgumentModification(ArgumentModification &&);
    ArgumentModification &operator=(ArgumentModification &&);
    ~ArgumentModification();

    // Reference count flags for this argument
    const QList<ReferenceCount> &referenceCounts() const;
    void addReferenceCount(const ReferenceCount &value);

    // The text given for the new type of the argument
    const QString &modifiedType() const;
    void setModifiedType(const QString &value);
    bool isTypeModified() const;

    QString pyiType() const;
    void setPyiType(const QString &value);

     // The text of the new default expression of the argument
    QString replacedDefaultExpression() const;
    void setReplacedDefaultExpression(const QString &value);

    // The new definition of ownership for a specific argument

    TypeSystem::Ownership targetOwnerShip() const;
    void setTargetOwnerShip(TypeSystem::Ownership o);
    TypeSystem::Ownership nativeOwnership() const;
    void setNativeOwnership(TypeSystem::Ownership o);

    // Different conversion rules
    const QList<CodeSnip> &conversionRules() const;
    QList<CodeSnip> &conversionRules();

    // QObject parent(owner) of this argument
    ArgumentOwner owner() const;
    void setOwner(const ArgumentOwner &value);

    // New name
    QString renamedToName() const;
    void setRenamedToName(const QString &value);

    int index() const;
    void setIndex(int value);

    bool removedDefaultExpression() const;
    void setRemovedDefaultExpression(const uint &value);

    bool isRemoved() const;
    void setRemoved(bool value);

    bool noNullPointers() const;
    void setNoNullPointers(bool value);

    bool resetAfterUse() const;
    void setResetAfterUse(bool value);

    // consider "int*" to be "int[]"
    bool isArray() const;
    void setArray(bool value);

private:
    QSharedDataPointer<ArgumentModificationData> d;
};

class FunctionModification
{
public:
    using AllowThread = TypeSystem::AllowThread;

    FunctionModification();
    FunctionModification(const FunctionModification &);
    FunctionModification &operator=(const FunctionModification &);
    FunctionModification(FunctionModification &&);
    FunctionModification &operator=(FunctionModification &&);
    ~FunctionModification();

    enum ModifierFlag {
        Private =               0x0001,
        Protected =             0x0002,
        Public =                0x0003,
        Friendly =              0x0004,
        AccessModifierMask =    0x000f,

        Final =                 0x0010,
        NonFinal =              0x0020,
        FinalMask =             Final | NonFinal,

        Readable =              0x0100,
        Writable =              0x0200,

        CodeInjection =         0x1000,
        Rename =                0x2000,
        Deprecated =            0x4000,
        ReplaceExpression =     0x8000
    };

    Q_DECLARE_FLAGS(Modifiers, ModifierFlag);

    QString renamedToName() const;
    void setRenamedToName(const QString &value);

    Modifiers modifiers() const;
    void setModifiers(Modifiers m);
    void setModifierFlag(ModifierFlag f);
    void clearModifierFlag(ModifierFlag f);
    bool isRemoved() const;
    void setRemoved(bool r);

    bool isAccessModifier() const
    {
        return (modifiers() & AccessModifierMask) != 0;
    }
    Modifiers accessModifier() const
    {
        return modifiers() & AccessModifierMask;
    }
    bool isPrivate() const
    {
        return accessModifier() == Private;
    }
    bool isProtected() const
    {
        return accessModifier() == Protected;
    }
    bool isPublic() const
    {
        return accessModifier() == Public;
    }
    bool isFriendly() const
    {
        return accessModifier() == Friendly;
    }
    bool isFinal() const
    {
        return modifiers().testFlag(Final);
    }
    bool isNonFinal() const
    {
        return modifiers().testFlag(NonFinal);
    }
    QString accessModifierString() const;

    bool isDeprecated() const
    {
        return modifiers().testFlag(Deprecated);
    }

    bool isRenameModifier() const
    {
        return modifiers().testFlag(Rename);
    }

    bool isRemoveModifier() const { return isRemoved(); }



    bool isCodeInjection() const
    {
        return modifiers().testFlag(CodeInjection);
    }
    void setIsThread(bool flag);
    bool isThread() const;

    AllowThread allowThread() const;
    void setAllowThread(AllowThread allow);

    bool matches(const QStringList &functionSignatures) const;

    bool setSignature(const QString &s, QString *errorMessage =  nullptr);
    QString signature() const;

    void setOriginalSignature(const QString &s);
    QString originalSignature() const;

    TypeSystem::ExceptionHandling exceptionHandling() const;
    void setExceptionHandling(TypeSystem::ExceptionHandling e);

    int overloadNumber() const;
    void setOverloadNumber(int overloadNumber);

    const QList<CodeSnip> &snips() const;
    QList<CodeSnip> &snips();
    void appendSnip(const CodeSnip &snip);
    void setSnips(const QList<CodeSnip> &snips);

    const QList<ArgumentModification> &argument_mods() const;
    QList<ArgumentModification> &argument_mods();
    void setArgument_mods(const QList<ArgumentModification> &argument_mods);

    TypeSystem::SnakeCase snakeCase() const;
    void setSnakeCase(TypeSystem::SnakeCase s);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const;
#endif

private:
    QSharedDataPointer<FunctionModificationData> d;
};

Q_DECLARE_OPERATORS_FOR_FLAGS(FunctionModification::Modifiers)

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const ReferenceCount &);
QDebug operator<<(QDebug d, const CodeSnip &s);
QDebug operator<<(QDebug d, const ArgumentOwner &a);
QDebug operator<<(QDebug d, const ArgumentModification &a);
QDebug operator<<(QDebug d, const FunctionModification &fm);
#endif

class FieldModification
{
public:
    FieldModification();
    FieldModification(const FieldModification &);
    FieldModification &operator=(const FieldModification &);
    FieldModification(FieldModification &&);
    FieldModification &operator=(FieldModification &&);
    ~FieldModification();

    QString name() const;
    void setName(const QString &value);

    bool isRenameModifier() const;
    QString renamedToName() const;
    void setRenamedToName(const QString &value);

    bool isReadable() const;
    void setReadable(bool e);

    bool isWritable() const;
    void setWritable(bool e);

    bool isRemoved() const;
    void setRemoved(bool r);

    bool isOpaqueContainer() const;
    void setOpaqueContainer(bool r);

    TypeSystem::SnakeCase snakeCase() const;
    void setSnakeCase(TypeSystem::SnakeCase s);

private:
    QSharedDataPointer<FieldModificationData> d;
};

class DocModification
{
public:
    DocModification() = default;
    explicit DocModification(const QString& xpath, const QString& signature);
    explicit DocModification(TypeSystem::DocModificationMode mode, const QString& signature);

    void setCode(const QString& code);
    void setCode(QStringView code) { setCode(code.toString()); }

    QString code() const
    {
        return m_code;
    }
    QString xpath() const
    {
        return m_xpath;
    }
    QString signature() const
    {
        return m_signature;
    }
    TypeSystem::DocModificationMode mode() const
    {
        return m_mode;
    }

    TypeSystem::Language  format() const { return m_format; }
    void setFormat(TypeSystem::Language f) { m_format = f; }

private:
    QString m_code;
    QString m_xpath;
    QString m_signature;
    TypeSystem::DocModificationMode m_mode = TypeSystem::DocModificationXPathReplace;
    TypeSystem::Language m_format = TypeSystem::NativeCode;
};

#endif // MODIFICATIONS_H
