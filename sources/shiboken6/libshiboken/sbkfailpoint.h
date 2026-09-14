// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef SBK_FAILPOINT_H
#define SBK_FAILPOINT_H

#include "shibokenmacros.h"

/// \file
/// Named points where a test can stop one thread.
///
/// A lifetime race needs two threads in a particular order: one inside
/// deallocation, the other reaching the same wrapper before it finishes. A
/// stress run reaches that order by chance and needs thousands of rounds to
/// do it once; a test that arms a failpoint reaches it every time, and fails
/// on an unfixed revision instead of one run in fourteen.
///
/// A failpoint is inert until something arms it. Armed, the first thread to
/// reach it blocks until another thread releases it, or until the timeout
/// expires - a test that deadlocks must fail, not hang. The arming goes with
/// that first thread: a second one running the same code path goes through,
/// which is what lets a test park one thread and then reach the object it
/// holds from another. The parked thread waits detached, so it blocks
/// neither stop-the-world nor, on a GIL build, everyone else.
///
/// A second kind, SBK_FAILPOINT_THROW(), stands in for an allocation under a
/// binding lock: armed, it throws std::bad_alloc, so a test can see what a
/// transaction that unwinds leaves behind. It cannot park, since the thread
/// holds the lock. The two kinds arm separately and can be in flight at
/// once; parking points share one arming.
///
/// Debug builds only, and not with the limited API. Where they are absent,
/// SBK_FAILPOINT() and SBK_FAILPOINT_THROW() expand to nothing.

namespace Shiboken
{

// Parking has to detach, which needs PyGILState_Check() to know whether
// this thread is attached at all. That is not in the limited API, so a
// limited-API build has no failpoints, the way a release build has none.
#if defined(NDEBUG) || defined(Py_LIMITED_API)
#  define SBK_NO_FAILPOINTS
#endif

#ifndef SBK_NO_FAILPOINTS

/// Arm \a name so the next thread reaching it waits. Returns false if the
/// name is not one of the points in this build, which is what tells a test
/// that it is checking something that no longer exists - or something the
/// build does not have, since the free-threading windows are not there in a
/// build with a GIL.
LIBSHIBOKEN_API bool armFailpoint(const char *name, int timeoutMs = 5000);

/// Release whoever waits at \a name, and disarm it. Returns true if a thread
/// was parked there, false if the point was merely armed and never reached.
LIBSHIBOKEN_API bool releaseFailpoint(const char *name);

/// Whether a thread is parked at \a name right now. Lets a test wait for the
/// other thread to arrive instead of sleeping.
LIBSHIBOKEN_API bool failpointReached(const char *name);

/// Disarm everything. Called between tests.
LIBSHIBOKEN_API void clearFailpoints();

/// The names compiled into this build, comma-separated.
LIBSHIBOKEN_API const char *failpointNames();

/// Block here if this point is armed. Called from the code under test.
LIBSHIBOKEN_API void failpoint(const char *name);

/// Arm \a name so that the next thread reaching it throws std::bad_alloc.
/// Returns false if the name is not a throwing point in this build. One shot:
/// the point disarms itself as it throws.
LIBSHIBOKEN_API bool armFailpointThrow(const char *name);

/// Throw here if this point is armed. Unlike failpoint(), this may be called
/// with a binding lock held, and takes no lock itself.
LIBSHIBOKEN_API void failpointThrow(const char *name);

/// Disarm the throwing point only. Unlike clearFailpoints(), this leaves an
/// armed or parked parking point alone.
LIBSHIBOKEN_API void disarmFailpointThrow();

#else

// A build without them still has the control functions, so that callers
// need no conditionals: arming answers false, and a test that asks for the
// names gets an empty string and skips.
inline bool armFailpoint(const char *, int = 5000) { return false; }
inline bool releaseFailpoint(const char *) { return false; }
inline bool failpointReached(const char *) { return false; }
inline void clearFailpoints() {}
inline const char *failpointNames() { return ""; }
inline bool armFailpointThrow(const char *) { return false; }
inline void failpointThrow(const char *) {}
inline void disarmFailpointThrow() {}

#endif // SBK_NO_FAILPOINTS

} // namespace Shiboken

#ifndef SBK_NO_FAILPOINTS
#  define SBK_FAILPOINT(name) Shiboken::failpoint(name)
#  define SBK_FAILPOINT_THROW(name) Shiboken::failpointThrow(name)
#else
#  define SBK_FAILPOINT(name) ((void)0)
#  define SBK_FAILPOINT_THROW(name) ((void)0)
#endif

#endif // SBK_FAILPOINT_H
