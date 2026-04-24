// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBKENUM_P_H
#define SBKENUM_P_H

#include "sbkpython.h"

extern "C"
{

struct SbkConverter;

struct SbkEnumTypePrivate
{
    SbkConverter *converter;
    SbkConverter *flagsConverter;
};

}

#endif // SBKENUM_P_H
