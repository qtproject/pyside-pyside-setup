// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "dynamicslot_p.h"
#include "pysidestaticstrings.h"
#include "pysideutils.h"
#include "pysideweakref.h"
#include "signalmanager.h"

#include <autodecref.h>
#include <gilstate.h>
#include <pep384ext.h>

#include <QtCore/QDebug>
#include <QtCore/QtCompare>
#include <QtCore/QCoreApplication>
#include <QtCore/QHash>
#include <QtCore/QPointer>

namespace PySide
{

static void disconnectReceiver(PyObject *pythonSelf);

DynamicSlot::SlotType DynamicSlot::slotType(PyObject *callback)
{
    if (PyMethod_Check(callback) != 0)
        return SlotType::Method;
    if (PySide::isCompiledMethod(callback) != 0)
        return SlotType::CompiledMethod;
    if (PyCFunction_Check(callback) != 0)
        return SlotType::C_Function;
    return SlotType::Callable;
}

// Simple callable slot.
class CallbackDynamicSlot : public DynamicSlot
{
    Q_DISABLE_COPY_MOVE(CallbackDynamicSlot)
public:
    explicit CallbackDynamicSlot(PyObject *callback) noexcept;
    ~CallbackDynamicSlot() override;

    void call(const QByteArrayList &parameterTypes, const char *returnType,
              void **cppArgs) override;
    void formatDebug(QDebug &debug) const override;

private:
    PyObject *m_callback;
};

CallbackDynamicSlot::CallbackDynamicSlot(PyObject *callback) noexcept :
    m_callback(callback)
{
    Py_INCREF(m_callback);
}

CallbackDynamicSlot::~CallbackDynamicSlot()
{
    Shiboken::GilState gil;
    Py_DECREF(m_callback);
}

void CallbackDynamicSlot::call(const QByteArrayList &parameterTypes, const char *returnType,
                               void **cppArgs)
{
    SignalManager::callPythonMetaMethod(parameterTypes, returnType, cppArgs, m_callback);
    // SignalManager::callPythonMetaMethod might have failed, in that case we have to print the
    // error so it considered "handled".
    if (PyErr_Occurred() != nullptr)
        SignalManager::handleMetaCallError();
}

void CallbackDynamicSlot::formatDebug(QDebug &debug) const
{
    debug << "CallbackDynamicSlot(" << PySide::debugPyObject(m_callback) << ')';
}

// A method given by "signal.connect(foo.method)" is a temporarily created
// callable/partial function where self is bound as a first parameter.
// It can be split into self and the function. Keeping a reference on
// the callable itself would prevent object deletion. Instead, keep a
// reference on the function.
class MethodDynamicSlot : public DynamicSlot
{
    Q_DISABLE_COPY_MOVE(MethodDynamicSlot)
public:

    explicit MethodDynamicSlot(PyObject *function, PyObject *pythonSelf);
    ~MethodDynamicSlot() override;

    PyObject *pythonSelf() const { return m_pythonSelf; }

    void call(const QByteArrayList &parameterTypes, const char *returnType,
              void **cppArgs) override;
    void formatDebug(QDebug &debug) const override;

private:
    PyObject *m_function;
    PyObject *m_pythonSelf;
};

MethodDynamicSlot::MethodDynamicSlot(PyObject *function, PyObject *pythonSelf) :
    m_function(function),
    m_pythonSelf(pythonSelf)
{
}

MethodDynamicSlot::~MethodDynamicSlot()
{
    Shiboken::GilState gil;
    Py_DECREF(m_function);
}

void MethodDynamicSlot::call(const QByteArrayList &parameterTypes, const char *returnType,
                             void **cppArgs)
{
    // create a callback based on method data
    Shiboken::AutoDecRef callable(PepExt_Type_CallDescrGet(m_function,
                                                           m_pythonSelf, nullptr));
    SignalManager::callPythonMetaMethod(parameterTypes, returnType,
                                        cppArgs, callable.object());
    // SignalManager::callPythonMetaMethod might have failed, in that case we have to print the
    // error so it considered "handled".
    if (PyErr_Occurred() != nullptr)
        SignalManager::handleMetaCallError();
}

void MethodDynamicSlot::formatDebug(QDebug &debug) const
{
    debug << "MethodDynamicSlot(self=" << PySide::debugPyObject(m_pythonSelf)
        << ", function=" << PySide::debugPyObject(m_function) << ')';
}

// Store a weak reference on pythonSelf.
class TrackingMethodDynamicSlot : public MethodDynamicSlot
{
    Q_DISABLE_COPY_MOVE(TrackingMethodDynamicSlot)
public:
    explicit TrackingMethodDynamicSlot(PyObject *function, PyObject *pythonSelf,
                                       PyObject *weakRef);
    ~TrackingMethodDynamicSlot() override;

    void releaseWeakRef() { m_weakRef = nullptr; }

private:
    PyObject *m_weakRef;
};

TrackingMethodDynamicSlot::TrackingMethodDynamicSlot(PyObject *function, PyObject *pythonSelf,
                                                     PyObject *weakRef) :
    MethodDynamicSlot(function, pythonSelf),
    m_weakRef(weakRef)
{
}

TrackingMethodDynamicSlot::~TrackingMethodDynamicSlot()
{
    if (m_weakRef != nullptr) {
        Shiboken::GilState gil;
        // weakrefs must not be de-refed after the object has been deleted,
        // else they get negative refcounts.
        if (PepExt_Weakref_IsAlive(m_weakRef))
            Py_DECREF(m_weakRef);
    }
}

// Delete the connection on receiver deletion by weakref
class PysideReceiverMethodSlot : public TrackingMethodDynamicSlot
{
    Q_DISABLE_COPY_MOVE(PysideReceiverMethodSlot)
public:
    explicit PysideReceiverMethodSlot(PyObject *function, PyObject *pythonSelf);

    ~PysideReceiverMethodSlot() override = default;
};

static void onPysideReceiverSlotDestroyed(void *data)
{
    auto *self = reinterpret_cast<PysideReceiverMethodSlot *>(data);
    // Ensure the weakref is gone in case the connection stored in
    // Qt's internals outlives Python.
    self->releaseWeakRef();
    Py_BEGIN_ALLOW_THREADS
    disconnectReceiver(self->pythonSelf());
    Py_END_ALLOW_THREADS
}

PysideReceiverMethodSlot::PysideReceiverMethodSlot(PyObject *function, PyObject *pythonSelf) :
    TrackingMethodDynamicSlot(function, pythonSelf,
                              WeakRef::create(pythonSelf, onPysideReceiverSlotDestroyed, this))
{
}

DynamicSlot* DynamicSlot::create(PyObject *callback)
{
    Shiboken::GilState gil;
    switch (slotType(callback)) {
    case SlotType::Method: {
        PyObject *function = PyMethod_GET_FUNCTION(callback);
        Py_INCREF(function);
        PyObject *pythonSelf = PyMethod_GET_SELF(callback);
        return new PysideReceiverMethodSlot(function, pythonSelf);
    }
    case SlotType::CompiledMethod: {
        // PYSIDE-1523: PyMethod_Check is not accepting compiled form, we just go by attributes.
        PyObject *function = PyObject_GetAttr(callback, PySide::PySideName::im_func());
        Py_DECREF(function);
        PyObject *pythonSelf = PyObject_GetAttr(callback, PySide::PySideName::im_self());
        Py_DECREF(pythonSelf);
        return new PysideReceiverMethodSlot(function, pythonSelf);
    }
    case SlotType::C_Function: // Treat C-function as normal callables
    case SlotType::Callable:
        break;
    }
    return new CallbackDynamicSlot(callback);
}

QDebug operator<<(QDebug debug, const DynamicSlot *ds)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    if (ds != nullptr)
        ds->formatDebug(debug);
    else
        debug << "DynamicSlot(0";
    return debug;
}

// Connection code for signal connections that use a Python callable not
// targeting the QMetaMethod of a QObject (no index). They require
// invocation in a class inheriting QtPrivate::QSlotObjectBase (PySideQSlotObject
// aggregating DynamicSlot), which is passed to:
// QObjectPrivate::connect(const QObject *, int signal, QtPrivate::QSlotObjectBase *, ...).
// For each of those connections (identified by ConnectionKey), we maintain a
// hash of ConnectionKey->QMetaObject::Connection for:
//
// - Disconnecting: Retrieve QMetaObject::Connection for the connection parameters
//
// - Tracking sender (QObject) life time and clean hash on destroyed()
//
// - Tracking receiver (PyObject*) life time via weakref in case of a
//       connection to a method and proactively disconnect on weakref
//       notification as not to cause leaks of the instance.

struct ConnectionKey
{
    const QObject *sender;
    int senderIndex;
    const PyObject *object;
    const void *method;

    friend constexpr size_t qHash(const ConnectionKey &k, size_t seed = 0) noexcept
    {
        return qHashMulti(seed, k.sender, k.senderIndex, k.object, k.method);
    }

    friend constexpr bool comparesEqual(const ConnectionKey &lhs,
                                        const ConnectionKey &rhs) noexcept
    {
        return lhs.sender == rhs.sender && lhs.senderIndex == rhs.senderIndex
               && lhs.object == rhs.object && lhs.method == rhs.method;
    }

    Q_DECLARE_EQUALITY_COMPARABLE(ConnectionKey);
};

QDebug operator<<(QDebug debug, const ConnectionKey &k)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "ConnectionKey(" << static_cast<const void *>(k.sender)
          << '/' << k.sender->metaObject()->className();
    auto on =  k.sender->objectName();
    if (!on.isEmpty())
        debug << "/\"" << on << '"';
    debug << ", index=" << k.senderIndex << ", target="
          << PySide::debugPyObject(const_cast<PyObject *>(k.object));
    if (k.method != nullptr)
        debug << ", method=" << k.method;
    debug << ')';
    return debug;
}

QDebug operator<<(QDebug debug, const QMetaObject::Connection &c)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Connection(";
    if (c)
        debug << static_cast<const void *>(&c); // d-ptr;
    else
        debug << '0';
    debug << ')';
    return debug;
}

using ConnectionHash = QHash<ConnectionKey, QMetaObject::Connection>;

static ConnectionHash connectionHash;

static ConnectionKey connectionKey(const QObject *sender, int senderIndex,
                                   PyObject *callback)
{
    PyObject *object{};
    void *method{};

    switch (DynamicSlot::slotType(callback)) {
    case DynamicSlot::SlotType::Method:
        // PYSIDE-1422: Avoid hash on self which might be unhashable.
        object = PyMethod_GET_SELF(callback);
        method = PyMethod_GET_FUNCTION(callback);
        break;
    case DynamicSlot::SlotType::CompiledMethod: {
        // PYSIDE-1589: Fix for slots in compiled functions
        Shiboken::AutoDecRef self(PyObject_GetAttr(callback, PySide::PySideName::im_self()));
        Shiboken::AutoDecRef func(PyObject_GetAttr(callback, PySide::PySideName::im_func()));
        object = self.object();
        method = func.object();
        break;
    }
    case DynamicSlot::SlotType::Callable:
        method = callback;
        break;
    case DynamicSlot::SlotType::C_Function:
        object = PyCFunction_GetSelf(callback);
        method = reinterpret_cast<void *>(PyCFunction_GetFunction(callback));
        break;
    }

    return {sender, senderIndex, object, method};
}

// Listens to QObject::destroyed of senders and removes them from the hash.
class SenderSignalDeletionTracker : public QObject
{
    Q_OBJECT
public:
    using QObject::QObject;

public Q_SLOTS:
    void senderDestroyed(QObject *o);
};

void SenderSignalDeletionTracker::senderDestroyed(QObject *o)
{
    for (auto it = connectionHash.begin(); it != connectionHash.end(); ) {
        if (it.key().sender == o)
            it = connectionHash.erase(it);
        else
            ++it;
    }
}

static QPointer<SenderSignalDeletionTracker> senderSignalDeletionTracker;

static void disconnectReceiver(PyObject *pythonSelf)
{
    // A check for reentrancy was added for PYSIDE-88, but has not been
    // observed yet.
    for (bool keepGoing = true; keepGoing; ) {
        keepGoing = false;
        for (auto it = connectionHash.begin(); it != connectionHash.end(); ) {
            if (it.key().object == pythonSelf) {
                const auto oldSize = connectionHash.size();
                QObject::disconnect(it.value());
                it = connectionHash.erase(it);
                // Check for a disconnection causing deletion of further objects
                // by a re-entrant call.
                if (connectionHash.size() < oldSize - 1) {
                    keepGoing = true;
                    break; // Iterators were invalidated, retry
                }
            } else {
                ++it;
            }
        }
    }
}

static void clearConnectionHash()
{
    connectionHash.clear();
}

void registerSlotConnection(QObject *source, int signalIndex, PyObject *callback,
                            const QMetaObject::Connection &connection)
{
    connectionHash.insert(connectionKey(source, signalIndex, callback), connection);
    if (senderSignalDeletionTracker.isNull()) {
        auto *app = QCoreApplication::instance();
        senderSignalDeletionTracker = new SenderSignalDeletionTracker(app);
        Py_AtExit(clearConnectionHash);
    }

    QObject::connect(source, &QObject::destroyed,
                     senderSignalDeletionTracker, &SenderSignalDeletionTracker::senderDestroyed,
                     Qt::UniqueConnection);
}

bool disconnectSlot(QObject *source, int signalIndex, PyObject *callback)
{
    auto it = connectionHash.find(connectionKey(source, signalIndex, callback));
    const bool ok = it != connectionHash.end();
    if (ok) {
        QObject::disconnect(it.value());
        connectionHash.erase(it);
    }
    return ok;
}

} // namespace PySide

#include "dynamicslot.moc"
