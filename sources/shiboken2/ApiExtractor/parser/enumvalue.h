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

#ifndef ENUMVALUE_H
#define ENUMVALUE_H

#include <QtCore/QtGlobal>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QString)
QT_FORWARD_DECLARE_CLASS(QTextStream)

class EnumValue
{
public:
    enum Type
    {
        Signed,
        Unsigned
    };

    QString toString() const;

    Type type() { return m_type; }
    qint64 value() const { return m_value; }
    quint64 unsignedValue() const { return m_unsignedValue; }
    bool isNullValue() const { return m_type == Signed ? m_value == 0 : m_unsignedValue == 0u; }

    void setValue(qint64 v);
    void setUnsignedValue(quint64 v);

private:
#ifndef QT_NO_DEBUG_STREAM
    friend QDebug operator<<(QDebug, const EnumValue &);
#endif
    friend QTextStream &operator<<(QTextStream &, const EnumValue &);

    union
    {
        qint64 m_value = 0;
        quint64 m_unsignedValue;
    };
    Type m_type = Signed;
};

#endif // ENUMVALUE_H
