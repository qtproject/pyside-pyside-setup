// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "blackbox.h"

using namespace std;

BlackBox::~BlackBox()
{
    // Free all maps.
    while (!m_objects.empty()) {
        delete (*m_objects.begin()).second;
        m_objects.erase(m_objects.begin());
    }
    while (!m_points.empty()) {
        delete (*m_points.begin()).second;
        m_points.erase(m_points.begin());
    }
}

int
BlackBox::keepObjectType(ObjectType* object)
{
    m_ticket++;
    std::pair<int, ObjectType*> item(m_ticket, object);
    m_objects.insert(item);
    object->setParent(nullptr);

    return m_ticket;
}

ObjectType*
BlackBox::retrieveObjectType(int ticket)
{
    const auto it = m_objects.find(ticket);
    if (it != m_objects.end()) {
        ObjectType* second = it->second;
        m_objects.erase(it);
        return second;
    }
    return nullptr;
}

void
BlackBox::disposeObjectType(int ticket)
{
    ObjectType* object = retrieveObjectType(ticket);
    if (object)
        delete object;
}

int
BlackBox::keepPoint(Point* point)
{
    m_ticket++;
    std::pair<int, Point*> item(m_ticket, point);
    m_points.insert(item);

    return m_ticket;
}

Point*
BlackBox::retrievePoint(int ticket)
{
    const auto it = m_points.find(ticket);
    if (it != m_points.end()) {
        Point* second = it->second;
        m_points.erase(it);
        return second;
    }
    return nullptr;
}

void
BlackBox::disposePoint(int ticket)
{
    Point* point = retrievePoint(ticket);
    if (point)
        delete point;
}


std::list<ObjectType*>
BlackBox::objects()
{
    std::list<ObjectType*> l;

    for (auto it = m_objects.begin(), end = m_objects.end(); it != end; ++it)
        l.push_back((*it).second);

    return l;
}

std::list<Point*>
BlackBox::points()
{
    std::list<Point*> l;

    for (auto it = m_points.begin(), end = m_points.end(); it != end; ++it)
        l.push_back((*it).second);

    return l;
}

