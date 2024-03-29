// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef LIST_H
#define LIST_H

#include <list>
#include "libsamplemacros.h"
#include "point.h"

class ObjectType;

template<class T>
class List : public std::list<T>
{
};

class IntList : public List<int>
{
public:
    LIBMINIMAL_DEFAULT_MOVE(IntList)

    enum CtorEnum {
        NoParamsCtor,
        IntCtor,
        CopyCtor,
        ListOfIntCtor
    };

    inline IntList() noexcept : m_ctorUsed(NoParamsCtor) {}
    inline explicit IntList(int val) : m_ctorUsed(IntCtor) { push_back(val); }
    inline IntList(const List<int> &lst) : List<int>(lst), m_ctorUsed(ListOfIntCtor) {}
    ~IntList() = default;

    inline IntList(const IntList &lst) : List<int>(lst), m_ctorUsed(CopyCtor) {}
    IntList &operator=(const IntList &) = default;

    inline void append(int v) { insert(end(), v); }
    CtorEnum constructorUsed() { return m_ctorUsed; }
private:
    CtorEnum m_ctorUsed;
};

class PointValueList : public List<Point>
{
public:
    LIBMINIMAL_DEFAULT_MOVE(PointValueList)

    enum CtorEnum {
        NoParamsCtor,
        PointCtor,
        CopyCtor,
        ListOfPointValuesCtor
    };

    inline PointValueList() noexcept : m_ctorUsed(NoParamsCtor) {}
    inline explicit PointValueList(Point val) : m_ctorUsed(PointCtor) { push_back(val); }
    inline PointValueList(const List<Point> &lst) : List<Point>(lst), m_ctorUsed(ListOfPointValuesCtor) {}

    inline PointValueList(const PointValueList &lst) : List<Point>(lst), m_ctorUsed(CopyCtor) {}
    PointValueList &operator=(const PointValueList &) = default;
    ~PointValueList() = default;

    inline void append(Point v) { insert(end(), v); }
    CtorEnum constructorUsed() { return m_ctorUsed; }
private:
    CtorEnum m_ctorUsed;
};

class ObjectTypePtrList : public List<ObjectType*>
{
public:
    LIBMINIMAL_DEFAULT_MOVE(ObjectTypePtrList)

    enum CtorEnum {
        NoParamsCtor,
        ObjectTypeCtor,
        CopyCtor,
        ListOfObjectTypePtrCtor
    };

    inline ObjectTypePtrList() = default;
    inline ObjectTypePtrList(const ObjectTypePtrList &lst) :
        List<ObjectType*>(lst), m_ctorUsed(CopyCtor) {}
    inline explicit ObjectTypePtrList(ObjectType *val) :
        m_ctorUsed(ObjectTypeCtor) { push_back(val); }
    inline ObjectTypePtrList(const List<ObjectType*> &lst) :
        List<ObjectType*>(lst), m_ctorUsed(ListOfObjectTypePtrCtor) {}
    ~ObjectTypePtrList() = default;

    ObjectTypePtrList &operator=(const ObjectTypePtrList &) = default;

    inline void append(ObjectType *v) { insert(end(), v); }
    CtorEnum constructorUsed() { return m_ctorUsed; }
private:
    CtorEnum m_ctorUsed = NoParamsCtor;
};

#endif // LIST_H
