// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PROPERTYSPEC_H
#define PROPERTYSPEC_H

class AbstractMetaType;

#include "abstractmetalang_typedefs.h"
#include "typesystem_typedefs.h"

#include <QtCore/QStringList>
#include <QtCore/QSharedDataPointer>

#include <optional>

class AbstractMetaClass;
class AbstractMetaBuilderPrivate;
class AbstractMetaType;
class Documentation;
class TypeEntry;

struct TypeSystemProperty;

class QPropertySpecData;

QT_FORWARD_DECLARE_CLASS(QDebug)

class QPropertySpec
{
public:
    explicit QPropertySpec(const TypeSystemProperty &ts,
                           const AbstractMetaType &type);
    QPropertySpec(const QPropertySpec &);
    QPropertySpec &operator=(const QPropertySpec &);
    QPropertySpec(QPropertySpec &&);
    QPropertySpec &operator=(QPropertySpec &&);
    ~QPropertySpec();

    static TypeSystemProperty typeSystemPropertyFromQ_Property(const QString &declarationIn,
                                                               QString *errorMessage);


    static std::optional<QPropertySpec>
        fromTypeSystemProperty(AbstractMetaBuilderPrivate *b,
                               const AbstractMetaClassPtr &metaClass,
                               const TypeSystemProperty &ts,
                               const QStringList &scopes,
                               QString *errorMessage);

    static std::optional<QPropertySpec>
        parseQ_Property(AbstractMetaBuilderPrivate *b,
                        const AbstractMetaClassPtr &metaClass,
                        const QString &declarationIn,
                        const QStringList &scopes,
                        QString *errorMessage);

    const AbstractMetaType &type() const;
    void setType(const AbstractMetaType &t);

    TypeEntryCPtr typeEntry() const;

    QString name() const;
    void setName(const QString &name);

    Documentation documentation() const;
    void setDocumentation(const Documentation &doc);

    QString read() const;
    void setRead(const QString &read);

    QString write() const;
    void setWrite(const QString &write);
    bool hasWrite() const;

    QString designable() const;
    void setDesignable(const QString &designable);

    QString reset() const;
    void setReset(const QString &reset);

    QString notify() const; // Q_PROPERTY/C++ only
    void setNotify(const QString &notify);

    int index() const;
    void setIndex(int index);

    // Indicates whether actual code is generated instead of relying on libpyside.
    bool generateGetSetDef() const;
    void setGenerateGetSetDef(bool generateGetSetDef);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const;
#endif

private:
    QSharedDataPointer<QPropertySpecData> d;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const QPropertySpec &p);
#endif

#endif // PROPERTYSPEC_H
