/****************************************************************************
**
** Copyright (C) 2017 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the test suite of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "smart.h"

#include <algorithm>
#include <iostream>

static inline bool verbose()
{
    return Registry::getInstance()->verbose();
}

void SharedPtrBase::logDefaultConstructor(const char *instantiation, const void *t)
{
    if (verbose())
        std::cout << "SharedPtr<" << instantiation << "> default constructor " << t << '\n';
}

void SharedPtrBase::logConstructor(const char *instantiation, const void *t,
                                   const void *pointee)
{
    if (verbose()) {
        std::cout << "SharedPtr<" << instantiation << "> constructor "
            << t << " with pointer " << pointee << '\n';
    }
}

void SharedPtrBase::logCopyConstructor(const char *instantiation, const void *t,
                                       const void *refData)
{
    if (verbose()) {
        std::cout << "SharedPtr<" << instantiation << ">) copy constructor "
            << t << " with pointer " << refData << '\n';
    }
}

void SharedPtrBase::logAssignment(const char *instantiation, const void *t, const void *refData)
{
    if (verbose()) {
        std::cout << "SharedPtr<" << instantiation << ">::operator= " << t
            << " with pointer " << refData << "\n";
    }
}

void SharedPtrBase::logDestructor(const char *instantiation, const void *t,
                                  int remainingRefCount)
{
    if (verbose()) {
        std::cout << "~SharedPtr<" << instantiation << "> " << t << ", remaining refcount "
            << remainingRefCount << '\n';
    }
}

Obj::Obj() : m_integer(123), m_internalInteger(new Integer)
{
    Registry::getInstance()->add(this);
    if (verbose())
        std::cout << "Obj constructor " << this << '\n';
}

Obj::~Obj()
{
    Registry::getInstance()->remove(this);
    delete m_internalInteger;
    if (verbose())
        std::cout << "~Obj " << this << '\n';
}


void Obj::printObj() {
    if (verbose()) {
        std::cout << "Obj::printObj(): integer value: " << m_integer
                  << " internal integer value: " << m_internalInteger->value() << '\n';
    }
}


SharedPtr<Obj> Obj::createSharedPtrObj()
{
    SharedPtr<Obj> o(new Obj);
    return o;
}

std::vector<SharedPtr<Obj> > Obj::createSharedPtrObjList(int size)
{
    std::vector<SharedPtr<Obj> > r;
    for (int i=0; i < size; i++)
        r.push_back(createSharedPtrObj());
    return r;
}


SharedPtr<Integer> Obj::createSharedPtrInteger()
{
    SharedPtr<Integer> o(new Integer);
    return o;
}

SharedPtr<Smart::Integer2> Obj::createSharedPtrInteger2()
{
    SharedPtr<Smart::Integer2> o(new Smart::Integer2);
    return o;
}

int Obj::takeSharedPtrToObj(SharedPtr<Obj> pObj)
{
    pObj->printObj();
    return pObj->m_integer;
}

int Obj::takeSharedPtrToInteger(SharedPtr<Integer> pInt)
{
    if (pInt.isNull()) {
        std::cout << "SharedPtr<Integer>(nullptr) passed!\n";
        return -1;
    }
    pInt->printInteger();
    return pInt->value();
}

int Obj::takeSharedPtrToIntegerByConstRef(const SharedPtr<Integer> &pInt)
{
    if (pInt.isNull()) {
        std::cout << "SharedPtr<Integer>(nullptr) passed!\n";
        return -1;
    }
    pInt->printInteger();
    return pInt->value();
}

SharedPtr<Integer> Obj::createSharedPtrInteger(int value)
{
    auto *i = new Integer;
    i->setValue(value);
    return SharedPtr<Integer>(i);
}

SharedPtr<Integer> Obj::createNullSharedPtrInteger()
{
    return {};
}

SharedPtr<const Integer> Obj::createSharedPtrConstInteger()
{
    SharedPtr<const Integer> co(new Integer);
    return co;
}

int Obj::takeSharedPtrToConstInteger(SharedPtr<const Integer> pInt)
{
    return pInt->m_int;
}

Integer Obj::takeInteger(Integer val)
{
    return val;
}

Integer::Integer() : m_int(456)
{
    Registry::getInstance()->add(this);
    if (verbose())
        std::cout << "Integer constructor " << this << '\n';
}

Integer::Integer(const Integer &other)
{
    Registry::getInstance()->add(this);
    if (verbose())
        std::cout << "Integer copy constructor " << this << '\n';
    m_int = other.m_int;
}

Integer &Integer::operator=(const Integer &other)
{
    Registry::getInstance()->add(this);
    if (verbose())
        std::cout << "Integer operator= " << this << '\n';
    m_int = other.m_int;
    return *this;
}

Integer::~Integer()
{
    Registry::getInstance()->remove(this);
    if (verbose())
        std::cout << "~Integer " << this << " (" << m_int << ")\n";
}

int Integer::value() const
{
    return m_int;
}

void Integer::setValue(int v)
{
    m_int = v;
    if (verbose())
        std::cout << "Integer::setValue(" << v << ") " << this << '\n';
}

int Integer::compare(const Integer &rhs) const
{
    if (m_int < rhs.m_int)
        return -1;
    return m_int > rhs.m_int ? 1 : 0;
}

void Integer::printInteger() const
{
    if (verbose())
        std::cout << "Integer value for object " << this << " is " << m_int << '\n';
}

Registry *Registry::getInstance()
{
    static Registry registry;
    return &registry;
}

Registry::Registry() = default;

Registry::~Registry() = default;

void Registry::add(Obj *p)
{
    m_objects.push_back(p);
}

void Registry::add(Integer *p)
{
    m_integers.push_back(p);
}

void Registry::remove(Obj *p)
{
    m_objects.erase(std::remove(m_objects.begin(), m_objects.end(), p), m_objects.end());
}

void Registry::remove(Integer *p)
{
    m_integers.erase(std::remove(m_integers.begin(), m_integers.end(), p), m_integers.end());
}

int Registry::countObjects() const
{
    return static_cast<int>(m_objects.size());
}

int Registry::countIntegers() const
{
    return static_cast<int>(m_integers.size());
}

bool Registry::verbose() const
{
    return m_verbose;
}

void Registry::setVerbose(bool flag)
{
    m_verbose = flag;
}

Smart::Integer2::Integer2()
    : Integer ()
{
}

Smart::Integer2::Integer2(const Smart::Integer2 &other)
    : Integer (other)
{
}
