// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef DYNAMICSLOT_P_H
#define DYNAMICSLOT_P_H

#include <sbkpython.h>

#include <QtCore/QtCompare>

QT_FORWARD_DECLARE_CLASS(QDebug)

namespace PySide
{

class GlobalReceiverV2;

class DynamicSlot
{
    Q_DISABLE_COPY_MOVE(DynamicSlot)
public:
    enum SlotType
    {
        Callable,
        Method,
        CompiledMethod
    };

    virtual ~DynamicSlot() = default;

    virtual void call(const QByteArrayList &parameterTypes, const char *returnType,
                      void **cppArgs) = 0;
    virtual void formatDebug(QDebug &debug) const = 0;

    static SlotType slotType(PyObject *callback);
    static DynamicSlot *create(PyObject *callback, GlobalReceiverV2 *parent = nullptr);

protected:
    DynamicSlot() noexcept = default;
};

QDebug operator<<(QDebug debug, const DynamicSlot *ds);

}

#endif // DYNAMICSLOT_P_H
