// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <numeric>
#include <cstdlib>
#include "listuser.h"

#include <algorithm>
#include <numeric>

std::list<int> ListUser::createIntList(int num)
{
    std::list<int> retval(num);
    std::iota(retval.begin(), retval.end(), 0);
    return retval;
}

int ListUser::sumIntList(std::list<int> intList)
{
    return std::accumulate(intList.begin(), intList.end(), 0);
}

std::list<MinBool> ListUser::createMinBoolList(MinBool mb1, MinBool mb2)
{
    std::list<MinBool> retval;
    retval.push_back(mb1);
    retval.push_back(mb2);
    return retval;
}

MinBool ListUser::oredMinBoolList(std::list<MinBool> minBoolList)
{
    MinBool result(false);
    for (const auto &m : minBoolList)
        result |= m;
    return result;
}

std::list<Val> ListUser::createValList(int num)
{
    std::list<Val> retval;
    for (int i = 0; i < num; ++i)
        retval.push_back(Val(i));
    return retval;
}

int ListUser::sumValList(std::list<Val> valList)
{
    int total = 0;
    for (const auto &v : valList)
        total += v.valId();
    return total;
}
std::list<Obj*> ListUser::createObjList(Obj* o1, Obj* o2)
{
    std::list<Obj*> retval;
    retval.push_back(o1);
    retval.push_back(o2);
    return retval;
}

int ListUser::sumObjList(std::list<Obj*> objList)
{
    int total = 0;
    for (const auto *obj : objList)
        total += obj->objId();
    return total;
}

std::list<std::list<int> > ListUser::createListOfIntLists(int num)
{
    std::list<std::list<int> > retval;
    for (int i = 0; i < num; ++i)
        retval.push_back(createIntList(num));
    return retval;
}

int ListUser::sumListOfIntLists(std::list<std::list<int> > intListList)
{
    int total = 0;
    for (const auto &list : intListList)
        total += std::accumulate(list.begin(), list.end(), 0);
    return total;
}

void ListUser::setStdIntList(const std::list<int> &l)
{
    m_stdIntList = l;
}

std::list<int> &ListUser::getIntList()
{
    return m_stdIntList;
}

const std::list<int> &ListUser::getConstIntList() const
{
    return m_stdIntList;
}

int ListUser::modifyIntListPtr(std::list<int> *list) const
{
    const int oldSize = int(list->size());
    list->push_back(42);
    return oldSize;
}

std::list<int> *ListUser::returnIntListByPtr() const
{
    return nullptr;
}

int ListUser::callReturnIntListByPtr() const
{
    auto *list = returnIntListByPtr();
    return list != nullptr ? int(list->size()) : 0;
}

int ListUser::modifyDoubleListPtr(std::list<double> *list) const
{
    const int oldSize = int(list->size());
    list->push_back(42);
    return oldSize;
}
