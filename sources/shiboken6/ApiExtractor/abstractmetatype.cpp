// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "abstractmetatype.h"
#include "abstractmetabuilder.h"
#include "abstractmetalang.h"
#include "messages.h"
#include "typedatabase.h"
#include "containertypeentry.h"

#include "qtcompat.h"
#include "typeinfo.h"

#ifndef QT_NO_DEBUG_STREAM
#  include <QtCore/QDebug>
#endif

#include <QtCore/QHash>
#include <QtCore/QSharedData>
#include <QtCore/QStack>

#include <memory>

using namespace Qt::StringLiterals;

using AbstractMetaTypeCPtr = std::shared_ptr<const AbstractMetaType>;

const QSet<QString> &AbstractMetaType::cppFloatTypes()
{
    static const QSet<QString> result{u"double"_s, u"float"_s};
    return result;
}

const QSet<QString> &AbstractMetaType::cppSignedCharTypes()
{
    static const QSet<QString> result{u"char"_s, u"signed char"_s};
    return result;
}

const QSet<QString> &AbstractMetaType::cppUnsignedCharTypes()
{
    static const QSet<QString> result{u"unsigned char"_s};
    return result;
}

const QSet<QString> &AbstractMetaType::cppCharTypes()
{
    static const QSet<QString> result = cppSignedCharTypes() | cppUnsignedCharTypes();
    return result;
}

const QSet<QString> &AbstractMetaType::cppSignedIntTypes()
{
    static QSet<QString> result;
    if (result.isEmpty()) {
        result = {u"char"_s, u"signed char"_s, u"short"_s, u"short int"_s,
                  u"signed short"_s, u"signed short int"_s,
                  u"int"_s, u"signed int"_s,
                  u"long"_s, u"long int"_s,
                  u"signed long"_s, u"signed long int"_s,
                  u"long long"_s, u"long long int"_s,
                  u"signed long long int"_s,
                  u"ptrdiff_t"_s};
        result |= cppSignedCharTypes();
    }
    return result;
}

const QSet<QString> &AbstractMetaType::cppUnsignedIntTypes()
{
    static QSet<QString> result;
    if (result.isEmpty()) {
        result = {u"unsigned short"_s, u"unsigned short int"_s,
                  u"unsigned"_s, u"unsigned int"_s,
                  u"unsigned long"_s, u"unsigned long int"_s,
                  u"unsigned long long"_s,
                  u"unsigned long long int"_s,
                  u"size_t"_s};
        result |= cppUnsignedCharTypes();
    }
    return result;
}

const QSet<QString> &AbstractMetaType::cppIntegralTypes()
{
    static QSet<QString> result;
    if (result.isEmpty()) {
        result |= cppSignedIntTypes();
        result |= cppUnsignedIntTypes();
        result.insert(u"bool"_s);
    }
    return result;
}

const QSet<QString> &AbstractMetaType::cppPrimitiveTypes()
{
    static QSet<QString> result;
    if (result.isEmpty()) {
        result |= cppIntegralTypes();
        result |= cppFloatTypes();
        result.insert(u"wchar_t"_s);
    }
    return result;
}

class AbstractMetaTypeData : public QSharedData
{
public:
    AbstractMetaTypeData(const TypeEntryCPtr &t);

    int actualIndirections() const;
    bool passByConstRef() const;
    bool passByValue() const;
    AbstractMetaType::TypeUsagePattern determineUsagePattern() const;
    bool hasTemplateChildren() const;
    QString formatSignature(bool minimal) const;
    QString formatPythonSignature() const;
    bool isEquivalent(const AbstractMetaTypeData &rhs) const;
    bool equals(const AbstractMetaTypeData &rhs) const;
    QStringList instantiationCppSignatures() const;

    template <class Predicate>
    bool generateOpaqueContainer(Predicate p) const;

    TypeEntryCPtr m_typeEntry;
    AbstractMetaTypeList m_instantiations;
    mutable QString m_cachedCppSignature;
    mutable QString m_cachedPythonSignature;
    QString m_originalTypeDescription;

    int m_arrayElementCount = -1;
    AbstractMetaTypeCPtr m_arrayElementType;
    AbstractMetaTypeCPtr m_originalTemplateType;
    AbstractMetaTypeCPtr m_viewOn;
    AbstractMetaType::Indirections m_indirections;

    AbstractMetaType::TypeUsagePattern m_pattern = AbstractMetaType::VoidPattern;
    uint m_constant : 1;
    uint m_volatile : 1;
    uint m_signaturesDirty : 1;
    uint m_reserved : 29; // unused

    ReferenceType m_referenceType = NoReference;
    AbstractMetaTypeList m_children;
};

AbstractMetaTypeData::AbstractMetaTypeData(const TypeEntryCPtr &t) :
    m_typeEntry(t),
    m_constant(false),
    m_volatile(false),
    m_signaturesDirty(true),
    m_reserved(0)
{
}

QStringList AbstractMetaTypeData::instantiationCppSignatures() const
{
    QStringList result;
    for (const auto &i : m_instantiations)
        result.append(i.cppSignature());
    return result;
}

AbstractMetaType::AbstractMetaType(const TypeEntryCPtr &t) :
    d(new AbstractMetaTypeData(t))
{
    Q_ASSERT(t);
}

AbstractMetaType::AbstractMetaType()
{
    *this = AbstractMetaType::createVoid();
}

AbstractMetaType &AbstractMetaType::operator=(const AbstractMetaType &) = default;

AbstractMetaType::AbstractMetaType(const AbstractMetaType &rhs) = default;

AbstractMetaType::AbstractMetaType(AbstractMetaType &&) = default;

AbstractMetaType &AbstractMetaType::operator=(AbstractMetaType &&) = default;

AbstractMetaType::~AbstractMetaType() = default;

QString AbstractMetaType::package() const
{
    return d->m_typeEntry->targetLangPackage();
}

QString AbstractMetaType::name() const
{
    return d->m_typeEntry->targetLangEntryName();
}

QString AbstractMetaType::fullName() const
{
    return d->m_typeEntry->qualifiedTargetLangName();
}

void AbstractMetaType::setTypeUsagePattern(AbstractMetaType::TypeUsagePattern pattern)
{
    if (d->m_pattern != pattern)
        d->m_pattern = pattern;
}

AbstractMetaType::TypeUsagePattern AbstractMetaType::typeUsagePattern() const
{
    return d->m_pattern;
}

bool AbstractMetaType::hasInstantiations() const
{
    return !d->m_instantiations.isEmpty();
}

void AbstractMetaType::addInstantiation(const AbstractMetaType &inst)
{
    d->m_instantiations << inst;
}

void AbstractMetaType::setInstantiations(const AbstractMetaTypeList &insts)
{
    if (insts != d->m_instantiations)
        d->m_instantiations = insts;
}

const AbstractMetaTypeList &AbstractMetaType::instantiations() const
{
    return d->m_instantiations;
}

QStringList AbstractMetaType::instantiationCppSignatures() const
{
    return d->instantiationCppSignatures();
}

// For applying the <array> function argument modification: change into a type
// where "int *" becomes "int[]".
bool AbstractMetaType::applyArrayModification(QString *errorMessage)
{

    if (d->m_pattern == AbstractMetaType::NativePointerAsArrayPattern) {
        *errorMessage = u"<array> modification already applied."_s;
        return false;
    }
    if (d->m_arrayElementType)  {
        QTextStream(errorMessage) << "The type \"" << cppSignature()
            << "\" is an array of " << d->m_arrayElementType->name() << '.';
        return false;
    }
    if (d->m_indirections.isEmpty()) {
        QTextStream(errorMessage) << "The type \"" << cppSignature()
            << "\" does not have indirections.";
        return false;
    }
    // Element type to be used for ArrayHandle<>, strip constness.

    auto elementType = new AbstractMetaType(*this);
    auto indir = indirectionsV();
    indir.pop_front();
    elementType->setIndirectionsV(indir);
    elementType->setConstant(false);
    elementType->setVolatile(false);
    elementType->decideUsagePattern();
    d->m_arrayElementType.reset(elementType);
    d->m_pattern = AbstractMetaType::NativePointerAsArrayPattern;
    return true;
}

TypeEntryCPtr AbstractMetaType::typeEntry() const
{
    return d->m_typeEntry;
}

void AbstractMetaType::setTypeEntry(const TypeEntryCPtr &type)
{
    if (d->m_typeEntry != type)
        d->m_typeEntry = type;
}

void AbstractMetaType::setOriginalTypeDescription(const QString &otd)
{
    if (d->m_originalTypeDescription != otd)
        d->m_originalTypeDescription = otd;
}

QString AbstractMetaType::originalTypeDescription() const
{
    return d->m_originalTypeDescription;
}

void AbstractMetaType::setOriginalTemplateType(const AbstractMetaType &type)
{
    if (!d->m_originalTemplateType || *d->m_originalTemplateType != type)
        d->m_originalTemplateType.reset(new AbstractMetaType(type));
}

const AbstractMetaType *AbstractMetaType::originalTemplateType() const
{
    return d->m_originalTemplateType.get();
}

AbstractMetaType AbstractMetaType::getSmartPointerInnerType() const
{
    Q_ASSERT(isSmartPointer());
    Q_ASSERT(!d->m_instantiations.isEmpty());
    AbstractMetaType innerType = d->m_instantiations.at(0);
    return innerType;
}

QString AbstractMetaType::getSmartPointerInnerTypeName() const
{
    Q_ASSERT(isSmartPointer());
    return getSmartPointerInnerType().name();
}

AbstractMetaTypeList AbstractMetaType::nestedArrayTypes() const
{
    AbstractMetaTypeList result;
    switch (d->m_pattern) {
    case ArrayPattern:
        for (AbstractMetaType t = *this; t.typeUsagePattern() == ArrayPattern; ) {
            const AbstractMetaType *elt = t.arrayElementType();
            result.append(*elt);
            t = *elt;
        }
        break;
    case NativePointerAsArrayPattern:
        result.append(*d->m_arrayElementType.get());
        break;
    default:
        break;
    }
    return result;
}

bool AbstractMetaTypeData::passByConstRef() const
{
    return m_constant && m_referenceType == LValueReference && m_indirections.isEmpty();
}

bool AbstractMetaType::passByConstRef() const
{
    return d->passByConstRef();
}

bool AbstractMetaTypeData::passByValue() const
{
    return m_referenceType == NoReference && m_indirections.isEmpty();
}

bool AbstractMetaType::passByValue() const
{
    return d->passByValue();
}

ReferenceType AbstractMetaType::referenceType() const
{
    return d->m_referenceType;
}

void AbstractMetaType::setReferenceType(ReferenceType ref)
{
    if (d->m_referenceType != ref) {
        d->m_referenceType = ref;
        d->m_signaturesDirty = true;
    }
}

int AbstractMetaTypeData::actualIndirections() const
{
    return m_indirections.size() + (m_referenceType == LValueReference ? 1 : 0);
}

int AbstractMetaType::actualIndirections() const
{
    return d->actualIndirections();
}

AbstractMetaType::Indirections AbstractMetaType::indirectionsV() const
{
    return d->m_indirections;
}

void AbstractMetaType::setIndirectionsV(const AbstractMetaType::Indirections &i)
{
    if (d->m_indirections != i) {
        d->m_indirections = i;
        d->m_signaturesDirty = true;
    }
}

void AbstractMetaType::clearIndirections()
{
    if (!d->m_indirections.isEmpty()) {
        d->m_indirections.clear();
        d->m_signaturesDirty = true;
    }
}

int AbstractMetaType::indirections() const
{
    return d->m_indirections.size();
}

void AbstractMetaType::setIndirections(int indirections)
{
    const Indirections newValue(indirections, Indirection::Pointer);
    if (d->m_indirections != newValue) {
        d->m_indirections = newValue;
        d->m_signaturesDirty = true;
    }
}

void AbstractMetaType::addIndirection(Indirection i)
{
    d->m_indirections.append(i);
}

void AbstractMetaType::setArrayElementCount(int n)
{
    if (d->m_arrayElementCount != n) {
        d->m_arrayElementCount = n;
        d->m_signaturesDirty = true;
    }
}

int AbstractMetaType::arrayElementCount() const
{
    return d->m_arrayElementCount;
}

const AbstractMetaType *AbstractMetaType::arrayElementType() const
{
    return d->m_arrayElementType.get();
}

void AbstractMetaType::setArrayElementType(const AbstractMetaType &t)
{
    if (!d->m_arrayElementType || *d->m_arrayElementType != t) {
        d->m_arrayElementType.reset(new AbstractMetaType(t));
        d->m_signaturesDirty = true;
    }
}

AbstractMetaType AbstractMetaType::plainType() const
{
    AbstractMetaType result = *this;
    result.clearIndirections();
    result.setReferenceType(NoReference);
    result.setConstant(false);
    result.setVolatile(false);
    result.decideUsagePattern();
    return result;
}

QString AbstractMetaType::cppSignature() const
{
    const AbstractMetaTypeData *cd = d.constData();
    if (cd->m_cachedCppSignature.isEmpty() || cd->m_signaturesDirty)
        cd->m_cachedCppSignature = formatSignature(false);
    return cd->m_cachedCppSignature;
}

QString AbstractMetaType::pythonSignature() const
{
    // PYSIDE-921: Handle container returntypes correctly.
    // This is now a clean reimplementation.
    const AbstractMetaTypeData *cd = d.constData();
    if (cd->m_cachedPythonSignature.isEmpty() || cd->m_signaturesDirty)
        cd->m_cachedPythonSignature = formatPythonSignature();
    return cd->m_cachedPythonSignature;
}

AbstractMetaType::TypeUsagePattern AbstractMetaTypeData::determineUsagePattern() const
{
    if (m_typeEntry->isTemplateArgument())
        return AbstractMetaType::TemplateArgument;

    if (m_typeEntry->type() == TypeEntry::ConstantValueType)
        return AbstractMetaType::NonTypeTemplateArgument;

    if (m_typeEntry->isPrimitive() && (actualIndirections() == 0 || passByConstRef()))
        return AbstractMetaType::PrimitivePattern;

    if (m_typeEntry->isVoid()) {
        return m_arrayElementCount < 0 && m_referenceType == NoReference
            && m_indirections.isEmpty() && m_constant == 0 && m_volatile == 0
            ? AbstractMetaType::VoidPattern : AbstractMetaType::NativePointerPattern;
    }

    if (m_typeEntry->isVarargs())
        return AbstractMetaType::VarargsPattern;

    if (m_typeEntry->isEnum() && (actualIndirections() == 0 || passByConstRef()))
        return AbstractMetaType::EnumPattern;

    if (m_typeEntry->isObject()) {
        if (m_indirections.isEmpty() && m_referenceType == NoReference)
            return AbstractMetaType::ValuePattern;
        return AbstractMetaType::ObjectPattern;
    }

    if (m_typeEntry->isContainer() && m_indirections.isEmpty())
        return AbstractMetaType::ContainerPattern;

    if (m_typeEntry->isSmartPointer() && m_indirections.isEmpty())
        return AbstractMetaType::SmartPointerPattern;

    if (m_typeEntry->isFlags() && (actualIndirections() == 0 || passByConstRef()))
        return AbstractMetaType::FlagsPattern;

    if (m_typeEntry->isArray())
        return AbstractMetaType::ArrayPattern;

    if (m_typeEntry->isValue())
        return m_indirections.size() == 1 ? AbstractMetaType::ValuePointerPattern : AbstractMetaType::ValuePattern;

    return AbstractMetaType::NativePointerPattern;
}

AbstractMetaType::TypeUsagePattern AbstractMetaType::determineUsagePattern() const
{
    return d->determineUsagePattern();
}

void AbstractMetaType::decideUsagePattern()
{
    TypeUsagePattern pattern = determineUsagePattern();
    if (d->m_typeEntry->isObject() && indirections() == 1
        && d->m_referenceType == LValueReference && isConstant()) {
        // const-references to pointers can be passed as pointers
        setReferenceType(NoReference);
        setConstant(false);
        pattern = ObjectPattern;
    }
    setTypeUsagePattern(pattern);
}

bool AbstractMetaTypeData::hasTemplateChildren() const
{
    QStack<AbstractMetaType> children;
    children << m_instantiations;

    // Recursively iterate over the children / descendants of the type, to check if any of them
    // corresponds to a template argument type.
    while (!children.isEmpty()) {
        AbstractMetaType child = children.pop();
        if (child.typeEntry()->isTemplateArgument())
            return true;
        children << child.instantiations();
    }
    return false;
}

bool AbstractMetaType::hasTemplateChildren() const
{
    return d->hasTemplateChildren();
}

static inline QString formatArraySize(int e)
{
    QString result;
    result += u'[';
    if (e >= 0)
        result += QString::number(e);
    result += u']';
    return result;
}

// Return the number of template parameters; remove the default
// non template type parameter of std::span from the signature.
static qsizetype stripDefaultTemplateArgs(const TypeEntryCPtr &te,
                                          const AbstractMetaTypeList &instantiations)
{
    static const char16_t dynamicExtent64[] = u"18446744073709551615"; // size_t(-1)
    static const char16_t dynamicExtent32[] = u"4294967295";

    qsizetype result = instantiations.size();
    if (result == 0 || !te->isContainer())
        return result;
    auto cte = std::static_pointer_cast<const ContainerTypeEntry>(te);
    if (cte->containerKind() != ContainerTypeEntry::SpanContainer)
        return result;
    const auto lastTe = instantiations.constLast().typeEntry();
    if (lastTe->type() == TypeEntry::ConstantValueType) {
        const QString &name = lastTe->name();
        if (name == dynamicExtent64 || name == dynamicExtent32)
           --result;
    }
    return result;
}

QString AbstractMetaTypeData::formatSignature(bool minimal) const
{
    QString result;
    if (m_constant)
        result += u"const "_s;
    if (m_volatile)
        result += u"volatile "_s;
    if (m_pattern == AbstractMetaType::ArrayPattern) {
        // Build nested array dimensions a[2][3] in correct order
        result += m_arrayElementType->minimalSignature();
        const int arrayPos = result.indexOf(u'[');
        if (arrayPos != -1)
            result.insert(arrayPos, formatArraySize(m_arrayElementCount));
        else
            result.append(formatArraySize(m_arrayElementCount));
    } else {
        result += m_typeEntry->qualifiedCppName();
    }
    if (!m_instantiations.isEmpty()) {
        result += u'<';
        if (minimal)
            result += u' ';
        const auto size = stripDefaultTemplateArgs(m_typeEntry, m_instantiations);
        for (qsizetype i = 0; i < size; ++i) {
            if (i > 0)
                result += u',';
            result += m_instantiations.at(i).minimalSignature();
        }
        result += u'>';
    }

    if (!minimal && (!m_indirections.isEmpty() || m_referenceType != NoReference))
        result += u' ';
    for (Indirection i : m_indirections)
        result += TypeInfo::indirectionKeyword(i);
    switch (m_referenceType) {
    case NoReference:
        break;
    case LValueReference:
        result += u'&';
        break;
    case RValueReference:
        result += u"&&"_s;
        break;
    }
    return result;
}

QString AbstractMetaType::formatSignature(bool minimal) const
{
    return d->formatSignature(minimal);
}

QString AbstractMetaTypeData::formatPythonSignature() const
{
    /*
     * This is a version of the above, more suitable for Python.
     * We avoid extra keywords that are not needed in Python.
     * We prepend the package name, unless it is a primitive type.
     *
     * Primitive types like 'int', 'char' etc.:
     * When we have a primitive with an indirection, we use that '*'
     * character for later postprocessing, since those indirections
     * need to be modified into a result tuple.
     * Smart pointer instantiations: Drop the package
     */
    QString result;
    if (m_pattern == AbstractMetaType::NativePointerAsArrayPattern)
        result += u"array "_s;
    // We no longer use the "const" qualifier for heuristics. Instead,
    // NativePointerAsArrayPattern indicates when we have <array> in XML.
    // if (m_typeEntry->isPrimitive() && isConstant())
    //     result += QLatin1String("const ");
    if (!m_typeEntry->isPrimitive() && !m_typeEntry->isSmartPointer()) {
        const QString package = m_typeEntry->targetLangPackage();
        if (!package.isEmpty())
            result += package + u'.';
    }
    if (m_pattern == AbstractMetaType::ArrayPattern) {
        // Build nested array dimensions a[2][3] in correct order
        result += m_arrayElementType->formatPythonSignature();
        const int arrayPos = result.indexOf(u'[');
        if (arrayPos != -1)
            result.insert(arrayPos, formatArraySize(m_arrayElementCount));
        else
            result.append(formatArraySize(m_arrayElementCount));
    } else {
        result += m_typeEntry->targetLangName();
    }
    if (!m_instantiations.isEmpty()) {
        result += u'[';
        for (qsizetype i = 0, size = m_instantiations.size(); i < size; ++i) {
            if (i > 0)
                result += u", "_s;
            result += m_instantiations.at(i).formatPythonSignature();
        }
        result += u']';
    }
    if (m_typeEntry->isPrimitive())
        for (Indirection i : m_indirections)
            result += TypeInfo::indirectionKeyword(i);
    // If it is a flags type, we replace it with the full name:
    // "PySide6.QtCore.Qt.ItemFlags" instead of "PySide6.QtCore.QFlags<Qt.ItemFlag>"
    if (m_typeEntry->isFlags())
        result = m_typeEntry->qualifiedTargetLangName();
    result.replace(u"::"_s, u"."_s);
    return result;
}

QString AbstractMetaType::formatPythonSignature() const
{
    return d->formatPythonSignature();
}

bool AbstractMetaType::isCppPrimitive() const
{
    return d->m_pattern == PrimitivePattern && ::isCppPrimitive(d->m_typeEntry);
}

bool AbstractMetaType::isConstant() const
{
    return d->m_constant;
}

void AbstractMetaType::setConstant(bool constant)
{
    if (d->m_constant != constant) {
        d->m_constant = constant;
        d->m_signaturesDirty = true;
    }
}

bool AbstractMetaType::isVolatile() const
{
    return d->m_volatile;
}

void AbstractMetaType::setVolatile(bool v)
{
    if (d->m_volatile != v) {
        d->m_volatile = v;
        d->m_signaturesDirty = true;\
    }
}

static bool equalsCPtr(const AbstractMetaTypeCPtr &t1, const AbstractMetaTypeCPtr &t2)
{
    if (bool(t1) != bool(t2))
        return false;
    return !t1 || *t1 == *t2;
}

bool AbstractMetaTypeData::isEquivalent(const AbstractMetaTypeData &rhs) const
{
    if (m_typeEntry != rhs.m_typeEntry
        || m_indirections != rhs.m_indirections
        || m_arrayElementCount != rhs.m_arrayElementCount) {
        return false;
    }

    if (!equalsCPtr(m_arrayElementType, rhs.m_arrayElementType))
        return false;

    if (!equalsCPtr(m_viewOn, rhs.m_viewOn))
        return false;

    if (m_instantiations != rhs.m_instantiations)
        return false;
    return true;
}

bool AbstractMetaTypeData::equals(const AbstractMetaTypeData &rhs) const
{
    return m_constant == rhs.m_constant && m_volatile == rhs.m_volatile
        && m_referenceType == rhs.m_referenceType && isEquivalent(rhs);
}

bool AbstractMetaType::equals(const AbstractMetaType &rhs) const
{
    return d->equals(*rhs.d);
}

bool AbstractMetaType::isEquivalent(const AbstractMetaType &rhs) const
{
    return  d->isEquivalent(*rhs.d);
}

const AbstractMetaType *AbstractMetaType::viewOn() const
{
    return d->m_viewOn.get();
}

void AbstractMetaType::setViewOn(const AbstractMetaType &v)
{
    if (!d->m_viewOn || *d->m_viewOn != v)
        d->m_viewOn.reset(new AbstractMetaType(v));
}

AbstractMetaType AbstractMetaType::createVoid()
{
    static QScopedPointer<AbstractMetaType> metaType;
    if (metaType.isNull()) {
        static TypeEntryCPtr voidTypeEntry = TypeDatabase::instance()->findType(u"void"_s);
        Q_ASSERT(voidTypeEntry);
        metaType.reset(new AbstractMetaType(voidTypeEntry));
        metaType->decideUsagePattern();
    }
    return *metaType.data();
}

void AbstractMetaType::dereference(QString *type)
{
    type->prepend(u"(*"_s);
    type->append(u')');
}

QString AbstractMetaType::dereferencePrefix(qsizetype n)
{
    const QChar c = n > 0 ? u'*' : u'&';
    return QString(qAbs(n), c);
}

void AbstractMetaType::applyDereference(QString *type, qsizetype n)
{
    if (n == 0)
        return;

    type->prepend(dereferencePrefix(n));
    type->prepend(u'(');
    type->append(u')');
}

bool AbstractMetaType::stripDereference(QString *type)
{
    if (type->startsWith(u"(*") && type->endsWith(u')')) {
        type->chop(1);
        type->remove(0, 2);
        *type = type->trimmed();
        return true;
    }
    if (type->startsWith(u'*')) {
        type->remove(0, 1);
        *type = type->trimmed();
        return true;
    }
    return false;
}

// Query functions for generators
bool AbstractMetaType::isObjectType() const
{
    return d->m_typeEntry->isObject();
}

bool AbstractMetaType::isUniquePointer() const
{
    return isSmartPointer() && d->m_typeEntry->isUniquePointer();
}

bool AbstractMetaType::isPointer() const
{
    return !d->m_indirections.isEmpty()
        || isNativePointer() || isValuePointer();
}

bool AbstractMetaType::isPointerToConst() const
{
    return d->m_constant && !d->m_indirections.isEmpty()
        && d->m_indirections.constLast() != Indirection::ConstPointer;
}

bool AbstractMetaType::isCString() const
{
    return isNativePointer()
        && d->m_indirections.size() == 1
        && name() == u"char";
}

bool AbstractMetaType::isVoidPointer() const
{
    return isNativePointer()
        && d->m_indirections.size() == 1
        && name() == u"void";
}

bool AbstractMetaType::isUserPrimitive() const
{
    return d->m_indirections.isEmpty() && ::isUserPrimitive(d->m_typeEntry);
}

bool AbstractMetaType::isObjectTypeUsedAsValueType() const
{
    return d->m_typeEntry->isObject() && d->m_referenceType == NoReference
        && d->m_indirections.isEmpty();
}

bool AbstractMetaType::isWrapperType() const
{
    return d->m_typeEntry->isWrapperType();
}

bool AbstractMetaType::isPointerToWrapperType() const
{
    return (isObjectType() && d->m_indirections.size() == 1) || isValuePointer();
}

bool AbstractMetaType::isWrapperPassedByReference() const
{
    return d->m_referenceType == LValueReference && isWrapperType()
           && !isPointer();
}

bool AbstractMetaType::isCppIntegralPrimitive() const
{
    return ::isCppIntegralPrimitive(d->m_typeEntry);
}

bool AbstractMetaType::isExtendedCppPrimitive() const
{
    if (isCString() || isVoidPointer())
        return true;
    if (!d->m_indirections.isEmpty())
        return false;
    return ::isExtendedCppPrimitive(d->m_typeEntry);
}

bool AbstractMetaType::isValueTypeWithCopyConstructorOnly() const
{
    bool result = false;
    if (d->m_typeEntry->isComplex()) {
        const auto cte = std::static_pointer_cast<const ComplexTypeEntry>(d->m_typeEntry);
        result = cte->isValueTypeWithCopyConstructorOnly();
    }
    return result;
}

bool AbstractMetaType::valueTypeWithCopyConstructorOnlyPassed() const
{
    return (passByValue() || passByConstRef())
           && isValueTypeWithCopyConstructorOnly();
}

using AbstractMetaTypeCache = QHash<QString, AbstractMetaType>;

Q_GLOBAL_STATIC(AbstractMetaTypeCache, metaTypeFromStringCache)

std::optional<AbstractMetaType>
AbstractMetaType::fromString(QString typeSignature, QString *errorMessage)
{
    typeSignature = typeSignature.trimmed();
    if (typeSignature.startsWith(u"::"))
        typeSignature.remove(0, 2);

    auto &cache = *metaTypeFromStringCache();
    auto it = cache.find(typeSignature);
    if (it == cache.end()) {
        auto metaType =
            AbstractMetaBuilder::translateType(typeSignature, nullptr, {}, errorMessage);
        if (Q_UNLIKELY(!metaType.has_value())) {
            if (errorMessage)
                errorMessage->prepend(msgCannotBuildMetaType(typeSignature));
            return {};
        }
        it = cache.insert(typeSignature, metaType.value());
    }
    return it.value();
}

AbstractMetaType AbstractMetaType::fromTypeEntry(const TypeEntryCPtr &typeEntry)
{
    QString typeName = typeEntry->qualifiedCppName();
    if (typeName.startsWith(u"::"))
        typeName.remove(0, 2);
    auto &cache  = *metaTypeFromStringCache();
    auto it = cache.find(typeName);
    if (it != cache.end())
        return it.value();
    AbstractMetaType metaType = AbstractMetaType(typeEntry).plainType();
    cache.insert(typeName, metaType);
    return metaType;
}

AbstractMetaType AbstractMetaType::fromAbstractMetaClass(const AbstractMetaClassCPtr &metaClass)
{
    return fromTypeEntry(metaClass->typeEntry());
}

template <class Predicate> // Predicate(containerTypeEntry, signature)
bool AbstractMetaTypeData::generateOpaqueContainer(Predicate pred) const
{
    // Allow for passing containers by pointer as well.
    if (!m_typeEntry->isContainer())
        return false;
    if (m_indirections.size() > 1)
        return false;
    auto containerTypeEntry = std::static_pointer_cast<const ContainerTypeEntry>(m_typeEntry);
    auto kind = containerTypeEntry->containerKind();
    if (kind != ContainerTypeEntry::ListContainer && kind != ContainerTypeEntry::SpanContainer)
        return false;

    const auto &firstInstantiation = m_instantiations.constFirst();
    if (firstInstantiation.referenceType() != NoReference)
        return false;
    switch (firstInstantiation.typeEntry()->type()) {
    case TypeEntry::PrimitiveType:
    case TypeEntry::FlagsType:
    case TypeEntry::EnumType:
    case TypeEntry::BasicValueType:
    case TypeEntry::ObjectType:
    case TypeEntry::CustomType:
        break;
    default:
        return false;
    }

    return pred(containerTypeEntry, instantiationCppSignatures());
}

// Simple predicate for checking whether an opaque container should be generated
static bool opaqueContainerPredicate(const ContainerTypeEntryCPtr &t,
                                     const QStringList &instantiations)
{
    return t->generateOpaqueContainer(instantiations);
}

bool AbstractMetaType::generateOpaqueContainer() const
{
    return d->generateOpaqueContainer(opaqueContainerPredicate);
}

// Helper for determining whether a function should return an opaque container,
// that is, the function return type is modified accordingly
// (cf AbstractMetaFunction::generateOpaqueContainerReturn())
bool AbstractMetaType::generateOpaqueContainerForGetter(const QString &modifiedType) const
{
    auto predicate = [&modifiedType](const ContainerTypeEntryCPtr &t,
                                     const QStringList &instantiations) {
        return t->opaqueContainerName(instantiations) == modifiedType;
    };
    return d->generateOpaqueContainer(predicate);
}

#ifndef QT_NO_DEBUG_STREAM
void AbstractMetaType::formatDebug(QDebug &debug) const
{
    debug << '"' << name() << '"';
    if (debug.verbosity() > 2 && !isVoid()) {
        auto te = typeEntry();
        debug << ", typeEntry=";
        if (debug.verbosity() > 3)
            debug << te;
        else
            debug << "(\"" << te->qualifiedCppName() << "\", " << te->type() << ')';
        debug << ", signature=\"" << cppSignature() << "\", pattern="
            << typeUsagePattern();
        const auto indirections = indirectionsV();
        if (!indirections.isEmpty()) {
            debug << ", indirections=";
            for (auto i : indirections)
                debug << ' ' << TypeInfo::indirectionKeyword(i);
        }
        if (referenceType())
            debug << ", reftype=" << referenceType();
        if (isConstant())
            debug << ", [const]";
        if (isVolatile())
            debug << ", [volatile]";
        if (isArray()) {
            debug << ", array of \"" << arrayElementType()->cppSignature()
                << "\", arrayElementCount="  << arrayElementCount();
        }
        const auto &instantiations = this->instantiations();
        if (const auto instantiationsSize = instantiations.size()) {
            debug << ", instantiations[" << instantiationsSize << "]=<";
            for (qsizetype i = 0; i < instantiationsSize; ++i) {
                if (i)
                    debug << ", ";
                instantiations.at(i).formatDebug(debug);
            }
        }
        debug << '>';
        if (viewOn())
            debug << ", views " << viewOn()->name();
    }
}

QDebug operator<<(QDebug d, const AbstractMetaType &at)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "AbstractMetaType(";
    at.formatDebug(d);
    d << ')';
    return d;
}

QDebug operator<<(QDebug d, const AbstractMetaType *at)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    if (at)
        d << *at;
    else
        d << "AbstractMetaType(0)";
    return d;
}

#endif // !QT_NO_DEBUG_STREAM
