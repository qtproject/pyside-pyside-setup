// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef SBK_HELDLOCKS_H
#define SBK_HELDLOCKS_H

#include "shibokenmacros.h"

#include <cassert>

/// \file
/// Which binding-owned raw locks the current thread holds.
///
/// The state lock has tracked its own since phase 1, which is how
/// SBK_ASSERT_STATE_LOCKED() catches a broken transaction boundary. The same
/// question applies to the other raw locks the binding owns, and it is asked
/// at the other end: a helper that calls into Python, waits, or allocates
/// must know that no raw lock is held, because a raw lock held across Python
/// deadlocks against stop-the-world and against re-entrant calls.
///
/// Debug builds only. In a release build every query answers "none held" and
/// the assertions vanish, exactly as the state lock's do.

namespace Shiboken
{

/// The binding-owned raw locks, one bit each. Qt's and the application's
/// locks are not here: they are not ours, and no order over them is claimed.
enum class RawLock : unsigned
{
    State           = 1u << 0,  ///< sbkstatelock.cpp, process-wide
    WrapperMap      = 1u << 1,  ///< bindingmanager.cpp, recursive
    MainThreadDelete= 1u << 2,  ///< bindingmanager.cpp, one vector operation
    LazyType        = 1u << 3,  ///< sbkmodule.cpp, recursive
    ModuleData      = 1u << 4,  ///< sbkmodule.cpp, compiler-generated guard, never noted
    ConnectionHash  = 1u << 5,  ///< dynamicslot.cpp
    MetaObject      = 1u << 6,  ///< signalmanager.cpp, recursive
};

/// The order they may be taken in. A thread may only take a lock whose rank
/// is higher than every rank it already holds, so any two of them are always
/// taken in the same order and no pair of threads can hold them crosswise.
///
/// The state lock has the highest rank because it is the leaf: nothing may
/// be acquired while it is held, which is what lets every lease and
/// lifecycle transaction end without waiting for anything. The lazy-type
/// lock has the lowest because it is the one that legitimately spans other
/// work, type creation included.
///
/// A rank is a claim about the code, and this one is checked rather than
/// written down: checkLockRank() asserts it at every acquisition, and
/// lockNestings() reports which pairs a run actually produced, so the table
/// in the documentation says what happened and not what was intended.
enum class LockRank : int
{
    LazyType = 1, ModuleData, MetaObject, ConnectionHash,
    WrapperMap, MainThreadDelete, State,
};

/// The rank of \a lock. Defined in both builds: the order is a property of
/// the code, and only the checking of it is a debug build's business.
LIBSHIBOKEN_API int lockRank(RawLock lock);

#ifndef NDEBUG

/// Assert that \a lock may be taken while holding what this thread holds,
/// and record the nesting. Separate from noteLockAcquired() so that it can
/// run *before* the acquisition: a lock taken out of rank order deadlocks
/// inside lock(), and an assertion after it would never be reached.
LIBSHIBOKEN_API void checkLockRank(RawLock lock);

/// Note that this thread took \a lock. Recursive locks may be noted twice;
/// the count is what a matching release decrements.
LIBSHIBOKEN_API void noteLockAcquired(RawLock lock);

/// Record that a place the inventory names as an exception ran with \a lock
/// held. Counted next to the lazy-type exception, so the report says how
/// many there are and neither can grow unnoticed.
LIBSHIBOKEN_API void noteContractException(RawLock lock);

/// Note that this thread gave \a lock back.
LIBSHIBOKEN_API void noteLockReleased(RawLock lock);

/// Whether this thread holds \a lock.
LIBSHIBOKEN_API bool holdsLock(RawLock lock);
/// Whether this thread holds any binding raw lock.
LIBSHIBOKEN_API bool holdsAnyLock();
/// Names of the locks held, for an assertion message. "none" when the
/// thread holds none.
LIBSHIBOKEN_API const char *heldLockNames();

/// The nestings this run produced, as "outer -> inner" lines. Empty when no
/// two binding locks were ever held at once, which is the answer the
/// inventory wants for most of them.
LIBSHIBOKEN_API const char *lockNestings();

/// Write which locks are held and where, and answer false. Used by the
/// assertions below so that a failing one names the lock: "a raw lock is
/// held" tells whoever reads the abort nothing they can act on.
LIBSHIBOKEN_API bool reportLocksHeld(const char *where, const char *what);

/// Assert that no lock the contract covers is held at \a where, and count
/// the documented exception rather than aborting on it.
///
/// The exception is the lazy-type lock. It spans type creation, and type
/// creation is Python: Module::get() holds it across PyObject_GetAttr(),
/// so anything can happen underneath - a refcount reaching zero, a wrapper
/// being destroyed, a deferred destructor running. It is the lazy-type
/// lock's own finding (B13-5) seen from the destruction end, it is owned by
/// the lazy protocol's replacement, and asserting on it would only mean
/// nobody can run a debug build until that lands. Counted instead, so the finding stays visible and measurable.
LIBSHIBOKEN_API void checkNoRawLock(const char *where);

/// How often a documented exception was taken, per lock. Empty when never.
LIBSHIBOKEN_API const char *contractExceptions();

#else

inline const char *heldLockNames() { return ""; }
inline const char *lockNestings() { return ""; }
inline bool reportLocksHeld(const char *, const char *) { return false; }
inline void checkNoRawLock(const char *) {}
inline const char *contractExceptions() { return ""; }
inline void checkLockRank(RawLock) {}
inline void noteLockAcquired(RawLock) {}
inline void noteContractException(RawLock) {}
inline void noteLockReleased(RawLock) {}
inline bool holdsLock(RawLock) { return false; }
inline bool holdsAnyLock() { return false; }

#endif // NDEBUG

/// A lock_guard that also notes which lock it is. Used wherever a plain
/// scoped guard fits; the three waiters that detach or switch their mutex
/// off for an A/B run note by hand instead, and those are the only ones.
template <typename Mutex, RawLock Which>
class TrackedGuard
{
public:
    explicit TrackedGuard(Mutex &mutex) : m_mutex(mutex)
    {
        checkLockRank(Which);
        m_mutex.lock();
        noteLockAcquired(Which);
    }
    ~TrackedGuard()
    {
        noteLockReleased(Which);
        m_mutex.unlock();
    }
    TrackedGuard(const TrackedGuard &) = delete;
    TrackedGuard &operator=(const TrackedGuard &) = delete;
private:
    Mutex &m_mutex;
};

} // namespace Shiboken

/// Assert at a place that calls Python, waits, or allocates: no raw lock of
/// ours may be held here.
#define SBK_ASSERT_NO_RAW_LOCK() Shiboken::checkNoRawLock(__func__)

/// Assert that one specific lock is NOT held, where the contract names that
/// lock and not the others. The state lock's leaf property is stated this
/// way: the CPython type helpers say it, so a path that reaches them from a
/// transaction aborts instead of being found again by the next review.
#define SBK_ASSERT_LOCK_NOT_HELD(lock) \
    assert(!Shiboken::holdsLock(Shiboken::RawLock::lock) \
           || Shiboken::reportLocksHeld(__func__, "the " #lock \
                                        " lock may not be held here"))

#endif // SBK_HELDLOCKS_H
