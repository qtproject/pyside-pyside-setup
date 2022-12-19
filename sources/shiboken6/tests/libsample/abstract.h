// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACT_H
#define ABSTRACT_H

#include "libsamplemacros.h"
#include "point.h"
#include "complex.h"

class ObjectType;

// this class is not exported to python
class HideType
{
};

class LIBSAMPLE_API Abstract
{
private:
    enum PrivateEnum {
        PrivValue0,
        PrivValue1,
        PrivValue2 = PrivValue1 + 2
    };
public:
    enum PrintFormat {
        Short,
        Verbose,
        OnlyId,
        ClassNameAndId,
        DummyItemToTestPrivateEnum1 = Abstract::PrivValue1,
        DummyItemToTestPrivateEnum2 = PrivValue2,
    };

    enum Type {
        TpAbstract, TpDerived
    };

    static const int staticPrimitiveField;
    int primitiveField = 123;
    Complex userPrimitiveField;
    Point valueTypeField{12, 34};
    ObjectType *objectTypeField = nullptr;
    int toBeRenamedField = 123;
    int readOnlyField = 123;

    Abstract(int id = -1);
    virtual ~Abstract();

    inline int id() const { return m_id; }

    // factory method
    inline static Abstract *createObject() { return nullptr; }

    // method that receives an Object Type
    inline static int getObjectId(Abstract *obj) { return obj->id(); }

    virtual void pureVirtual() = 0;
    virtual void *pureVirtualReturningVoidPtr() = 0;
    virtual void unpureVirtual();

    virtual PrintFormat returnAnEnum() = 0;
    void callVirtualGettingEnum(PrintFormat p);
    virtual void virtualGettingAEnum(PrintFormat p);

    void callPureVirtual();
    void callUnpureVirtual();

    void show(PrintFormat format = Verbose) const;
    virtual Type type() const { return TpAbstract; }

    virtual void hideFunction(HideType *arg) = 0;

protected:
    virtual const char *className() const { return "Abstract"; }

    // Protected bit-field structure member.
    unsigned int bitField: 1;

private:
    virtual void pureVirtualPrivate() = 0;
    int m_id;
};

#endif // ABSTRACT_H
