// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pep384ext.h"
#include "autodecref.h"
#include "sbkstaticstrings_p.h"
#include "sbkstring.h"

const char *PepExt_TypeGetQualName(PyTypeObject *type)
{
    Shiboken::AutoDecRef qualName(PepType_GetQualName(type));
    return qualName.isNull() ? type->tp_name : Shiboken::String::toCString(qualName.object());
}
