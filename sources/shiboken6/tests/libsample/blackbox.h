// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef BLACKBOX_H
#define BLACKBOX_H

#include "libsamplemacros.h"
#include "objecttype.h"
#include "point.h"

#include <list>
#include <map>

class LIBSAMPLE_API BlackBox
{
public:
    using ObjectTypeMap = std::map<int, ObjectType*>;
    using PointMap = std::map<int, Point*>;

    BlackBox() = default;
    ~BlackBox();

    int keepObjectType(ObjectType *object);
    ObjectType *retrieveObjectType(int ticket);
    void disposeObjectType(int ticket);

    int keepPoint(Point *point);
    Point *retrievePoint(int ticket);
    void disposePoint(int ticket);

    std::list<ObjectType*> objects();
    std::list<Point*> points();

    inline void referenceToValuePointer(Point*&) {}
    inline void referenceToObjectPointer(ObjectType*&) {}

private:
    ObjectTypeMap m_objects;
    PointMap m_points;
    int m_ticket = -1;
};

#endif // BLACKBOX_H
