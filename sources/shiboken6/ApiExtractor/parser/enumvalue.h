// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ENUMVALUE_H
#define ENUMVALUE_H

#include <QtCore/qtypes.h>
#include <QtCore/qtclasshelpermacros.h>
#include <QtCore/QtCompare>

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
    QString toHex(int fieldWidth = 0) const;

    Type type() { return m_type; }
    qint64 value() const { return m_value; }
    quint64 unsignedValue() const { return m_unsignedValue; }
    bool isNullValue() const { return m_type == Signed ? m_value == 0 : m_unsignedValue == 0u; }
    bool isNegative() const { return m_type == Signed && m_value < 0; }

    void setValue(qint64 v);
    void setUnsignedValue(quint64 v);

    EnumValue toUnsigned() const;

    bool equals(const EnumValue &rhs) const;

    void formatDebug(QDebug &d) const;
    void formatDebugHex(QDebug &d) const;

private:
    friend bool comparesEqual(const EnumValue &lhs,
                              const EnumValue &rhs) noexcept;
    Q_DECLARE_EQUALITY_COMPARABLE(EnumValue)

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
