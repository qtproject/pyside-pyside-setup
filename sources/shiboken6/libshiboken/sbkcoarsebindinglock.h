// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_COARSEBINDINGLOCK_H
#define SBK_COARSEBINDINGLOCK_H

#include "sbkpython.h"
#include "shibokenmacros.h"

#ifdef Py_GIL_DISABLED
#  include <cassert>
#  include <cstdint>
#  if defined(Py_LIMITED_API)
// Under the limited API (abi3t) critical_section.h exposes the
// PyCriticalSection type and PyCriticalSection_End(), but the PyMutex type and
// PyCriticalSection_BeginMutex() live in the cpython/ headers. The mutex is a
// single zero-initializable byte and the entry point is an exported function,
// so we declare the little we use here. (A fully conforming stable-ABI build
// would use a sentinel PyObject with PyCriticalSection_Begin() instead.)
extern "C" {
typedef struct PyMutex { uint8_t _bits; } PyMutex;
PyAPI_FUNC(void) PyCriticalSection_BeginMutex(PyCriticalSection *c, PyMutex *m);
}
#  endif
#endif

namespace Shiboken {

// The coarse binding lock.
//
// On a free-threaded build (Py_GIL_DISABLED) the real interpreter GIL is off,
// so several Python threads may enter shiboken concurrently. The BindingManager
// wrapper registry is already protected by its own lock, but the *per-object*
// bookkeeping (ownership flags, parent-child graph, wrapper lifecycle) is not.
//
// This is a single, process-wide lock that serializes exactly that
// bookkeeping. Effect: the Qt/shiboken object graph stays effectively
// single-threaded (which is what the free-threading contract requires: GUI
// single-threaded), while pure-Python threads that never enter shiboken run
// truly in parallel.
//
// The physical lock is a process-wide PyMutex, but it is only ever taken
// through a Python critical section (PyCriticalSection_BeginMutex). That gives
// the lock the GIL's *release* semantics, not just its exclusion semantics:
//
// - Whenever the holding thread detaches (PyEval_SaveThread around allow-thread
//   regions and destructors, blocking on a threading.Lock/queue/event, waiting
//   for an import lock, a contended per-object critical section), the runtime
//   suspends the section and releases the mutex; on reattach the section is
//   resumed. A raw mutex held across such waits deadlocks against any thread
//   that needs the graph lock to make progress - that was the central flaw of
//   the previous PyMutex-only design.
// - A nested guard on the same thread suspends the outer section and
//   reacquires, so the lock behaves like a reentrant lock without a
//   hand-maintained depth counter.
// - A thread parked on a contended acquisition is detached, so blocking here
//   never stalls a stop-the-world.
//
// Residual exposure, documented as GIL-equivalent: waits the runtime cannot
// see (a raw C++/Qt mutex acquired under the guard) still hold the section,
// exactly as the GIL is held across unannotated C++ calls. And a nested guard
// or contended per-object lock is a potential suspension point, so atomicity
// is slightly weaker than under the GIL: shared state must be consistent
// whenever a guarded helper is entered.
//
// Constructing a guard requires an attached Python thread state.
//
// On a normal (GIL-enabled) build the guard compiles to nothing.

#ifdef Py_GIL_DISABLED

// The mutex must be a single instance in the process. Defining it in this
// header gives every shared library that includes it - libshiboken, libpyside
// and every generated module - a copy of its own, because -fvisibility=hidden
// keeps the symbol private to each library. It is defined in basewrapper.cpp
// and exported.
LIBSHIBOKEN_API PyMutex &coarseBindingMutex();

// Runtime kill switch. Clear the CoarseBindingLock bit of PYSIDE6_OPTION_FT
// (see sbkftoptions.h) to disable the lock, which is what the free-threading
// stress harness uses for its A/B proof: without the lock the stress must
// crash, with it it must survive.
LIBSHIBOKEN_API bool coarseBindingLockEnabled();

class CoarseBindingGuard
{
public:
    CoarseBindingGuard(const CoarseBindingGuard &) = delete;
    CoarseBindingGuard &operator=(const CoarseBindingGuard &) = delete;
    CoarseBindingGuard(CoarseBindingGuard &&) = delete;
    CoarseBindingGuard &operator=(CoarseBindingGuard &&) = delete;

    CoarseBindingGuard() : m_active(coarseBindingLockEnabled())
    {
        if (m_active) {
            assert(PyThreadState_GetUnchecked() != nullptr
                   && "CoarseBindingGuard requires an attached thread state");
            PyCriticalSection_BeginMutex(&m_section, &coarseBindingMutex());
        }
    }
    ~CoarseBindingGuard()
    {
        if (m_active) {
            PyCriticalSection_End(&m_section);
        }
    }

private:
    PyCriticalSection m_section;
    bool m_active;
};

#endif // Py_GIL_DISABLED

} // namespace Shiboken

#endif // SBK_COARSEBINDINGLOCK_H
