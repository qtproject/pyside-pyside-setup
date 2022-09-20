// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETAARGUMENT_H
#define ABSTRACTMETAARGUMENT_H

#include <QtCore/QSharedDataPointer>

QT_FORWARD_DECLARE_CLASS(QDebug)

class AbstractMetaType;
class AbstractMetaArgumentData;
class Documentation;

class AbstractMetaArgument
{
public:
    AbstractMetaArgument();
    ~AbstractMetaArgument();
    AbstractMetaArgument(const AbstractMetaArgument &);
    AbstractMetaArgument &operator=(const AbstractMetaArgument &);
    AbstractMetaArgument(AbstractMetaArgument &&);
    AbstractMetaArgument &operator=(AbstractMetaArgument &&);


    const AbstractMetaType &type() const;
    void setType(const AbstractMetaType &type);
    void setModifiedType(const AbstractMetaType &type);
    const AbstractMetaType &modifiedType() const;
    bool isTypeModified() const;

    bool isModifiedRemoved() const;
    void setModifiedRemoved(bool v);

    QString name() const;
    void setName(const QString &name, bool realName = true);
    bool hasName() const;

    void setDocumentation(const Documentation& doc);
    Documentation documentation() const;

    QString defaultValueExpression() const;
    void setDefaultValueExpression(const QString &expr);

    QString originalDefaultValueExpression() const;
    void setOriginalDefaultValueExpression(const QString &expr);

    bool hasDefaultValueExpression() const;
    bool hasOriginalDefaultValueExpression() const;
    bool hasUnmodifiedDefaultValueExpression() const;
    bool hasModifiedDefaultValueExpression() const;

    QString toString() const;

    int argumentIndex() const;
    void setArgumentIndex(int argIndex);

private:
    QSharedDataPointer<AbstractMetaArgumentData> d;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const AbstractMetaArgument &aa);
QDebug operator<<(QDebug d, const AbstractMetaArgument *aa);
#endif

#endif // ABSTRACTMETAARGUMENT_H
