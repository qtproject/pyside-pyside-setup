// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBKARRAYSPAN_H
#define SBKARRAYSPAN_H

#include <cstddef>

#if __cplusplus >= 202002L
#  error "Use std::span instead"
#endif

namespace Shiboken {

// A primitive span based on pointers for C arrays, vectors and single instances.
template <class value_type>
class ArraySpan
{
public:
    using iterator = value_type*;

    explicit ArraySpan(iterator begin, iterator end) : m_begin(begin), m_end(end) {}

    iterator begin() const { return m_begin; }
    iterator end()  const { return m_end; }

    const value_type &operator[](std::size_t i) const { return *(m_begin + i); }
    value_type &operator[](std::size_t i) { return *(m_begin + i); }
    std::size_t size() const { return m_end - m_begin; }

private:
    iterator m_begin;
    iterator m_end;
};

} // namespace Shiboken

#endif // SBKARRAYSPAN_H
