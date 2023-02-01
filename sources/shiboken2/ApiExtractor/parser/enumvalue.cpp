/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d,const EnumValue &v)
{
    QDebugStateSaver saver(d);
    d.nospace();
    d.noquote();
    d << "EnumValue(";
    if (v.m_type == EnumValue::Signed)
        d << v.m_value;
    else
        d << v.m_unsignedValue << 'u';
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
