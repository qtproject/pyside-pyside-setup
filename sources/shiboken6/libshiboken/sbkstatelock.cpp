// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "sbkpython.h"

#ifdef Py_GIL_DISABLED

#include "sbkstatelock.h"
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

#ifndef NDEBUG
static bool &stateLockHeld()
{
    static thread_local bool held = false;
    return held;
}

bool stateLockHeldByCurrentThread()
{
    return stateLockHeld();
}
#else
bool stateLockHeldByCurrentThread()
{
    return false;
}
#endif

void stateLockAcquire()
{
    // Deliberately not recursive: a nested acquisition means the transaction
    // boundary is unclear, and unclear boundaries are how call-outs end up
    // beneath the lock.
    assert(!stateLockHeldByCurrentThread());
    if (stateLockEnabled())
        stateMutex().lock();
#ifndef NDEBUG
    stateLockHeld() = true;
#endif
}

void stateLockRelease()
{
    assert(stateLockHeldByCurrentThread());
#ifndef NDEBUG
    stateLockHeld() = false;
#endif
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
    SBK_ASSERT_STATE_UNLOCKED();
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
