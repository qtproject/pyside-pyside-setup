// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "dynamicslot_p.h"

#include <sbkfailpoint.h>
#include <sbkftoptions.h>
#include <sbkheldlocks.h>
#include "pysidestaticstrings.h"
#include "pysideutils.h"
#include "pysideweakref.h"
#include "signalmanager_p.h"

#include <autodecref.h>
#include <helper.h>
#include <gilstate.h>
#include <pep384ext.h>

#include <QtCore/qdebug.h>
#include <QtCore/qcompare.h>
#include <QtCore/qcoreapplication.h>
#include <QtCore/qhash.h>
#include <QtCore/qpointer.h>
#include <QtCore/qthread.h>

#include <mutex>
#include <utility>

namespace PySide
{

static void disconnectReceiver(PyObject *pythonSelf);

DynamicSlot::SlotType DynamicSlot::slotType(PyObject *callback)
{
    if (PyMethod_Check(callback) != 0)
        return SlotType::Method;
    if (Shiboken::isCompiledMethod(callback))
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
// reference on the function and a weak reference on the receiver.
//
// PYSIDE-3148: the weak reference is the slot's only authority over the
// receiver. Its callback disconnects when the receiver dies, and call()
// upgrades it for the delivery.
// See "Method slots own their receiver for the call" in the free-threading notes.
class MethodDynamicSlot : public DynamicSlot
{
    Q_DISABLE_COPY_MOVE(MethodDynamicSlot)
public:
    // function and receiverRef are transferred, rawReceiver is borrowed and
    // required: receiverRef may be null, the receiver itself never is.
    MethodDynamicSlot(PyObject *function, PyObject *receiverRef,
                      PyObject *rawReceiver) noexcept;
    ~MethodDynamicSlot() override;

    void call(const QByteArrayList &parameterTypes, const char *returnType,
              void **cppArgs) override;
    void formatDebug(QDebug &debug) const override;

private:
    // receiver is borrowed and must outlive the call; the caller owns it.
    void deliver(const QByteArrayList &parameterTypes, const char *returnType,
                 void **cppArgs, PyObject *receiver);

    PyObject *m_function;
    PyObject *m_receiverRef;
    // Borrowed. A build with a GIL binds it for every delivery, as it always
    // did; free-threaded it is read only with MethodReceiverUpgrade cleared.
    PyObject *m_rawReceiver;
};

MethodDynamicSlot::MethodDynamicSlot(PyObject *function, PyObject *receiverRef,
                                     PyObject *rawReceiver) noexcept :
    m_function(function),
    m_receiverRef(receiverRef)
{
#ifndef Py_GIL_DISABLED
    // The receiver the delivery binds, as this slot always bound it. The
    // weakref is what disconnects when the receiver dies, and with a GIL
    // nothing runs between that callback and a delivery.
    m_rawReceiver = rawReceiver;
#else
    // Only with MethodReceiverUpgrade cleared; filling it costs an upgrade.
    m_rawReceiver = nullptr;
    if (!Shiboken::FreeThreading::optionEnabled(
            Shiboken::FreeThreading::MethodReceiverUpgrade)) {
        m_rawReceiver = rawReceiver;
    }
#endif
}

MethodDynamicSlot::~MethodDynamicSlot()
{
    // The slot is the sole owner of the weakref, on a disconnect as after the
    // receiver died (PYSIDE-3148).
    Shiboken::GilState gil;
    Py_DECREF(m_function);
    Py_XDECREF(m_receiverRef); // null only with MethodReceiverUpgrade cleared
}

void MethodDynamicSlot::call(const QByteArrayList &parameterTypes, const char *returnType,
                             void **cppArgs)
{
#ifndef Py_GIL_DISABLED
    // Bound raw, the way this slot always bound it: no upgrade per delivery.
    deliver(parameterTypes, returnType, cppArgs, m_rawReceiver);
#else
    // Cleared, bind the raw pointer without touching the refcount:
    // an upgrade and release here could deallocate inside the delivery.
    if (!Shiboken::FreeThreading::optionEnabled(
            Shiboken::FreeThreading::MethodReceiverUpgrade)) {
        deliver(parameterTypes, returnType, cppArgs, m_rawReceiver);
        return;
    }
    // A delivery already inside QSlotObjectBase::Call keeps running while
    // another thread drops the receiver. Own the receiver for the whole call.
    Shiboken::AutoDecRef pythonSelf(WeakRef::deref(m_receiverRef));
    deliver(parameterTypes, returnType, cppArgs, pythonSelf.object());
#endif
}

void MethodDynamicSlot::deliver(const QByteArrayList &parameterTypes, const char *returnType,
                                void **cppArgs, PyObject *receiver)
{
    if (receiver == nullptr) {
        if (PyErr_Occurred() != nullptr)
            SignalManager::handleMetaCallError();
        return; // The receiver is gone; its disconnect is under way.
    }
    // B12-4: a test drops the receiver from another thread here.
    SBK_FAILPOINT("method-receiver-before-bind");
    // create a callback based on method data
    Shiboken::AutoDecRef callable(PepExt_Type_CallDescrGet(m_function,
                                                           receiver, nullptr));
    SignalManager::callPythonMetaMethod(parameterTypes, returnType,
                                        cppArgs, callable.object());
    // SignalManager::callPythonMetaMethod might have failed, in that case we have to print the
    // error so it considered "handled".
    if (PyErr_Occurred() != nullptr)
        SignalManager::handleMetaCallError();
}

void MethodDynamicSlot::formatDebug(QDebug &debug) const
{
#ifndef Py_GIL_DISABLED
    debug << "MethodDynamicSlot(self=" << PySide::debugPyObject(m_rawReceiver)
        << ", function=" << PySide::debugPyObject(m_function) << ')';
#else
    debug << "MethodDynamicSlot(receiverRef=" << PySide::debugPyObject(m_receiverRef)
        << ", function=" << PySide::debugPyObject(m_function) << ')';
#endif
}

static void onPysideReceiverSlotDestroyed(void *data)
{
    auto *pythonSelf = reinterpret_cast<PyObject *>(data);
#ifdef Py_GIL_DISABLED
    // disconnectReceiver() detaches around the Qt disconnects itself.
    disconnectReceiver(pythonSelf);
#else
    Py_BEGIN_ALLOW_THREADS
    disconnectReceiver(pythonSelf);
    Py_END_ALLOW_THREADS
#endif
}

// \a function is handed over, \a pythonSelf is borrowed. Returns nullptr only
// on a free-threaded build, for a receiver that supports no weak reference:
// there the slot has nothing to upgrade for the delivery.
static DynamicSlot *createMethodSlot(PyObject *function, PyObject *pythonSelf)
{
    // PYSIDE-3148: the slot owns the returned reference (keepReference) for its
    // whole life, so the destructor releases it on an ordinary disconnect too.
    PyObject *weakRef = WeakRef::create(pythonSelf, onPysideReceiverSlotDestroyed,
                                        pythonSelf, true);
    if (weakRef == nullptr) {
#ifdef Py_GIL_DISABLED
        // Only the TypeError of a receiver without __weakref__ selects the
        // fallback silently; any other error (e.g. MemoryError) is reported.
        if (PyErr_Occurred() != nullptr && !PyErr_ExceptionMatches(PyExc_TypeError))
            PyErr_WriteUnraisable(pythonSelf);
        PyErr_Clear();
        if (Shiboken::FreeThreading::optionEnabled(
                Shiboken::FreeThreading::MethodReceiverUpgrade)) {
            Py_DECREF(function);
            return nullptr;
        }
#endif
        // A build with a GIL builds the slot anyway and binds the raw
        // receiver, as it always has. That the connection then outlives the
        // receiver, and that WeakRef::create() left its exception behind, are
        // that build's own defects and are fixed in a change of their own.
        return new MethodDynamicSlot(function, nullptr, pythonSelf);
    }
    return new MethodDynamicSlot(function, weakRef, pythonSelf);
}

DynamicSlot* DynamicSlot::create(PyObject *callback)
{
    Shiboken::GilState gil;
    switch (slotType(callback)) {
    case SlotType::Method: {
        PyObject *function = PyMethod_GET_FUNCTION(callback);
        Py_INCREF(function);
        PyObject *pythonSelf = PyMethod_GET_SELF(callback);
        if (auto *slot = createMethodSlot(function, pythonSelf))
            return slot;
        break;
    }
    case SlotType::CompiledMethod: {
        // PYSIDE-1523: PyMethod_Check is not accepting compiled form, we just go by attributes.
#ifdef Py_GIL_DISABLED
        Shiboken::AutoDecRef function(PyObject_GetAttr(callback, PySide::PySideName::im_func()));
        Shiboken::AutoDecRef pythonSelf(PyObject_GetAttr(callback, PySide::PySideName::im_self()));
        if (function.isNull() || pythonSelf.isNull()) {
            PyErr_Clear();
            break;
        }
        if (auto *slot = createMethodSlot(Py_NewRef(function.object()), pythonSelf))
            return slot;
#else
        // The references are dropped at once and the slot then runs on what
        // the callback holds - unbalanced, and left that way on purpose: it
        // is this build's own defect and is fixed in a change of its own.
        PyObject *function = PyObject_GetAttr(callback, PySide::PySideName::im_func());
        Py_DECREF(function);
        PyObject *pythonSelf = PyObject_GetAttr(callback, PySide::PySideName::im_self());
        Py_DECREF(pythonSelf);
        if (auto *slot = createMethodSlot(function, pythonSelf))
            return slot;
#endif
        break;
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

#ifdef Py_GIL_DISABLED
// The hash is global and reached from every thread that connects, disconnects
// or lets a sender die, so it needs a lock of its own. Container work only:
// nothing calls Qt or Python while it is held, because QObject::disconnect
// takes Qt's own signal-slot locks and can re-enter here through a destroyed()
// delivery. Every user below takes the entries out under the lock and does the
// Qt part after it.
static std::mutex &connectionHashMutex()
{
    static std::mutex mutex;
    return mutex;
}

using ConnectionHashLock =
    Shiboken::TrackedGuard<std::mutex, Shiboken::RawLock::ConnectionHash>;
#endif // Py_GIL_DISABLED

/// The hash key, and whatever had to be created to compute it.
///
/// Computing it runs Python: slotType() asks the callback for three
/// attributes, and a callback that is itself a QObject answers through the
/// meta-object machinery, which takes a lock and a call lease of its own.
/// None of that may happen under the hash mutex - a mutex held across
/// Python deadlocks against stop-the-world, and the lease it takes can
/// start a deferred destructor while the mutex is held. So the key is built
/// first and the mutex only sees a finished one.
///
/// The two references the compiled-method case creates are kept here rather
/// than dropped where they were read: they are what the key's addresses
/// point at, and letting them die before the entry goes in would leave a
/// key made of addresses that anything may reuse. They outlive the
/// transaction. Outliving the *stored entry* is a different question - it
/// needs a slot owner that knows about Python lifetimes, and that belongs
/// with the signal and slot work; holding these references in the hash
/// instead would keep receivers alive for as long as the connection and
/// trade a stale address for a leak.
class PreparedConnectionKey
{
public:
    PreparedConnectionKey(const QObject *sender, int senderIndex,
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
        case DynamicSlot::SlotType::CompiledMethod:
            // PYSIDE-1589: Fix for slots in compiled functions
            m_self.reset(PyObject_GetAttr(callback, PySide::PySideName::im_self()));
            m_func.reset(PyObject_GetAttr(callback, PySide::PySideName::im_func()));
            object = m_self.object();
            method = m_func.object();
            break;
        case DynamicSlot::SlotType::Callable:
            method = callback;
            break;
        case DynamicSlot::SlotType::C_Function:
            object = PyCFunction_GetSelf(callback);
            method = reinterpret_cast<void *>(PyCFunction_GetFunction(callback));
            break;
        }

        m_key = {sender, senderIndex, object, method};
    }

    const ConnectionKey &key() const { return m_key; }

private:
    Shiboken::AutoDecRef m_self;
    Shiboken::AutoDecRef m_func;
    ConnectionKey m_key;
};

// Listens to QObject::destroyed of senders and removes them from the hash.
class SenderSignalDeletionTracker : public QObject
{
    Q_OBJECT
public:
    using QObject::QObject;

public Q_SLOTS:
    void senderDestroyed(QObject *o);
    void reparentOnQApp();
};

void SenderSignalDeletionTracker::senderDestroyed(QObject *o)
{
    Shiboken::GilState gil; // PYSIDE-3072
    // Qt delivers destroyed() from whichever thread the sender died on, so
    // this races registerSlotConnection() and disconnectSlot(). Erasing is all
    // it does, so the hash lock is the whole story.
#ifdef Py_GIL_DISABLED
    ConnectionHashLock hashLock(connectionHashMutex());
#endif
    for (auto it = connectionHash.begin(); it != connectionHash.end(); ) {
        if (it.key().sender == o)
            it = connectionHash.erase(it);
        else
            ++it;
    }
}

void SenderSignalDeletionTracker::reparentOnQApp()
{
    if (auto *app = QCoreApplication::instance())
        setParent(app);
}

static QPointer<SenderSignalDeletionTracker> senderSignalDeletionTracker;

static void disconnectReceiver(PyObject *pythonSelf)
{
#ifdef Py_GIL_DISABLED
    // Pull the matching entries out of the hash under its lock (container work
    // only, QTBUG-144929: take copies), then run the Qt disconnects with no
    // lock held and the thread detached: QObject::disconnect takes Qt's
    // internal signal-slot locks and can come back here through a destroyed()
    // delivery. Disconnecting may re-entrantly delete further receivers
    // (PYSIDE-88); their callbacks then find a hash that no longer contains
    // these entries, so no iterator is invalidated under our feet. Kept to
    // free-threaded builds: the GIL build serializes itself and this code is
    // regression-prone.
    QList<QMetaObject::Connection> connections;
    {
        ConnectionHashLock hashLock(connectionHashMutex());
        for (auto it = connectionHash.begin(); it != connectionHash.end(); ) {
            if (it.key().object == pythonSelf) {
                connections.append(it.value());
                it = connectionHash.erase(it);
            } else {
                ++it;
            }
        }
    }
    Py_BEGIN_ALLOW_THREADS
    for (const auto &connection : std::as_const(connections))
        QObject::disconnect(connection);
    Py_END_ALLOW_THREADS
#else
    // A check for reentrancy was added for PYSIDE-88, but has not been
    // observed yet.
    for (bool keepGoing = true; keepGoing; ) {
        keepGoing = false;
        for (auto it = connectionHash.begin(); it != connectionHash.end(); ) {
            if (it.key().object == pythonSelf) {
                const auto oldSize = connectionHash.size();
                auto connId = it.value(); // QTBUG-144929, take copy
                QObject::disconnect(connId);
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
#endif
}

static void clearConnectionHash()
{
#ifdef Py_GIL_DISABLED
    ConnectionHashLock hashLock(connectionHashMutex());
#endif
    connectionHash.clear();
}

void registerSlotConnection(QObject *source, int signalIndex, PyObject *callback,
                            const QMetaObject::Connection &connection)
{
    const PreparedConnectionKey prepared(source, signalIndex, callback);
    {
#ifdef Py_GIL_DISABLED
        ConnectionHashLock hashLock(connectionHashMutex());
#endif
        connectionHash.insert(prepared.key(), connection);
    }

    if (senderSignalDeletionTracker.isNull()) {
        auto *app = QCoreApplication::instance();
        if (app == nullptr || QThread::currentThread() == app->thread()) {
            senderSignalDeletionTracker = new SenderSignalDeletionTracker(app);
        } else {
            senderSignalDeletionTracker = new SenderSignalDeletionTracker(nullptr);
            senderSignalDeletionTracker->moveToThread(app->thread());
            QMetaObject::invokeMethod(senderSignalDeletionTracker, "reparentOnQApp",
                                      Qt::QueuedConnection);
        }
        Py_AtExit(clearConnectionHash);
    }

    QObject::connect(source, &QObject::destroyed,
                     senderSignalDeletionTracker, &SenderSignalDeletionTracker::senderDestroyed,
                     Qt::UniqueConnection);
}

bool disconnectSlot(QObject *source, int signalIndex, PyObject *callback)
{
    const PreparedConnectionKey prepared(source, signalIndex, callback);
    QMetaObject::Connection connId;
    bool ok = false;
    {
#ifdef Py_GIL_DISABLED
        ConnectionHashLock hashLock(connectionHashMutex());
#endif
        auto it = connectionHash.find(prepared.key());
        ok = it != connectionHash.end();
        if (ok) {
            connId = it.value(); // QTBUG-144929, take copy
            connectionHash.erase(it);
        }
    }
    // Outside the lock, like disconnectReceiver(): the disconnect can re-enter
    // through destroyed().
    if (ok)
        QObject::disconnect(connId);
    return ok;
}

} // namespace PySide

#include "dynamicslot.moc"
