// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "sbkcallguard.h"

#ifdef Py_GIL_DISABLED

#include "sbkftoptions.h"

#include <array>
#include <cstdlib>

namespace Shiboken::Object {

// A power of two, so the index is a mask. The table has to be one instance for
// the whole process, which is why it lives here and not in the header:
// -fvisibility=hidden would otherwise give every module a copy of its own.
static constexpr std::size_t StripeCount = 1024;

// PyMutex is a single byte, so an unpadded table would put 64 stripes on one
// cache line and two threads locking unrelated objects would still bounce it
// between cores. That is not a corner case: objects a program creates in a
// row get neighbouring addresses and therefore neighbouring stripes, so the
// natural layout is the bad one. Eight threads calling methods on eight
// freshly made objects, with the state lock out of the way so this is what is
// being measured: 0.15s padded against 0.58s unpadded, where no guard at all
// is 0.14s. The table costs 64 KB.
struct alignas(64) PaddedMutex
{
    PyMutex mutex;
    char padding[64 - sizeof(PyMutex)];
};

static std::array<PaddedMutex, StripeCount> &stripes()
{
    static std::array<PaddedMutex, StripeCount> table{};
    return table;
}

// How many entries are actually used, read once. One makes the guard a single
// process-wide lock, which is the coarse binding lock again.
static std::size_t activeStripes()
{
    static const std::size_t count = [] {
        const char *e = std::getenv("PYSIDE6_FT_CALLGUARD_STRIPES");
        if (e == nullptr || *e == '\0')
            return StripeCount;
        const long value = std::strtol(e, nullptr, 10);
        if (value < 1)
            return StripeCount;
        std::size_t n = 1;
        while (n * 2 <= static_cast<std::size_t>(value) && n * 2 <= StripeCount)
            n *= 2;
        return n;
    }();
    return count;
}

static PyMutex *mutexFor(const void *cppObject)
{
    // The low bits of an allocation are alignment padding and carry no
    // information, so shift them out before masking.
    const auto value = reinterpret_cast<std::uintptr_t>(cppObject) >> 4;
    return &stripes()[value & (activeStripes() - 1)].mutex;
}

void CallGuard::acquire(const void *cppObject)
{
    if (cppObject == nullptr
        || !FreeThreading::optionEnabled(FreeThreading::CallGuard)) {
        return;
    }

    PyCriticalSection_BeginMutex(&m_section, mutexFor(cppObject));
    m_active = true;
}

void CallGuard::release()
{
    if (m_active) {
        PyCriticalSection_End(&m_section);
        m_active = false;
    }
}

} // namespace Shiboken::Object

#endif // Py_GIL_DISABLED
