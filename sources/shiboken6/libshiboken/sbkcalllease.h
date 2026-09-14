// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_CALLLEASE_H
#define SBK_CALLLEASE_H

#include "sbkpython.h"
#include "shibokenmacros.h"

#ifdef Py_GIL_DISABLED

#include "sbkcallguard.h"

#include <optional> // generated constructors hold std::optional<CallLease>

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
 * Construction validates the wrapper, increments its active call count and
 * copies the C++ pointer in one state transaction; destruction decrements it.
 * Holders use that copy instead of reading the wrapper's pointer array again.
 *
 * Destruction requested while a lease is outstanding is *marked and
 * deferred*, never waited for: waiting would deadlock whenever the in-flight
 * call needs the deleting thread. The last lease to be released runs the
 * destructor, with no lock held.
 *
 * A lease is not a lock. It says nothing about calling a Qt class concurrently:
 * Qt thread affinity and class-specific thread-safety rules still apply. It
 * also does not keep the Python wrapper alive - the caller's own reference
 * does.
 *
 * It defers only the destruction the binding drives. A delete issued by C++
 * does not wait for leases: the pointer a lease hands out stays readable,
 * the object behind it may be gone.
 * See "What a lease hands out" in the free-threading notes.
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
    /// Acquire a lease whose pointer() is the one for base desiredType.
    /// The guard stays keyed on the object, whichever base is asked for.
    explicit CallLease(PyObject *pyObj, PyTypeObject *desiredType,
                       Guard guardMode = Guard::Take);
    ~CallLease();

    explicit operator bool() const { return m_valid; }

    /// The C++ pointer copied when the lease was granted; null for an
    /// inactive lease.
    void *pointer() const { return m_pointer; }
    template <class T>
    T *pointer() const { return reinterpret_cast<T *>(m_pointer); }

private:
    void acquire(PyObject *pyObj, PyTypeObject *desiredType, Guard guardMode);

    SbkObject *m_self = nullptr; // Non-null only while a lease is held.
    CallGuard m_guard;           // Serializes calls on the same C++ object.
    void *m_pointer = nullptr;   // The copy the holder uses.
    bool m_valid = false;
};

/**
 * Keeps the leases an argument conversion takes on wrappers it does not
 * receive itself - the elements of a container, a wrapper passed as void * -
 * until the native call has returned.
 *
 * pythonToCppPointer() and the void * converter lease the wrapper they read
 * a pointer from. On their own that lease ends when the converter returns,
 * and only the pointer is left: a concurrent Shiboken.delete() on an element
 * frees the object before the call uses it. While a holder is collecting,
 * the converters put their lease, with a reference on the wrapper, into it.
 *
 * Generated code declares the holder in the scope of the call, collects
 * across one argument's conversion and stops with endCollect(). Collecting
 * is per thread and nests. The destructor releases the leases with no lock
 * held: the last one may run a deferred C++ destructor.
 * See "Leases taken inside a conversion" in the free-threading notes.
 */
class LIBSHIBOKEN_API ConversionLeases
{
public:
    ConversionLeases(const ConversionLeases &) = delete;
    ConversionLeases &operator=(const ConversionLeases &) = delete;
    ConversionLeases(ConversionLeases &&) = delete;
    ConversionLeases &operator=(ConversionLeases &&) = delete;

    /// Starts collecting on this thread.
    ConversionLeases();
    ~ConversionLeases();

    /// Stops collecting; the leases collected so far are kept.
    void endCollect();

    /// The holder collecting on this thread, or null.
    static ConversionLeases *collecting();

    /// Lease pyObj for desiredType (null for its own pointer) and keep the
    /// lease. Writes the lease's pointer to cppOut. On failure a Python error
    /// is set, null is written and false returned.
    bool add(PyObject *pyObj, PyTypeObject *desiredType, void **cppOut);

private:
    struct Entry;

    Entry *m_entries = nullptr;             // Most recent first.
    ConversionLeases *m_previous = nullptr; // The holder collecting before.
    bool m_collecting = true;
};

} // namespace Shiboken::Object

#endif // Py_GIL_DISABLED

#endif // SBK_CALLLEASE_H
