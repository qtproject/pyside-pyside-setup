/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "pysidestaticstrings.h"
#include <sbkstring.h>

#define STATIC_STRING_IMPL(funcName, value) \
PyObject *funcName() \
{ \
    static PyObject *const s = Shiboken::String::createStaticString(value); \
    return s; \
}

namespace PySide
{
namespace PyName
{
STATIC_STRING_IMPL(qtStaticMetaObject, "staticMetaObject")
STATIC_STRING_IMPL(qtConnect, "connect")
STATIC_STRING_IMPL(qtDisconnect, "disconnect")
STATIC_STRING_IMPL(qtEmit, "emit")
STATIC_STRING_IMPL(dict_ring, "dict_ring")
STATIC_STRING_IMPL(name, "name")
STATIC_STRING_IMPL(property, "property")
STATIC_STRING_IMPL(select_id, "select_id")
} // namespace PyName
namespace PyMagicName
{
STATIC_STRING_IMPL(doc, "__doc__")
STATIC_STRING_IMPL(name, "__name__")
STATIC_STRING_IMPL(property_methods, "__property_methods__")
} // namespace PyMagicName
} // namespace PySide
