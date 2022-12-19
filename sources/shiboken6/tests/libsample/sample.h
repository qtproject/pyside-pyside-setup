// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SAMPLE_H
#define SAMPLE_H

#include "libsamplemacros.h"

// namespace with the same name of the current package to try to mess up with the generator
namespace sample
{
    // to increase the mess we add a class with the same name of the package/namespace
    class LIBSAMPLE_API sample
    {
    public:
        sample(int value = 0);
        int value() const;
    private:
        int m_value;
    };

    // shiboken must not generate richcompare for namespace sample
    LIBSAMPLE_API bool operator==(const sample &s1, const sample &s2);

    const int INT_CONSTANT = 42;
}

#endif // SAMPLE_H
