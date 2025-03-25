// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OVERRIDECACHEENTRY_H
#define OVERRIDECACHEENTRY_H

#include <abstractmetafunction.h>
#include <modifications.h>

#include <QtCore/qhash.h>

// Cache a (virtual function) by types and modifications for reusing Python
// override code.
class OverrideCacheEntry
{
public:
    explicit OverrideCacheEntry(const AbstractMetaFunctionCPtr &f);

    const AbstractMetaFunctionCPtr &function() const { return m_func; }

    size_t hashValue(size_t seed) const noexcept;

private:
    bool equals(const OverrideCacheEntry &rhs) const noexcept;

    friend bool comparesEqual(const OverrideCacheEntry &lhs,
                              const OverrideCacheEntry &rhs) noexcept
    { return lhs.equals(rhs); }

    Q_DECLARE_EQUALITY_COMPARABLE(OverrideCacheEntry)

    AbstractMetaFunctionCPtr m_func;
    QList<AbstractMetaType> m_types;
    FunctionModificationList m_modifications;
};

inline size_t qHash(const OverrideCacheEntry &e, size_t seed = 0) noexcept
{
    return e.hashValue(seed);
}

#endif // OVERRIDECACHEENTRY_H
