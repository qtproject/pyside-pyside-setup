// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "listuser.h"

#include <numeric>
#include <cstdlib>

std::list<int> ListUser::callCreateList()
{
    return createList();
}

ListUser::ListUser() = default;
ListUser::ListUser(const ListUser &other) = default;
ListUser::ListUser(ListUser &&other) = default;
ListUser &ListUser::operator=(const ListUser &other) = default;
ListUser &ListUser::operator=(ListUser &&other) = default;
ListUser::~ListUser() = default;

std::list<int> ListUser::createList()
{
    std::list<int> retval;
    for (int i = 0; i < 4; i++)
        retval.push_front(rand());
    return retval;
}

std::list<Complex> ListUser::createComplexList(Complex cpx0, Complex cpx1)
{
    std::list<Complex> retval;
    retval.push_back(cpx0);
    retval.push_back(cpx1);
    return retval;
}

double ListUser::sumList(std::list<int> vallist)
{
    return std::accumulate(vallist.begin(), vallist.end(), 0.0);
}

double ListUser::sumList(std::list<double> vallist)
{
    return std::accumulate(vallist.begin(), vallist.end(), 0.0);
}

ListUser::ListOfSomething ListUser::listOfPoints(const std::list<Point> &)
{
    return ListOfPoint;
}

ListUser::ListOfSomething ListUser::listOfPoints(const std::list<PointF> &)
{
    return ListOfPointF;
}

void ListUser::multiplyPointList(PointList &points, double multiplier)
{
    for (auto *point : points) {
        point->setX(point->x() * multiplier);
        point->setY(point->y() * multiplier);
    }
}
