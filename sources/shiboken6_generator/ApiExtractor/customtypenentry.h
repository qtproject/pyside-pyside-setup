// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef CUSTOMTYPENENTRY_H
#define CUSTOMTYPENENTRY_H

#include "cpptypeentry.h"

class CustomTypeEntryPrivate;

class CustomTypeEntry : public CppTypeEntry
{
public:
    explicit CustomTypeEntry(const QString &entryName, const QVersionNumber &vr,
                             const TypeEntryCPtr &parent);

    TypeEntry *clone() const override;

    bool hasCheckFunction() const;
    QString checkFunction() const;
    void setCheckFunction(const QString &f);

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif

protected:
    explicit CustomTypeEntry(CustomTypeEntryPrivate *d);
};


#endif // CUSTOMTYPENENTRY_H
