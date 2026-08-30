// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_STATELOCK_H
#define SBK_STATELOCK_H

#ifdef Py_GIL_DISABLED

#include "sbkpython.h"
#include "sbkdestructorentry.h"
#include "shibokenmacros.h"

#include <cassert>
#include <vector>

struct SbkObject;

namespace Shiboken {

// The state lock.
//
// One process-wide, *non-recursive* lock that serializes access to the shared
// binding bookkeeping: the parent/child graph, the ownership and validity
// flags, the referred-object map and the wrapper lifecycle state.
//
// It replaced a coarse lock that was taken at wrapper entry and kept until
// the wrapper returned, so arbitrary Python, Qt and third-party code ran
// beneath it and it joined the lock order of the whole process. This one is
// held only across a short, bounded state transaction.
//
// Contract - code holding the state lock must not:
//
//   - invoke Python or any Python protocol;
//   - decref an object or run a weakref callback;
//   - import, allocate through Python or raise a Python exception;
//   - call Qt, emit a signal, invoke a virtual method or run a destructor;
//   - block, perform I/O, or attach/detach the thread state;
//   - acquire any other lock (in particular not the BindingManager wrapper map
//     lock, and not the per-object call guard, which is taken before the
//     transaction and released after it).
//
// Permitted: validation, pointer and flag updates, bounded container
// operations, plain malloc/free, and reference *increments* that only pin an
// object (an increment cannot run user code; decrements can, and must be
// deferred). Everything else is collected in a DeferredActions list and run
// after the lock is released.
//
// Because a holder can neither block nor request a stop-the-world, a plain
// non-detaching std::mutex is the right primitive here: an attached waiter may
// delay a stop-the-world, but the holder always reaches the unlock in finite
// time without needing to run Python. That also keeps a pthread_atfork policy
// feasible.
//
// Free-threaded builds only. A build with a GIL keeps the implementations this
// lock replaced, so nothing here is compiled for it - see basewrapper.cpp,
// where the two versions sit side by side. The debug ownership tracking below
// catches contract violations in an ordinary free-threaded developer build.

LIBSHIBOKEN_API void stateLockAcquire();
LIBSHIBOKEN_API void stateLockRelease();

/// Debug-build ownership tracking; always false in release builds.
LIBSHIBOKEN_API bool stateLockHeldByCurrentThread();

#define SBK_ASSERT_STATE_LOCKED()   assert(Shiboken::stateLockHeldByCurrentThread())
#define SBK_ASSERT_STATE_UNLOCKED() assert(!Shiboken::stateLockHeldByCurrentThread())

/// RAII form of the state lock. Keep the scope as small as the transaction.
class StateLockGuard
{
public:
    StateLockGuard(const StateLockGuard &) = delete;
    StateLockGuard &operator=(const StateLockGuard &) = delete;
    StateLockGuard(StateLockGuard &&) = delete;
    StateLockGuard &operator=(StateLockGuard &&) = delete;

    StateLockGuard() { stateLockAcquire(); }
    ~StateLockGuard() { stateLockRelease(); }
};

// Work that a state transaction has decided on but must not perform itself:
// reference decrements and C++ destructor calls. The list is filled under the
// state lock and run() is called after it has been released.
//
// The list must only contain owning references (the transaction transfers a
// reference into it), never borrowed ones.
class LIBSHIBOKEN_API DeferredActions
{
public:
    DeferredActions(const DeferredActions &) = delete;
    DeferredActions &operator=(const DeferredActions &) = delete;
    DeferredActions(DeferredActions &&) = delete;
    DeferredActions &operator=(DeferredActions &&) = delete;

    DeferredActions() noexcept = default;
    /// Runs anything left over; a transaction should call run() explicitly.
    ~DeferredActions();

    /// Transfer an owning reference into the list, to be released after unlock.
    void addDecref(PyObject *o);
    void addDecref(SbkObject *o) { addDecref(reinterpret_cast<PyObject *>(o)); }
    /// Record a C++ destructor call. It is run with the thread state released,
    /// like the ThreadStateSaver in the current destruction paths.
    void addDestructor(ObjectDestructor destructor, void *cppInstance);

    /// Run and clear the list. Asserts that the state lock is not held.
    void run();

private:
    struct Action
    {
        // Null means: Py_DECREF(static_cast<PyObject *>(arg)); anything else
        // is a C++ destructor and runs with the thread state released.
        void (*fn)(void *);
        void *arg;
    };

    // No reserve(): the common transaction defers nothing, and the vector must
    // not allocate on that path. Growth under the lock is plain malloc, which
    // the contract allows.
    std::vector<Action> m_actions;
};

} // namespace Shiboken

#endif // Py_GIL_DISABLED

#endif // SBK_STATELOCK_H
