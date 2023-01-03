// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "customconversion.h"
#include "containertypeentry.h"
#include "customtypenentry.h"
#include "primitivetypeentry.h"
#include "valuetypeentry.h"

#include <QtCore/qdebug.h>

using namespace Qt::StringLiterals;

CustomConversion::CustomConversion(const TypeEntryCPtr &ownerType) :
    m_ownerType(ownerType)
{
}

TypeEntryCPtr CustomConversion::ownerType() const
{
    return m_ownerType;
}

QString CustomConversion::nativeToTargetConversion() const
{
    return m_nativeToTargetConversion;
}

void CustomConversion::setNativeToTargetConversion(const QString &nativeToTargetConversion)
{
    m_nativeToTargetConversion = nativeToTargetConversion;
}

bool CustomConversion::replaceOriginalTargetToNativeConversions() const
{
    return m_replaceOriginalTargetToNativeConversions;
}

void CustomConversion::setReplaceOriginalTargetToNativeConversions(bool r)
{
    m_replaceOriginalTargetToNativeConversions = r;
}

bool CustomConversion::hasTargetToNativeConversions() const
{
    return !(m_targetToNativeConversions.isEmpty());
}

TargetToNativeConversions &CustomConversion::targetToNativeConversions()
{
    return m_targetToNativeConversions;
}

const TargetToNativeConversions &CustomConversion::targetToNativeConversions() const
{
    return m_targetToNativeConversions;
}

void CustomConversion::addTargetToNativeConversion(const QString &sourceTypeName,
                                                   const QString &sourceTypeCheck,
                                                   const QString &conversion)
{
    m_targetToNativeConversions.append(TargetToNativeConversion(sourceTypeName,
                                                                   sourceTypeCheck,
                                                                   conversion));
}

TargetToNativeConversion::TargetToNativeConversion(const QString &sourceTypeName,
                                                   const QString &sourceTypeCheck,
                                                   const QString &conversion) :
    m_sourceTypeName(sourceTypeName), m_sourceTypeCheck(sourceTypeCheck),
    m_conversion(conversion)
{
}

TypeEntryCPtr TargetToNativeConversion::sourceType() const
{
    return m_sourceType;
}

void TargetToNativeConversion::setSourceType(const TypeEntryCPtr &sourceType)
{
    m_sourceType = sourceType;
}

bool TargetToNativeConversion::isCustomType() const
{
    return m_sourceType == nullptr;
}

QString TargetToNativeConversion::sourceTypeName() const
{
    return m_sourceTypeName;
}

QString TargetToNativeConversion::sourceTypeCheck() const
{
    if (!m_sourceTypeCheck.isEmpty())
        return m_sourceTypeCheck;

    if (m_sourceType != nullptr && m_sourceType->isCustom()) {
        const auto cte = std::static_pointer_cast<const CustomTypeEntry>(m_sourceType);
        if (cte->hasCheckFunction()) {
            QString result = cte->checkFunction();
            if (result != u"true") // For PyObject, which is always true
                result += u"(%in)"_s;
            return result;
        }
    }

    return {};
}

QString TargetToNativeConversion::conversion() const
{
    return m_conversion;
}

void TargetToNativeConversion::setConversion(const QString &conversion)
{
    m_conversion = conversion;
}

void TargetToNativeConversion::formatDebug(QDebug &debug) const
{
    debug << "(source=\"" << m_sourceTypeName << '"';
    if (debug.verbosity() > 2)
        debug << ", conversion=\"" << m_conversion << '"';
    if (isCustomType())
        debug << ", [custom]";
    debug << ')';
}

CustomConversionPtr CustomConversion::getCustomConversion(const TypeEntryCPtr &type)
{
    if (type->isPrimitive())
        return std::static_pointer_cast<const PrimitiveTypeEntry>(type)->customConversion();
    if (type->isContainer())
        return std::static_pointer_cast<const ContainerTypeEntry>(type)->customConversion();
    if (type->isValue())
        return std::static_pointer_cast<const ValueTypeEntry>(type)->customConversion();
    return {};
}

void CustomConversion::formatDebug(QDebug &debug) const
{
    debug << "(owner=\"" << m_ownerType->qualifiedCppName() << '"';
    if (!m_nativeToTargetConversion.isEmpty())
        debug << ", nativeToTargetConversion=\"" << m_nativeToTargetConversion << '"';
    if (!m_targetToNativeConversions.isEmpty()) {
        debug << ", targetToNativeConversions=[";
        for (qsizetype i = 0, size = m_targetToNativeConversions.size(); i < size; ++i) {
            if (i)
                debug << ", ";
            debug << m_targetToNativeConversions.at(i);

        }
        debug << ']';
    }
    if (m_replaceOriginalTargetToNativeConversions)
        debug << ", [replaceOriginalTargetToNativeConversions]";
    debug << ')';
}

QDebug operator<<(QDebug debug, const TargetToNativeConversion &t)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "TargetToNativeConversion";
    t.formatDebug(debug);
    return debug;
}

QDebug operator<<(QDebug debug, const CustomConversion &c)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "CustomConversion";
    c.formatDebug(debug);
    return debug;
}

QDebug operator<<(QDebug debug, const CustomConversionPtr &cptr)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "CustomConversionPtr";
    if (auto *c = cptr.get()) {
        c->formatDebug(debug);
    } else {
        debug << "(0)";
    }
    return debug;
}
