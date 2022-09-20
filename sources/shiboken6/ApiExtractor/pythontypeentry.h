// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PYTHONTYPEENTRY_H
#define PYTHONTYPEENTRY_H

#include "customtypenentry.h"
#include "typesystem_enums.h"

class PythonTypeEntry : public CustomTypeEntry
{
public:
    explicit PythonTypeEntry(const QString &entryName,
                             const QString &checkFunction,
                             TypeSystem::CPythonType type);

    TypeEntry *clone() const override;

    TypeSystem::CPythonType cPythonType() const;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &d) const override;
#endif

protected:
    explicit PythonTypeEntry(TypeEntryPrivate *d);
};

#endif // PYTHONTYPEENTRY_H
