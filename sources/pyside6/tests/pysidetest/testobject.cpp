// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testobject.h"

#include <QtCore/QDebug>

void TestObject::emitIdValueSignal()
{
    emit idValue(m_idValue);
}

void TestObject::emitStaticMethodDoubleSignal()
{
    emit staticMethodDouble();
}

void TestObject::emitSignalWithDefaultValue_void()
{
    emit signalWithDefaultValue();
}

void TestObject::emitSignalWithDefaultValue_bool()
{
    emit signalWithDefaultValue(true);
}

void TestObject::emitSignalWithTypedefValue(int value)
{
    emit signalWithTypedefValue(TypedefValue(value));
}

void TestObject::emitSignalWithContainerTypedefValue(const IntList &il)
{
    emit signalWithContainerTypedefValue(il);
}

void TestObject::emitFlagsSignal(Qt::Alignment alignment)
{
    emit flagsSignal(alignment);
}

void TestObject::setQLatin1String(QLatin1String v)
{
    m_qLatin1String = v;
}

QString TestObject::qLatin1String() const
{
    return m_qLatin1String;
}

QDebug operator<<(QDebug dbg, TestObject& testObject)
{
    QDebugStateSaver saver(dbg);
    dbg.nospace() << "TestObject(id=" << testObject.idValue() << ") ";
    return dbg;
}

namespace PySideCPP {
    QDebug operator<<(QDebug dbg, TestObjectWithNamespace& testObject)
    {
        QDebugStateSaver saver(dbg);
        dbg.nospace() << "TestObjectWithNamespace(" << testObject.name() << ") ";
        return dbg;
    }
    QDebug operator<<(QDebug dbg, TestObject2WithNamespace& testObject)
    {
        QDebugStateSaver saver(dbg);
        dbg.nospace() << "TestObject2WithNamespace(" << testObject.name() << ") ";
        return dbg;
    }
}
