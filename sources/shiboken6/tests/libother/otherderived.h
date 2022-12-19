// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OTHERDERIVED_H
#define OTHERDERIVED_H

#include "libothermacros.h"
#include "abstract.h"
#include "derived.h"
#include "objecttype.h"
#include "complex.h"

class ObjectType;

class LIBOTHER_API OtherDerived : public Abstract
{
public:
    OtherDerived(int id = -1);
    ~OtherDerived() override;
    void pureVirtual() override;
    void *pureVirtualReturningVoidPtr() override;
    void unpureVirtual() override;
    PrintFormat returnAnEnum()  override { return Short; }

    inline void useObjectTypeFromOtherModule(ObjectType *) {}
    inline Event useValueTypeFromOtherModule(const Event &e) { return e; }
    inline Complex useValueTypeFromOtherModule(const Complex &c) { return c; }
    inline void useEnumTypeFromOtherModule(OverloadedFuncEnum) {}

    // factory method
    static Abstract *createObject();

    void hideFunction(HideType*) override {}

protected:
    inline const char *getClassName() { return className(); }
    virtual const char *className() const override { return "OtherDerived"; }

private:
    void pureVirtualPrivate() override;
};

#endif // OTHERDERIVED_H
