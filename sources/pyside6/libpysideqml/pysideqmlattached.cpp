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

#include "pysideqmlattached.h"
#include "pysideqmlattached_p.h"
#include "pysideqmltypeinfo_p.h"
#include "pysideqmlregistertype_p.h"

#include <signalmanager.h>
#include <pyside_p.h>
#include <pysideclassdecorator_p.h>

#include <shiboken.h>
#include <signature.h>
#include <sbkstring.h>

#include <QtCore/QtGlobal>
#include <QtQml/qqml.h>

#include <algorithm>

// The QmlAttached decorator modifies QmlElement to register an attached property
// type. Due to the (reverse) execution order of decorators, it needs to follow
// QmlElement.
class PySideQmlAttachedPrivate : public PySide::ClassDecorator::TypeDecoratorPrivate
{
public:
    PyObject *tp_call(PyObject *self, PyObject *args, PyObject * /* kw */) override;
    const char *name() const override;
};

// The call operator is passed the class type and registers the type
// in QmlTypeInfo.
PyObject *PySideQmlAttachedPrivate::tp_call(PyObject *self, PyObject *args, PyObject * /* kw */)
{
    PyObject *klass = tp_call_check(args, CheckMode::WrappedType);
    if (klass == nullptr)
        return nullptr;

    auto *data = DecoratorPrivate::get<PySideQmlAttachedPrivate>(self);
    PySide::Qml::ensureQmlTypeInfo(klass)->attachedType = data->type();

    Py_INCREF(klass);
    return klass;
}

const char *PySideQmlAttachedPrivate::name() const
{
    return "QmlAttached";
}

extern "C" {

static PyTypeObject *createPySideQmlAttachedType(void)
{
    auto typeSlots =
        PySide::ClassDecorator::Methods<PySideQmlAttachedPrivate>::typeSlots();

    PyType_Spec PySideQmlAttachedType_spec = {
        "2:PySide6.QtCore.qmlAttached",
        sizeof(PySideClassDecorator),
        0,
        Py_TPFLAGS_DEFAULT,
        typeSlots.data()
    };
    return SbkType_FromSpec(&PySideQmlAttachedType_spec);
}

PyTypeObject *PySideQmlAttached_TypeF(void)
{
    static auto *type = createPySideQmlAttachedType();
    return type;
}

} // extern "C"

static const char *qmlAttached_SignatureStrings[] = {
    "PySide6.QtQml.QmlAttached(self,type:type)",
    nullptr // Sentinel
};

namespace PySide::Qml {

static QObject *attachedFactoryHelper(PyTypeObject *attachingType, QObject *o)
{
    // Call static qmlAttachedProperties() on type. If there is an error
    // and nullptr is returned, a crash occurs. So, errors should at least be
    // printed.

    Shiboken::GilState gilState;
    Shiboken::Conversions::SpecificConverter converter("QObject");
    Q_ASSERT(converter);

    static const char methodName[] = "qmlAttachedProperties";
    static PyObject *const pyMethodName = Shiboken::String::createStaticString(methodName);
    PyObject *attachingTypeObj = reinterpret_cast<PyObject *>(attachingType);
    Shiboken::AutoDecRef pyResult(PyObject_CallMethodObjArgs(attachingTypeObj, pyMethodName,
                                                             attachingTypeObj /* self */,
                                                             converter.toPython(&o),
                                                             nullptr));
    if (pyResult.isNull() || PyErr_Occurred()) {
        PyErr_Print();
        return nullptr;
    }

    if (PyType_IsSubtype(pyResult->ob_type, qObjectType()) == 0) {
        qWarning("QmlAttached: Attached objects must inherit QObject, got %s.",
                 pyResult->ob_type->tp_name);
        return nullptr;
    }

    QObject *result = nullptr;
    converter.toCpp(pyResult.object(), &result);
    return result;
}

// Since the required attached factory signature does not have a void *user
// parameter to store the attaching type, we employ a template trick, storing
// the attaching types in an array and create non-type-template (int) functions
// taking the array index as template parameter.
// We initialize the attachedFactories array with factory functions
// accessing the attachingTypes[N] using template metaprogramming.

enum { MAX_ATTACHING_TYPES = 50};

using AttachedFactory = QObject *(*)(QObject *);

static int nextAttachingType = 0;
static PyTypeObject *attachingTypes[MAX_ATTACHING_TYPES];
static AttachedFactory attachedFactories[MAX_ATTACHING_TYPES];

template <int N>
static QObject *attachedFactory(QObject *o)
{
    return attachedFactoryHelper(attachingTypes[N], o);
}

template<int N>
struct AttachedFactoryInitializerBase
{
};

template<int N>
struct AttachedFactoryInitializer : AttachedFactoryInitializerBase<N>
{
    static void init()
    {
        attachedFactories[N] = attachedFactory<N>;
        AttachedFactoryInitializer<N-1>::init();
    }
};

template<>
struct  AttachedFactoryInitializer<0> : AttachedFactoryInitializerBase<0>
{
    static void init()
    {
        attachedFactories[0] = attachedFactory<0>;
    }
};

void initQmlAttached(PyObject *module)
{
    std::fill(attachingTypes, attachingTypes + MAX_ATTACHING_TYPES, nullptr);
    AttachedFactoryInitializer<MAX_ATTACHING_TYPES - 1>::init();

    if (InitSignatureStrings(PySideQmlAttached_TypeF(), qmlAttached_SignatureStrings) < 0)
        return;

    Py_INCREF(PySideQmlAttached_TypeF());
    PyModule_AddObject(module, "QmlAttached",
                       reinterpret_cast<PyObject *>(PySideQmlAttached_TypeF()));
}

PySide::Qml::QmlExtensionInfo qmlAttachedInfo(PyTypeObject *t,
                                              const QSharedPointer<QmlTypeInfo> &info)
{
    PySide::Qml::QmlExtensionInfo result{nullptr, nullptr};
    if (info.isNull() || info->attachedType == nullptr)
        return result;

    auto *name = reinterpret_cast<PyTypeObject *>(t)->tp_name;
    if (nextAttachingType >= MAX_ATTACHING_TYPES) {
        qWarning("Unable to initialize attached type \"%s\": "
                 "The limit %d of  attached types has been reached.",
                 name, MAX_ATTACHING_TYPES);
        return result;
    }

    result.metaObject = PySide::retrieveMetaObject(info->attachedType);
    if (result.metaObject == nullptr) {
        qWarning("Unable to retrieve meta object for %s", name);
        return result;
    }

    attachingTypes[nextAttachingType] = t;
    result.factory = attachedFactories[nextAttachingType];
    ++nextAttachingType;

    return result;
}

QObject *qmlAttachedPropertiesObject(PyObject *typeObject, QObject *obj, bool create)
{
    auto *type = reinterpret_cast<PyTypeObject *>(typeObject);
    auto *end = attachingTypes + nextAttachingType;
    auto *typePtr = std::find(attachingTypes, end, type);
    if (typePtr == end) {
        qWarning("%s: Attaching type \"%s\" not found.", __FUNCTION__, type->tp_name);
        return nullptr;
    }

    auto func = attachedFactories[std::uintptr_t(typePtr - attachingTypes)];
    return ::qmlAttachedPropertiesObject(obj, func, create);
}

} // namespace PySide::Qml
