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

#include <shiboken.h>
#include <signature.h>
#include <sbkcppstring.h>

#include <string>
#include <unordered_map>

#include <QtCore/QtGlobal>

struct PySideQmlUncreatablePrivate
{
    std::string reason;
};

extern "C"
{

// The call operator is passed the class type and registers the reason
// in the uncreatableReasonMap()
static PyObject *classInfo_tp_call(PyObject *self, PyObject *args, PyObject * /* kw */)
{
    if (!PyTuple_Check(args) || PyTuple_Size(args) != 1) {
        PyErr_Format(PyExc_TypeError,
                     "The QmlUncreatable decorator takes exactly 1 positional argument (%zd given)",
                     PyTuple_Size(args));
        return nullptr;
    }

    PyObject *klass = PyTuple_GetItem(args, 0);
    // This will sometimes segfault if you mistakenly use it on a function declaration
    if (!PyType_Check(klass)) {
        PyErr_SetString(PyExc_TypeError,
                        "This decorator can only be used on class declarations");
        return nullptr;
    }

    PyTypeObject *klassType = reinterpret_cast<PyTypeObject *>(klass);
    if (!Shiboken::ObjectType::checkType(klassType)) {
        PyErr_SetString(PyExc_TypeError,
                        "This decorator can only be used on classes that are subclasses of QObject");
        return nullptr;
    }

    auto data = reinterpret_cast<PySideQmlUncreatable *>(self);
    auto &info = PySide::Qml::ensureQmlTypeInfo(klass);
    info.flags.setFlag(PySide::Qml::QmlTypeFlag::Uncreatable);
    info.noCreationReason = data->d->reason;

    Py_INCREF(klass);
    return klass;
}

static PyObject *qmlUncreatableTpNew(PyTypeObject *subtype, PyObject * /* args */,
                                     PyObject * /* kwds */)
{
    auto *me = reinterpret_cast<PySideQmlUncreatable *>(subtype->tp_alloc(subtype, 0));
    me->d = new PySideQmlUncreatablePrivate;
    return reinterpret_cast<PyObject *>(me);
}

static int qmlUncreatableTpInit(PyObject *self, PyObject *args, PyObject * /* kwds */)
{
    PySideQmlUncreatable *data = reinterpret_cast<PySideQmlUncreatable *>(self);
    PySideQmlUncreatablePrivate *pData = data->d;

    bool ok = false;
    const auto argsCount = PyTuple_Size(args);
    if (argsCount == 0) {
        ok = true; // QML-generated reason
    } else if (argsCount == 1) {
        PyObject *arg = PyTuple_GET_ITEM(args, 0);
        if (arg == Py_None) {
            ok = true; // QML-generated reason
        } else if (PyUnicode_Check(arg)) {
            ok = true;
            Shiboken::String::toCppString(arg, &(pData->reason));
        }
    }

    if (!ok) {
        PyErr_Format(PyExc_TypeError,
                     "QmlUncreatable() takes a single string argument or no argument");
        return -1;
    }

    return 0;
}

static void qmlUncreatableFree(void *self)
{
    auto pySelf = reinterpret_cast<PyObject *>(self);
    auto data = reinterpret_cast<PySideQmlUncreatable *>(self);

    delete data->d;
    Py_TYPE(pySelf)->tp_base->tp_free(self);
}

static PyType_Slot PySideQmlUncreatableType_slots[] = {
    {Py_tp_call, reinterpret_cast<void *>(classInfo_tp_call)},
    {Py_tp_init, reinterpret_cast<void *>(qmlUncreatableTpInit)},
    {Py_tp_new, reinterpret_cast<void *>(qmlUncreatableTpNew)},
    {Py_tp_free, reinterpret_cast<void *>(qmlUncreatableFree)},
    {Py_tp_dealloc, reinterpret_cast<void *>(Sbk_object_dealloc)},
    {0, nullptr}
};

static PyType_Spec PySideQmlUncreatableType_spec = {
    "2:PySide6.QtCore.qmlUncreatable",
    sizeof(PySideQmlUncreatable),
    0,
    Py_TPFLAGS_DEFAULT,
    PySideQmlUncreatableType_slots,
};

PyTypeObject *PySideQmlUncreatable_TypeF(void)
{
    static auto *type = SbkType_FromSpec(&PySideQmlUncreatableType_spec);
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
