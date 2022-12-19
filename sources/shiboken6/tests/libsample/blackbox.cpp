// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "blackbox.h"

BlackBox::~BlackBox()
{
    // Free all maps.
    for (auto it = m_objects.begin(), end = m_objects.end(); it != end; ++it)
        delete it->second;
    for (auto it = m_points.begin(), end = m_points.end(); it != end; ++it)
        delete it->second;
}

int BlackBox::keepObjectType(ObjectType *object)
{
    ++m_ticket;
    m_objects.insert({m_ticket, object});
    object->setParent(nullptr);

    return m_ticket;
}

ObjectType *BlackBox::retrieveObjectType(int ticket)
{
    const auto it = m_objects.find(ticket);
    if (it != m_objects.end()) {
        ObjectType *second = it->second;
        m_objects.erase(it);
        return second;
    }
    return nullptr;
}

void BlackBox::disposeObjectType(int ticket)
{
    delete retrieveObjectType(ticket);
}

int BlackBox::keepPoint(Point *point)
{
    ++m_ticket;
    m_points.insert({m_ticket, point});
    return m_ticket;
}

Point *BlackBox::retrievePoint(int ticket)
{
    const auto it = m_points.find(ticket);
    if (it != m_points.end()) {
        Point *second = it->second;
        m_points.erase(it);
        return second;
    }
    return nullptr;
}

void BlackBox::disposePoint(int ticket)
{
    delete retrievePoint(ticket);
}

std::list<ObjectType*> BlackBox::objects()
{
    std::list<ObjectType*> l;

    for (auto it = m_objects.begin(), end = m_objects.end(); it != end; ++it)
        l.push_back((*it).second);

    return l;
}

std::list<Point*> BlackBox::points()
{
    std::list<Point*> l;

    for (auto it = m_points.begin(), end = m_points.end(); it != end; ++it)
        l.push_back((*it).second);

    return l;
}
