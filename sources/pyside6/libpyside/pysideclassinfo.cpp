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

#include <sbkpython.h>

#include "pysideclassinfo.h"
#include "pyside_p.h"
#include "pysideclassinfo_p.h"
#include "dynamicqmetaobject.h"

#include <shiboken.h>
#include <signature.h>

extern "C"
{

static PyTypeObject *createClassInfoType(void)
{
    auto typeSlots =
        PySide::ClassDecorator::Methods<PySide::ClassInfo::ClassInfoPrivate>::typeSlots();

    PyType_Spec PySideClassInfoType_spec = {
        "2:PySide6.QtCore.ClassInfo",
        sizeof(PySideClassDecorator),
        0,
        Py_TPFLAGS_DEFAULT,
        typeSlots.data()};
    return SbkType_FromSpec(&PySideClassInfoType_spec);
};

PyTypeObject *PySideClassInfo_TypeF(void)
{
    static auto *type = createClassInfoType();
    return type;
}

}  // extern "C"

namespace PySide { namespace ClassInfo {

const char *ClassInfoPrivate::name() const
{
    return "ClassInfo";
}

PyObject *ClassInfoPrivate::tp_call(PyObject *self, PyObject *args, PyObject * /* kw */)
{
    PyObject *klass = tp_call_check(args, CheckMode::QObjectType);
    if (klass == nullptr)
        return nullptr;

    auto *pData = DecoratorPrivate::get<ClassInfoPrivate>(self);

    if (pData->m_alreadyWrapped) {
        PyErr_SetString(PyExc_TypeError, "This instance of ClassInfo() was already used to wrap an object");
        return nullptr;
    }

    bool validClass = false;

    PyTypeObject *klassType = reinterpret_cast<PyTypeObject *>(klass);
    if (auto userData = PySide::retrieveTypeUserData(klassType)) {
        PySide::MetaObjectBuilder &mo = userData->mo;
        mo.addInfo(pData->m_data);
        pData->m_alreadyWrapped = true;
        validClass = true;
    }

    if (!validClass) {
        PyErr_SetString(PyExc_TypeError, "This decorator can only be used on classes that are subclasses of QObject");
        return nullptr;
    }

    Py_INCREF(klass);
    return klass;
}

int ClassInfoPrivate::tp_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *infoDict = nullptr;
    auto size = PyTuple_Size(args);
    if (size == 1 && !kwds) {
        PyObject *tmp = PyTuple_GET_ITEM(args, 0);
        if (PyDict_Check(tmp))
            infoDict = tmp;
    } else if (size == 0 && kwds && PyDict_Check(kwds)) {
        infoDict = kwds;
    }

    if (!infoDict) {
        PyErr_Format(PyExc_TypeError, "ClassInfo() takes either keyword argument(s) or "
                                      "a single dictionary argument");
        return -1;
    }

    auto *pData = DecoratorPrivate::get<ClassInfoPrivate>(self);

    PyObject *key;
    PyObject *value;
    Py_ssize_t pos = 0;

    // PyDict_Next causes a segfault if kwds is empty
    if (PyDict_Size(infoDict) > 0) {
        while (PyDict_Next(infoDict, &pos, &key, &value)) {
            if (Shiboken::String::check(key) && Shiboken::String::check(value)) {
                pData->m_data[Shiboken::String::toCString(key)] = Shiboken::String::toCString(value);
            } else {
                PyErr_SetString(PyExc_TypeError, "All keys and values provided to ClassInfo() "
                                                 "must be strings");
                return -1;
            }
        }
    }

    return PyErr_Occurred() ? -1 : 0;
}

static const char *ClassInfo_SignatureStrings[] = {
    "PySide6.QtCore.ClassInfo(self,**info:typing.Dict[str,str])",
    nullptr}; // Sentinel

void init(PyObject *module)
{
    if (InitSignatureStrings(PySideClassInfo_TypeF(), ClassInfo_SignatureStrings) < 0)
        return;

    Py_INCREF(PySideClassInfo_TypeF());
    PyModule_AddObject(module, "ClassInfo", reinterpret_cast<PyObject *>(PySideClassInfo_TypeF()));
}

bool checkType(PyObject *pyObj)
{
    if (pyObj)
        return PyType_IsSubtype(Py_TYPE(pyObj), PySideClassInfo_TypeF());
    return false;
}

QMap<QByteArray, QByteArray> getMap(PyObject *obj)
{
    auto *pData = PySide::ClassDecorator::DecoratorPrivate::get<ClassInfoPrivate>(obj);
    return pData->m_data;
}

} //namespace Property
} //namespace PySide
