/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the test suite of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include <numeric>
#include <cstdlib>
#include "listuser.h"

#include <algorithm>
#include <numeric>

std::list<int>
ListUser::createIntList(int num)
{
    std::list<int> retval(num);
    std::iota(retval.begin(), retval.end(), 0);
    return retval;
}

int
ListUser::sumIntList(std::list<int> intList)
{
    return std::accumulate(intList.begin(), intList.end(), 0);
}

std::list<MinBool>
ListUser::createMinBoolList(MinBool mb1, MinBool mb2)
{
    std::list<MinBool> retval;
    retval.push_back(mb1);
    retval.push_back(mb2);
    return retval;
}

MinBool
ListUser::oredMinBoolList(std::list<MinBool> minBoolList)
{
    MinBool result(false);
    for (const auto &m : minBoolList)
        result |= m;
    return result;
}

std::list<Val>
ListUser::createValList(int num)
{
    std::list<Val> retval;
    for (int i = 0; i < num; ++i)
        retval.push_back(Val(i));
    return retval;
}

int
ListUser::sumValList(std::list<Val> valList)
{
    int total = 0;
    for (const auto &v : valList)
        total += v.valId();
    return total;
}

std::list<Obj*>
ListUser::createObjList(Obj* o1, Obj* o2)
{
    std::list<Obj*> retval;
    retval.push_back(o1);
    retval.push_back(o2);
    return retval;
}

int
ListUser::sumObjList(std::list<Obj*> objList)
{
    int total = 0;
    for (const auto *obj : objList)
        total += obj->objId();
    return total;
}

std::list<std::list<int> >
ListUser::createListOfIntLists(int num)
{
    std::list<std::list<int> > retval;
    for (int i = 0; i < num; ++i)
        retval.push_back(createIntList(num));
    return retval;
}

int
ListUser::sumListOfIntLists(std::list<std::list<int> > intListList)
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
