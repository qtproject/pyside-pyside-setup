// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "sbkpython.h"

#ifdef Py_GIL_DISABLED

#include "sbkstatelock.h"
#include "sbkfailpoint.h"
#include "sbkheldlocks.h"
#include "threadstatesaver.h"
#include "sbkftoptions.h"

#include <exception>
#include <mutex>

namespace Shiboken {

// One instance per process: the definition lives here rather than in the
// header, because a header definition ends up private to every shared library
// that includes it (-fvisibility=hidden) and would only exclude callers within
// the same library.
static std::mutex &stateMutex()
{
    static std::mutex mutex;
    return mutex;
}

static bool stateLockEnabled()
{
    return FreeThreading::optionEnabled(FreeThreading::StateLock);
}

bool stateLockHeldByCurrentThread()
{
    return holdsLock(RawLock::State);
}

void stateLockAcquire()
{
    // Deliberately not recursive: a nested acquisition means the transaction
    // boundary is unclear, and unclear boundaries are how call-outs end up
    // beneath the lock.
    assert(!stateLockHeldByCurrentThread());
    checkLockRank(RawLock::State);
    if (stateLockEnabled())
        stateMutex().lock();
    noteLockAcquired(RawLock::State);
}

void stateLockRelease()
{
    assert(stateLockHeldByCurrentThread());
    noteLockReleased(RawLock::State);
    if (stateLockEnabled())
        stateMutex().unlock();
}

DeferredActions::~DeferredActions()
{
    if (m_committed) {
        // Committed, run() not reached: the list owns these references.
        run();
        return;
    }
    // Uncommitted: either nothing was deferred, or the transaction unwinds and
    // the state still owns what the list holds. Work left without an unwind
    // is an early return that skipped run().
    assert(m_actions.empty() || std::uncaught_exceptions() > 0);
    m_actions.clear();
}

void DeferredActions::grow(std::size_t needed)
{
    if (needed <= m_actions.capacity())
        return;
    // Every growth of the list passes here, prepared or not.
    SBK_FAILPOINT_THROW("deferred-slot-alloc");
    m_actions.reserve(needed);
}

void DeferredActions::reserve(std::size_t n)
{
    SBK_ASSERT_STATE_LOCKED();
    // Exact: the caller knows its count.
    grow(m_actions.size() + n);
}

void DeferredActions::makeRoom()
{
    if (m_actions.size() < m_actions.capacity())
        return;
    // Geometric, so an unprepared loop does not allocate per element.
    grow(m_actions.empty() ? 4 : m_actions.capacity() * 2);
}

void DeferredActions::addDecref(PyObject *o)
{
    SBK_ASSERT_STATE_LOCKED();
    // Allocates only where the transaction did not reserve().
    makeRoom();
    m_actions.push_back(Action{nullptr, o});
}

void DeferredActions::addDestructor(ObjectDestructor destructor, void *cppInstance)
{
    SBK_ASSERT_STATE_LOCKED();
    makeRoom();
    m_actions.push_back(Action{destructor, cppInstance});
}

void DeferredActions::run()
{
    // Not just the state lock: an action runs decrefs and native destructors,
    // so it reaches Python, Qt and user code. Holding any binding raw lock
    // here is what deadlocks against stop-the-world and re-entrant calls.
    SBK_ASSERT_NO_RAW_LOCK();
    // Index-based: an action can run arbitrary code, but it cannot reach this
    // list, which is a local of the transaction that created it.
    for (size_t i = 0, size = m_actions.size(); i < size; ++i) {
        const Action &action = m_actions[i];
        if (action.fn == nullptr) {
            Py_DECREF(static_cast<PyObject *>(action.arg));
        } else {
            ThreadStateSaver threadSaver;
            if (Py_IsInitialized())
                threadSaver.save();
            action.fn(action.arg);
        }
    }
    m_actions.clear();
    // The transfer is done. A list that is refilled needs its own commit.
    m_committed = false;
}

} // namespace Shiboken

#endif // Py_GIL_DISABLED
