// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:build-tool

#include "overridecacheentry.h"

#include <abstractmetaargument.h>
#include <abstractmetatype.h>

OverrideCacheEntry::OverrideCacheEntry(const AbstractMetaFunctionCPtr &f) :
    m_func(f), m_modifications(f->modifications())
{
    m_types.reserve(1 + m_func->arguments().size());
    m_types.append(m_func->type());
    for (const auto &arg: m_func->arguments())
        m_types.append(arg.type());
}

bool OverrideCacheEntry::equals(const OverrideCacheEntry &rhs) const noexcept
{
    return m_types == rhs.m_types && m_modifications == rhs.m_modifications;
}

size_t OverrideCacheEntry::hashValue(size_t seed) const noexcept
{
    return qHashMulti(seed,
                      qHashRange(m_types.cbegin(), m_types.cend(), seed),
                      qHashRange(m_modifications.cbegin(), m_modifications.cend(), seed));
}
