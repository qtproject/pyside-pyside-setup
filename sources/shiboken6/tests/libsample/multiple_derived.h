// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef MDERIVED_H
#define MDERIVED_H

#include "libsamplemacros.h"

#include <string>

class Base1
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(Base1)

    Base1() noexcept = default;
    virtual ~Base1() = default;

    virtual int base1Method() { return m_value; }

    virtual void publicMethod() {};

private:
    int m_value = 1;
};

class Base2
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(Base2)

    Base2() noexcept = default;
    virtual ~Base2() = default;
    virtual int base2Method() { return m_value; }

private:
    int m_value = 2;
};

class LIBSAMPLE_API MDerived1 : public Base1, public Base2
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(MDerived1)

    MDerived1() noexcept;
    ~MDerived1() override = default;

    int mderived1Method() { return m_value; }
    int base1Method () override { return Base1::base1Method() * 10; }
    int base2Method() override { return Base2::base2Method() * 10; }

    inline Base1 *castToBase1() { return (Base1*) this; }
    inline Base2 *castToBase2() { return (Base2*) this; }

    static MDerived1 *transformFromBase1(Base1 *self);
    static MDerived1 *transformFromBase2(Base2 *self);

private:
    void publicMethod() override {}
    int m_value = 100;
};

class SonOfMDerived1 : public MDerived1
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(SonOfMDerived1)

    SonOfMDerived1() noexcept = default;
    ~SonOfMDerived1() = default;

    inline MDerived1 *castToMDerived1() { return this; }

    int sonOfMDerived1Method() { return m_value; }

private:
    int m_value = 0;
};

class Base3
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(Base3)

    explicit Base3(int val = 3) noexcept : m_value(val) {}
    virtual ~Base3() = default;
    int base3Method() { return m_value; }

private:
    int m_value;
};

class Base4
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(Base4)

    Base4() noexcept = default;
    virtual ~Base4() = default;
    int base4Method() { return m_value; }

private:
    int m_value = 4;
};

class Base5
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(Base5)

    Base5() noexcept = default;
    virtual ~Base5() = default;
    virtual int base5Method() { return m_value; }

private:
    int m_value = 5;
};

class Base6
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(Base6)

    Base6() noexcept = default;
    virtual ~Base6() = default;
    virtual int base6Method() { return m_value; }

private:
    int m_value = 6;
};

class LIBSAMPLE_API MDerived2 : public Base3, public Base4, public Base5, public Base6
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(MDerived2)

    MDerived2() noexcept;
    virtual ~MDerived2() = default;

    inline int base4Method() { return Base3::base3Method() * 10; }
    inline int mderived2Method() { return m_value; }

    inline Base3 *castToBase3() { return this; }
    inline Base4 *castToBase4() { return this; }
    inline Base5 *castToBase5() { return this; }
    inline Base6 *castToBase6() { return this; }

private:
    int m_value = 200;
};

class LIBSAMPLE_API MDerived3 : public MDerived1, public MDerived2
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(MDerived3)

    MDerived3() noexcept;
    virtual ~MDerived3() = default;

    inline virtual int mderived3Method() { return m_value; }

    inline MDerived1 *castToMDerived1() { return this; }
    inline MDerived2 *castToMDerived2() { return this; }

    inline Base3 *castToBase3() { return (Base3*) this; }

private:
    int m_value = 3000;
};

class LIBSAMPLE_API MDerived4 : public Base3, public Base4
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(MDerived4)

    MDerived4() noexcept;
    ~MDerived4() = default;

    inline int mderived4Method() { return 0; }
    inline int justDummyMethod() { return m_value; }

    inline Base3 *castToBase3() { return this; }
    inline Base4 *castToBase4() { return this; }

private:
    int m_value;
};

class LIBSAMPLE_API MDerived5 : public Base3, public Base4
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(MDerived5)

    MDerived5() noexcept;
    virtual ~MDerived5() = default;

    virtual int mderived5Method() { return 0; }

    inline Base3 *castToBase3() { return this; }
    inline Base4 *castToBase4() { return this; }
};

#endif // MDERIVED_H
