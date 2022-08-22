// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "enumvalue.h"

#include <QtCore/QDebug>
#include <QtCore/QString>
#include <QtCore/QTextStream>

QString EnumValue::toString() const
{
    return m_type == EnumValue::Signed
        ? QString::number(m_value) : QString::number(m_unsignedValue);
}

void EnumValue::setValue(qint64 v)
{
    m_value = v;
    m_type = Signed;
}

void EnumValue::setUnsignedValue(quint64 v)
{
    m_unsignedValue = v;
    m_type = Unsigned;
}

bool EnumValue::equals(const EnumValue &rhs) const
{
    if (m_type != rhs.m_type)
        return false;
    return m_type == Signed ? m_value == rhs.m_value : m_unsignedValue == rhs.m_unsignedValue;
}

void EnumValue::formatDebug(QDebug &d) const
{
    if (m_type == EnumValue::Signed)
        d << m_value;
    else
        d << m_unsignedValue << 'u';
}

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d,const EnumValue &v)
{
    QDebugStateSaver saver(d);
    d.nospace();
    d.noquote();
    d << "EnumValue(";
    v.formatDebug(d);
    d << ')';
    return d;
}
#endif // !QT_NO_DEBUG_STREAM

QTextStream &operator<<(QTextStream &s, const EnumValue &v)
{
    if (v.m_type == EnumValue::Signed)
        s << v.m_value;
    else
        s << v.m_unsignedValue;
    return s;
}
