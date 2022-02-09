/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
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

#include "pysideqmlforeign_p.h"
#include "pysideqmltypeinfo_p.h"

#include <signalmanager.h>
#include <pysideclassdecorator_p.h>

#include <shiboken.h>
#include <signature.h>
#include <sbkstring.h>

#include <QtCore/QtGlobal>
#include <QtCore/QDebug>

// The QmlForeign decorator modifies QmlElement to create a different type
// QmlElement.
class PySideQmlForeignPrivate : public PySide::ClassDecorator::TypeDecoratorPrivate
{
public:
    PyObject *tp_call(PyObject *self, PyObject *args, PyObject * /* kw */) override;
    const char *name() const override;
};

// The call operator is passed the class type and registers the type
// in QmlTypeInfo.
PyObject *PySideQmlForeignPrivate::tp_call(PyObject *self, PyObject *args, PyObject * /* kw */)
{
    PyObject *klass = tp_call_check(args, CheckMode::WrappedType);
    if (klass == nullptr)
        return nullptr;

    auto *data = DecoratorPrivate::get<PySideQmlForeignPrivate>(self);
    const auto info = PySide::Qml::ensureQmlTypeInfo(klass);
    info->foreignType = data->type();
    // Insert an alias to be used by the factory functions of Decorators like
    // @QmlExtended and @QmlAttached.
    auto *foreignObj = reinterpret_cast<const PyObject *>(info->foreignType);
    PySide::Qml::insertQmlTypeInfoAlias(foreignObj, info);

    Py_INCREF(klass);
    return klass;
}

const char *PySideQmlForeignPrivate::name() const
{
    return "QmlForeign";
}

extern "C" {

static PyTypeObject *createPySideQmlForeignType(void)
{
    auto typeSlots =
        PySide::ClassDecorator::Methods<PySideQmlForeignPrivate>::typeSlots();

    PyType_Spec PySideQmlForeignType_spec = {
        "2:PySide6.QtCore.qmlForeign",
        sizeof(PySideClassDecorator),
        0,
        Py_TPFLAGS_DEFAULT,
        typeSlots.data()
    };
    return SbkType_FromSpec(&PySideQmlForeignType_spec);
}

PyTypeObject *PySideQmlForeign_TypeF(void)
{
    static auto *type = createPySideQmlForeignType();
    return type;
}

} // extern "C"

static const char *qmlAttached_SignatureStrings[] = {
    "PySide6.QtQml.QmlForeign(self,type:type)",
    nullptr // Sentinel
};

namespace PySide::Qml {

void initQmlForeign(PyObject *module)
{
    if (InitSignatureStrings(PySideQmlForeign_TypeF(), qmlAttached_SignatureStrings) < 0)
        return;

    Py_INCREF(PySideQmlForeign_TypeF());
    PyModule_AddObject(module, "QmlForeign",
                       reinterpret_cast<PyObject *>(PySideQmlForeign_TypeF()));
}

} // namespace PySide::Qml
