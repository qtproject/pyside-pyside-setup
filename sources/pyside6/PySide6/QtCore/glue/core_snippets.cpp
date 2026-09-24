// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "core_snippets_p.h"
#include "qtcorehelper.h"
#include "pysideqobject.h"

#include "sbkpython.h"
#include "sbkconverter.h"
#ifdef Py_GIL_DISABLED
#include "sbkerrors.h"
#endif
#include "sbkpep.h"
#ifndef Py_LIMITED_API
#  include <datetime.h>
#endif
#include "basewrapper.h"
#include "autodecref.h"
#include "gilstate.h"
#include "pysideutils.h"
#ifdef Py_GIL_DISABLED
#  include "sbkfailpoint.h"
#  include "sbkftoptions.h"
#  include "sbkheldlocks.h"
#  include <atomic>
#  include <cassert>
#  include <cstdio>
#  include <mutex>
#endif

#include <QtCore/QCoreApplication>
#include <QtCore/QDebug>
#include <QtCore/QMetaType>
#include <QtCore/QObject>
#include <QtCore/QRegularExpression>
#include <QtCore/QStack>

#include <cstring>

// Helpers for qAddPostRoutine

namespace PySide {

static QStack<PyObject *> globalPostRoutineFunctions;

#ifdef Py_GIL_DISABLED
// Container work only; the callbacks run after the lock.
// See "Post routines run from a batch" in the free-threading notes.
static std::mutex &postRoutineMutex()
{
    static std::mutex mutex;
    return mutex;
}

using PostRoutineLock =
    Shiboken::TrackedGuard<std::mutex, Shiboken::RawLock::PostRoutine>;

static bool batchedPostRoutines()
{
    return Shiboken::FreeThreading::optionEnabled(
        Shiboken::FreeThreading::PostRoutineBatch);
}

#ifndef NDEBUG
// Depth of live-queue walks; addPostRoutine() asserts zero. A depth, so a
// nested run cannot disarm the outer one.
static std::atomic_int walkingLiveQueue{0};

static bool reportLiveWalk()
{
    std::fprintf(stderr, "qAddPostRoutine() was called while the post-routine "
                         "queue was being walked live\n");
    return false;
}
#endif // NDEBUG

// Batches per runner call; bounds only a routine that re-registers itself
// forever.
static constexpr int MaxPostRoutineRounds = 1024;

// The pending callbacks, taken out whole; the queue stays free for the
// registrations the callbacks make.
static QStack<PyObject *> takePostRoutines()
{
    QStack<PyObject *> batch;
    PostRoutineLock lock(postRoutineMutex());
    batch.swap(globalPostRoutineFunctions);
    return batch;
}
#endif // Py_GIL_DISABLED

void globalPostRoutineCallback()
{
    Shiboken::GilState state;

#ifndef Py_GIL_DISABLED
    // The walk a build with a GIL always had: one pass, and a registration
    // made while it runs is cleared unrun. The rounds below are the answer
    // to that, and they are the free-threaded build's alone.
    for (auto *callback : globalPostRoutineFunctions) {
        Shiboken::AutoDecRef result(PyObject_CallObject(callback, nullptr));
        Py_DECREF(callback);
    }
    globalPostRoutineFunctions.clear();
#else
    if (!batchedPostRoutines()) {
        // PostRoutineBatch cleared: walk the live queue.
#  ifndef NDEBUG
        walkingLiveQueue.fetch_add(1, std::memory_order_relaxed);
#  endif
        for (auto *callback : globalPostRoutineFunctions) {
            Shiboken::AutoDecRef result(PyObject_CallObject(callback, nullptr));
            Py_DECREF(callback);
        }
        globalPostRoutineFunctions.clear();
#  ifndef NDEBUG
        walkingLiveQueue.fetch_sub(1, std::memory_order_relaxed);
#  endif
        return;
    }

    // Registrations made by a callback go into the next batch; the loop ends
    // on an empty one. Within a batch the order is the registration order.
    for (int round = 0; round < MaxPostRoutineRounds; ++round) {
        auto batch = takePostRoutines();
        if (batch.isEmpty())
            break;
        for (auto *callback : batch) {
            Shiboken::AutoDecRef result(PyObject_CallObject(callback, nullptr));
            // Report a raising callback and run the rest of the batch.
            if (result.isNull())
                PyErr_WriteUnraisable(callback);
            Py_DECREF(callback);
        }
    }

    // What a runaway registrar left behind is reported and released, not run.
    if (auto leftovers = takePostRoutines(); !leftovers.isEmpty()) {
        PyErr_Format(PyExc_RuntimeWarning,
                     "qAddPostRoutine: %lld routine(s) still queued after %d "
                     "rounds; abandoning them",
                     static_cast<long long>(leftovers.size()),
                     MaxPostRoutineRounds);
        PyErr_WriteUnraisable(nullptr);
        for (auto *callback : leftovers)
            Py_DECREF(callback);
    }
#endif
}

void addPostRoutine(PyObject *callback)
{
#ifndef Py_GIL_DISABLED
    if (PyCallable_Check(callback)) {
        globalPostRoutineFunctions << callback;
        Py_INCREF(callback);
    } else {
        PyErr_SetString(PyExc_TypeError, "qAddPostRoutine: The argument must be a callable object.");
    }
#else
    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError, "qAddPostRoutine: The argument must be a callable object.");
        return;
    }

#  ifndef NDEBUG
    // A registration during a live walk aborts, whether or not the append
    // would have reallocated.
    assert(walkingLiveQueue.load(std::memory_order_relaxed) == 0
           || reportLiveWalk());
#  endif

    if (!batchedPostRoutines()) {
        globalPostRoutineFunctions << callback;  // published before it is owned
        Py_INCREF(callback);
        return;
    }

    // Owned before it is published: a runner on another thread may take the
    // batch and release this reference as soon as the lock is gone.
    // See "Post routines run from a batch" in the free-threading notes.
    // No try/catch: the modules may be built with -fno-exceptions.
    Py_INCREF(callback);
    {
        PostRoutineLock lock(postRoutineMutex());
        globalPostRoutineFunctions << callback;
    }
    SBK_FAILPOINT("post-routine-after-append");
#endif
}
} // namespace PySide

// Helpers for QObject::findChild(ren)()

static bool _findChildTypeMatch(const QObject *child, PyTypeObject *desiredType)
{
#ifdef Py_GIL_DISABLED
    return PySide::qObjectTypeMatches(child, desiredType);
#else
    auto *pyChildType = PySide::getTypeForQObject(child);
    return pyChildType != nullptr && PyType_IsSubtype(pyChildType, desiredType);
#endif
}

static inline bool _findChildrenComparator(const QObject *child,
                                           const QRegularExpression &name)
{
    return name.match(child->objectName()).hasMatch();
}

static inline bool _findChildrenComparator(const QObject *child,
                                           const QString &name)
{
    return name.isNull() || name == child->objectName();
}

QObject *qObjectFindChild(const QObject *parent, const QString &name,
                          PyTypeObject *desiredType, Qt::FindChildOptions options)
{
    for (auto *child : parent->children()) {
        if (_findChildrenComparator(child, name)
            && _findChildTypeMatch(child, desiredType)) {
            return child;
        }
    }

    if (options.testFlag(Qt::FindChildrenRecursively)) {
        for (auto *child : parent->children()) {
            if (auto *obj = qObjectFindChild(child, name, desiredType, options))
                return obj;
        }
    }
    return nullptr;
}

template<typename T> // QString/QRegularExpression
static void _findChildrenHelper(const QObject *parent, const T& name, PyTypeObject *desiredType,
                                Qt::FindChildOptions options, FindChildHandler handler)
{
    for (auto *child : parent->children()) {
        if (_findChildrenComparator(child, name) && _findChildTypeMatch(child, desiredType))
            handler(child);
        if (options.testFlag(Qt::FindChildrenRecursively))
            _findChildrenHelper(child, name, desiredType, options, handler);
    }
}

void qObjectFindChildren(const QObject *parent, const QString &name,
                         PyTypeObject *desiredType, Qt::FindChildOptions options,
                         FindChildHandler handler)
{
    _findChildrenHelper(parent, name, desiredType, options, handler);
}

void qObjectFindChildren(const QObject *parent, const QRegularExpression &pattern,
                         PyTypeObject *desiredType, Qt::FindChildOptions options,
                         FindChildHandler handler)
{
    _findChildrenHelper(parent, pattern, desiredType, options, handler);
}

//////////////////////////////////////////////////////////////////////////////
// Helpers for translation:
// PYSIDE-131: Use the class name as context where the calling function is
//             living. Derived Python classes have the wrong context.
//
// The original patch uses Python introspection to look up the current
// function (from the frame stack) in the class __dict__ along the mro.
//
// The problem is that looking into the frame stack works for Python
// functions, only. For including builtin function callers, the following
// approach turned out to be much simpler:
//
// Walk the __mro__
// - translate the string
// - if the translated string is changed:
//   - return the translation.

QString qObjectTr(PyTypeObject *type, const char *sourceText, const char *disambiguation, int n)
{
#ifdef Py_GIL_DISABLED
    QString result = QString::fromUtf8(sourceText);
    PepMroRef mro(type);
    if (mro.isNull()) {
        Shiboken::Errors::storeErrorOrPrint();
        return result;
    }
    auto len = PyTuple_Size(mro.object());
    QString oldResult = result;
    auto *sbkObjectType = reinterpret_cast<PyTypeObject *>(SbkObject_TypeF());
    for (Py_ssize_t idx = 0; idx < len - 1; ++idx) {
        // Skip the last class which is `object`.
        auto *type = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(mro.object(), idx));
        if (type == sbkObjectType)
            continue;
        const char *context = PepType_GetNameStr(type);
        result = QCoreApplication::translate(context, sourceText, disambiguation, n);
        if (result != oldResult)
            break;
    }
#else
    PyObject *mro = type->tp_mro;
    auto len = PyTuple_Size(mro);
    QString result = QString::fromUtf8(sourceText);
    QString oldResult = result;
    auto *sbkObjectType = reinterpret_cast<PyTypeObject *>(SbkObject_TypeF());
    for (Py_ssize_t idx = 0; idx < len - 1; ++idx) {
        // Skip the last class which is `object`.
        auto *type = reinterpret_cast<PyTypeObject *>(PyTuple_GetItem(mro, idx));
        if (type == sbkObjectType)
            continue;
        const char *context = PepType_GetNameStr(type);
        result = QCoreApplication::translate(context, sourceText, disambiguation, n);
        if (result != oldResult)
            break;
    }
#endif
    return result;
}

bool PyDate_ImportAndCheck(PyObject *pyIn)
{
    if (!PyDateTimeAPI)
        PyDateTime_IMPORT;
    return PyDate_Check(pyIn);
}

bool PyDateTime_ImportAndCheck(PyObject *pyIn)
{
    if (!PyDateTimeAPI)
        PyDateTime_IMPORT;
    return PyDateTime_Check(pyIn);
}

bool PyTime_ImportAndCheck(PyObject *pyIn)
{
    if (!PyDateTimeAPI)
        PyDateTime_IMPORT;
    return PyTime_Check(pyIn);
}

PyObject *invokeMetaMethod(const InvokeMetaMethodFunc &f,
                           const QtCoreHelper::QGenericArgumentHolder &a0,
                           const QtCoreHelper::QGenericArgumentHolder &a1,
                           const QtCoreHelper::QGenericArgumentHolder &a2,
                           const QtCoreHelper::QGenericArgumentHolder &a3,
                           const QtCoreHelper::QGenericArgumentHolder &a4,
                           const QtCoreHelper::QGenericArgumentHolder &a5,
                           const QtCoreHelper::QGenericArgumentHolder &a6,
                           const QtCoreHelper::QGenericArgumentHolder &a7,
                           const QtCoreHelper::QGenericArgumentHolder &a8,
                           const QtCoreHelper::QGenericArgumentHolder &a9)
{
    PyThreadState *_save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
    const bool resultB = f(a0.toGenericArgument(), a1.toGenericArgument(), a2.toGenericArgument(),
                           a3.toGenericArgument(), a4.toGenericArgument(), a5.toGenericArgument(),
                           a6.toGenericArgument(), a7.toGenericArgument(), a8.toGenericArgument(),
                           a9.toGenericArgument());
    PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
    PyObject *result = resultB ? Py_True : Py_False;
    Py_INCREF(result);
    return result;
}

// Convert a QGenericReturnArgument to Python for QMetaObject::invokeMethod
static PyObject *convertGenericReturnArgument(const void *retData, QMetaType metaType)
{
    PyObject *result = nullptr;
    switch (metaType.id()) {
    case QMetaType::Bool:
        result = *reinterpret_cast<const bool *>(retData) ? Py_True : Py_False;
        Py_INCREF(result);
        break;
    case QMetaType::Int:
        result = PyLong_FromLong(*reinterpret_cast<const int *>(retData));
        break;
    case QMetaType::Double:
        result = PyFloat_FromDouble(*reinterpret_cast<const double *>(retData));
        break;
    case QMetaType::QString:
        result = PySide::qStringToPyUnicode(*reinterpret_cast<const QString *>(retData));
        break;
    default: {
        Shiboken::Conversions::SpecificConverter converter(metaType.name());
        const auto type = converter.conversionType();
        if (type == Shiboken::Conversions::SpecificConverter::InvalidConversion) {
            PyErr_Format(PyExc_RuntimeError, "%s: Unable to find converter for \"%s\".",
                         __FUNCTION__, metaType.name());
            return nullptr;
        }
        result = converter.toPython(retData);
    }
    }
    return result;
}

PyObject *invokeMetaMethodWithReturn(const InvokeMetaMethodFuncWithReturn &f,
                                     const QtCoreHelper::QGenericReturnArgumentHolder &r,
                                     const QtCoreHelper::QGenericArgumentHolder &a0,
                                     const QtCoreHelper::QGenericArgumentHolder &a1,
                                     const QtCoreHelper::QGenericArgumentHolder &a2,
                                     const QtCoreHelper::QGenericArgumentHolder &a3,
                                     const QtCoreHelper::QGenericArgumentHolder &a4,
                                     const QtCoreHelper::QGenericArgumentHolder &a5,
                                     const QtCoreHelper::QGenericArgumentHolder &a6,
                                     const QtCoreHelper::QGenericArgumentHolder &a7,
                                     const QtCoreHelper::QGenericArgumentHolder &a8,
                                     const QtCoreHelper::QGenericArgumentHolder &a9)
{
    PyThreadState *_save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
    const bool callResult = f(r.toGenericReturnArgument(),
                              a0.toGenericArgument(), a1.toGenericArgument(), a2.toGenericArgument(),
                              a3.toGenericArgument(), a4.toGenericArgument(), a5.toGenericArgument(),
                              a6.toGenericArgument(), a7.toGenericArgument(), a8.toGenericArgument(),
                              a9.toGenericArgument());
    PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
    if (!callResult)
        return PyErr_Format(PyExc_RuntimeError, "QMetaMethod invocation failed.");
    return convertGenericReturnArgument(r.data(), r.metaType());
}
