// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef LISTUSER_H
#define LISTUSER_H

#include "obj.h"
#include "val.h"
#include "minbool.h"

#include "libminimalmacros.h"

#include <list>

struct LIBMINIMAL_API ListUser
{
    virtual ~ListUser() {}

    // List of C++ primitive type items
    virtual std::list<int> createIntList(int num);
    std::list<int> callCreateIntList(int num) { return createIntList(num); }
    virtual int sumIntList(std::list<int> intList);
    int callSumIntList(std::list<int> intList) { return sumIntList(intList); }

    // List of C++ MinBool objects used as primitives in Python
    virtual std::list<MinBool> createMinBoolList(MinBool mb1, MinBool mb2);
    std::list<MinBool> callCreateMinBoolList(MinBool mb1, MinBool mb2) { return createMinBoolList(mb1, mb2); }
    virtual MinBool oredMinBoolList(std::list<MinBool> minBoolList);
    MinBool callOredMinBoolList(std::list<MinBool> minBoolList) { return oredMinBoolList(minBoolList); }

    // List of C++ value types
    virtual std::list<Val> createValList(int num);
    std::list<Val> callCreateValList(int num) { return createValList(num); }
    virtual int sumValList(std::list<Val> valList);
    int callSumValList(std::list<Val> valList) { return sumValList(valList); }

    // List of C++ object types
    virtual std::list<Obj*> createObjList(Obj* o1, Obj* o2);
    std::list<Obj*> callCreateObjList(Obj* o1, Obj* o2) { return createObjList(o1, o2); }
    virtual int sumObjList(std::list<Obj*> objList);
    int callSumObjList(std::list<Obj*> objList) { return sumObjList(objList); }

    // List of lists of C++ primitive type items
    virtual std::list<std::list<int> > createListOfIntLists(int num);
    std::list<std::list<int> > callCreateListOfIntLists(int num) { return createListOfIntLists(num); }
    virtual int sumListOfIntLists(std::list<std::list<int> > intListList);
    int callSumListOfIntLists(std::list<std::list<int> > intListList) { return sumListOfIntLists(intListList); }

    void setStdIntList(const std::list<int> &l);
    std::list<int> &getIntList();
    const std::list<int> &getConstIntList() const;

    int modifyIntListPtr(std::list<int> *list) const;

    virtual std::list<int> *returnIntListByPtr() const;

    int callReturnIntListByPtr() const;

    int modifyDoubleListPtr(std::list<double> *list) const;

    std::list<int> m_stdIntList;
};

#endif // LISTUSER_H

