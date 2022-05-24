// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysideqmluncreatable.h"
#include "pysideqmltypeinfo_p.h"
#include <pysideclassdecorator_p.h>

#include <shiboken.h>
#include <signature.h>
#include <sbkcppstring.h>

#include <string>
#include <unordered_map>

#include <QtCore/QtGlobal>

class PySideQmlUncreatablePrivate : public PySide::ClassDecorator::StringDecoratorPrivate
{
public:
    PyObject *tp_call(PyObject *self, PyObject *args, PyObject * /* kw */) override;
    int tp_init(PyObject *self, PyObject *args, PyObject *kwds) override;
    const char *name() const override;
};

const char *PySideQmlUncreatablePrivate::name() const
{
    return "QmlUncreatable";
}

// The call operator is passed the class type and registers the reason
// in the uncreatableReasonMap()
PyObject *PySideQmlUncreatablePrivate::tp_call(PyObject *self, PyObject *args, PyObject * /* kw */)
{
    PyObject *klass = tp_call_check(args, CheckMode::WrappedType);
    if (klass== nullptr)
        return nullptr;

    auto *data = DecoratorPrivate::get<PySideQmlUncreatablePrivate>(self);

    const auto info = PySide::Qml::ensureQmlTypeInfo(klass);
    info->flags.setFlag(PySide::Qml::QmlTypeFlag::Uncreatable);
    info->noCreationReason = data->string();

    Py_INCREF(klass);
    return klass;
}

int PySideQmlUncreatablePrivate::tp_init(PyObject *self, PyObject *args, PyObject * /* kwds */)
{
    int result = -1;
    const auto argsCount = PyTuple_Size(args);
    if (argsCount == 0) {
        result = 0; // QML-generated reason
    } else if (argsCount == 1) {
        PyObject *arg = PyTuple_GET_ITEM(args, 0);
        result = arg == Py_None
            ? 0 // QML-generated reason
            : convertToString(self, args);
    }

    if (result != 0) {
        PyErr_Format(PyExc_TypeError,
                     "QmlUncreatable() takes a single string argument or no argument");
    }

    return result;
}

extern "C" {

PyTypeObject *createPySideQmlUncreatableType(void)
{
    auto typeSlots =
        PySide::ClassDecorator::Methods<PySideQmlUncreatablePrivate>::typeSlots();

    PyType_Spec PySideQmlUncreatableType_spec = {
        "2:PySide6.QtCore.qmlUncreatable",
        sizeof(PySideClassDecorator),
        0,
        Py_TPFLAGS_DEFAULT,
        typeSlots.data()
    };
    return SbkType_FromSpec(&PySideQmlUncreatableType_spec);
}

PyTypeObject *PySideQmlUncreatable_TypeF(void)
{
    static auto *type = createPySideQmlUncreatableType();
    return type;
}

} // extern "C"

static const char *qmlUncreatable_SignatureStrings[] = {
    "PySide6.QtQml.QmlUncreatable(self,reason:str)",
    nullptr // Sentinel
};

void initQmlUncreatable(PyObject *module)
{
    if (InitSignatureStrings(PySideQmlUncreatable_TypeF(), qmlUncreatable_SignatureStrings) < 0)
        return;

    Py_INCREF(PySideQmlUncreatable_TypeF());
    PyModule_AddObject(module, "QmlUncreatable",
                       reinterpret_cast<PyObject *>(PySideQmlUncreatable_TypeF()));
}
