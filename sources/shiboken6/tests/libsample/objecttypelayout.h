// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OBJECTTYPELAYOUT_H
#define OBJECTTYPELAYOUT_H

#include "libsamplemacros.h"
#include "objecttype.h"

#include <list>

class ObjectType;

class LIBSAMPLE_API ObjectTypeLayout : public ObjectType
{
public:
    void addObject(ObjectType *obj);
    std::list<ObjectType*> objects() const;

    bool isLayoutType() override { return true; }
    inline static ObjectTypeLayout *create() { return new ObjectTypeLayout(); }

    ObjectType *takeChild(const Str &name) override { return ObjectType::takeChild(name); }

private:
    std::list<ObjectType*> m_objects;

    void reparentChildren(ObjectType *parent);
    friend LIBSAMPLE_API void ObjectType::setLayout(ObjectTypeLayout *l);
};

#endif // OBJECTTYPELAYOUT_H
