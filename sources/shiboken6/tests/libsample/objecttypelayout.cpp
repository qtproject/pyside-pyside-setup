// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "objecttypelayout.h"

#include <iostream>

void ObjectTypeLayout::addObject(ObjectType *obj)
{
    if (obj->isLayoutType()) {
        auto *l = reinterpret_cast<ObjectTypeLayout*>(obj);
        if (l->parent()) {
            std::cerr << "[WARNING] ObjectTypeLayout::addObject: layout '"
                << l->objectName().cstring() << "' already has a parent.\n";
            return;
        }

        l->setParent(this);

        if (parent() && !parent()->isLayoutType())
            l->reparentChildren(parent());
    }

    m_objects.push_back(obj);
}

std::list<ObjectType*> ObjectTypeLayout::objects() const
{
    return m_objects;
}

void ObjectTypeLayout::reparentChildren(ObjectType *parent)
{
    for (auto *o : m_objects) {
        if (o->isLayoutType())
            reinterpret_cast<ObjectTypeLayout *>(o)->reparentChildren(parent);
        else
            o->setParent(parent);
    }
}
