// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef STRLIST_H
#define STRLIST_H

#include <list>
#include "str.h"

#include "libsamplemacros.h"

class LIBSAMPLE_API StrList : public std::list<Str>
{
public:
    enum CtorEnum {
        NoParamsCtor,
        StrCtor,
        CopyCtor,
        ListOfStrCtor
    };

    inline StrList() : m_ctorUsed(NoParamsCtor) {}
    inline explicit StrList(const Str& str) : m_ctorUsed(StrCtor) { push_back(str); }
    inline StrList(const StrList& lst) : std::list<Str>(lst), m_ctorUsed(CopyCtor) {}
    inline StrList(const std::list<Str>& lst) : std::list<Str>(lst), m_ctorUsed(ListOfStrCtor) {}

    inline void append(Str str) { push_back(str); }
    Str join(const Str& sep) const;

    bool operator==(const std::list<Str>& other) const;
    inline bool operator!=(const std::list<Str>& other) const { return !(*this == other); }

    CtorEnum constructorUsed() { return m_ctorUsed; }
private:
    CtorEnum m_ctorUsed;
};

using PStrList = StrList;

#endif // STRLIST_H
