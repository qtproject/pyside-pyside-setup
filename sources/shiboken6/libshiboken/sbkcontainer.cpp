// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "sbkcontainer.h"
#include "sbkpep.h"
#include "sbkstaticstrings.h"
#include "autodecref.h"

// The functionality was moved to a source to reduce size
// and remove PepType_GetSlot() usage from the public header.
ShibokenContainer *ShibokenSequenceContainerPrivateBase::allocContainer(PyTypeObject *subtype)
{
    allocfunc allocFunc = reinterpret_cast<allocfunc>(PyType_GetSlot(subtype, Py_tp_alloc));
    return reinterpret_cast<ShibokenContainer *>(allocFunc(subtype, 0));
}

void ShibokenSequenceContainerPrivateBase::freeSelf(PyObject *pySelf)
{
    auto freeFunc = reinterpret_cast<freefunc>(PyType_GetSlot(Py_TYPE(pySelf)->tp_base,
                                                              Py_tp_free));
    freeFunc(pySelf);
}

namespace Shiboken
{
bool isOpaqueContainer(PyObject *o)
{
    if (!o)
        return false;
    Shiboken::AutoDecRef tpDict(PepType_GetDict(o->ob_type));
    return o != nullptr && o != Py_None
        && PyDict_Contains(tpDict.object(), Shiboken::PyMagicName::opaque_container()) == 1;

}
} // Shiboken
