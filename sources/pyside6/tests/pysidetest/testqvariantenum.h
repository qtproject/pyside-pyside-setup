// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTQVARIANT_H
#define TESTQVARIANT_H

#include "pysidetest_macros.h"

#include <QtCore/QVariant>

class PYSIDETEST_API TestQVariantEnum
{
public:
    TestQVariantEnum(QVariant lvalue_enum) : m_enum(lvalue_enum) {}
    QVariant getLValEnum() const;
    static int getNumberFromQVarEnum(QVariant variantEnum = QVariant());
    bool isEnumChanneled() const;
    virtual QVariant getRValEnum() const;
    virtual bool channelingEnum(QVariant rvalEnum) const;
    virtual ~TestQVariantEnum() = default;
private:
    QVariant m_enum;
};

#endif // TESTQVARIANT_H
