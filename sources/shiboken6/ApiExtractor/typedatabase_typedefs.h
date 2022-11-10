// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPEDATABASE_TYPEDEFS_H
#define TYPEDATABASE_TYPEDEFS_H

#include "typesystem_typedefs.h"

#include <QtCore/QMultiMap>
#include <QtCore/QString>
#include <QtCore/QList>

using TemplateEntryMap =QMap<QString, TemplateEntry *>;

template <class Key, class Value>
struct QMultiMapConstIteratorRange // A range of iterator for a range-based for loop
{
    using ConstIterator = typename QMultiMap<Key, Value>::const_iterator;

    ConstIterator begin() const { return m_begin; }
    ConstIterator end() const { return m_end; }

    ConstIterator m_begin;
    ConstIterator m_end;
};

using TypeEntryMultiMap = QMultiMap<QString, TypeEntry *>;
using TypeEntryMultiMapConstIteratorRange = QMultiMapConstIteratorRange<QString, TypeEntry *>;

using TypeEntryMap = QMap<QString, TypeEntry *>;
using TypedefEntryMap = QMap<QString, TypedefEntry *>;

#endif // TYPEDATABASE_TYPEDEFS_H
