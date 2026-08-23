// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_CALLGUARD_H
#define SBK_CALLGUARD_H

#include "sbkpython.h"
#include "shibokenmacros.h"

#ifdef Py_GIL_DISABLED

#  include <cstdint>
#  if defined(Py_LIMITED_API)
// Under the limited API (abi3t) critical_section.h exposes PyCriticalSection
// and PyCriticalSection_End(), but PyMutex and PyCriticalSection_BeginMutex()
// live in the cpython/ headers. The mutex is a single zero-initializable byte
// and the entry point is exported, so declare the little that is used here.
extern "C" {
typedef struct PyMutex { uint8_t _bits; } PyMutex;
PyAPI_FUNC(void) PyCriticalSection_BeginMutex(PyCriticalSection *c, PyMutex *m);
}
#  endif

namespace Shiboken::Object {

/**
 * Keeps two threads out of the same wrapped C++ object for the duration of a
 * call.
 *
 * Qt is not thread-safe per instance, and until the generated wrappers moved
 * to the state lock the coarse binding lock kept that rule by accident: it was
 * taken at the entry of every wrapper. What replaced it protects the binding's
 * bookkeeping, not the object underneath, and the difference is a crash -
 * eight threads on one QObject's setter corrupt the heap inside Qt and the
 * process aborts.
 *
 * The lock is a PyCriticalSection over a PyMutex, exactly as the coarse lock
 * was, and for the same reason: that gives it the GIL's *release* semantics,
 * not merely its exclusion semantics. Whenever the holder detaches its thread
 * state - a blocking call, a contended section, an import - the runtime
 * suspends the section and hands the mutex over, then resumes it. A raw mutex
 * held across such a wait deadlocks against anyone who needs the same object
 * to make progress; that was measured, twice, before this went back to the
 * primitive the coarse lock had already been using.
 *
 * What is new is the granularity. The mutex is chosen by the object's address
 * out of a fixed table, so calls on different objects run in parallel, where
 * the coarse lock serialized all of them. Two unrelated objects can share an
 * entry and serialize needlessly; PYSIDE6_FT_CALLGUARD_STRIPES sizes the table
 * and 1 turns the guard back into a single process-wide lock, so the two can
 * be compared in one binary.
 *
 * The window this leaves - another thread may change the object while this one
 * is suspended inside Python - is the window a build with a GIL has always
 * had. Matching it is the goal; closing it is not.
 *
 * Constructing a guard requires an attached Python thread state.
 */
class LIBSHIBOKEN_API CallGuard
{
public:
    CallGuard(const CallGuard &) = delete;
    CallGuard &operator=(const CallGuard &) = delete;
    CallGuard(CallGuard &&) = delete;
    CallGuard &operator=(CallGuard &&) = delete;

    CallGuard() noexcept = default;
    ~CallGuard() { release(); }

    /// Enter the section for cppObject. A null pointer needs no guard.
    void acquire(const void *cppObject);

    /// Leave it early. The destructor does the same, but the lease has to let
    /// go before it may run the C++ destructor.
    void release();

private:
    PyCriticalSection m_section;
    bool m_active = false;
};

} // namespace Shiboken::Object

#endif // Py_GIL_DISABLED

#endif // SBK_CALLGUARD_H
