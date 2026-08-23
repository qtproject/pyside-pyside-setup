// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_ACQUIREDWRAPPER_H
#define SBK_ACQUIREDWRAPPER_H

#ifdef Py_GIL_DISABLED

#include "sbkpython.h"

#include <utility>

struct SbkObject;

namespace Shiboken
{

class BindingManager;

/// An owning reference to a wrapper, as returned by acquireWrapper(). Empty
/// means "no wrapper, or it is already being deallocated" - the same answer
/// as far as the caller is concerned. WrapperEntry in bindingmanager.cpp has
/// the reason the map cannot hand out a borrowed reference instead.
///
/// No implicit conversion to SbkObject *: the raw pointer takes an explicit
/// object(), so the lifetime it depends on stays visible at the call site.
///
/// Needs an attached thread state, to take and to drop - the C++ destructor
/// of a wrapped class, for one, has none.
class AcquiredWrapper
{
public:
    AcquiredWrapper() noexcept = default;
    AcquiredWrapper(const AcquiredWrapper &) = delete;
    AcquiredWrapper &operator=(const AcquiredWrapper &) = delete;

    AcquiredWrapper(AcquiredWrapper &&o) noexcept : m_obj(std::exchange(o.m_obj, nullptr)) {}
    AcquiredWrapper &operator=(AcquiredWrapper &&o) noexcept
    {
        if (this != &o) {
            reset();
            m_obj = std::exchange(o.m_obj, nullptr);
        }
        return *this;
    }

    ~AcquiredWrapper() { reset(); }

    /// Only on a named reference. On a temporary the pointer would outlive
    /// the reference that keeps it alive, so those overloads are deleted:
    /// acquireWrapper(p).object() is a compile error, not a dangling pointer.
    [[nodiscard]] SbkObject *object() const & noexcept { return m_obj; }
    SbkObject *object() const && = delete;
    [[nodiscard]] PyObject *pyObject() const & noexcept
    { return reinterpret_cast<PyObject *>(m_obj); }
    PyObject *pyObject() const && = delete;
    [[nodiscard]] bool isNull() const noexcept { return m_obj == nullptr; }
    explicit operator bool() const noexcept { return m_obj != nullptr; }

    /// Hand the reference on to the caller, leaving this empty. For functions
    /// whose own contract is to return a new reference.
    [[nodiscard]] SbkObject *release() noexcept { return std::exchange(m_obj, nullptr); }

    void reset() noexcept
    {
        Py_XDECREF(reinterpret_cast<PyObject *>(std::exchange(m_obj, nullptr)));
    }

private:
    /// Only BindingManager may hand a raw pointer in: it is the one place that
    /// knows the reference was taken rather than borrowed, which is the bug
    /// this class exists to prevent.
    friend class BindingManager;
    static AcquiredWrapper fromOwned(SbkObject *obj) noexcept { return AcquiredWrapper(obj); }

    explicit AcquiredWrapper(SbkObject *obj) noexcept : m_obj(obj) {}

    SbkObject *m_obj = nullptr;
};

} // namespace Shiboken

#endif // Py_GIL_DISABLED

#endif // SBK_ACQUIREDWRAPPER_H
