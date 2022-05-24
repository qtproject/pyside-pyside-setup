// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OBJ_H
#define OBJ_H

#include "libminimalmacros.h"

class LIBMINIMAL_API Obj
{
public:
    explicit Obj(int objId);
    virtual ~Obj();

    int objId() const { return m_objId; }
    void setObjId(int objId) { m_objId = objId; }

    virtual bool virtualMethod(int val);
    bool callVirtualMethod(int val) { return virtualMethod(val); }

    virtual Obj* passObjectType(Obj* obj) { return obj; }
    Obj* callPassObjectType(Obj* obj) { return passObjectType(obj); }

    virtual Obj* passObjectTypeReference(Obj& obj) { return &obj; }
    Obj* callPassObjectTypeReference(Obj& obj) { return passObjectTypeReference(obj); }

private:
    Obj(const Obj&);
    Obj& operator=(const Obj&);
    int m_objId;
};

#endif // OBJ_H

