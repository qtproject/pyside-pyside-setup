// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "abstractmetaargument.h"
#include "abstractmetatype.h"
#include "documentation.h"

#include "qtcompat.h"

#include <QtCore/QDebug>
#include <QtCore/QSharedData>

using namespace Qt::StringLiterals;

class AbstractMetaArgumentData : public QSharedData
{
public:
    QString toString() const;

    QString m_name;
    AbstractMetaType m_type;
    AbstractMetaType m_modifiedType;
    bool m_hasName = false;
    Documentation m_doc;
    QString m_expression;
    QString m_originalExpression;
    int m_argumentIndex = 0;
    bool m_modifiedRemoved = false;
};

AbstractMetaArgument::AbstractMetaArgument() : d(new AbstractMetaArgumentData)
{
}

AbstractMetaArgument::~AbstractMetaArgument() = default;

AbstractMetaArgument::AbstractMetaArgument(const AbstractMetaArgument &) = default;

AbstractMetaArgument &AbstractMetaArgument::operator=(const AbstractMetaArgument &) = default;

AbstractMetaArgument::AbstractMetaArgument(AbstractMetaArgument &&) = default;

AbstractMetaArgument &AbstractMetaArgument::operator=(AbstractMetaArgument &&) = default;

const AbstractMetaType &AbstractMetaArgument::type() const
{
    return d->m_type;
}

void AbstractMetaArgument::setType(const AbstractMetaType &type)
{
    if (d->m_type != type)
        d->m_type = d->m_modifiedType = type;
}

const AbstractMetaType &AbstractMetaArgument::modifiedType() const
{
    return d->m_modifiedType;
}

bool AbstractMetaArgument::isTypeModified() const
{
    return modifiedType() != type();
}

bool AbstractMetaArgument::isModifiedRemoved() const
{
    return d->m_modifiedRemoved;
}

void AbstractMetaArgument::setModifiedRemoved(bool v)
{
    if (d->m_modifiedRemoved != v)
        d->m_modifiedRemoved = v;
}

void AbstractMetaArgument::setModifiedType(const AbstractMetaType &type)
{
    if (d->m_modifiedType != type)
        d->m_modifiedType = type;
}

QString AbstractMetaArgument::name() const
{
    return d->m_name;
}

void AbstractMetaArgument::setName(const QString &name, bool realName)
{
    if (d->m_name != name || d->m_hasName != realName) {
        d->m_name = name;
        d->m_hasName = realName;
    }
}

bool AbstractMetaArgument::hasName() const
{
    return d->m_hasName;
}

void AbstractMetaArgument::setDocumentation(const Documentation &doc)
{
    if (d->m_doc != doc)
        d->m_doc = doc;
}

Documentation AbstractMetaArgument::documentation() const
{
    return d->m_doc;
}

QString AbstractMetaArgument::defaultValueExpression() const
{
    return d->m_expression;
}

void AbstractMetaArgument::setDefaultValueExpression(const QString &expr)
{
    if (d->m_expression != expr)
        d->m_expression = expr;
}

QString AbstractMetaArgument::originalDefaultValueExpression() const
{
    return d->m_originalExpression;
}

void AbstractMetaArgument::setOriginalDefaultValueExpression(const QString &expr)
{
    if (d->m_originalExpression != expr)
        d->m_originalExpression = expr;
}

bool AbstractMetaArgument::hasOriginalDefaultValueExpression() const
{
    return !d->m_originalExpression.isEmpty();
}

bool AbstractMetaArgument::hasDefaultValueExpression() const
{
    return !d->m_expression.isEmpty();
}

bool AbstractMetaArgument::hasUnmodifiedDefaultValueExpression() const
{
    return !d->m_originalExpression.isEmpty() && d->m_originalExpression == d->m_expression;
}

bool AbstractMetaArgument::hasModifiedDefaultValueExpression() const
{
    return !d->m_expression.isEmpty() && d->m_originalExpression != d->m_expression;
}

QString AbstractMetaArgumentData::toString() const
{
    QString result = m_type.name() + u' ' + m_name;
    if (!m_expression.isEmpty())
        result += u" = "_s + m_expression;
    return result;
}

QString AbstractMetaArgument::toString() const
{
    return d->toString();
}

int AbstractMetaArgument::argumentIndex() const
{
    return d->m_argumentIndex;
}

void AbstractMetaArgument::setArgumentIndex(int argIndex)
{
    if (d->m_argumentIndex != argIndex)
        d->m_argumentIndex = argIndex;
}

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const AbstractMetaArgument &aa)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "AbstractMetaArgument(" << aa.toString() << ')';
    return d;
}

QDebug operator<<(QDebug d, const AbstractMetaArgument *aa)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "AbstractMetaArgument(";
    if (aa)
        d << aa->toString();
    else
        d << '0';
    d << ')';
    return d;
}
#endif // !QT_NO_DEBUG_STREAM
