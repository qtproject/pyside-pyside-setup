// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "objecttype.h"
#include "objecttypelayout.h"

#include <algorithm>
#include <iostream>
#include <string>
#include <assert.h>

ObjectType::ObjectType(ObjectType *parent)
{
    setParent(parent);
}

ObjectType::~ObjectType()
{
    for (auto *o : m_children)
        delete o;
}

ObjectType *ObjectType::createWithChild()
{
    ObjectType *parent = create();
    ObjectType *child = create();
    child->setObjectName("child");
    child->setParent(parent);
    return parent;
}

const ObjectType *ObjectType::defaultInstance()
{
    static ObjectType result;
    return &result;
}

void ObjectType::removeChild(ObjectType *child)
{
    if (!child)
        return;

    auto child_iter = std::find(m_children.begin(), m_children.end(), child);
    if (child_iter != m_children.end()) {
        m_children.erase(child_iter);
        child->m_parent = nullptr;
    }
}

ObjectType *ObjectType::takeChild(ObjectType *child)
{
    if (!child)
        return nullptr;

    auto child_iter = std::find(m_children.begin(), m_children.end(), child);
    if (child_iter != m_children.end()) {
        m_children.erase(child_iter);
        child->m_parent = nullptr;
        return child;
    }
    return nullptr;
}

ObjectType *ObjectType::takeChild(const Str &name)
{
    return takeChild(findChild(name));

}

ObjectTypeList::iterator ObjectType::findChildByName(const Str &name)
{
    return std::find_if(m_children.begin(), m_children.end(),
                        [&name](const ObjectType *o) {
                            return o->objectName() == name;
                        });
}

ObjectType *ObjectType::findChild(const Str &name)
{
    auto it = findChildByName(name);
    return it != m_children.end() ? *it : nullptr;
}

void ObjectType::killChild(const Str &name)
{
    auto it = findChildByName(name);
    if (it != m_children.end()) {
        ObjectType *child = *it;
        removeChild(child);
        delete child;
    }
}

void ObjectType::setParent(ObjectType *parent)
{
    if (m_parent == parent)
        return;

    if (m_parent)
        m_parent->removeChild(this);

    m_parent = parent;
    if (m_parent)
        m_parent->m_children.push_back(this);
}

void ObjectType::setObjectName(const Str &name)
{
    m_objectName = name;
}

Str ObjectType::objectName() const
{
    return m_objectName;
}

bool ObjectType::causeEvent(Event::EventType eventType)
{
    Event e(eventType);
    return event(&e);
}

bool ObjectType::event(Event *)
{
    return true;
}

int ObjectType::processEvent(ObjectTypeList objects, Event *event)
{
    return std::count_if(objects.begin(), objects.end(),
                         [event] (ObjectType *o) {
                             return o->event(event);
                         });
}

void ObjectType::callInvalidateEvent(Event *event)
{
    invalidateEvent(event);
}

void ObjectType::invalidateEvent(Event *)
{
}

void ObjectType::setLayout(ObjectTypeLayout *l)
{
    if (!l) {
        std::cerr << "[WARNING] ObjectType::setLayout: Cannot set layout to 0.\n";
        return;
    }

    if (layout()) {
        if (layout() != l) {
            std::cerr << "[WARNING] ObjectType::setLayout: Attempting to set ObjectTypeLayout '"
                << l->objectName().cstring()
                << "' on ObjectType '" << objectName().cstring()
                << "', which already has a layout.\n";
        }
        return;
    }

    ObjectType *oldParent = l->parent();
    if (oldParent && oldParent != this) {
        if (oldParent->isLayoutType()) {
            std::cerr << "[WARNING] ObjectType::setLayout: Attempting to set ObjectTypeLayout '"
                << l->objectName().cstring()
                << "' on ObjectType '" << objectName().cstring()
                << "', when the ObjectTypeLayout already has a parent layout.\n";
            return;
        } else {
            // Steal the layout from an ObjectType parent.
            oldParent->takeLayout();
        }
    }

    m_layout = l;
    if (oldParent != this) {
        l->setParent(this);
        l->reparentChildren(this);
    }
}

ObjectTypeLayout *ObjectType::takeLayout()
{
    ObjectTypeLayout *l = layout();
    if (!l)
        return nullptr;
    m_layout = nullptr;
    l->setParent(nullptr);
    return l;
}

unsigned int objectTypeHash(const ObjectType *objectType)
{
    return reinterpret_cast<std::size_t>(objectType);
}

unsigned char ObjectType::callWithEnum(const Str &, Event::EventType, unsigned char value)
{
    return value * value;
}

unsigned char ObjectType::callWithEnum(const Str &, unsigned char value)
{
    return value;
}

void ObjectType::setObjectSplittedName(const char *, const Str &prefix, const Str &suffix)
{
    std::string result(prefix.cstring());
    result += suffix.cstring();
    m_objectName = result.c_str();
}

void ObjectType::setObjectNameWithSize(const char *, int size, const Str &name)
{
    std::string result(name.cstring(), size);
    m_objectName = result.c_str();
}

void ObjectType::setObjectNameWithSize(const Str &name, int size)
{
    setObjectNameWithSize("", size, name);
}

void ObjectType::setObject(ObjectType *)
{
    m_call_id = 0;
}

void ObjectType::setObject(const Null&)
{
    m_call_id = 1;
}

int ObjectType::callId() const
{
    return m_call_id;
}

void ObjectType::callVirtualCreateChild()
{
    ObjectType *fake_parent = new ObjectType();
    ObjectType *fake_child = createChild(fake_parent);
    assert(fake_child->isPython());
    (void)fake_child;
    delete fake_parent;
}

ObjectType *ObjectType::createChild(ObjectType *parent)
{
    return new ObjectType(parent);
}

std::size_t ObjectType::createObjectType()
{
    void *addr = new ObjectType();
    return (std::size_t) addr;
}

OtherBase::~OtherBase() = default;

ObjectTypeDerived::~ObjectTypeDerived() = default;

bool ObjectTypeDerived::event(Event *)
{
    return true;
}
