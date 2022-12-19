// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef BYTEARRAY_H
#define BYTEARRAY_H

#include "str.h"
#include "libsamplemacros.h"

#include <vector>

class LIBSAMPLE_API ByteArray
{
public:
    ByteArray();
    explicit ByteArray(char data);
    explicit ByteArray(const char *data);
    explicit ByteArray(const char *data, int len);

    int size() const;
    char at(int i) const;
    char operator[](int i) const;

    const char *data() const;

    ByteArray &append(char c);
    ByteArray &append(const char *data);
    ByteArray &append(const char *data, int len);
    ByteArray &append(const ByteArray &other);

    bool operator==(const ByteArray &other) const;
    bool operator!=(const ByteArray &other) const;

    ByteArray &operator+=(char c);
    ByteArray &operator+=(const char *data);
    ByteArray &operator+=(const ByteArray &other);

    static unsigned int hash(const ByteArray &byteArray);
private:
    std::vector<char> m_data;
    friend LIBSAMPLE_API bool operator==(const ByteArray &ba1, const char *ba2);
    friend LIBSAMPLE_API bool operator==(const char *ba1, const ByteArray &ba2);
    friend LIBSAMPLE_API bool operator!=(const ByteArray &ba1, const char *ba2);
    friend LIBSAMPLE_API bool operator!=(const char *ba1, const ByteArray &ba2);

    friend LIBSAMPLE_API ByteArray operator+(const ByteArray &ba1, const ByteArray &ba2);
    friend LIBSAMPLE_API ByteArray operator+(const ByteArray &ba1, const char *ba2);
    friend LIBSAMPLE_API ByteArray operator+(const char *ba1, const ByteArray &ba2);
    friend LIBSAMPLE_API ByteArray operator+(const ByteArray &ba1, char ba2);
    friend LIBSAMPLE_API ByteArray operator+(char ba1, const ByteArray &ba2);
};

LIBSAMPLE_API bool operator==(const ByteArray &ba1, const char *ba2);
LIBSAMPLE_API bool operator==(const char *ba1, const ByteArray &ba2);
LIBSAMPLE_API bool operator!=(const ByteArray &ba1, const char *ba2);
LIBSAMPLE_API bool operator!=(const char *ba1, const ByteArray &ba2);

LIBSAMPLE_API ByteArray operator+(const ByteArray &ba1, const ByteArray &ba2);
LIBSAMPLE_API ByteArray operator+(const ByteArray &ba1, const char *ba2);
LIBSAMPLE_API ByteArray operator+(const char *ba1, const ByteArray &ba2);
LIBSAMPLE_API ByteArray operator+(const ByteArray &ba1, char ba2);
LIBSAMPLE_API ByteArray operator+(char ba1, const ByteArray &ba2);

#endif // BYTEARRAY_H
