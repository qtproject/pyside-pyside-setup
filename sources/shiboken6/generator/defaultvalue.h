// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DEFAULTVALUE_H
#define DEFAULTVALUE_H

#include <QtCore/QString>

QT_FORWARD_DECLARE_CLASS(QDebug);

class DefaultValue
{
public:
    enum Type
    {
        Boolean,
        CppScalar, // A C++ scalar type (int,..) specified by value()
        Custom, // A custom constructor/expression, uses value() as is
        DefaultConstructor, // For classes named value()
        DefaultConstructorWithDefaultValues, // as DefaultConstructor, but can't return {} though.
        Enum, // Enum value as specified by value()
        Pointer, // Pointer of type value()
        Void  // "", for return values only
    };

    explicit DefaultValue(Type t, QString value = QString());
    explicit DefaultValue(QString customValue);

    QString returnValue() const;
    QString initialization() const;
    QString constructorParameter() const;

    QString value() const { return m_value; }
    void setValue(const QString &value) { m_value = value; }

    Type type() const { return m_type; }
    void setType(Type type) { m_type = type; }

private:
    Type m_type;
    QString m_value;
};

QDebug operator<<(QDebug debug, const DefaultValue &v);

#endif // DEFAULTVALUE_H
