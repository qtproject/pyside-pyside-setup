// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CONSTVALUELIST_H
#define CONSTVALUELIST_H

#include <list>
#include "libsamplemacros.h"

class CVValueType
{
    CVValueType();
};

typedef std::list<const CVValueType*> const_ptr_value_list;

// This tests binding generation for a container of a const value type. The
// class doesn't need to do anything; this is just to verify that the generated
// binding code (the container conversion in particular) is const-valid.

class CVListUser
{
public:
    static const_ptr_value_list produce() { return const_ptr_value_list(); }
    static void consume(const const_ptr_value_list &l) { (void)l; }
};

#endif // LIST_H
