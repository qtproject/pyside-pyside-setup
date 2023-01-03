// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETALANG_HELPERS_H
#define ABSTRACTMETALANG_HELPERS_H

#include "abstractmetalang_typedefs.h"

template <class MetaClass>
std::shared_ptr<MetaClass> findByName(const QList<std::shared_ptr<MetaClass> > &haystack,
                                      QStringView needle)
{
    for (const auto &c : haystack) {
        if (c->name() == needle)
            return c;
    }
    return {};
}

// Helper for recursing the base classes of an AbstractMetaClass.
// Returns the class for which the predicate is true.
template <class Predicate>
AbstractMetaClassCPtr recurseClassHierarchy(const AbstractMetaClassCPtr &klass,
                                            Predicate pred)
{
    if (pred(klass))
        return klass;
    for (auto base : klass->baseClasses()) {
        if (auto r = recurseClassHierarchy(base, pred))
            return r;
    }
    return {};
}

#endif // ABSTRACTMETALANG_HELPERS_H
