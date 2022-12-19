// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DERIVED_H
#define DERIVED_H

#include "libsamplemacros.h"
#include "abstract.h"

enum OverloadedFuncEnum {
    OverloadedFunc_ii,
    OverloadedFunc_d
};

class LIBSAMPLE_API Derived : public Abstract
{
public:
    enum OtherOverloadedFuncEnum {
        OtherOverloadedFunc_iibd,
        OtherOverloadedFunc_id
    };

    class SomeInnerClass {
    public:
        void uselessMethod() {}
        SomeInnerClass operator+(const SomeInnerClass &other) { return other; }
        bool operator==(const SomeInnerClass &) { return true; }
    };

    explicit Derived(int id = -1);
    ~Derived() override;
    void pureVirtual() override;
    void *pureVirtualReturningVoidPtr() override;
    void unpureVirtual() override;

    PrintFormat returnAnEnum()  override { return Short; }
    Type type() const override { return TpDerived; }

    // factory method
    static Abstract *createObject();

    // single argument
    bool singleArgument(bool b);

    // method with default value
    double defaultValue(int n = 0);

    // overloads
    OverloadedFuncEnum overloaded(int i = 0, int d = 0);
    OverloadedFuncEnum overloaded(double n);

    // more overloads
    OtherOverloadedFuncEnum otherOverloaded(int a, int b, bool c, double d);
    OtherOverloadedFuncEnum otherOverloaded(int a, double b);

    inline SomeInnerClass returnMyParameter(const SomeInnerClass &s) { return s; }

    static Abstract *triggerImpossibleTypeDiscovery();
    static Abstract *triggerAnotherImpossibleTypeDiscovery();

    void hideFunction(HideType*) override {}
protected:
    const char *getClassName() { return className(); }
    virtual const char *className() const override { return "Derived"; }

private:
    void pureVirtualPrivate() override;
};
#endif // DERIVED_H

