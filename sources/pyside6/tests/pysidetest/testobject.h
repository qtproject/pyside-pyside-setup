// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTOBJECT_H
#define TESTOBJECT_H

#include "pysidetest_macros.h"

#include <QtWidgets/QApplication>

#include <QtCore/QObject>
#include <QtCore/QMetaType>
#include <QtCore/QVariant>

QT_FORWARD_DECLARE_CLASS(QDebug)

class IntValue
{
public:

    IntValue(int val): value(val){};
    IntValue() : value(0) {};
    int value;
};

typedef IntValue TypedefValue;

class PYSIDETEST_API TestObject : public QObject
{
    Q_OBJECT
public:
    static void createApp() { int argc=0; new QApplication(argc, 0); };
    static int checkType(const QVariant& var) { return var.metaType().id(); }

    TestObject(int idValue, QObject* parent = 0) : QObject(parent), m_idValue(idValue) {}
    int idValue() const { return m_idValue; }
    static int staticMethodDouble(int value) { return value * 2; }
    void addChild(QObject* c) { m_children.append(c); emit childrenChanged(m_children); }

    void emitIdValueSignal();
    void emitStaticMethodDoubleSignal();

    void emitSignalWithDefaultValue_void();
    void emitSignalWithDefaultValue_bool();

    void emitSignalWithTypedefValue(int value);

signals:
    void idValue(int newValue);
    void justASignal();
    void staticMethodDouble();
    void childrenChanged(const QList<QObject*>&);
    void signalWithDefaultValue(bool value = false);
    void signalWithTypedefValue(TypedefValue value);

private:
    int m_idValue;
    QList<QObject*> m_children;
};

PYSIDETEST_API QDebug operator<<(QDebug dbg, TestObject &testObject);

typedef int PySideInt;


namespace PySideCPP {

class PYSIDETEST_API TestObjectWithNamespace :  public QObject
{
    Q_OBJECT
public:
    TestObjectWithNamespace(QObject* parent) : QObject(parent) {}
    QString name() { return QStringLiteral("TestObjectWithNamespace"); }

    void callSignal(TestObjectWithNamespace* obj) { emit emitSignal(obj); }
    void callSignalWithNamespace(TestObjectWithNamespace* obj) { emit emitSignalWithNamespace(obj); }
    void callSignalWithTypedef(int val) { emit emitSignalWithTypedef(val); }

signals:
    void emitSignal(TestObjectWithNamespace* obj);
    void emitSignalWithNamespace(PySideCPP::TestObjectWithNamespace* obj);
    void emitSignalWithTypedef(PySideInt val);
};

PYSIDETEST_API QDebug operator<<(QDebug dbg, TestObjectWithNamespace &testObject);

class PYSIDETEST_API TestObject2WithNamespace :  public QObject
{
    Q_OBJECT
public:
    TestObject2WithNamespace(QObject* parent) : QObject(parent) {}
    QString name() { return QStringLiteral("TestObject2WithNamespace"); }
};

PYSIDETEST_API QDebug operator<<(QDebug dbg, TestObject2WithNamespace& testObject);

} // Namespace PySideCPP

namespace PySideCPP2 {

enum Enum1 { Option1 = 1, Option2 = 2 };


typedef long PySideLong;

class PYSIDETEST_API TestObjectWithoutNamespace :  public QObject
{
    Q_OBJECT
public:
    enum Enum2 { Option3 = 3, Option4 =  4};
    TestObjectWithoutNamespace(QObject* parent) : QObject(parent) {}
    QString name() { return QStringLiteral("TestObjectWithoutNamespace"); }

    void callSignal(TestObjectWithoutNamespace* obj) { emitSignal(obj); }
    void callSignalWithNamespace(TestObjectWithoutNamespace* obj) { emitSignalWithNamespace(obj); }
    void callSignalWithTypedef(long val) { emitSignalWithTypedef(val); }

signals:
    void emitSignal(TestObjectWithoutNamespace* obj);
    void emitSignalWithNamespace(PySideCPP2::TestObjectWithoutNamespace* obj);
    void emitSignalWithTypedef(PySideLong val);
};


} // Namespace PySideCPP2

#endif // TESTOBJECT_H

