// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "modifications.h"
#include "codesnip.h"

#include "qtcompat.h"

#include <QtCore/QDebug>
#include <QtCore/QRegularExpression>

#include <algorithm>
#include <limits>

using namespace Qt::StringLiterals;

// ---------------------- Modification
QString FunctionModification::accessModifierString() const
{
    if (isPrivate())
        return u"private"_s;
    if (isProtected())
        return u"protected"_s;
    if (isPublic())
        return u"public"_s;
    if (isFriendly())
        return u"friendly"_s;
    return QString();
}

// ---------------------- FieldModification

class FieldModificationData : public QSharedData
{
public:
    QString m_name;
    QString m_renamedToName;
    bool m_readable = true;
    bool m_writable = true;
    bool m_removed = false;
    bool m_opaqueContainer = false;
    TypeSystem::SnakeCase snakeCase = TypeSystem::SnakeCase::Unspecified;
};

FieldModification::FieldModification() : d(new FieldModificationData)
{
}

FieldModification::FieldModification(const FieldModification &) = default;
FieldModification &FieldModification::operator=(const FieldModification &) = default;
FieldModification::FieldModification(FieldModification &&) = default;
FieldModification &FieldModification::operator=(FieldModification &&) = default;
FieldModification::~FieldModification() = default;

QString FieldModification::name() const
{
    return d->m_name;
}

void FieldModification::setName(const QString &value)
{
    if (d->m_name != value)
        d->m_name = value;
}

bool FieldModification::isRenameModifier() const
{
    return !d->m_renamedToName.isEmpty();
}

QString FieldModification::renamedToName() const
{
    return d->m_renamedToName;
}

void FieldModification::setRenamedToName(const QString &value)
{
    if (d->m_renamedToName != value)
        d->m_renamedToName = value;
}

bool FieldModification::isReadable() const
{
    return d->m_readable;
}

void FieldModification::setReadable(bool e)
{
    if (d->m_readable != e)
        d->m_readable = e;
}

bool FieldModification::isWritable() const
{
    return d->m_writable;
}

void FieldModification::setWritable(bool e)
{
    if (d->m_writable != e)
        d->m_writable = e;
}

bool FieldModification::isRemoved() const
{
    return d->m_removed;
}

void FieldModification::setRemoved(bool r)
{
    if (d->m_removed != r)
        d->m_removed = r;
}

bool FieldModification::isOpaqueContainer() const
{
    return d->m_opaqueContainer;
}

void FieldModification::setOpaqueContainer(bool r)
{
    if (d->m_opaqueContainer != r)
        d->m_opaqueContainer = r;
}

TypeSystem::SnakeCase FieldModification::snakeCase() const
{
    return d->snakeCase;
}

void FieldModification::setSnakeCase(TypeSystem::SnakeCase s)
{
    if (d->snakeCase != s)
        d->snakeCase = s;
}

// Remove the parameter names enclosed in '@' from an added function signature
// so that it matches the C++ type signature.
static QString removeParameterNames(QString signature)
{
    while (true) {
        const auto ampPos = signature.indexOf(u'@');
        if (ampPos == -1)
            break;
        const auto closingAmpPos = signature.indexOf(u'@', ampPos + 1);
        if (closingAmpPos == -1)
            break;
        signature.remove(ampPos, closingAmpPos - ampPos + 1);
    }
    return signature;
}

DocModification::DocModification(const QString &xpath, const QString &signature) :
    m_xpath(xpath), m_signature(removeParameterNames(signature))
{
}

DocModification::DocModification(TypeSystem::DocModificationMode mode, const QString &signature) :
    m_signature(removeParameterNames(signature)), m_mode(mode)
{
}

void DocModification::setCode(const QString &code)
{
    m_code = CodeSnipAbstract::fixSpaces(code);
}

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const ReferenceCount &r)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "ReferenceCount(" << r.varName << ", action=" << r.action << ')';
    return d;
}

QDebug operator<<(QDebug d, const CodeSnip &s)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    const auto size = s.codeList.size();
    d << "CodeSnip(language=" << s.language << ", position=" << s.position
        << ", fragments[" << size << "]=";
    for (qsizetype i = 0; i < size; ++i) {
        const auto &f = s.codeList.at(i);
        if (i)
            d << ", ";
        d << '#' << i << ' ';
        if (!f.instance()) {
            d << '"';
            const QString &code = f.code();
            const auto lines = QStringView{code}.split(u'\n');
            for (qsizetype i = 0, size = lines.size(); i < size; ++i) {
                if (i)
                    d << "\\n";
                d << lines.at(i).trimmed();
            }
            d << '"';
        } else {
            d << "template=\"" << f.instance()->name() << '"';
        }
    }
    d << ')';
    return d;
}

class ArgumentModificationData : public QSharedData
{
public:
    ArgumentModificationData(int idx = -1) :  index(idx),
        removedDefaultExpression(false), removed(false),
        noNullPointers(false), resetAfterUse(false), array(false)
    {}

    QList<ReferenceCount> referenceCounts;
    QString modified_type;
    QString pyiType;
    QString replacedDefaultExpression;
    TypeSystem::Ownership m_targetOwnerShip = TypeSystem::UnspecifiedOwnership;
    TypeSystem::Ownership m_nativeOwnerShip = TypeSystem::UnspecifiedOwnership;
    CodeSnipList conversion_rules;
    ArgumentOwner owner;
    QString renamed_to;
    int index = -1;
    uint removedDefaultExpression : 1;
    uint removed : 1;
    uint noNullPointers : 1;
    uint resetAfterUse : 1;
    uint array : 1;
};

ArgumentModification::ArgumentModification() : d(new ArgumentModificationData)
{
}

ArgumentModification::ArgumentModification(int idx) : d(new ArgumentModificationData(idx))
{
}

ArgumentModification::ArgumentModification(const ArgumentModification &) = default;
ArgumentModification &ArgumentModification::operator=(const ArgumentModification &) = default;
ArgumentModification::ArgumentModification(ArgumentModification &&) = default;
ArgumentModification &ArgumentModification::operator=(ArgumentModification &&) = default;
ArgumentModification::~ArgumentModification() = default;

const QString &ArgumentModification::modifiedType() const
{
    return d->modified_type;
}

void ArgumentModification::setModifiedType(const QString &value)
{
    if (d->modified_type != value)
        d->modified_type = value;
}

bool ArgumentModification::isTypeModified() const
{
    return !d->modified_type.isEmpty();
}

QString ArgumentModification::pyiType() const
{
    return d->pyiType;
}

void ArgumentModification::setPyiType(const QString &value)
{
    if (d->pyiType != value)
        d->pyiType = value;
}

QString ArgumentModification::replacedDefaultExpression() const
{
    return d->replacedDefaultExpression;
}

void ArgumentModification::setReplacedDefaultExpression(const QString &value)
{
    if (d->replacedDefaultExpression != value)
        d->replacedDefaultExpression = value;
}

TypeSystem::Ownership ArgumentModification::targetOwnerShip() const
{
    return d->m_targetOwnerShip;
}

void ArgumentModification::setTargetOwnerShip(TypeSystem::Ownership o)
{
    if (o != d->m_targetOwnerShip)
        d->m_targetOwnerShip = o;
}

TypeSystem::Ownership ArgumentModification::nativeOwnership() const
{
    return d->m_nativeOwnerShip;
}

void ArgumentModification::setNativeOwnership(TypeSystem::Ownership o)
{
    if (o != d->m_nativeOwnerShip)
        d->m_nativeOwnerShip = o;
}

const CodeSnipList &ArgumentModification::conversionRules() const
{
    return d->conversion_rules;
}

CodeSnipList &ArgumentModification::conversionRules()
{
    return d->conversion_rules;
}

ArgumentOwner ArgumentModification::owner() const
{
    return d->owner;
}

void ArgumentModification::setOwner(const ArgumentOwner &value)
{
    d->owner = value;
}

QString ArgumentModification::renamedToName() const
{
    return d->renamed_to;
}

void ArgumentModification::setRenamedToName(const QString &value)
{
    if (d->renamed_to != value)
        d->renamed_to = value;
}

int ArgumentModification::index() const
{
    return d->index;
}

void ArgumentModification::setIndex(int value)
{
    if (d->index != value)
        d->index = value;
}

bool ArgumentModification::removedDefaultExpression() const
{
    return d->removedDefaultExpression;
}

void ArgumentModification::setRemovedDefaultExpression(const uint &value)
{
    if (d->removedDefaultExpression != value)
        d->removedDefaultExpression = value;
}

bool ArgumentModification::isRemoved() const
{
    return d->removed;
}

void ArgumentModification::setRemoved(bool value)
{
    if (d->removed != value)
        d->removed = value;
}

bool ArgumentModification::noNullPointers() const
{
    return d->noNullPointers;
}

void ArgumentModification::setNoNullPointers(bool value)
{
    if (d->noNullPointers != value)
        d->noNullPointers = value;
}

bool ArgumentModification::resetAfterUse() const
{
    return d->resetAfterUse;
}

void ArgumentModification::setResetAfterUse(bool value)
{
    if (d->resetAfterUse != value)
        d->resetAfterUse = value;
}

bool ArgumentModification::isArray() const
{
    return d->array;
}

void ArgumentModification::setArray(bool value)
{
    if (d->array != value)
        d->array = value;
}

const QList<ReferenceCount> &ArgumentModification::referenceCounts() const
{
    return d->referenceCounts;
}

void ArgumentModification::addReferenceCount(const ReferenceCount &value)
{
    d->referenceCounts.append(value);
}

class FunctionModificationData : public QSharedData
{
public:
    QString renamedToName;
    FunctionModification::Modifiers modifiers;
    CodeSnipList m_snips;
    QList<ArgumentModification> m_argument_mods;
    QString m_signature;
    QString m_originalSignature;
    QRegularExpression m_signaturePattern;
    int m_overloadNumber = TypeSystem::OverloadNumberUnset;
    bool m_thread = false;
    bool removed = false;
    TypeSystem::AllowThread m_allowThread = TypeSystem::AllowThread::Unspecified;
    TypeSystem::ExceptionHandling m_exceptionHandling = TypeSystem::ExceptionHandling::Unspecified;
    TypeSystem::SnakeCase snakeCase = TypeSystem::SnakeCase::Unspecified;
};

FunctionModification::FunctionModification() : d(new FunctionModificationData)
{
}

FunctionModification::FunctionModification(const FunctionModification &) = default;
FunctionModification &FunctionModification::operator=(const FunctionModification &) = default;
FunctionModification::FunctionModification(FunctionModification &&) = default;
FunctionModification &FunctionModification::operator=(FunctionModification &&) = default;
FunctionModification::~FunctionModification() = default;

void FunctionModification::formatDebug(QDebug &debug) const
{
    if (d->m_signature.isEmpty())
        debug << "pattern=\"" << d->m_signaturePattern.pattern();
    else
        debug << "signature=\"" << d->m_signature;
    debug << "\", modifiers=" << d->modifiers;
    if (d->removed)
        debug << ", removed";
    if (!d->renamedToName.isEmpty())
        debug << ", renamedToName=\"" << d->renamedToName << '"';
    if (d->m_allowThread != TypeSystem::AllowThread::Unspecified)
        debug << ", allowThread=" << int(d->m_allowThread);
    if (d->m_thread)
        debug << ", thread";
    if (d->m_exceptionHandling != TypeSystem::ExceptionHandling::Unspecified)
        debug << ", exceptionHandling=" << int(d->m_exceptionHandling);
    if (!d->m_snips.isEmpty())
        debug << ", snips=(" << d->m_snips << ')';
    if (!d->m_argument_mods.isEmpty())
        debug << ", argument_mods=(" << d->m_argument_mods << ')';
}

QString FunctionModification::renamedToName() const
{
    return d->renamedToName;
}

void FunctionModification::setRenamedToName(const QString &value)
{
    if (d->renamedToName != value)
        d->renamedToName = value;
}

FunctionModification::Modifiers FunctionModification::modifiers() const
{
    return d->modifiers;
}

void FunctionModification::setModifiers(Modifiers m)
{
    if (d->modifiers != m)
        d->modifiers = m;
}

void FunctionModification::setModifierFlag(FunctionModification::ModifierFlag f)
{
    auto newMods = d->modifiers | f;
    if (d->modifiers != newMods)
        d->modifiers = newMods;
}

void FunctionModification::clearModifierFlag(ModifierFlag f)
{
    auto newMods = d->modifiers & ~f;
    if (d->modifiers != newMods)
        d->modifiers = newMods;
}

bool FunctionModification::isRemoved() const
{
    return d->removed;
}

void FunctionModification::setRemoved(bool r)
{
    if (d->removed != r)
        d->removed = r;
}

const QList<ArgumentModification> &FunctionModification::argument_mods() const
{
    return d->m_argument_mods;
}

QList<ArgumentModification> &FunctionModification::argument_mods()
{
    return d->m_argument_mods;
}

void FunctionModification::setArgument_mods(const QList<ArgumentModification> &argument_mods)
{
    d->m_argument_mods = argument_mods;
}

TypeSystem::SnakeCase FunctionModification::snakeCase() const
{
    return d->snakeCase;
}

void FunctionModification::setSnakeCase(TypeSystem::SnakeCase s)
{
    if (d->snakeCase != s)
        d->snakeCase = s;
}

const CodeSnipList &FunctionModification::snips() const
{
    return d->m_snips;
}

CodeSnipList &FunctionModification::snips()
{
    return d->m_snips;
}

void FunctionModification::appendSnip(const CodeSnip &snip)
{
    d->m_snips.append(snip);
}

void FunctionModification::setSnips(const CodeSnipList &snips)
{
    d->m_snips = snips;
}

// ---------------------- FunctionModification
void FunctionModification::setIsThread(bool flag)
{
    if (d->m_thread != flag)
        d->m_thread = flag;
}

bool FunctionModification::isThread() const
{
    return d->m_thread;
}

FunctionModification::AllowThread FunctionModification::allowThread() const
{
    return d->m_allowThread;
}

void FunctionModification::setAllowThread(FunctionModification::AllowThread allow)
{
    if (d->m_allowThread != allow)
        d->m_allowThread = allow;
}

bool FunctionModification::matches(const QStringList &functionSignatures) const
{
    if (!d->m_signature.isEmpty())
        return functionSignatures.contains(d->m_signature);

    for (const auto &s : functionSignatures) {
        if (d->m_signaturePattern.match(s).hasMatch())
            return true;
    }
    return false;
}

bool FunctionModification::setSignature(const QString &s, QString *errorMessage)
{
    if (s.startsWith(u'^')) {
        d->m_signaturePattern.setPattern(s);
        if (!d->m_signaturePattern.isValid()) {
            if (errorMessage) {
                *errorMessage = u"Invalid signature pattern: \""_s
                    + s + u"\": "_s + d->m_signaturePattern.errorString();
            }
            return false;
        }
    } else {
        d->m_signature = s;
    }
    return true;
}

QString FunctionModification::signature() const
{
    return d->m_signature.isEmpty() ? d->m_signaturePattern.pattern() : d->m_signature;
}

void FunctionModification::setOriginalSignature(const QString &s)
{
    if (d->m_originalSignature != s)
        d->m_originalSignature = s;
}

QString FunctionModification::originalSignature() const
{
    return d->m_originalSignature;
}

TypeSystem::ExceptionHandling FunctionModification::exceptionHandling() const
{
    return d->m_exceptionHandling;
}

void FunctionModification::setExceptionHandling(TypeSystem::ExceptionHandling e)
{
    if (d->m_exceptionHandling != e)
        d->m_exceptionHandling = e;
}

int FunctionModification::overloadNumber() const
{
    return d->m_overloadNumber;
}

void FunctionModification::setOverloadNumber(int overloadNumber)
{
    d->m_overloadNumber = overloadNumber;
}

QDebug operator<<(QDebug d, const ArgumentOwner &a)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "ArgumentOwner(index=" << a.index << ", action=" << a.action << ')';
    return d;
}

QDebug operator<<(QDebug d, const ArgumentModification &a)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "ArgumentModification(index=" << a.index();
    if (a.removedDefaultExpression())
        d << ", removedDefaultExpression";
    if (a.isRemoved())
        d << ", removed";
    if (a.noNullPointers())
        d << ", noNullPointers";
    if (a.isArray())
        d << ", array";
    if (!a.referenceCounts().isEmpty())
        d << ", referenceCounts=" << a.referenceCounts();
    if (!a.modifiedType().isEmpty())
        d << ", modified_type=\"" << a.modifiedType() << '"';
    if (!a.replacedDefaultExpression().isEmpty())
        d << ", replacedDefaultExpression=\"" << a.replacedDefaultExpression() << '"';
    if (a.targetOwnerShip() != TypeSystem::UnspecifiedOwnership)
        d << ", target ownership=" << a.targetOwnerShip();
    if (a.nativeOwnership() != TypeSystem::UnspecifiedOwnership)
        d << ", native ownership=" << a.nativeOwnership();
    if (!a.renamedToName().isEmpty())
        d << ", renamed_to=\"" << a.renamedToName() << '"';
    const auto &rules = a.conversionRules();
    if (!rules.isEmpty())
        d << ", conversionRules[" << rules.size() << "]=" << rules;
     d << ", owner=" << a.owner() << ')';
    return  d;
}

QDebug operator<<(QDebug d, const FunctionModification &fm)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "FunctionModification(";
    fm.formatDebug(d);
    d << ')';
    return d;
}
#endif // !QT_NO_DEBUG_STREAM
