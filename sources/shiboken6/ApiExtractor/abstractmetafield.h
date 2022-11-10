// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETAFIELD_H
#define ABSTRACTMETAFIELD_H

#include "abstractmetalang_typedefs.h"
#include "parser/codemodel_enums.h"
#include "typesystem_enums.h"
#include "modifications_typedefs.h"
#include "typesystem_typedefs.h"
#include "enclosingclassmixin.h"

#include <QtCore/QSharedDataPointer>

#include <optional>

QT_FORWARD_DECLARE_CLASS(QDebug)

class Documentation;
class AbstractMetaFieldData;

class AbstractMetaField : public EnclosingClassMixin
{
public:
    AbstractMetaField();
    AbstractMetaField(const AbstractMetaField &);
    AbstractMetaField &operator=(const AbstractMetaField &);
    AbstractMetaField(AbstractMetaField &&);
    AbstractMetaField &operator=(AbstractMetaField &&);
    ~AbstractMetaField();

    FieldModificationList modifications() const;

    bool isModifiedRemoved() const;
    bool generateOpaqueContainer() const;

    const AbstractMetaType &type() const;
    void setType(const AbstractMetaType &type);

    QString name() const;
    void setName(const QString &name);

    Access access() const;
    void setAccess(Access a);
    bool isPrivate() const { return access() == Access::Private; }
    bool isProtected() const { return access() == Access::Protected; }

    bool isStatic() const;
    void setStatic(bool s);

    QString qualifiedCppName() const;

    // Names under which the field will be registered to Python.
    QStringList definitionNames() const;

    QString originalName() const;
    void setOriginalName(const QString& name);

    const Documentation &documentation() const;
    void setDocumentation(const Documentation& doc);

    bool isGetterEnabled() const; // Modifications
    void setGetterEnabled(bool e);
    bool isSetterEnabled() const; // Modifications
    void setSetterEnabled(bool e);

    bool canGenerateGetter() const;
    bool canGenerateSetter() const;

    TypeSystem::SnakeCase snakeCase() const;

    static std::optional<AbstractMetaField>
        find(const AbstractMetaFieldList &haystack, QStringView needle);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const;
#endif
private:
    QSharedDataPointer<AbstractMetaFieldData> d;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const AbstractMetaField *af);
QDebug operator<<(QDebug d, const AbstractMetaField &af);
#endif

#endif // ABSTRACTMETAFIELD_H
