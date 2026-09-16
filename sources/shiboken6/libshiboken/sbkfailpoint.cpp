// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#include "sbkpython.h"

#include "sbkfailpoint.h"

#ifndef SBK_NO_FAILPOINTS

#include "sbkheldlocks.h"

#include <array>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstring>
#include <mutex>
#include <string>

namespace Shiboken
{

// The points this build has - the truth about it, not a wish list. Arming a
// name that is not here answers false, which is what tells a test that the
// point was renamed, removed with the code around it, or never existed in
// this build. A name that were listed but never placed would be worse than
// missing: the test would wait for a thread that cannot arrive and report
// the point as unreached.
#ifdef Py_GIL_DISABLED
static constexpr std::array KnownFailpoints = {
    "dealloc-before-weakrefs",   // in the deallocator, before clearing weakrefs
    "dealloc-before-destroy",    // after the state snapshot, before the C++ dtor
    "dealloc-before-cpp-dtor",   // wrapper freed, C++ destructor still to come
    "dealloc-before-retire",     // C++ destructor past, tombstone still standing
    "delete-before-owned-dtor",  // children handed back, parent dtor still to come
    "lease-after-acquire",       // lease taken, before the native call
    "lease-before-release",      // native call done, before giving the lease back
    "destroy-before-detach",     // Object::destroy(), before cptr is detached
    "destroy-after-tombstone",   // Object::destroy() is past, the memory is not
    "ctor-before-publish",       // setCppPointer(), between the check and the write
    "hierarchy-mid-traversal",   // in the class graph, one iterator alive
    "metaobject-before-commit",  // instance builder built, not committed yet
    "parent-before-commit",      // leases held, the new edge not published yet
    "dict-before-publish",       // instance dict found missing, not created yet
    "clear-before-dict",         // tp_clear, children detached, the dict to come
};
#else
// A build with a GIL has none of these windows: no lease, and a deallocator
// the free-threading branch replaces wholesale.
static constexpr std::array<const char *, 0> KnownFailpoints = {};
#endif

struct FailpointState
{
    std::mutex mutex;
    std::condition_variable released;
    /// The point the next thread arriving there stops at. Cleared by the
    /// thread that takes it: an armed point stops one thread, not every
    /// thread that comes past. A test that parks a call and then drives the
    /// same code from another thread needs that second one to run through -
    /// otherwise both park and the test measures nothing.
    std::string armed;
    std::string parked;          ///< where a thread is stopped right now
    bool release = false;        ///< the parked thread may go
    int timeoutMs = 5000;
};

static FailpointState &state()
{
    static FailpointState s;
    return s;
}

// True while a point is armed. failpoint() sits on the lease and on
// deallocation, so the fast path may not take the process-wide mutex: that
// would serialize threads working on unrelated objects. Nothing is armed in
// almost every run, and then this load is the whole cost. A thread that
// misses a just-published arming runs on, which the tests allow for: they
// arm before starting the thread they want to park.
static std::atomic<bool> anyArmed{false};

static bool isKnown(const char *name)
{
    for (const char *known : KnownFailpoints) {
        if (std::strcmp(known, name) == 0)
            return true;
    }
    return false;
}

bool armFailpoint(const char *name, int timeoutMs)
{
    if (!isKnown(name))
        return false;
    auto &s = state();
    std::lock_guard<std::mutex> guard(s.mutex);
    s.armed = name;
    s.parked.clear();
    s.release = false;
    s.timeoutMs = timeoutMs;
    anyArmed.store(true, std::memory_order_release);
    return true;
}

bool releaseFailpoint(const char *name)
{
    auto &s = state();
    bool wasParked = false;
    {
        std::lock_guard<std::mutex> guard(s.mutex);
        // Either state counts: the point may still be armed with nobody
        // there yet, or a thread may already be parked at it and the arming
        // gone. Disarming both is what ends the point.
        if (s.armed != name && s.parked != name)
            return false;
        wasParked = s.parked == name;
        s.armed.clear();
        anyArmed.store(false, std::memory_order_release);
        s.release = true;
    }
    s.released.notify_all();
    return wasParked;
}

bool failpointReached(const char *name)
{
    auto &s = state();
    std::lock_guard<std::mutex> guard(s.mutex);
    return s.parked == name;
}

void clearFailpoints()
{
    auto &s = state();
    {
        std::lock_guard<std::mutex> guard(s.mutex);
        s.armed.clear();
        anyArmed.store(false, std::memory_order_release);
        s.release = true;
    }
    s.released.notify_all();
}

const char *failpointNames()
{
    static std::string all = [] {
        std::string result;
        for (const char *name : KnownFailpoints) {
            if (!result.empty())
                result += ',';
            result += name;
        }
        return result;
    }();
    return all.c_str();
}

void failpoint(const char *name)
{
    if (!anyArmed.load(std::memory_order_acquire))
        return;
    auto &s = state();
    std::unique_lock<std::mutex> guard(s.mutex);
    if (s.armed != name)
        return;
    // Whoever waits here holds no binding raw lock: the point of stopping is
    // to let another thread reach the same object, and it cannot if this one
    // still holds the lock that guards it. A failpoint under a lock would
    // deadlock the test rather than expose the race it was placed for.
    assert(!holdsAnyLock());
    // Take the arming with us. The next thread through here runs on, which
    // is what lets a test park one thread and then use the same code path
    // from another to reach the object the parked one is holding.
    s.armed.clear();
    anyArmed.store(false, std::memory_order_release);
    s.parked = name;
    const auto deadline = std::chrono::steady_clock::now()
                          + std::chrono::milliseconds(s.timeoutMs);
    // Park detached. A thread that stops here with its thread state attached
    // blocks stop-the-world on a free-threaded build, and on a GIL build it
    // blocks every other thread outright - the test could then never put the
    // second thread where it wants it, and would report the point as never
    // reached. It is the same rule the deferred destructors follow.
    PyThreadState *saved = PyGILState_Check() ? PyEval_SaveThread() : nullptr;
    // Timed: a test that never releases must fail, not hang the suite.
    s.released.wait_until(guard, deadline, [&s] { return s.release; });
    s.parked.clear();
    // Reattaching can wait for a stop-the-world pause, so let go of our own
    // mutex first: a thread arming or releasing a point must not queue behind
    // that.
    guard.unlock();
    if (saved != nullptr)
        PyEval_RestoreThread(saved);
}

} // namespace Shiboken

#endif // SBK_NO_FAILPOINTS
