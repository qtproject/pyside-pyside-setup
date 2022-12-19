// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef STRLIST_H
#define STRLIST_H

#include "libsamplemacros.h"
#include "str.h"

#include <list>

class LIBSAMPLE_API StrList : public std::list<Str>
{
public:
    enum CtorEnum {
        NoParamsCtor,
        StrCtor,
        CopyCtor,
        ListOfStrCtor
    };

    inline StrList() = default;
    inline StrList(const std::list<Str> &lst) :
        std::list<Str>(lst), m_ctorUsed(ListOfStrCtor) {}
    inline explicit StrList(const Str &str) :
        m_ctorUsed(StrCtor) { push_back(str); }
    inline StrList(const StrList &lst) :
        std::list<Str>(lst), m_ctorUsed(CopyCtor) {}

    StrList(StrList &&) = default;
    StrList &operator=(const StrList &) = default;
    StrList &operator=(StrList &&) = default;

    inline void append(const Str &str) { push_back(str); }
    Str join(const Str &sep) const;

    bool operator==(const std::list<Str> &other) const;
    inline bool operator!=(const std::list<Str> &other) const { return !(*this == other); }

    CtorEnum constructorUsed() const { return m_ctorUsed; }

private:
    CtorEnum m_ctorUsed = NoParamsCtor;
};

using PStrList = StrList;

#endif // STRLIST_H
