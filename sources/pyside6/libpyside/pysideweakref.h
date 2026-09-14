// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDEWEAKREF_H
#define PYSIDEWEAKREF_H

#include <pysidemacros.h>
#include <sbkpython.h>

using PySideWeakRefFunction = void (*)(void *userData);

namespace PySide::WeakRef {

// Create a weak reference to \a ob that calls \a func(userData) when \a ob dies.
// By default the callback also drops the weak reference itself once it fires, so
// the caller may discard the returned reference. Pass keepReference = true to own
// the returned reference instead: the callback then leaves it alone and the caller
// must release it (needed when the reference has to survive until some later,
// possibly deferred, teardown).
PYSIDE_API PyObject* create(PyObject* ob, PySideWeakRefFunction func, void* userData,
                            bool keepReference = false);

#ifdef Py_GIL_DISABLED
/// Upgrade a weak reference to a strong one. Returns a new reference, or
/// nullptr when the referent is gone (no error set) or on error (error set).
/// A referent being destroyed is already gone: its weak references are
/// cleared before any callback runs.
PYSIDE_API PyObject* deref(PyObject* weakRef);
#endif

} // namespace PySide::WeakRef

#endif // PYSIDEWEAKREF_H
