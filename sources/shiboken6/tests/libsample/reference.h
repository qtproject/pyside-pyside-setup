// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef REFERENCE_H
#define REFERENCE_H

#include "libsamplemacros.h"

class LIBSAMPLE_API Reference
{
public:
    explicit Reference(int objId = -1)
            : m_objId(objId) {}
    virtual ~Reference() = default;

    inline int objId() const { return m_objId; }
    inline void setObjId(int objId) { m_objId = objId; }

    inline static int usesReference(Reference &r) { return r.m_objId; }
    inline static int usesConstReference(const Reference &r) { return r.m_objId; }

    virtual int usesReferenceVirtual(Reference &r, int inc);
    virtual int usesConstReferenceVirtual(const Reference &r, int inc);

    int callUsesReferenceVirtual(Reference &r, int inc);
    int callUsesConstReferenceVirtual(const Reference &r, int inc);

    virtual void alterReferenceIdVirtual(Reference &r);
    void callAlterReferenceIdVirtual(Reference &r);

    void show() const;

    inline static int multiplier() { return 10; }

    virtual Reference &returnMyFirstArg(Reference &ref) { return ref; }
    virtual Reference &returnMySecondArg(int a, Reference &ref);

    // nonsense operator to test if Shiboken is ignoring dereference operators.
    int operator*() { return m_objId; }

private:
    int m_objId;
};

class LIBSAMPLE_API ObjTypeReference
{
public:
    ObjTypeReference() = default;
    ObjTypeReference(const ObjTypeReference &) {}
    virtual ~ObjTypeReference();

    virtual ObjTypeReference &returnMyFirstArg(ObjTypeReference &ref) { return ref; }
    virtual ObjTypeReference &returnMySecondArg(int a, ObjTypeReference &ref);
    virtual ObjTypeReference &justAPureVirtualFunc(ObjTypeReference &ref) = 0;
};

#endif // REFERENCE_H
