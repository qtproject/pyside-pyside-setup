// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysidequickregistertype.h"

#include <pyside.h>
#include <pysideqmlregistertype.h>
#include <pyside_p.h>
#include <shiboken.h>

#include <QtQuick/QQuickPaintedItem>
#include <QtQuick/QQuickFramebufferObject>

bool pyTypeObjectInheritsFromClass(PyTypeObject *pyObjType, const char *classPtrName)
{
    PyTypeObject *classPyType = Shiboken::Conversions::getPythonTypeObject(classPtrName);
    bool isDerived = PySequence_Contains(pyObjType->tp_mro,
                                         reinterpret_cast<PyObject *>(classPyType));
    return isDerived;
}

template <class WrappedClass>
bool registerTypeIfInheritsFromClass(const char *classPtrName,
                                     PyTypeObject *typeToRegister,
                                     QQmlPrivate::RegisterType *type)
{
    if (!pyTypeObjectInheritsFromClass(typeToRegister, classPtrName))
        return false;
    type->parserStatusCast =
            QQmlPrivate::StaticCastSelector<WrappedClass, QQmlParserStatus>::cast();
    type->valueSourceCast =
            QQmlPrivate::StaticCastSelector<WrappedClass, QQmlPropertyValueSource>::cast();
    type->valueInterceptorCast =
            QQmlPrivate::StaticCastSelector<WrappedClass, QQmlPropertyValueInterceptor>::cast();
    return true;
}

bool quickRegisterType(PyObject *pyObj, QQmlPrivate::RegisterType *type)
{
    using namespace Shiboken;

    PyTypeObject *pyObjType = reinterpret_cast<PyTypeObject *>(pyObj);
    PyTypeObject *qQuickItemPyType =
            Shiboken::Conversions::getPythonTypeObject("QQuickItem*");
    bool isQuickItem = PySequence_Contains(pyObjType->tp_mro,
                                           reinterpret_cast<PyObject *>(qQuickItemPyType));

    // Register only classes that inherit QQuickItem or its children.
    if (!isQuickItem)
        return false;

    return registerTypeIfInheritsFromClass<QQuickPaintedItem>("QQuickPaintedItem*",
                                                              pyObjType, type)
        || registerTypeIfInheritsFromClass<QQuickFramebufferObject>("QQuickFramebufferObject*",
                                                                    pyObjType, type)
        || registerTypeIfInheritsFromClass<QQuickItem>("QQuickItem*",
                                                       pyObjType, type);
}

void PySide::initQuickSupport(PyObject *module)
{
    Q_UNUSED(module);
    // We need to manually register a pointer version of these types in order for them to be used as property types.
    qRegisterMetaType<QQuickPaintedItem*>("QQuickPaintedItem*");
    qRegisterMetaType<QQuickFramebufferObject*>("QQuickFramebufferObject*");
    qRegisterMetaType<QQuickItem*>("QQuickItem*");

    Qml::setQuickRegisterItemFunction(quickRegisterType);
}
