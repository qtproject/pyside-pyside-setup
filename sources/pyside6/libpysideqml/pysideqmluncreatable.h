// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLUNCREATABLE_H
#define PYSIDEQMLUNCREATABLE_H

#include <sbkpython.h>

// The QmlUncreatable decorator modifies QmlElement to register an uncreatable
// type. Due to the (reverse) execution order of decorators, it needs to follow
// QmlElement.
extern "C"
{
    extern PyTypeObject *PySideQmlUncreatable_TypeF(void);
}

void initQmlUncreatable(PyObject *module);

#endif // PYSIDEQMLUNCREATABLE_H
