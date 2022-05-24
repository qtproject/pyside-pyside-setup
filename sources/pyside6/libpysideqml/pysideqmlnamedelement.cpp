// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
