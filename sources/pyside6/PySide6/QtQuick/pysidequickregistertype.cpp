/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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
