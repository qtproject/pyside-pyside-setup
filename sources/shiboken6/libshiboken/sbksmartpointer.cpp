// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "sbksmartpointer.h"
#include "sbkstring.h"
#include "autodecref.h"

namespace Shiboken::SmartPointer
{

PyObject *repr(PyObject *pointer, PyObject *pointee)
{
    Shiboken::AutoDecRef pointerRepr(Shiboken::String::repr(pointer));
    if (pointer == nullptr)
        return pointerRepr.release();

    Shiboken::AutoDecRef pointeeRepr(pointee != nullptr
                                     ? PyObject_Repr(pointee)
                                     : Shiboken::String::repr(pointee));

    return PyUnicode_FromFormat("%U (%U)", pointerRepr.object(), pointeeRepr.object());
}

} // namespace Shiboken::SmartPointer
