// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "defaultvalue.h"

#include "qtcompat.h"

#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

// DefaultValue is used for storing default values of types for which code is
// generated in different contexts:
//
// Context             | Example: "Class *"            | Example: "Class" with default Constructor
// --------------------+-------------------------------+------------------------------------------
// Variable            |  var{nullptr};                | var;
// initializations     |                               |
// --------------------+-------------------------------+------------------------------------------
// Return values       | return nullptr;               | return {}
// --------------------+-------------------------------+------------------------------------------
// constructor         | static_cast<Class *>(nullptr) | Class()
// arguments lists     |                               |
// (recursive, precise |                               |
// matching).          |                               |

DefaultValue::DefaultValue(Type t, QString value) :
    m_type(t), m_value(std::move(value))
{
}

DefaultValue::DefaultValue(QString customValue) :
    m_type(Custom), m_value(std::move(customValue))
{
}

QString DefaultValue::returnValue() const
{
    switch (m_type) {
    case DefaultValue::Boolean:
        return u"false"_s;
    case DefaultValue::CppScalar:
        return u"0"_s;
    case DefaultValue::Custom:
    case DefaultValue::Enum:
        return m_value;
    case DefaultValue::Pointer:
        return u"nullptr"_s;
    case DefaultValue::Void:
        return QString();
    case DefaultValue::DefaultConstructorWithDefaultValues:
        return m_value + u"()"_s;
    case DefaultValue::DefaultConstructor:
        break;
    }
    return u"{}"_s;
}

QString DefaultValue::initialization() const
{
    switch (m_type) {
    case DefaultValue::Boolean:
        return u"{false}"_s;
    case DefaultValue::CppScalar:
        return u"{0}"_s;
    case DefaultValue::Custom:
        return u" = "_s + m_value;
    case DefaultValue::Enum:
        return u'{' + m_value + u'}';
    case DefaultValue::Pointer:
        return u"{nullptr}"_s;
    case DefaultValue::Void:
        Q_ASSERT(false);
        break;
    case DefaultValue::DefaultConstructor:
    case DefaultValue::DefaultConstructorWithDefaultValues:
        break;
    }
    return QString();
}

QString DefaultValue::constructorParameter() const
{
    switch (m_type) {
    case DefaultValue::Boolean:
        return u"false"_s;
    case DefaultValue::CppScalar: {
        // PYSIDE-846: Use static_cast in case of "unsigned long" and similar
        const QString cast = m_value.contains(u' ')
            ? u"static_cast<"_s + m_value + u'>'
            : m_value;
        return cast + u"(0)"_s;
    }
    case DefaultValue::Custom:
    case DefaultValue::Enum:
        return m_value;
    case DefaultValue::Pointer:
        // Be precise here to be able to differentiate between constructors
        // taking different pointer types, cf
        // QTreeWidgetItemIterator(QTreeWidget *) and
        // QTreeWidgetItemIterator(QTreeWidgetItemIterator *).
        return u"static_cast<"_s + m_value + u"*>(nullptr)"_s;
    case DefaultValue::Void:
        Q_ASSERT(false);
        break;
    case DefaultValue::DefaultConstructor:
    case DefaultValue::DefaultConstructorWithDefaultValues:
        break;
    }
    return m_value + u"()"_s;
}

QDebug operator<<(QDebug debug, const DefaultValue &v)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "DefaultValue(" <<  v.type() << ", \"" << v.value() << "\")";
    return debug;
}
