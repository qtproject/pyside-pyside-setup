/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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

typedef QMap<QByteArray, GlobalReceiverV2 *> GlobalReceiverV2Map;
typedef QSharedPointer<GlobalReceiverV2Map> SharedMap;

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
    GlobalReceiverV2(PyObject *callback, SharedMap map);

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
    QByteArray hash() const;

    /**
     * Use to retrieve the unique hash of the PyObject based on GlobalReceiver rules
     *
     * @param   callback The Python callable object used to calculate the id
     * @return  a string with a unique id based on GlobalReceiver contents
     **/
    static QByteArray hash(PyObject *callback);

    const MetaObjectBuilder &metaObjectBuilder() const { return m_metaObject; }
    MetaObjectBuilder &metaObjectBuilder() { return m_metaObject; }

private:
    MetaObjectBuilder m_metaObject;
    DynamicSlotDataV2 *m_data;
    QList<const QObject *> m_refs;
    SharedMap m_sharedMap;
};

}

#endif
