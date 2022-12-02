// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef USINGMEMBER_H
#define USINGMEMBER_H

#include "abstractmetalang_typedefs.h"
#include "parser/codemodel_enums.h"

QT_FORWARD_DECLARE_CLASS(QDebug)

struct UsingMember // Introducing a base class member via 'using' directive
{
    QString memberName;
    AbstractMetaClassCPtr baseClass;
    Access access;
};

QDebug operator<<(QDebug debug, const UsingMember &d);

#endif // USINGMEMBER_H
