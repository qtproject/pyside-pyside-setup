// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysideqmluncreatable.h"
#include <pysideclassdecorator_p.h>
#include <pysideclassinfo.h>

#include <shiboken.h>
#include <signature.h>
#include <sbkcppstring.h>

#include <QtCore/qbytearray.h>
#include <private/qmetaobjectbuilder_p.h>

using namespace Qt::StringLiterals;

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

    auto *type = reinterpret_cast<PyTypeObject *>(klass);
    auto *data = DecoratorPrivate::get<PySideQmlUncreatablePrivate>(self);
    setUncreatableClassInfo(type, data->string());

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

void setUncreatableClassInfo(PyTypeObject *type, const QByteArray &reason)
{
    PySide::ClassInfo::setClassInfo(type, {
        {"QML.Creatable"_ba, "false"_ba},
        {"QML.UncreatableReason"_ba, reason} });
}

void setUncreatableClassInfo(QMetaObjectBuilder *builder, const QByteArray &reason)
{
    builder->addClassInfo("QML.Creatable", "false");
    builder->addClassInfo("QML.UncreatableReason", reason);
}
