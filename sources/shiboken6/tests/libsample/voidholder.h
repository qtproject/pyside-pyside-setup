// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef VOIDHOLDER_H
#define VOIDHOLDER_H

class VoidHolder
{
public:
    explicit VoidHolder(void *ptr = nullptr) : m_ptr(ptr) {}
    ~VoidHolder() = default;

    inline void *voidPointer() { return m_ptr; }
    inline static void *gimmeMeSomeVoidPointer()
    {
        static void *pointerToSomething = new VoidHolder();
        return pointerToSomething;
    }
    void *takeVoidPointer(void *item)
    {
        return item;
    }

private:
    void *m_ptr;
};

#endif // VOIDHOLDER_H
