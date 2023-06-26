// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "globalreceiverv2.h"
#include "pysideweakref.h"
#include "pysidestaticstrings.h"
#include "pysideutils.h"
#include "signalmanager.h"

#include <autodecref.h>
#include <gilstate.h>

#include <QtCore/qhashfunctions.h>
#include <QtCore/QMetaMethod>
#include <QtCore/QSet>
#include <QtCore/QDebug>

#include <cstring>

#define RECEIVER_DESTROYED_SLOT_NAME "__receiverDestroyed__(QObject*)"


namespace PySide
{

size_t qHash(const GlobalReceiverKey &k, size_t seed)
{
    QtPrivate::QHashCombine hash;
    seed = hash(seed, k.object);
    seed = hash(seed, k.method);
    return seed;
}

class DynamicSlotDataV2
{
    Q_DISABLE_COPY(DynamicSlotDataV2)
    public:
        DynamicSlotDataV2(PyObject *callback, GlobalReceiverV2 *parent);
        ~DynamicSlotDataV2();

        int addSlot(const char *signature);
        int id(const char *signature) const;
        PyObject *callback();
        GlobalReceiverKey key() const { return {m_pythonSelf, m_callback}; }
        void notify();

        static void onCallbackDestroyed(void *data);
        static GlobalReceiverKey key(PyObject *callback);

        void formatDebug(QDebug &debug) const;

    private:
        bool m_isMethod;
        PyObject *m_callback;
        PyObject *m_pythonSelf = nullptr;
        PyObject *m_pyClass = nullptr;
        PyObject *m_weakRef = nullptr;
        QMap<QByteArray, int> m_signatures;
        GlobalReceiverV2 *m_parent;
};

void DynamicSlotDataV2::formatDebug(QDebug &debug) const
{
    debug << "method=" << m_isMethod << ", m_callback=" << m_callback;
    if (m_callback != nullptr)
        debug << '/' << Py_TYPE(m_callback)->tp_name;
    debug << ", self=" << m_pythonSelf;
    if (m_pythonSelf != nullptr)
        debug << '/' << Py_TYPE(m_pythonSelf)->tp_name;
    debug << ", m_pyClass=" << m_pyClass;
    if (m_pyClass != nullptr)
        debug << '/' << Py_TYPE(m_pyClass)->tp_name;
    debug << ", signatures=" << m_signatures.keys();
}

QDebug operator<<(QDebug debug, const DynamicSlotDataV2 *d)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "DynamicSlotDataV2(";
    if (d)
        d->formatDebug(debug);
    else
        debug << '0';
    debug << ')';
    return debug;
}

using namespace PySide;

DynamicSlotDataV2::DynamicSlotDataV2(PyObject *callback, GlobalReceiverV2 *parent) :
    m_parent(parent)
{
    Shiboken::GilState gil;

    if (PyMethod_Check(callback)) {
        m_isMethod = true;
        // To avoid increment instance reference keep the callback information
        m_callback = PyMethod_GET_FUNCTION(callback);
        Py_INCREF(m_callback);
        m_pythonSelf = PyMethod_GET_SELF(callback);

        //monitor class from method lifetime
        m_weakRef = WeakRef::create(m_pythonSelf, DynamicSlotDataV2::onCallbackDestroyed, this);
    } else if (PySide::isCompiledMethod(callback)) {
        // PYSIDE-1523: PyMethod_Check is not accepting compiled form, we just go by attributes.
        m_isMethod = true;

        m_callback = PyObject_GetAttr(callback, PySide::PySideName::im_func());
        Py_DECREF(m_callback);

        m_pythonSelf = PyObject_GetAttr(callback, PySide::PySideName::im_self());
        Py_DECREF(m_pythonSelf);

        //monitor class from method lifetime
        m_weakRef = WeakRef::create(m_pythonSelf, DynamicSlotDataV2::onCallbackDestroyed, this);
    } else {
        m_isMethod = false;

        m_callback = callback;
        Py_INCREF(m_callback);
    }
}

GlobalReceiverKey DynamicSlotDataV2::key(PyObject *callback)
{
    Shiboken::GilState gil;
    if (PyMethod_Check(callback)) {
        // PYSIDE-1422: Avoid hash on self which might be unhashable.
        return {PyMethod_GET_SELF(callback), PyMethod_GET_FUNCTION(callback)};
    } else if (PySide::isCompiledMethod(callback)) {
        // PYSIDE-1589: Fix for slots in compiled functions
        Shiboken::AutoDecRef self(PyObject_GetAttr(callback, PySide::PySideName::im_self()));
        Shiboken::AutoDecRef func(PyObject_GetAttr(callback, PySide::PySideName::im_func()));
        return {self, func};
    }
    return {nullptr, callback};
}

PyObject *DynamicSlotDataV2::callback()
{
    PyObject *callback = m_callback;

    //create a callback based on method data
    if (m_isMethod)
        callback = Py_TYPE(m_callback)->tp_descr_get(m_callback, m_pythonSelf, nullptr);
    else
        Py_INCREF(callback);

    return callback;
}

int DynamicSlotDataV2::id(const char *signature) const
{
    const auto it = m_signatures.constFind(signature);
    return it != m_signatures.cend() ? it.value() : -1;
}

int DynamicSlotDataV2::addSlot(const char *signature)
{
    int index = id(signature);
    if (index == -1)
        index = m_signatures[signature] = m_parent->metaObjectBuilder().addSlot(signature);
    return index;
}

void DynamicSlotDataV2::onCallbackDestroyed(void *data)
{
    auto self = reinterpret_cast<DynamicSlotDataV2 *>(data);
    self->m_weakRef = nullptr;
    Py_BEGIN_ALLOW_THREADS
    SignalManager::instance().deleteGobalReceiver(self->m_parent);
    Py_END_ALLOW_THREADS
}

DynamicSlotDataV2::~DynamicSlotDataV2()
{
    Shiboken::GilState gil;

    Py_XDECREF(m_weakRef);
    m_weakRef = nullptr;

    Py_DECREF(m_callback);
}

const char *GlobalReceiverV2::senderDynamicProperty = "_q_pyside_sender";

GlobalReceiverV2::GlobalReceiverV2(PyObject *callback, QObject *receiver) :
    QObject(nullptr),
    m_metaObject("__GlobalReceiver__", &QObject::staticMetaObject),
    m_receiver(receiver)
{
    m_data = new DynamicSlotDataV2(callback, this);
}

GlobalReceiverV2::~GlobalReceiverV2()
{
    m_refs.clear();
    // Remove itself from map.
    // Suppress handling of destroyed() for objects whose last reference is contained inside
    // the callback object that will now be deleted. The reference could be a default argument,
    // a callback local variable, etc.
    // The signal has to be suppressed because it would lead to the following situation:
    // Callback is deleted, hence the last reference is decremented,
    // leading to the object being deleted, which emits destroyed(), which would try to invoke
    // the already deleted callback, and also try to delete the object again.
    DynamicSlotDataV2 *data = m_data;
    m_data = nullptr;
    delete data;
}

int GlobalReceiverV2::addSlot(const char *signature)
{
    return m_data->addSlot(signature);
}

void GlobalReceiverV2::incRef(const QObject *link)
{
    Q_ASSERT(link);
    m_refs.append(link);
}

void GlobalReceiverV2::decRef(const QObject *link)
{
    Q_ASSERT(link);
    m_refs.removeOne(link);
}

void GlobalReceiverV2::notify()
{
    purgeDeletedSenders();
}

static bool isNull(const QPointer<const QObject> &p)
{
    return p.isNull();
}

void GlobalReceiverV2::purgeDeletedSenders()
{
    m_refs.erase(std::remove_if(m_refs.begin(), m_refs.end(), isNull), m_refs.end());
}

bool GlobalReceiverV2::isEmpty() const
{
    return std::all_of(m_refs.cbegin(), m_refs.cend(), isNull);
}

GlobalReceiverKey GlobalReceiverV2::key() const
{
    return m_data->key();
}

GlobalReceiverKey GlobalReceiverV2::key(PyObject *callback)
{
    return DynamicSlotDataV2::key(callback);
}

const QMetaObject *GlobalReceiverV2::metaObject() const
{
    return const_cast<GlobalReceiverV2 *>(this)->m_metaObject.update();
}

int GlobalReceiverV2::qt_metacall(QMetaObject::Call call, int id, void **args)
{
    Shiboken::GilState gil;
    Q_ASSERT(call == QMetaObject::InvokeMetaMethod);
    Q_ASSERT(id >= QObject::staticMetaObject.methodCount());

    QMetaMethod slot = metaObject()->method(id);
    Q_ASSERT(slot.methodType() == QMetaMethod::Slot);

    if (!m_data) {
        const QByteArray message = "PySide6 Warning: Skipping callback call "
            + slot.methodSignature() + " because the callback object is being destructed.";
        PyErr_WarnEx(PyExc_RuntimeWarning, message.constData(), 0);
        return -1;
    }

    const bool setSenderDynamicProperty = !m_receiver.isNull();
    if (setSenderDynamicProperty)
        m_receiver->setProperty(senderDynamicProperty, QVariant::fromValue(sender()));

    const bool isShortCuit = std::strchr(slot.methodSignature(), '(') == nullptr;
    Shiboken::AutoDecRef callback(m_data->callback());
    SignalManager::callPythonMetaMethod(slot, args, callback, isShortCuit);

    if (setSenderDynamicProperty)
        m_receiver->setProperty(senderDynamicProperty, QVariant{});

    // SignalManager::callPythonMetaMethod might have failed, in that case we have to print the
    // error so it considered "handled".
    if (PyErr_Occurred()) {
        int reclimit = Py_GetRecursionLimit();
        // Inspired by Python's errors.c: PyErr_GivenExceptionMatches() function.
        // Temporarily bump the recursion limit, so that PyErr_Print will not raise a recursion
        // error again. Don't do it when the limit is already insanely high, to avoid overflow.
        if (reclimit < (1 << 30))
            Py_SetRecursionLimit(reclimit + 5);
        PyErr_Print();
        Py_SetRecursionLimit(reclimit);
    }

    return -1;
}

void GlobalReceiverV2::formatDebug(QDebug &debug) const
{
    debug << "receiver=" << m_receiver << ", slot=" << m_data;
    if (isEmpty())
        debug << ", empty";
    else
        debug << ", refs=" << m_refs;
};

QDebug operator<<(QDebug debug, const GlobalReceiverV2 *g)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "GlobalReceiverV2(";
    if (g)
        g->formatDebug(debug);
    else
        debug << '0';
    debug << ')';
    return debug;
}

} // namespace PySide
