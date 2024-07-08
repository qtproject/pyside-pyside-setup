// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "globalreceiverv2.h"
#include "dynamicslot_p.h"
#include "pysideweakref.h"
#include "pysidestaticstrings.h"
#include "pysideutils.h"
#include "signalmanager.h"

#include <autodecref.h>
#include <gilstate.h>
#include <pep384ext.h>

#include <QtCore/QMetaMethod>
#include <QtCore/QSet>
#include <QtCore/QDebug>

#include <cstring>
#include <utility>

namespace PySide
{

GlobalReceiverKey GlobalReceiverV2::key(PyObject *callback)
{
    Shiboken::GilState gil;
    switch (DynamicSlot::slotType(callback)) {
    case DynamicSlot::SlotType::Method:
        // PYSIDE-1422: Avoid hash on self which might be unhashable.
        return {PyMethod_GET_SELF(callback), PyMethod_GET_FUNCTION(callback)};
    case DynamicSlot::SlotType::CompiledMethod: {
        // PYSIDE-1589: Fix for slots in compiled functions
        Shiboken::AutoDecRef self(PyObject_GetAttr(callback, PySide::PySideName::im_self()));
        Shiboken::AutoDecRef func(PyObject_GetAttr(callback, PySide::PySideName::im_func()));
        return {self, func};
    }
    case DynamicSlot::SlotType::Callable:
        break;
    }
    return {nullptr, callback};
}

const char *GlobalReceiverV2::senderDynamicProperty = "_q_pyside_sender";

GlobalReceiverV2::GlobalReceiverV2(PyObject *callback, QObject *receiver) :
    QObject(nullptr),
    m_metaObject("__GlobalReceiver__", &QObject::staticMetaObject),
    m_data(DynamicSlot::create(callback, this)),
    m_receiver(receiver)
{
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
    delete std::exchange(m_data, nullptr);
}

int GlobalReceiverV2::addSlot(const QByteArray &signature)
{
    auto it = m_signatures.find(signature);
    if (it == m_signatures.end()) {
        const int index = metaObjectBuilder().addSlot(signature);
        it = m_signatures.insert(signature, index);
    }
    return it.value();
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

    m_data->call(slot.parameterTypes(), slot.typeName(), args);

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
    debug << "receiver=" << m_receiver
        << ", signatures=" << m_signatures.keys() << ", slot=" << m_data;
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
