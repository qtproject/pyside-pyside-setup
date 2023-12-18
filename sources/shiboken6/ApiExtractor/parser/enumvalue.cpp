// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "enumvalue.h"

#include <QtCore/QDebug>
#include <QtCore/QString>
#include <QtCore/QTextStream>

using namespace Qt::StringLiterals;

QString EnumValue::toString() const
{
    return m_type == EnumValue::Signed
        ? QString::number(m_value) : QString::number(m_unsignedValue);
}

QString EnumValue::toHex(int fieldWidth) const
{
    QString result;
    QTextStream str(&result);
    // Note: Qt goofes up formatting of negative padded hex numbers, it ends up
    // with "0x00-1". Write '-' before.
    if (isNegative())
        str << '-';
    str << "0x" << Qt::hex;
    if (fieldWidth) {
        str.setFieldWidth(fieldWidth);
        str.setPadChar(u'0');
    }
    if (m_type == EnumValue::Signed)
        str << qAbs(m_value);
    else
        str << m_unsignedValue;
    return result;
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

EnumValue EnumValue::toUnsigned() const
{
    if (m_type == Unsigned)
        return *this;
    EnumValue result;
    result.setUnsignedValue(m_value < 0 ? quint64(-m_value) : quint64(m_value));
    return result;
}

bool comparesEqual(const EnumValue &lhs, const EnumValue &rhs) noexcept
{
    if (lhs.m_type != rhs.m_type)
        return false;
    return lhs.m_type == EnumValue::Signed
        ? lhs.m_value == rhs.m_value : lhs.m_unsignedValue == rhs.m_unsignedValue;
}

void EnumValue::formatDebugHex(QDebug &d) const
{
    d << "0x" << Qt::hex;
    formatDebug(d);
    d << Qt::dec;
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
