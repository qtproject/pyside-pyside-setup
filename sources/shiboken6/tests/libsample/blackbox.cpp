// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "blackbox.h"

BlackBox::~BlackBox()
{
    // Free all maps.
    for (const auto &p :m_objects)
        delete p.second;
    for (const auto &p : m_points)
        delete p.second;
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

    for (const auto &p : m_objects)
        l.push_back(p.second);

    return l;
}

std::list<Point*> BlackBox::points()
{
    std::list<Point*> l;

    for (const auto &p : m_points)
        l.push_back(p.second);

    return l;
}
