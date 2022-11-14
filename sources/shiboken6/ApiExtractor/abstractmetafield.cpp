// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "abstractmetafield.h"
#include "abstractmetabuilder.h"
#include "abstractmetalang.h"
#include "abstractmetatype.h"
#include "documentation.h"
#include "modifications.h"
#include "complextypeentry.h"
#include "typesystemtypeentry.h"
#include "parser/codemodel.h"

#include "qtcompat.h"

#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

class AbstractMetaFieldData : public QSharedData
{
public:
    QString m_originalName;
    QString m_name;
    AbstractMetaType m_type;
    Documentation m_doc;
    bool m_setterEnabled = true; // Modifications
    bool m_getterEnabled = true; // Modifications
    bool m_static = false;
    Access m_access = Access::Public;
};

AbstractMetaField::AbstractMetaField() : d(new AbstractMetaFieldData)
{
}

AbstractMetaField::AbstractMetaField(const AbstractMetaField &) = default;
AbstractMetaField &AbstractMetaField::operator=(const AbstractMetaField &) = default;
AbstractMetaField::AbstractMetaField(AbstractMetaField &&) = default;
AbstractMetaField &AbstractMetaField::operator=(AbstractMetaField &&) = default;
AbstractMetaField::~AbstractMetaField() = default;

//    returned->setEnclosingClass(nullptr);

std::optional<AbstractMetaField>
    AbstractMetaField::find(const AbstractMetaFieldList &haystack,
                            QStringView needle)
{
    for (const auto &f : haystack) {
        if (f.name() == needle)
            return f;
    }
    return {};
}

/*******************************************************************************
 * Indicates that this field has a modification that removes it
 */
bool AbstractMetaField::isModifiedRemoved() const
{
    const FieldModificationList &mods = modifications();
    for (const FieldModification &mod : mods) {
        if (mod.isRemoved())
            return true;
    }

    return false;
}

bool AbstractMetaField::generateOpaqueContainer() const
{
    const FieldModificationList &mods = modifications();
    for (const FieldModification &mod : mods) {
        if (mod.isOpaqueContainer())
            return true;
    }
    return false;
}

const AbstractMetaType &AbstractMetaField::type() const
{
    return d->m_type;
}

void AbstractMetaField::setType(const AbstractMetaType &type)
{
    if (d->m_type != type)
        d->m_type = type;
}

QString AbstractMetaField::name() const
{
    return d->m_name;
}

void AbstractMetaField::setName(const QString &name)
{
    if (d->m_name != name)
        d->m_name = name;
}

Access AbstractMetaField::access() const
{
    return d->m_access;
}

void AbstractMetaField::setAccess(Access a)
{
    if (a != d->m_access)
        d->m_access = a;
}

bool AbstractMetaField::isStatic() const
{
    return d->m_static;
}

void AbstractMetaField::setStatic(bool s)
{
    if (s != d->m_static)
        d->m_static = s;
}

QString AbstractMetaField::qualifiedCppName() const
{
    return enclosingClass()->qualifiedCppName() + u"::"_s
           + originalName();
}

QStringList AbstractMetaField::definitionNames() const
{
    return AbstractMetaBuilder::definitionNames(d->m_name, snakeCase());
}

QString AbstractMetaField::originalName() const
{
    return d->m_originalName.isEmpty() ? d->m_name : d->m_originalName;
}

void AbstractMetaField::setOriginalName(const QString &name)
{
    if (d->m_originalName != name)
        d->m_originalName = name;
}

const Documentation &AbstractMetaField::documentation() const
{
    return d->m_doc;
}

void AbstractMetaField::setDocumentation(const Documentation &doc)
{
    if (d->m_doc != doc)
        d->m_doc = doc;
}

bool AbstractMetaField::isGetterEnabled() const
{
    return d->m_getterEnabled;
}

void AbstractMetaField::setGetterEnabled(bool e)
{
    if (d->m_getterEnabled != e)
        d->m_getterEnabled = e;
}

bool AbstractMetaField::isSetterEnabled() const
{
    return d->m_setterEnabled;
}

void AbstractMetaField::setSetterEnabled(bool e)
{
    if (e != d->m_setterEnabled)
        d->m_setterEnabled = e;
}

bool AbstractMetaField::canGenerateGetter() const
{
    return d->m_getterEnabled && !isStatic() && !d->m_type.isArray();
}

bool AbstractMetaField::canGenerateSetter() const
{
    return d->m_setterEnabled && !isStatic()
        && !d->m_type.isArray()
        && (!d->m_type.isConstant() || d->m_type.isPointerToConst());
}

TypeSystem::SnakeCase AbstractMetaField::snakeCase() const
{
    // Renamed?
    if (!d->m_originalName.isEmpty() && d->m_originalName != d->m_name)
        return TypeSystem::SnakeCase::Disabled;

    for (const auto &mod : modifications()) {
        if (mod.snakeCase() != TypeSystem::SnakeCase::Unspecified)
            return mod.snakeCase();
    }

    auto typeEntry = enclosingClass()->typeEntry();
    const auto snakeCase = typeEntry->snakeCase();
    return snakeCase != TypeSystem::SnakeCase::Unspecified
        ? snakeCase : typeSystemTypeEntry(typeEntry)->snakeCase();
}

FieldModificationList AbstractMetaField::modifications() const
{
    const FieldModificationList &mods = enclosingClass()->typeEntry()->fieldModifications();
    FieldModificationList returned;

    for (const FieldModification &mod : mods) {
        if (mod.name() == name())
            returned += mod;
    }

    return returned;
}

#ifndef QT_NO_DEBUG_STREAM
void AbstractMetaField::formatDebug(QDebug &d) const
{
    if (isStatic())
        d << "static ";
    d << access() << ' ' << type().name() << " \"" << name() << '"';

}

QDebug operator<<(QDebug d, const AbstractMetaField *af)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "AbstractMetaField(";
    if (af)
        af->formatDebug(d);
    else
        d << '0';
    d << ')';
    return d;
}

QDebug operator<<(QDebug d, const AbstractMetaField &af)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "AbstractMetaField(";
    af.formatDebug(d);
    d << ')';
    return d;
}
#endif // !QT_NO_DEBUG_STREAM
