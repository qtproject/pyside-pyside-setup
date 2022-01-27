/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
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

    auto &info = PySide::Qml::ensureQmlTypeInfo(klass);
    info.flags.setFlag(PySide::Qml::QmlTypeFlag::Uncreatable);
    info.noCreationReason = data->string();

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
