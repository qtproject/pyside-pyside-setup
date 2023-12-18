// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef GLOBALRECEIVER_V2_H
#define GLOBALRECEIVER_V2_H

#include <sbkpython.h>

#include "dynamicqmetaobject.h"

#include <QtCore/QtCompare>
#include <QtCore/QByteArray>
#include <QtCore/QHashFunctions>
#include <QtCore/QObject>
#include <QtCore/QPointer>
#include <QtCore/QMap>

#include <memory>

QT_FORWARD_DECLARE_CLASS(QDebug);

namespace PySide
{

class DynamicSlotDataV2;
class GlobalReceiverV2;

struct GlobalReceiverKey
{
    const PyObject *object;
    const PyObject *method;

    friend constexpr size_t qHash(GlobalReceiverKey k, size_t seed = 0) noexcept
    {
        return qHashMulti(seed, k.object, k.method);
    }
    friend constexpr bool comparesEqual(const GlobalReceiverKey &lhs,
                                        const GlobalReceiverKey &rhs) noexcept
    {
        return lhs.object == rhs.object && lhs.method == rhs.method;
    }
    Q_DECLARE_EQUALITY_COMPARABLE_LITERAL_TYPE(GlobalReceiverKey)
};

/// A class used to link C++ Signals to non C++ slots (Python callbacks) by
/// providing fake slots for QObject::connect().
/// It keeps a Python callback and the list of QObject senders. It is stored
/// in SignalManager by a hash of the Python callback.
class GlobalReceiverV2 : public QObject
{
public:
    Q_DISABLE_COPY_MOVE(GlobalReceiverV2)

    /// Create a GlobalReceiver object that will call 'callback'
    /// @param callback A Python callable object (can be a method or not)
    explicit GlobalReceiverV2(PyObject *callback, QObject *receiver = nullptr);

    ~GlobalReceiverV2() override;

    /// Reimplemented function from QObject
    int qt_metacall(QMetaObject::Call call, int id, void **args) override;
    const QMetaObject *metaObject() const override;

    /// Add a extra slot to this object
    /// @param  signature The signature of the slot to be added
    /// @return The index of this slot on metaobject
    int addSlot(const char *signature);

    /// Notify to GlobalReceiver about when a new connection was made
    void notify();

    /// Used to increment the reference of the GlobalReceiver object
    /// @param link This is a parameter used to link the ref to
    ///             some QObject life.
    void incRef(const QObject *link);

    /// Used to decrement the reference of the GlobalReceiver object.
    /// @param link This is a parameter used to dismiss the link
    ///             ref to some QObject.
    void decRef(const QObject *link);

    /// Returns whether any senders are registered.
    bool isEmpty() const;

    /// Use to retrieve the unique hash of this GlobalReceiver object
    /// @return hash key
    GlobalReceiverKey key() const;

    /// Use to retrieve the unique hash of the PyObject based on GlobalReceiver rules
    /// @param callback The Python callable object used to calculate the id
    /// @return hash key
    static GlobalReceiverKey key(PyObject *callback);

    const MetaObjectBuilder &metaObjectBuilder() const { return m_metaObject; }
    MetaObjectBuilder &metaObjectBuilder() { return m_metaObject; }

    static const char *senderDynamicProperty;

    void formatDebug(QDebug &debug) const;

private:
    void purgeDeletedSenders();

    MetaObjectBuilder m_metaObject;
    DynamicSlotDataV2 *m_data;
    using QObjectPointer = QPointer<const QObject>;
    QList<QObjectPointer> m_refs;
    QPointer<QObject> m_receiver;
};

QDebug operator<<(QDebug debug, const GlobalReceiverV2 *g);

}

#endif
