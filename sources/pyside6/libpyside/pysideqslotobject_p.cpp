// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysideqslotobject_p.h"

#include <autodecref.h>
#include <gilstate.h>

namespace PySide
{

void PySideQSlotObject::impl(int which, QSlotObjectBase *this_, QObject *receiver,
                             void **args, bool *ret)
{
    auto self = static_cast<PySideQSlotObject *>(this_);
    switch (which) {
    case Destroy:
        delete self;
        break;
    case Call:
        {
            Shiboken::GilState state;
            Shiboken::AutoDecRef arglist(PyTuple_New(0));
            Shiboken::AutoDecRef ret(PyObject_CallObject(self->callable, arglist));
            break;
        }
    case Compare:
    case NumOperations:
        Q_UNUSED(receiver);
        Q_UNUSED(args);
        Q_UNUSED(ret);
        break;
    }
}

} // namespace PySide
