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

#include "pysideqmlnamedelement_p.h"
#include "pysideqmltypeinfo_p.h"
#include <pysideclassdecorator_p.h>
#include <pysideqmlregistertype_p.h>

#include <shiboken.h>
#include <signature.h>

#include <QtCore/QtGlobal>

class PySideQmlNamedElementPrivate : public PySide::ClassDecorator::StringDecoratorPrivate
{
public:
    PyObject *tp_call(PyObject *self, PyObject *args, PyObject * /* kw */) override;
    const char *name() const override;
};

const char *PySideQmlNamedElementPrivate::name() const
{
    return "QmlNamedElement";
}

// The call operator is passed the class type and registers the type
PyObject *PySideQmlNamedElementPrivate::tp_call(PyObject *self, PyObject *args, PyObject *)
{
    PyObject *klass = tp_call_check(args, CheckMode::WrappedType);
    if (klass == nullptr)
        return nullptr;

    auto *data = DecoratorPrivate::get<PySideQmlNamedElementPrivate>(self);
    auto *result = PySide::Qml::qmlNamedElementMacro(klass, data->string().c_str());
    Py_XINCREF(result);
    return result;
}

extern "C" {

PyTypeObject *createPySideQmlNamedElementType(void)
{
    auto typeSlots =
        PySide::ClassDecorator::Methods<PySideQmlNamedElementPrivate>::typeSlots();

    PyType_Spec PySideQmlNamedElementType_spec = {
        "2:PySide6.QtCore.qmlNamedElement",
        sizeof(PySideClassDecorator),
        0,
        Py_TPFLAGS_DEFAULT,
        typeSlots.data()
    };
    return SbkType_FromSpec(&PySideQmlNamedElementType_spec);
}

PyTypeObject *PySideQmlNamedElement_TypeF(void)
{
    static auto *type = createPySideQmlNamedElementType();
    return type;
}

} // extern "C"

static const char *qmlNamedElement_SignatureStrings[] = {
    "PySide6.QtQml.QmlNamedElement(self,reason:str)",
    nullptr // Sentinel
};

void initQmlNamedElement(PyObject *module)
{
    if (InitSignatureStrings(PySideQmlNamedElement_TypeF(), qmlNamedElement_SignatureStrings) < 0)
        return;

    Py_INCREF(PySideQmlNamedElement_TypeF());
    PyModule_AddObject(module, "QmlNamedElement",
                       reinterpret_cast<PyObject *>(PySideQmlNamedElement_TypeF()));
}
