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

#include "pysideqmlextended_p.h"
#include "pysideqmltypeinfo_p.h"
#include "pysideqmlregistertype_p.h"

#include <pyside_p.h>
#include <pysideclassdecorator_p.h>

#include <shiboken.h>
#include <signature.h>
#include <sbkstring.h>

#include <QtCore/QtGlobal>
#include <QtQml/qqml.h>

// The QmlExtended decorator modifies QmlElement to register an extension.
// Due to the (reverse) execution order of decorators, it needs to follow
// QmlElement.
class PySideQmlExtendedPrivate : public PySide::ClassDecorator::TypeDecoratorPrivate
{
public:
    PyObject *tp_call(PyObject *self, PyObject *args, PyObject * /* kw */) override;
    const char *name() const override;
};

// The call operator is passed the class type and registers the type
// in QmlTypeInfo.
PyObject *PySideQmlExtendedPrivate::tp_call(PyObject *self, PyObject *args, PyObject * /* kw */)
{
    PyObject *klass = tp_call_check(args, CheckMode::WrappedType);
    if (klass == nullptr)
        return nullptr;

    auto *data = DecoratorPrivate::get<PySideQmlExtendedPrivate>(self);
    PySide::Qml::ensureQmlTypeInfo(klass)->extensionType = data->type();

    Py_INCREF(klass);
    return klass;
}

const char *PySideQmlExtendedPrivate::name() const
{
    return "QmlExtended";
}

extern "C" {

static PyTypeObject *createPySideQmlExtendedType(void)
{
    auto typeSlots =
        PySide::ClassDecorator::Methods<PySideQmlExtendedPrivate>::typeSlots();

    PyType_Spec PySideQmlExtendedType_spec = {
        "2:PySide6.QtCore.qmlExtended",
        sizeof(PySideClassDecorator),
        0,
        Py_TPFLAGS_DEFAULT,
        typeSlots.data()
    };
    return SbkType_FromSpec(&PySideQmlExtendedType_spec);
}

PyTypeObject *PySideQmlExtended_TypeF(void)
{
    static auto *type = createPySideQmlExtendedType();
    return type;
}

} // extern "C"

static const char *qmlExtended_SignatureStrings[] = {
    "PySide6.QtQml.QmlExtended(self,type:type)",
    nullptr // Sentinel
};

namespace PySide::Qml {

static QObject *extensionFactory(QObject *o)
{
    Shiboken::GilState gilState;
    Shiboken::Conversions::SpecificConverter converter("QObject");
    Q_ASSERT(converter);
    PyObject *pyObj = converter.toPython(&o);
    Q_ASSERT(pyObj);

    // Search for the extension type and create an instance by invoking
    // the call operator on type with the parent parameter.
    // If there is an error and nullptr is returned, a crash occurs,
    // so, errors should at least be printed.

    auto *pyObjType = Py_TYPE(pyObj);
    const auto info = qmlTypeInfo(reinterpret_cast<PyObject *>(pyObjType));
    if (info.isNull() || info->extensionType == nullptr) {
        qWarning("QmlExtended: Cannot find extension of %s.", pyObjType->tp_name);
        return nullptr;
    }

    Shiboken::AutoDecRef args(PyTuple_New(1));
    PyTuple_SET_ITEM(args.object(), 0, pyObj);
    auto *extensionTypeObj = reinterpret_cast<PyObject *>(info->extensionType);
    Shiboken::AutoDecRef pyResult(PyObject_Call(extensionTypeObj, args, nullptr));
    if (pyResult.isNull() || PyErr_Occurred()) {
        PyErr_Print();
        return nullptr;
    }

    if (PyType_IsSubtype(pyResult->ob_type, qObjectType()) == 0) {
        qWarning("QmlExtended: Extension objects must inherit QObject, got %s.",
                 pyResult->ob_type->tp_name);
        return nullptr;
    }

    QObject *result = nullptr;
    converter.toCpp(pyResult.object(), &result);
    return result;
}

void initQmlExtended(PyObject *module)
{
    if (InitSignatureStrings(PySideQmlExtended_TypeF(), qmlExtended_SignatureStrings) < 0)
        return;

    Py_INCREF(PySideQmlExtended_TypeF());
    PyModule_AddObject(module, "QmlExtended",
                       reinterpret_cast<PyObject *>(PySideQmlExtended_TypeF()));
}

PySide::Qml::QmlExtensionInfo qmlExtendedInfo(PyObject *t,
                                              const QSharedPointer<QmlTypeInfo> &info)
{
    PySide::Qml::QmlExtensionInfo result{nullptr, nullptr};
    if (!info.isNull() && info->extensionType) {
        result.metaObject = PySide::retrieveMetaObject(info->extensionType);
        if (result.metaObject) {
            result.factory = extensionFactory;
        } else {
            qWarning("Unable to retrieve meta object for %s",
                     reinterpret_cast<PyTypeObject *>(t)->tp_name);
        }
    }
    return result;
}

} // namespace PySide::Qml
