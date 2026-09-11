// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_CACHESLOT_H
#define SBK_CACHESLOT_H

#include "sbkpython.h"

#ifdef Py_GIL_DISABLED
#  include <atomic>
#endif

namespace Shiboken {

/// One slot of a lazily filled cache in generated wrapper code: the name of a
/// virtual method, and the Python override found for it.
///
/// Several threads reaching the same virtual method for the first time all
/// find the slot empty and all compute the value. They compute the same one,
/// so the cache is never wrong - what a plain pointer costs is a reference
/// per lost race, because only the pointer that ends up in the slot is ever
/// owned by anyone, and a data race that a sanitizer reports on every run -
/// the kind of noise a real finding hides in.
///
/// The slot does not order anything else. It holds one pointer and says who
/// won.
class CacheSlot
{
public:
    CacheSlot() noexcept = default;
    CacheSlot(const CacheSlot &) = delete;
    CacheSlot &operator=(const CacheSlot &) = delete;

#ifdef Py_GIL_DISABLED
    /// The value, or null while nobody has published one. Borrowed: the slot
    /// keeps the reference for the life of the process.
    PyObject *get() const noexcept
    {
        return m_value.load(std::memory_order_acquire);
    }

    /// Publish \a candidate, a reference the caller owns. Returns what the
    /// slot holds afterwards: the candidate if this call won, the winner's
    /// value if it lost - and the losing reference is dropped here, which is
    /// the whole point. Null is a candidate too: interning can fail, and a
    /// failed candidate must not become the slot's value.
    PyObject *publish(PyObject *candidate) noexcept
    {
        if (candidate == nullptr)
            return m_value.load(std::memory_order_acquire);
        PyObject *expected = nullptr;
        if (m_value.compare_exchange_strong(expected, candidate,
                                            std::memory_order_release,
                                            std::memory_order_acquire)) {
            return candidate;
        }
        Py_DECREF(candidate);
        return expected;
    }

    /// Empty the slot. Used where feature switching invalidates what was
    /// cached; the reference is deliberately not dropped, as it was not
    /// dropped before either - these are interned strings and overrides the
    /// process keeps anyway.
    void reset() noexcept { m_value.store(nullptr, std::memory_order_release); }

private:
    std::atomic<PyObject *> m_value{nullptr};

#else // Py_GIL_DISABLED

    PyObject *get() const noexcept { return m_value; }

    PyObject *publish(PyObject *candidate) noexcept
    {
        if (candidate != nullptr)
            m_value = candidate;
        return m_value;
    }

    void reset() noexcept { m_value = nullptr; }

private:
    PyObject *m_value{nullptr};
#endif // Py_GIL_DISABLED
};

#ifdef Py_GIL_DISABLED
static_assert(std::atomic<PyObject *>::is_always_lock_free,
              "CacheSlot must not compile to a mutex");
#endif
static_assert(sizeof(CacheSlot) == sizeof(PyObject *)
              && alignof(CacheSlot) == alignof(PyObject *),
              "CacheSlot must cost no more than the pointer it replaces");

} // namespace Shiboken

#endif // SBK_CACHESLOT_H
