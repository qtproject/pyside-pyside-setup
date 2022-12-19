// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "str.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sstream>

Str::Str(char c)
{
    char str[2] = { c, 0 };
    init(str);
}

Str::Str(const char *cstr)
{
    init(cstr);
}

void Str::init(const char *cstr)
{
    if (cstr)
        m_str = cstr;
}

Str Str::arg(const Str &s) const
{
    size_t idx = m_str.find_first_of("%VAR");
    if (idx == std::string::npos)
        return *this;

    std::string result = m_str;
    result.replace(idx, 4, s.m_str);
    return result.c_str();
}

Str &Str::append(const Str &s)
{
    m_str += s.m_str;
    return *this;
}

Str &Str::prepend(const Str &s)
{
    m_str = s.m_str + m_str;
    return *this;
}

const char *Str::cstring() const
{
    return m_str.c_str();
}

int Str::toInt(bool *ok, int base) const
{
    int result = 0;
    std::istringstream conv(m_str);
    switch (base) {
    case 8:
        conv >> std::oct >> result;
        break;
    case 10:
        conv >> std::dec >> result;
        break;
    case 16:
        conv >> std::hex >> result;
        break;
    }
    const bool my_ok = std::istringstream::eofbit  &conv.rdstate();
    if (!my_ok)
        result = 0;
    if (ok)
        *ok = my_ok;
    return result;
}

void Str::show() const
{
    std::printf("%s", cstring());
}

char Str::get_char(int pos) const
{
    return m_str[pos];
}

bool Str::set_char(int pos, char ch)
{
    m_str[pos] = ch;
    return true;
}

Str Str::operator+(int number) const
{
    std::ostringstream in;
    in << m_str << number;
    return in.str().c_str();
}

bool Str::operator==(const Str &other) const
{
    return m_str == other.m_str;
}

Str operator+(int number, const Str &str)
{
    std::ostringstream in;
    in << number << str.m_str;
    return in.str().c_str();
}

bool Str::operator<(const Str &other) const
{
    return m_str < other.m_str;
}

unsigned int strHash(const Str &str)
{
    unsigned int result = 0;
    for (char c : str.m_str)
        result = 5u * result + unsigned(c);
    return result;
}

void changePStr(PStr *pstr, const char *suffix)
{
    pstr->append(suffix);
}

void duplicatePStr(PStr *pstr)
{
    if (!pstr)
        return;
    pstr->append(*pstr);
}
