// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLREGISTERTYPE_P_H
#define PYSIDEQMLREGISTERTYPE_P_H

#include <sbkpython.h>

PyTypeObject *qObjectType();


namespace PySide::Qml {

PyObject *qmlNamedElementMacro(PyObject *pyObj, const char *typeName);

}

#endif // PYSIDEQMLREGISTERTYPE_P_H
