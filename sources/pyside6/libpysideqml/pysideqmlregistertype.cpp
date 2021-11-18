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

#include "pysideqmlregistertype.h"
#include "pysideqmlregistertype_p.h"
#include "pysideqmluncreatable.h"

#include <limits>

// shiboken
#include <shiboken.h>
#include <sbkstring.h>

// pyside
#include <pyside.h>
#include <pysideqobject.h>
#include <pyside_p.h>

#include <QtCore/QMutex>
#include <QtCore/QTypeRevision>

#include <QtQml/qqml.h>
#include <QtQml/QJSValue>
#include <QtQml/QQmlListProperty>

// Mutex used to avoid race condition on PySide::nextQObjectMemoryAddr.
static QMutex nextQmlElementMutex;

static void createInto(void *memory, void *type)
{
    QMutexLocker locker(&nextQmlElementMutex);
    PySide::setNextQObjectMemoryAddr(memory);
    Shiboken::GilState state;
    PyObject *obj = PyObject_CallObject(reinterpret_cast<PyObject *>(type), 0);
    if (!obj || PyErr_Occurred())
        PyErr_Print();
    PySide::setNextQObjectMemoryAddr(0);
}

PyTypeObject *qObjectType()
{
    static PyTypeObject *const result =
        Shiboken::Conversions::getPythonTypeObject("QObject*");
    assert(result);
    return result;
}

static PyTypeObject *qQmlEngineType()
{
    static PyTypeObject *const result =
        Shiboken::Conversions::getPythonTypeObject("QQmlEngine*");
    assert(result);
    return result;
}

static PyTypeObject *qQJSValueType()
{
    static PyTypeObject *const result =
        Shiboken::Conversions::getPythonTypeObject("QJSValue*");
    assert(result);
    return result;
}

int PySide::qmlRegisterType(PyObject *pyObj, const char *uri, int versionMajor,
                            int versionMinor, const char *qmlName, const char *noCreationReason,
                            bool creatable)
{
    using namespace Shiboken;

    PyTypeObject *qobjectType = qObjectType();

    PyTypeObject *pyObjType = reinterpret_cast<PyTypeObject *>(pyObj);
    if (!PySequence_Contains(pyObjType->tp_mro, reinterpret_cast<PyObject *>(qobjectType))) {
        PyErr_Format(PyExc_TypeError, "A type inherited from %s expected, got %s.",
                     qobjectType->tp_name, pyObjType->tp_name);
        return -1;
    }

    const QMetaObject *metaObject = PySide::retrieveMetaObject(pyObjType);
    Q_ASSERT(metaObject);

    QQmlPrivate::RegisterType type;

    // Allow registering Qt Quick items.
    bool registered = false;
    QuickRegisterItemFunction quickRegisterItemFunction = getQuickRegisterItemFunction();
    if (quickRegisterItemFunction) {
        registered =
            quickRegisterItemFunction(pyObj, uri, versionMajor, versionMinor,
                                      qmlName, creatable, noCreationReason, &type);
    }

    // Register as simple QObject rather than Qt Quick item.
    if (!registered) {
        // Incref the type object, don't worry about decref'ing it because
        // there's no way to unregister a QML type.
        Py_INCREF(pyObj);

        type.structVersion = 0;

        // FIXME: Fix this to assign new type ids each time.
        type.typeId = QMetaType(QMetaType::QObjectStar);
        type.listId = QMetaType::fromType<QQmlListProperty<QObject> >();
        type.attachedPropertiesFunction = QQmlPrivate::attachedPropertiesFunc<QObject>();
        type.attachedPropertiesMetaObject = QQmlPrivate::attachedPropertiesMetaObject<QObject>();

        type.parserStatusCast =
                QQmlPrivate::StaticCastSelector<QObject, QQmlParserStatus>::cast();
        type.valueSourceCast =
                QQmlPrivate::StaticCastSelector<QObject, QQmlPropertyValueSource>::cast();
        type.valueInterceptorCast =
                QQmlPrivate::StaticCastSelector<QObject, QQmlPropertyValueInterceptor>::cast();

        int objectSize = static_cast<int>(PySide::getSizeOfQObject(
                                              reinterpret_cast<PyTypeObject *>(pyObj)));
        type.objectSize = objectSize;
        type.create = creatable ? createInto : nullptr;
        type.noCreationReason = QString::fromUtf8(noCreationReason);
        type.userdata = pyObj;
        type.uri = uri;
        type.version = QTypeRevision::fromVersion(versionMajor, versionMinor);
        type.elementName = qmlName;

        type.extensionObjectCreate = 0;
        type.extensionMetaObject = 0;
        type.customParser = 0;
    }
    type.metaObject = metaObject; // Snapshot may have changed.

    int qmlTypeId = QQmlPrivate::qmlregister(QQmlPrivate::TypeRegistration, &type);
    if (qmlTypeId == -1) {
        PyErr_Format(PyExc_TypeError, "QML meta type registration of \"%s\" failed.",
                     qmlName);
    }
    return qmlTypeId;
}

int PySide::qmlRegisterSingletonType(PyObject *pyObj, const char *uri, int versionMajor,
                                     int versionMinor, const char *qmlName, PyObject *callback,
                                     bool isQObject, bool hasCallback)
{
    using namespace Shiboken;

    if (hasCallback) {
        if (!PyCallable_Check(callback)) {
            PyErr_Format(PyExc_TypeError, "Invalid callback specified.");
            return -1;
        }

        AutoDecRef funcCode(PyObject_GetAttrString(callback, "__code__"));
        AutoDecRef argCount(PyObject_GetAttrString(funcCode, "co_argcount"));

        int count = PyLong_AsLong(argCount);

        if (count != 1) {
            PyErr_Format(PyExc_TypeError, "Callback has a bad parameter count.");
            return -1;
        }

        // Make sure the callback never gets deallocated
        Py_INCREF(callback);
    }

    const QMetaObject *metaObject = nullptr;

    if (isQObject) {
        PyTypeObject *pyObjType = reinterpret_cast<PyTypeObject *>(pyObj);

        if (!isQObjectDerived(pyObjType, true))
            return -1;

        // If we don't have a callback we'll need the pyObj to stay allocated indefinitely
        if (!hasCallback)
            Py_INCREF(pyObj);

        metaObject = PySide::retrieveMetaObject(pyObjType);
        Q_ASSERT(metaObject);
    }

    QQmlPrivate::RegisterSingletonType type;
    type.structVersion = 0;

    type.uri = uri;
    type.version = QTypeRevision::fromVersion(versionMajor, versionMinor);
    type.typeName = qmlName;
    type.instanceMetaObject = metaObject;

    if (isQObject) {
        // FIXME: Fix this to assign new type ids each time.
        type.typeId = QMetaType(QMetaType::QObjectStar);

        type.qObjectApi =
            [callback, pyObj, hasCallback](QQmlEngine *engine, QJSEngine *) -> QObject * {
                Shiboken::GilState gil;
                AutoDecRef args(PyTuple_New(hasCallback ? 1 : 0));

                if (hasCallback) {
                    PyTuple_SET_ITEM(args, 0, Conversions::pointerToPython(
                                     qQmlEngineType(), engine));
                }

                AutoDecRef retVal(PyObject_CallObject(hasCallback ? callback : pyObj, args));

                // Make sure the callback returns something we can convert, else the entire application will crash.
                if (retVal.isNull() ||
                    Conversions::isPythonToCppPointerConvertible(qObjectType(), retVal) == nullptr) {
                    PyErr_Format(PyExc_TypeError, "Callback returns invalid value.");
                    return nullptr;
                }

                QObject *obj = nullptr;
                Conversions::pythonToCppPointer(qObjectType(), retVal, &obj);

                if (obj != nullptr)
                    Py_INCREF(retVal);

                return obj;
            };
    } else {
        type.scriptApi =
            [callback](QQmlEngine *engine, QJSEngine *) -> QJSValue {
                Shiboken::GilState gil;
                AutoDecRef args(PyTuple_New(1));

                PyTuple_SET_ITEM(args, 0, Conversions::pointerToPython(
                                 qQmlEngineType(), engine));

                AutoDecRef retVal(PyObject_CallObject(callback, args));

                PyTypeObject *qjsvalueType = qQJSValueType();

                // Make sure the callback returns something we can convert, else the entire application will crash.
                if (retVal.isNull() ||
                    Conversions::isPythonToCppPointerConvertible(qjsvalueType, retVal) == nullptr) {
                    PyErr_Format(PyExc_TypeError, "Callback returns invalid value.");
                    return QJSValue(QJSValue::UndefinedValue);
                }

                QJSValue *val = nullptr;
                Conversions::pythonToCppPointer(qjsvalueType, retVal, &val);

                Py_INCREF(retVal);

                return *val;
            };
    }

    return QQmlPrivate::qmlregister(QQmlPrivate::SingletonRegistration, &type);
}

int PySide::qmlRegisterSingletonInstance(PyObject *pyObj, const char *uri, int versionMajor,
                                         int versionMinor, const char *qmlName,
                                         PyObject *instanceObject)
{
    using namespace Shiboken;

    // Check if the Python Type inherit from QObject
    PyTypeObject *pyObjType = reinterpret_cast<PyTypeObject *>(pyObj);

    if (!isQObjectDerived(pyObjType, true))
        return -1;

    // Convert the instanceObject (PyObject) into a QObject
    QObject *instanceQObject = PySide::convertToQObject(instanceObject, true);
    if (instanceQObject == nullptr)
        return -1;

    // Create Singleton Functor to pass the QObject to the Type registration step
    // similarly to the case when we have a callback
    QQmlPrivate::SingletonFunctor registrationFunctor;
    registrationFunctor.m_object = instanceQObject;

    const QMetaObject *metaObject = PySide::retrieveMetaObject(pyObjType);
    Q_ASSERT(metaObject);

    QQmlPrivate::RegisterSingletonType type;
    type.structVersion = 0;

    type.uri = uri;
    type.version = QTypeRevision::fromVersion(versionMajor, versionMinor);
    type.typeName = qmlName;
    type.instanceMetaObject = metaObject;

    // FIXME: Fix this to assign new type ids each time.
    type.typeId = QMetaType(QMetaType::QObjectStar);
    type.qObjectApi = registrationFunctor;


    return QQmlPrivate::qmlregister(QQmlPrivate::SingletonRegistration, &type);
}

static std::string getGlobalString(const char *name)
{
    using Shiboken::AutoDecRef;

    PyObject *globals = PyEval_GetGlobals();

    AutoDecRef pyName(Py_BuildValue("s", name));

    PyObject *globalVar = PyDict_GetItem(globals, pyName);

    if (globalVar == nullptr || !PyUnicode_Check(globalVar))
        return "";

    const char *stringValue = _PepUnicode_AsString(globalVar);
    return stringValue != nullptr ? stringValue : "";
}

static int getGlobalInt(const char *name)
{
    using Shiboken::AutoDecRef;

    PyObject *globals = PyEval_GetGlobals();

    AutoDecRef pyName(Py_BuildValue("s", name));

    PyObject *globalVar = PyDict_GetItem(globals, pyName);

    if (globalVar == nullptr || !PyLong_Check(globalVar))
        return -1;

    long value = PyLong_AsLong(globalVar);

    if (value > std::numeric_limits<int>::max() || value < std::numeric_limits<int>::min())
        return -1;

    return value;
}

enum class RegisterMode {
    Normal,
    Anonymous,
    Uncreatable,
    Singleton
};

static PyObject *qmlElementMacroHelper(PyObject *pyObj,
                                       const char *decoratorName,
                                       RegisterMode mode = RegisterMode::Normal,
                                       const char *noCreationReason = nullptr)
{
    if (!PyType_Check(pyObj)) {
        PyErr_Format(PyExc_TypeError, "This decorator can only be used on classes.");
        return nullptr;
    }

    PyTypeObject *pyObjType = reinterpret_cast<PyTypeObject *>(pyObj);
    const char *typeName = pyObjType->tp_name;
    if (!PySequence_Contains(pyObjType->tp_mro, reinterpret_cast<PyObject *>(qObjectType()))) {
        PyErr_Format(PyExc_TypeError, "This decorator can only be used with classes inherited from QObject, got %s.",
                     typeName);
        return nullptr;
    }

    std::string importName = getGlobalString("QML_IMPORT_NAME");
    int majorVersion = getGlobalInt("QML_IMPORT_MAJOR_VERSION");
    int minorVersion = getGlobalInt("QML_IMPORT_MINOR_VERSION");

    if (importName.empty()) {
        PyErr_Format(PyExc_TypeError, "You need specify QML_IMPORT_NAME in order to use %s.",
                     decoratorName);
        return nullptr;
    }

    if (majorVersion == -1) {
       PyErr_Format(PyExc_TypeError, "You need specify QML_IMPORT_MAJOR_VERSION in order to use %s.",
                    decoratorName);
       return nullptr;
    }

    // Specifying a minor version is optional
    if (minorVersion == -1)
        minorVersion = 0;

    const char *uri = importName.c_str();
    const int result = mode == RegisterMode::Singleton
        ? PySide::qmlRegisterSingletonType(pyObj, uri, majorVersion, minorVersion,
                                          typeName, nullptr,
                                          PySide::isQObjectDerived(pyObjType, false),
                                          false)
        : PySide::qmlRegisterType(pyObj, uri, majorVersion, minorVersion,
                                  mode != RegisterMode::Anonymous ? typeName : nullptr,
                                  noCreationReason,
                                  mode == RegisterMode::Normal);

    if (result == -1) {
        PyErr_Format(PyExc_TypeError, "%s: Failed to register type %s.",
                     decoratorName, typeName);
    }

    return pyObj;
}

// FIXME: Store this in PySide::TypeUserData once it is moved to libpyside?
static QList<PyObject *> decoratedSingletons;

PyObject *PySide::qmlElementMacro(PyObject *pyObj)
{
    const char *noCreationReason = nullptr;
    RegisterMode mode = RegisterMode::Normal;
    if (decoratedSingletons.contains(pyObj))
        mode = RegisterMode::Singleton;
    else if ((noCreationReason = PySide::qmlNoCreationReason(pyObj)))
        mode = RegisterMode::Uncreatable;
    return qmlElementMacroHelper(pyObj, "QmlElement", mode, noCreationReason);
}

PyObject *PySide::qmlAnonymousMacro(PyObject *pyObj)
{
    return qmlElementMacroHelper(pyObj, "QmlAnonymous",
                                 RegisterMode::Anonymous);
}

PyObject *PySide::qmlSingletonMacro(PyObject *pyObj)
{
    decoratedSingletons.append(pyObj);
    Py_INCREF(pyObj);
    return pyObj;
}
