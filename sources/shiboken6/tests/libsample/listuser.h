// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef LISTUSER_H
#define LISTUSER_H

#include "complex.h"
#include "point.h"
#include "pointf.h"

#include "libsamplemacros.h"

#include <list>

class LIBSAMPLE_API ListUser
{
public:
    using PointList = std::list<Point *>;

    enum ListOfSomething {
        ListOfPoint,
        ListOfPointF
    };

    ListUser();
    ListUser(const ListUser &other);
    ListUser(ListUser &&other);
    ListUser &operator=(const ListUser &other);
    ListUser &operator=(ListUser &&other);
    virtual ~ListUser();

    virtual std::list<int> createList();
    std::list<int> callCreateList();

    static std::list<Complex> createComplexList(Complex cpx0, Complex cpx1);

    double sumList(std::list<int> vallist);
    double sumList(std::list<double> vallist);

    static ListOfSomething listOfPoints(const std::list<Point> &pointlist);
    static ListOfSomething listOfPoints(const std::list<PointF> &pointlist);

    static void multiplyPointList(PointList &points, double multiplier);

    inline void setList(std::list<int> lst) { m_lst = lst; }
    inline std::list<int> getList() const { return m_lst; }

private:
    std::list<int> m_lst;
};

#endif // LISTUSER_H

