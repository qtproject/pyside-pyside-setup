// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "sbkpython.h"

#ifdef Py_GIL_DISABLED

#include "sbkstatelock.h"
#include "sbkheldlocks.h"
#include "threadstatesaver.h"
#include "sbkftoptions.h"

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
    // A transaction is expected to call run() at a point it has chosen; getting
    // here with work left means some path returned early and left decrefs or a
    // destructor to an unspecified point.
    assert(m_actions.empty());
    run();
}

void DeferredActions::addDecref(PyObject *o)
{
    SBK_ASSERT_STATE_LOCKED();
    m_actions.push_back(Action{nullptr, o});
}

void DeferredActions::addDestructor(ObjectDestructor destructor, void *cppInstance)
{
    SBK_ASSERT_STATE_LOCKED();
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
}

} // namespace Shiboken

#endif // Py_GIL_DISABLED
