// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SMART_OBJ_H
#define SMART_OBJ_H

#include "libsmartmacros.h"
#include "smart_sharedptr.h"

#include <vector>

class Integer;
class Obj;
namespace Smart { class Integer2; }

// Couldn't name it Object because it caused some namespace clashes.
class LIB_SMART_API Obj {
public:
    Obj();
    virtual ~Obj();

    void printObj();
    Integer takeInteger(Integer val);
    static SharedPtr<Obj> createSharedPtrObj();
    std::vector<SharedPtr<Obj> > createSharedPtrObjList(int size);
    virtual SharedPtr<Integer> createSharedPtrInteger(); // virtual for PYSIDE-1188
    SharedPtr<const Integer> createSharedPtrConstInteger();
    int takeSharedPtrToConstInteger(SharedPtr<const Integer> pInt);
    SharedPtr<Smart::Integer2> createSharedPtrInteger2();
    int takeSharedPtrToObj(SharedPtr<Obj> pObj);
    int takeSharedPtrToInteger(SharedPtr<Integer> pInt);
    int takeSharedPtrToIntegerByConstRef(const SharedPtr<Integer> &pInt);

    static SharedPtr<Integer> createSharedPtrInteger(int value);
    static SharedPtr<Integer> createNullSharedPtrInteger();

    int m_integer;  // public for testing member field access.
    Integer *m_internalInteger;
};

#endif // SMART_OBJ_H
