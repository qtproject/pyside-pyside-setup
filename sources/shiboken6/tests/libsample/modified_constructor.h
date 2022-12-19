// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef MODIFIEDCONSTRUCTOR_H
#define MODIFIEDCONSTRUCTOR_H

#include "libsamplemacros.h"

class LIBSAMPLE_API ModifiedConstructor
{
public:

    explicit ModifiedConstructor(int first_arg);
    int retrieveValue() const;

private:
    int m_stored_value;
};

#endif // MODIFIEDCONSTRUCTOR_H

