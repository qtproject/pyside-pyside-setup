// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_CALLLEASE_H
#define SBK_CALLLEASE_H

#include "sbkpython.h"
#include "shibokenmacros.h"

#ifdef Py_GIL_DISABLED

#include "sbkcallguard.h"

struct SbkObject;

namespace Shiboken::Object {

/**
 * A lease on the C++ object of a wrapper, held across a call into C++.
 *
 * Replaces the isValid() check that used to precede a C++ call. The check alone
 * is not enough once the binding layer is no longer serialized by one coarse
 * lock: between the check and the call, another thread could run
 * Shiboken.delete() and free the C++ object the call is about to use.
 *
 * Construction validates the wrapper and increments its active call count in
 * one state transaction; destruction decrements it. Destruction requested while
 * a lease is outstanding is *marked and deferred*, never waited for: waiting
 * would deadlock whenever the in-flight call needs the deleting thread. The
 * last lease to be released runs the destructor, with no lock held.
 *
 * A lease is not a lock. It says nothing about calling a Qt class concurrently:
 * Qt thread affinity and class-specific thread-safety rules still apply. It
 * also does not keep the Python wrapper alive - the caller's own reference
 * does.
 *
 * Non-wrapper arguments (nullptr, None, a type, a plain Python object) are
 * accepted and produce an inactive, valid lease, so it can replace isValid()
 * one for one at generated call sites.
 *
 * Free-threaded builds only. With a GIL the generated code keeps the isValid()
 * check it always had, and nothing else asks for a lease.
 */
class LIBSHIBOKEN_API CallLease
{
public:
    CallLease(const CallLease &) = delete;
    CallLease &operator=(const CallLease &) = delete;
    CallLease(CallLease &&) = delete;
    CallLease &operator=(CallLease &&) = delete;

    /// What a lease does besides keeping the object alive for the call.
    ///
    /// A PyCriticalSection cannot be nested to lock two objects: the inner
    /// one suspends the outer, so an argument's guard would silently drop
    /// the guard on the receiver for the duration of the call. Arguments
    /// therefore take the lease - which is what keeps them from being
    /// destroyed mid-call - without the guard.
    enum class Guard
    {
        Take,   ///< For the receiver: serialize calls on this C++ object.
        Omit    ///< For arguments: lease only, no critical section.
    };

    /// Acquire a lease. On failure a Python error is set (RuntimeError), as
    /// isValid() did, and the lease tests false.
    explicit CallLease(PyObject *pyObj, Guard guardMode = Guard::Take);
    ~CallLease();

    explicit operator bool() const { return m_valid; }

private:
    SbkObject *m_self = nullptr; // Non-null only while a lease is held.
    CallGuard m_guard;           // Serializes calls on the same C++ object.
    bool m_valid = false;
};

} // namespace Shiboken::Object

#endif // Py_GIL_DISABLED

#endif // SBK_CALLLEASE_H
