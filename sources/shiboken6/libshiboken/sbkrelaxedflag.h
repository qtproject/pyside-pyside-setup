// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_RELAXEDFLAG_H
#define SBK_RELAXEDFLAG_H

#include "sbkpython.h"

#ifdef Py_GIL_DISABLED

#include <atomic>

namespace Shiboken {

/// A boolean that is written from threads which may not hold the state lock.
///
/// It exists for the memory model, not for the machine: on every target we
/// build for a relaxed load and store compile to the same ldrb/strb a plain
/// bool does, but a plain bool written by two threads is a data race and this
/// is not.
///
/// It gives no ordering and no atomicity beyond the single flag. Making two
/// flags agree, or a flag agree with cptr, remains the state lock's job.
class RelaxedFlag
{
public:
    RelaxedFlag() noexcept = default;
    RelaxedFlag(const RelaxedFlag &) = delete;
    RelaxedFlag &operator=(const RelaxedFlag &) = delete;

    RelaxedFlag &operator=(bool value) noexcept
    {
        m_value.store(value, std::memory_order_relaxed);
        return *this;
    }

    operator bool() const noexcept
    {
        return m_value.load(std::memory_order_relaxed);
    }

private:
    std::atomic<bool> m_value;
};

static_assert(std::atomic<bool>::is_always_lock_free,
              "RelaxedFlag must not compile to a mutex");
static_assert(sizeof(RelaxedFlag) == 1 && alignof(RelaxedFlag) == 1,
              "RelaxedFlag must cost no more than the bool it replaces");

} // namespace Shiboken

#endif // Py_GIL_DISABLED

#endif // SBK_RELAXEDFLAG_H
