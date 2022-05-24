// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
#ifndef PYSIDE_SLOT_P_H
#define PYSIDE_SLOT_P_H

#include <sbkpython.h>
#define PYSIDE_SLOT_LIST_ATTR "_slots"

namespace PySide { namespace Slot {
    void init(PyObject* module);
}}

#endif
