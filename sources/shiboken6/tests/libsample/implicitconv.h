// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef IMPLICITCONV_H
#define IMPLICITCONV_H

#include "libsamplemacros.h"
#include "null.h"

class ObjectType;

class LIBSAMPLE_API ImplicitConv
{
public:
    enum CtorEnum {
        CtorNone,
        CtorOne,
        CtorTwo,
        CtorThree,
        CtorObjectTypeReference,
        CtorPrimitiveType
    };

    enum ICOverloadedFuncEnum {
        OverFunc_Ii,
        OverFunc_Ib,
        OverFunc_i,
        OverFunc_C
    };

    ImplicitConv() = default;
    ImplicitConv(int objId) : m_ctorEnum(CtorOne), m_objId(objId) {}
    ImplicitConv(CtorEnum ctorEnum) : m_ctorEnum(ctorEnum) {}
    ImplicitConv(ObjectType&) : m_ctorEnum(CtorObjectTypeReference) {}
    ImplicitConv(double value, bool=true) : m_ctorEnum(CtorNone), m_value(value) {}
    ImplicitConv(const Null &null);
    ~ImplicitConv() = default;

    inline CtorEnum ctorEnum() const { return m_ctorEnum; }
    inline int objId() const { return m_objId; }
    inline double value() const { return m_value; }

    static ImplicitConv implicitConvCommon(ImplicitConv implicit);

    static ImplicitConv implicitConvDefault(ImplicitConv implicit = CtorTwo);

    static ICOverloadedFuncEnum implicitConvOverloading(ImplicitConv implicit, int dummyArg);
    static ICOverloadedFuncEnum implicitConvOverloading(ImplicitConv implicit, bool dummyArg);
    static ICOverloadedFuncEnum implicitConvOverloading(int dummyArg);
    static ICOverloadedFuncEnum implicitConvOverloading(CtorEnum dummyArg);

private:
    CtorEnum m_ctorEnum = CtorNone;
    int m_objId = -1;
    double m_value = -1.0;
};

#endif // IMPLICITCONV_H
