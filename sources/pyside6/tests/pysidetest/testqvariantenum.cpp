// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testqvariantenum.h"

QVariant TestQVariantEnum::getLValEnum() const
{
    return this->m_enum;
}

QVariant TestQVariantEnum::getRValEnum() const
{
    return QVariant(Qt::Orientation::Horizontal);
}

int TestQVariantEnum::getNumberFromQVarEnum(QVariant variantEnum)
{
    return variantEnum.toInt();
}

bool TestQVariantEnum::channelingEnum([[maybe_unused]] QVariant rvalEnum) const
{
   return false;
}

bool TestQVariantEnum::isEnumChanneled() const
{
    return this->channelingEnum(this->getRValEnum());
}
