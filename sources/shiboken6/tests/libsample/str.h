// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef STR_H
#define STR_H

#include "libsamplemacros.h"

#include <string>

class LIBSAMPLE_API Str
{
public:
    Str(char c);
    Str(const char *cstr = "");

    Str arg(const Str &s) const;

    Str &append(const Str &s);
    Str &prepend(const Str &s);

    const char *cstring() const;
    char get_char(int pos) const;
    bool set_char(int pos, char ch);

    int toInt(bool *ok = nullptr, int base = 10) const;

    void show() const;

    inline int size() const { return m_str.size(); }

    // nonsense operator just to test reverse operators
    Str operator+(int number) const;
    bool operator==(const Str &other) const;
    bool operator<(const Str &other) const;

private:
    void init(const char *cstr);
    std::string m_str;

    friend LIBSAMPLE_API Str operator+(int number, const Str &str);
    friend LIBSAMPLE_API unsigned int strHash(const Str &str);
};

LIBSAMPLE_API Str operator+(int number, const Str &str);
LIBSAMPLE_API unsigned int strHash(const Str &str);

using PStr = Str;
LIBSAMPLE_API void changePStr(PStr *pstr, const char *suffix);
LIBSAMPLE_API void duplicatePStr(PStr *pstr = nullptr);

#endif // STR_H
