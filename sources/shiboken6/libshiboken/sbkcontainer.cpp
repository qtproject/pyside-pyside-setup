// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "sbkcontainer.h"
#include "sbkstaticstrings.h"

namespace Shiboken
{
bool isOpaqueContainer(PyObject *o)
{
    return o != nullptr && o != Py_None
        && PyDict_Contains(o->ob_type->tp_dict,
                           Shiboken::PyMagicName::opaque_container()) == 1;

}
} // Shiboken
