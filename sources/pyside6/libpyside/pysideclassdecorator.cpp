// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include <sbkpython.h>

#include "pysideclassdecorator_p.h"
#include "pysideqobject.h"

#include <basewrapper.h>
#include <sbkcppstring.h>

namespace PySide::ClassDecorator {

DecoratorPrivate::~DecoratorPrivate() = default;

DecoratorPrivate *DecoratorPrivate::getPrivate(PyObject *o)
{
    auto *decorator = reinterpret_cast<PySideClassDecorator *>(o);
    return decorator->d;
}

PyObject *DecoratorPrivate::tp_call_check(PyObject *args, CheckMode checkMode) const
{
    if (!PyTuple_Check(args) || PyTuple_Size(args) != 1) {
        PyErr_Format(PyExc_TypeError,
                     "The %s decorator takes exactly 1 positional argument (%zd given)",
                     name(), PyTuple_Size(args));
        return nullptr;
    }

    PyObject *arg = PyTuple_GetItem(args, 0);

    // This will sometimes segfault if you mistakenly use it on a function declaration
    if (!PyType_Check(arg)) {
        PyErr_Format(PyExc_TypeError,
                     "The %s  decorator can only be used on class declarations", name());
        return nullptr;
    }

    auto type = reinterpret_cast<PyTypeObject *>(arg);

    if (checkMode != CheckMode::None && !Shiboken::ObjectType::checkType(type)) {
        PyErr_Format(PyExc_TypeError,
                     "The %s  decorator can only be used on wrapped types.", name());
        return nullptr;
    }

    if (checkMode == CheckMode::QObjectType && !isQObjectDerived(type, false)) {
        PyErr_Format(PyExc_TypeError,
                     "The %s  decorator can only be used on QObject-derived types.", name());
        return nullptr;
    }

    return arg;
}

int StringDecoratorPrivate::convertToString(PyObject *self, PyObject *args)
{
    int result = -1;
    if (PyTuple_Size(args) == 1) {
        PyObject *arg = PyTuple_GET_ITEM(args, 0);
        if (PyUnicode_Check(arg)) {
            auto *pData = DecoratorPrivate::get<StringDecoratorPrivate>(self);
            result = 0;
            Shiboken::String::toCppString(arg, &(pData->m_string));
        }
    }
    return result;
}

int StringDecoratorPrivate::tp_init(PyObject *self, PyObject *args, PyObject *)
{
    const int result = convertToString(self, args);
    if (result != 0)
        PyErr_Format(PyExc_TypeError, "%s takes a single string argument.", name());
    return result;
}

int TypeDecoratorPrivate::tp_init(PyObject *self, PyObject *args, PyObject *)
{
    const int result = convertToType(self, args);
    if (result != 0)
        PyErr_Format(PyExc_TypeError, "%s takes a single type argument.", name());
    return result;
}

int TypeDecoratorPrivate::convertToType(PyObject *self, PyObject *args)
{
    int result = -1;
    const auto argsCount = PyTuple_Size(args);
    if (argsCount == 1) {
        PyObject *arg = PyTuple_GET_ITEM(args, 0);
        if (PyType_Check(arg)) {
            result = 0;
            auto *pData = DecoratorPrivate::get<TypeDecoratorPrivate>(self);
            pData->m_type = reinterpret_cast<PyTypeObject *>(arg);
        }
    }
    return result;
}

} // namespace PySide::ClassDecorator
