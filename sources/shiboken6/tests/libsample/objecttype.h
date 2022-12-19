// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OBJECTTYPE_H
#define OBJECTTYPE_H

#include "str.h"
#include "null.h"

#include "libsamplemacros.h"

#include <list>

struct Event
{
    enum EventType {
        NO_EVENT,
        BASIC_EVENT,
        SOME_EVENT,
        ANY_EVENT
    };

    enum class EventTypeClass {
        Value1,
        Value2
    };

    explicit Event(EventType eventType) : m_eventType(eventType) {}
    EventType eventType() const { return m_eventType; }

    void setEventType(EventType et) { m_eventType = et; }
    void setEventTypeByConstRef(const EventType &et) { m_eventType = et; }
    void setEventTypeByConstPtr(const EventType *etPtr) { m_eventType = *etPtr; }

private:
    EventType m_eventType;
};

class ObjectTypeLayout;
class ObjectType;
using ObjectTypeList = std::list<ObjectType*>;

class LIBSAMPLE_API ObjectType
{
public:
    // ### Fixme: Use uintptr_t in C++ 11
    using Identifier = size_t;

    explicit ObjectType(ObjectType *parent = nullptr);
    virtual ~ObjectType();
    ObjectType(const ObjectType &) = delete;
    ObjectType &operator=(const ObjectType &) = delete;

    // factory method
    inline static ObjectType *create() { return new ObjectType(); }
    static ObjectType *createWithChild();

    static const ObjectType *defaultInstance();

    void setParent(ObjectType *parent);
    inline ObjectType *parent() const { return m_parent; }
    inline const ObjectTypeList &children() const { return m_children; }
    void killChild(const Str &name);
    void removeChild(ObjectType *child);
    ObjectType *takeChild(ObjectType *child);
    virtual ObjectType *takeChild(const Str &name);
    ObjectType *findChild(const Str &name);

    Str objectName() const;
    void setObjectName(const Str &name);

    inline Identifier identifier() const { return reinterpret_cast<Identifier>(this); }

    bool causeEvent(Event::EventType eventType);

    // Returns true if the event is processed.
    virtual bool event(Event *event);
    static int processEvent(ObjectTypeList objects, Event *event);

    void callInvalidateEvent(Event *event);
    virtual void invalidateEvent(Event *event);

    // This nonsense method emulate QWidget.setLayout method
    // All layout objects will became children of this object.
    void setLayout(ObjectTypeLayout *layout);
    inline ObjectTypeLayout *layout() const { return m_layout; }

    // This method should be reimplemented by ObjectTypeLayout.
    virtual bool isLayoutType() { return false; }

    unsigned char callWithEnum(const Str &prefix, Event::EventType type,
                               unsigned char value=80);
    unsigned char callWithEnum(const Str &prefix, unsigned char value=0);

    //Functions used in test with named arguments
    void setObjectSplittedName(const char *, const Str &prefix = Str("<unk"),
                               const Str &suffix = Str("nown>"));
    void setObjectNameWithSize(const char *, int size=9,
                               const Str &name = Str("<unknown>"));
    void setObjectNameWithSize(const Str &name = Str("<unknown>"), int size = 9);

    //Function used to confuse the generator when two values accept Null as arg
    void setObject(ObjectType *);
    void setObject(const Null &);
    int callId() const;

    //Function used to create a parent from C++
    virtual bool isPython() { return false; }
    void callVirtualCreateChild();
    virtual ObjectType *createChild(ObjectType *parent);
    static std::size_t createObjectType();

    //return a parent from C++
    ObjectType *getCppParent() {
        if (!m_parent) {
            ObjectType *parent = new ObjectType();
            setParent(parent);
        }
        return m_parent;
    }

    void destroyCppParent() {
        delete m_parent;
    }

    //Deprecated test
    bool deprecatedFunction() { return true; }

    // nextInFocusChain simply returns the parent to test object cycles; the parent
    // may be returned by the QWidget's implementation but isn't always returned
    ObjectType *nextInFocusChain() { return m_parent; }

private:
    ObjectTypeLayout *takeLayout();
    ObjectTypeList::iterator findChildByName(const Str &name);

    Str m_objectName;
    ObjectType *m_parent = nullptr;
    ObjectTypeList m_children;

    ObjectTypeLayout *m_layout = nullptr;
    //used on overload null test
    int m_call_id = -1;
};

LIBSAMPLE_API unsigned int objectTypeHash(const ObjectType *objectType);

class LIBSAMPLE_API OtherBase {
public:
    OtherBase() = default;
    virtual ~OtherBase();
};

class LIBSAMPLE_API ObjectTypeDerived: public ObjectType, public OtherBase {
public:
    ObjectTypeDerived() = default;

    bool event(Event *event) override;
    ~ObjectTypeDerived() override;
};

#endif // OBJECTTYPE_H
