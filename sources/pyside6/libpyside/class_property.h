// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef CLASS_PROPERTY_H
#define CLASS_PROPERTY_H

#include "pysidemacros.h"
#include <sbkpython.h>

extern "C" {

typedef struct {
    PyObject_HEAD
    PyObject *prop_get;
    PyObject *prop_set;
    PyObject *prop_del;
    PyObject *prop_doc;
    int getter_doc;
} propertyobject;

PYSIDE_API PyTypeObject *PyClassProperty_TypeF();

} // extern "C"

namespace PySide {
namespace ClassProperty {

PYSIDE_API void init(PyObject *module);

} // namespace ClassProperty
} // namespace PySide

#endif // CLASS_PROPERTY_H
