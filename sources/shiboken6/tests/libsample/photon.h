// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PHOTON_H
#define PHOTON_H

#include "libsamplemacros.h"

#include <list>

// This namespace and classes simulate
// situations found in Qt's phonon module.

namespace Photon
{

enum ClassType {
    BaseType = 0,
    IdentityType = 1,
    DuplicatorType = 2
};

class LIBSAMPLE_API Base
{
public:
    LIBMINIMAL_DEFAULT_COPY_MOVE(Base)

    explicit Base(int value) noexcept : m_value(value) {}
    virtual ~Base() = default;

    inline void setValue(int value) { m_value = value; }
    inline int value() const { return m_value; }

    template <class T> bool isType() { return type() == T::staticType; }
    bool isType(ClassType t) { return type() == t; }

    virtual ClassType type() const { return BaseType; };
    static const ClassType staticType = BaseType;

protected:
    int m_value;
};

template<ClassType CLASS_TYPE>
class LIBSAMPLE_API TemplateBase : public Base
{
public:
    explicit TemplateBase(int value) : Base(value) {}
    inline int multiplicator() const { return int(CLASS_TYPE); }
    inline int calculate() const { return m_value * (int(CLASS_TYPE)); }
    static inline ClassType classType() { return CLASS_TYPE; }

    inline int sumValueUsingPointer(TemplateBase<CLASS_TYPE> *other) const
    { return m_value + other->m_value; }
    inline int sumValueUsingReference(TemplateBase<CLASS_TYPE> &other) const
    { return m_value + other.m_value; }

    inline std::list<TemplateBase<CLASS_TYPE> > getListOfThisTemplateBase()
    {
        std::list<TemplateBase<CLASS_TYPE> > objs;
        objs.push_back(*this);
        objs.push_back(*this);
        return objs;
    }

    static inline TemplateBase<CLASS_TYPE> *passPointerThrough(TemplateBase<CLASS_TYPE> *obj)
    { return obj; }

    ClassType type() const override { return CLASS_TYPE; }
    static const ClassType staticType = CLASS_TYPE;
};

#if defined _WIN32 || defined __CYGWIN__
template class LIBSAMPLE_API TemplateBase<IdentityType>;
template class LIBSAMPLE_API TemplateBase<DuplicatorType>;
#endif

using ValueIdentity = TemplateBase<IdentityType>;
using ValueDuplicator = TemplateBase<DuplicatorType>;

LIBSAMPLE_API int callCalculateForValueDuplicatorPointer(ValueDuplicator *value);
LIBSAMPLE_API int callCalculateForValueDuplicatorReference(ValueDuplicator &value);
LIBSAMPLE_API int countValueIdentities(const std::list<ValueIdentity> &values);
LIBSAMPLE_API int countValueDuplicators(const std::list<TemplateBase<DuplicatorType> > &values);

class Pointer
{
public:
    Pointer() noexcept = default;
    explicit Pointer(int *p) : px(p) {}

    void reset() noexcept { Pointer().swap(*this); }

    int *get() const noexcept { return px; }
    int &operator*() const { return *px; }

    void swap(Pointer &rhs) noexcept
    {
        int *tmp = px;
        px = rhs.px;
        rhs.px = tmp;
    }

private:
    int *px = nullptr;
};

} // namespace Photon

#endif // PHOTON_H
