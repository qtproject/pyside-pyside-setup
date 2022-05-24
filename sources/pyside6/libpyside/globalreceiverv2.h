// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef GLOBALRECEIVER_V2_H
#define GLOBALRECEIVER_V2_H

#include <sbkpython.h>

#include "dynamicqmetaobject.h"

#include <QtCore/QByteArray>
#include <QtCore/QObject>
#include <QtCore/QMap>
#include <QtCore/QSharedPointer>

namespace PySide
{

class DynamicSlotDataV2;
class GlobalReceiverV2;

struct GlobalReceiverKey
{
    const PyObject *object;
    const PyObject *method;
};

inline bool operator==(const GlobalReceiverKey &k1, const GlobalReceiverKey &k2)
{
    return k1.object == k2.object && k1.method == k2.method;
}

inline bool operator!=(const GlobalReceiverKey &k1, const GlobalReceiverKey &k2)
{
    return k1.object != k2.object || k1.method != k2.method;
}

size_t qHash(const GlobalReceiverKey &k, size_t seed = 0);

using GlobalReceiverV2Map = QHash<GlobalReceiverKey, GlobalReceiverV2 *>;
using GlobalReceiverV2MapPtr = QSharedPointer<GlobalReceiverV2Map>;

/**
 * A class used to make the link between the C++ Signal/Slot and Python callback
 * This class is used internally by SignalManager
 **/

class GlobalReceiverV2 : public QObject
{
public:
    /**
     * Create a GlobalReceiver object that will call 'callback' argumentent
     *
     * @param   callback    A Python callable object (can be a method or not)
     * @param   ma          A SharedPointer used on Signal manager that contains all instaces of GlobalReceiver
     **/
    GlobalReceiverV2(PyObject *callback, GlobalReceiverV2MapPtr map);

    /**
     * Destructor
     **/
    ~GlobalReceiverV2() override;

    /**
     * Reimplemented function from QObject
     **/
    int qt_metacall(QMetaObject::Call call, int id, void **args) override;
    const QMetaObject *metaObject() const override;

    /**
     * Add a extra slot to this object
     *
     * @param   signature   The signature of the slot to be added
     * @return  The index of this slot on metaobject
     **/
    int addSlot(const char *signature);

    /**
     * Notify to GlobalReceiver about when a new connection was made
     **/
    void notify();

    /**
     * Used to increment the reference of the GlobalReceiver object
     *
     * @param   link    This is a optional paramenter used to link the ref to some QObject life
     **/
    void incRef(const QObject *link = nullptr);

    /**
     * Used to decrement the reference of the GlobalReceiver object
     *
     * @param   link    This is a optional paramenter used to dismiss the link ref to some QObject
     **/
    void decRef(const QObject *link = nullptr);

    /*
     * Return the count of refs which the GlobalReceiver has
     *
     * @param   link    If any QObject was passed, the function return the number of references relative to this 'link' object
     * @return  The number of references
     **/
    int refCount(const QObject *link) const;

    /**
     * Use to retrieve the unique hash of this GlobalReceiver object
     *
     * @return  a string with a unique id based on GlobalReceiver contents
     **/
    GlobalReceiverKey key() const;

    /**
     * Use to retrieve the unique hash of the PyObject based on GlobalReceiver rules
     *
     * @param   callback The Python callable object used to calculate the id
     * @return  a string with a unique id based on GlobalReceiver contents
     **/
    static GlobalReceiverKey key(PyObject *callback);

    const MetaObjectBuilder &metaObjectBuilder() const { return m_metaObject; }
    MetaObjectBuilder &metaObjectBuilder() { return m_metaObject; }

private:
    MetaObjectBuilder m_metaObject;
    DynamicSlotDataV2 *m_data;
    QList<const QObject *> m_refs;
    GlobalReceiverV2MapPtr m_sharedMap;
};

}

#endif
