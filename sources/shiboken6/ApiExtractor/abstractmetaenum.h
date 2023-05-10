// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETAENUM_H
#define ABSTRACTMETAENUM_H

#include "abstractmetalang_typedefs.h"
#include "enclosingclassmixin.h"
#include "parser/codemodel_enums.h"
#include "typesystem_typedefs.h"

#include <QtCore/QSharedDataPointer>
#include <QtCore/QString>

#include <optional>

QT_FORWARD_DECLARE_CLASS(QDebug)

class AbstractMetaEnumData;
class AbstractMetaEnumValueData;
class Documentation;
class EnumValue;
class EnumTypeEntry;

class AbstractMetaEnumValue
{
public:
    AbstractMetaEnumValue();
    AbstractMetaEnumValue(const AbstractMetaEnumValue &);
    AbstractMetaEnumValue &operator=(const AbstractMetaEnumValue &);
    AbstractMetaEnumValue(AbstractMetaEnumValue &&);
    AbstractMetaEnumValue &operator=(AbstractMetaEnumValue &&);
    ~AbstractMetaEnumValue();

    EnumValue value() const;
    void setValue(EnumValue value);

    QString stringValue() const;
    void setStringValue(const QString &v);

    QString name() const;
    void setName(const QString &name);

    bool isDeprecated() const;
    void setDeprecated(bool deprecated);

    Documentation documentation() const;
    void setDocumentation(const Documentation& doc);

private:
    QSharedDataPointer<AbstractMetaEnumValueData> d;
};

class AbstractMetaEnum : public EnclosingClassMixin
{
public:
    AbstractMetaEnum();
    AbstractMetaEnum(const AbstractMetaEnum &);
    AbstractMetaEnum &operator=(const AbstractMetaEnum &);
    AbstractMetaEnum(AbstractMetaEnum &&);
    AbstractMetaEnum &operator=(AbstractMetaEnum &&);
    ~AbstractMetaEnum();

    const AbstractMetaEnumValueList &values() const;
    void addEnumValue(const AbstractMetaEnumValue &enumValue);

    std::optional<AbstractMetaEnumValue> findEnumValue(QStringView value) const;

    QString name() const;
    QString qualifiedCppName() const;

    Access access() const;
    void setAccess(Access a);
    bool isPrivate() const { return access() == Access::Private; }
    bool isProtected() const { return access() == Access::Protected; }

    bool isDeprecated() const;
    void setDeprecated(bool deprecated);
    bool hasDeprecatedValues() const;
    AbstractMetaEnumValueList deprecatedValues() const;

    const Documentation &documentation() const;
    void setDocumentation(const Documentation& doc);

    QString qualifier() const;

    QString package() const;

    QString fullName() const;

    EnumKind enumKind() const;
    void setEnumKind(EnumKind kind);

    bool isAnonymous() const;

    // Has the enum been declared inside a Q_ENUMS() macro in its enclosing class?
    bool hasQEnumsDeclaration() const;
    void setHasQEnumsDeclaration(bool on);

    EnumTypeEntryCPtr typeEntry() const;
    void setTypeEntry(const EnumTypeEntryCPtr &entry);

    bool isSigned() const;
    void setSigned(bool s);

private:
    QSharedDataPointer<AbstractMetaEnumData> d;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const AbstractMetaEnumValue &ae);
QDebug operator<<(QDebug d, const AbstractMetaEnum *ae);
QDebug operator<<(QDebug d, const AbstractMetaEnum &ae);
#endif

#endif // ABSTRACTMETAENUM_H
