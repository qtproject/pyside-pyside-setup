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

#include "sbkstaticstrings.h"
#include "sbkstaticstrings_p.h"
#include "sbkstring.h"

#define STATIC_STRING_IMPL(funcName, value) \
PyObject *funcName() \
{ \
    static PyObject *const s = Shiboken::String::createStaticString(value); \
    return s; \
}

namespace Shiboken
{
namespace PyName {
// exported:
STATIC_STRING_IMPL(dumps, "dumps")
STATIC_STRING_IMPL(fget, "fget")
STATIC_STRING_IMPL(fset, "fset")
STATIC_STRING_IMPL(loads, "loads")
STATIC_STRING_IMPL(multi, "multi")
STATIC_STRING_IMPL(name, "name")
STATIC_STRING_IMPL(qApp, "qApp")
STATIC_STRING_IMPL(result, "result")
STATIC_STRING_IMPL(select_id, "select_id")
STATIC_STRING_IMPL(underscore, "_")
STATIC_STRING_IMPL(value, "value")
STATIC_STRING_IMPL(values, "values")

// Internal:
STATIC_STRING_IMPL(classmethod, "classmethod")
STATIC_STRING_IMPL(co_name, "co_name")
STATIC_STRING_IMPL(compile, "compile");
STATIC_STRING_IMPL(f_code, "f_code")
STATIC_STRING_IMPL(f_lineno, "f_lineno")
STATIC_STRING_IMPL(function, "function")
STATIC_STRING_IMPL(marshal, "marshal")
STATIC_STRING_IMPL(method, "method")
STATIC_STRING_IMPL(mro, "mro")
STATIC_STRING_IMPL(overload, "overload")
STATIC_STRING_IMPL(staticmethod, "staticmethod")
} // namespace PyName

namespace PyMagicName {
// exported:
STATIC_STRING_IMPL(class_, "__class__")
STATIC_STRING_IMPL(dict, "__dict__")
STATIC_STRING_IMPL(doc, "__doc__")
STATIC_STRING_IMPL(ecf, "__ecf__")
STATIC_STRING_IMPL(file, "__file__")
STATIC_STRING_IMPL(get, "__get__")
STATIC_STRING_IMPL(members, "__members__")
STATIC_STRING_IMPL(module, "__module__")
STATIC_STRING_IMPL(name, "__name__")
STATIC_STRING_IMPL(property_methods, "__property_methods__")
STATIC_STRING_IMPL(qualname, "__qualname__")
STATIC_STRING_IMPL(self, "__self__")

// Internal:
STATIC_STRING_IMPL(base, "__base__")
STATIC_STRING_IMPL(bases, "__bases__")
STATIC_STRING_IMPL(builtins, "__builtins__")
STATIC_STRING_IMPL(code, "__code__")
STATIC_STRING_IMPL(dictoffset, "__dictoffset__")
STATIC_STRING_IMPL(func, "__func__")
STATIC_STRING_IMPL(func_kind, "__func_kind__")
STATIC_STRING_IMPL(iter, "__iter__")
STATIC_STRING_IMPL(mro, "__mro__")
STATIC_STRING_IMPL(new_, "__new__")
STATIC_STRING_IMPL(objclass, "__objclass__")
STATIC_STRING_IMPL(signature, "__signature__")
STATIC_STRING_IMPL(weakrefoffset, "__weakrefoffset__")
} // namespace PyMagicName
} // namespace Shiboken
