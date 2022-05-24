// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETALANG_HELPERS_H
#define ABSTRACTMETALANG_HELPERS_H

template <class MetaClass>
MetaClass *findByName(QList<MetaClass *> haystack, QStringView needle)
{
    for (MetaClass *c : haystack) {
        if (c->name() == needle)
            return c;
    }
    return nullptr;
}

// Helper for recursing the base classes of an AbstractMetaClass.
// Returns the class for which the predicate is true.
template <class Predicate>
const AbstractMetaClass *recurseClassHierarchy(const AbstractMetaClass *klass,
                                               Predicate pred)
{
    if (pred(klass))
        return klass;
    for (auto base : klass->baseClasses()) {
        if (auto r = recurseClassHierarchy(base, pred))
            return r;
    }
    return nullptr;
}

#endif // ABSTRACTMETALANG_HELPERS_H
