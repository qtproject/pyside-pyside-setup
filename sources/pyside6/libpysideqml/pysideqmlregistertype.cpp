// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysideqmlregistertype.h"
#include "pysideqmlregistertype_p.h"
#include "pysideqmltypeinfo_p.h"
#include "pysideqmlattached_p.h"
#include "pysideqmlextended_p.h"
#include "pysideqmluncreatable.h"

#include <limits>
#include <optional>

// shiboken
#include <shiboken.h>
#include <sbkstring.h>

// pyside
#include <pyside.h>
#include <pysideqobject.h>
#include <pysideclassinfo.h>
#include <pyside_p.h>

#include <QtCore/QMutex>
#include <QtCore/QTypeRevision>

#include <QtQml/qqml.h>
#include <QtQml/QJSValue>
#include <QtQml/QQmlListProperty>
#include <private/qqmlmetatype_p.h>
#include <private/qmetaobjectbuilder_p.h>

#include <memory>

using namespace Qt::StringLiterals;

static PySide::Qml::QuickRegisterItemFunction quickRegisterItemFunction = nullptr;

static const auto qmlElementKey = "QML.Element"_ba;

static void createInto(void *memory, void *type)
{
    QMutexLocker locker(&PySide::nextQObjectMemoryAddrMutex());
    PySide::setNextQObjectMemoryAddr(memory);
    Shiboken::GilState state;
    PyObject *obj = PyObject_CallObject(reinterpret_cast<PyObject *>(type), 0);
    if (!obj || PyErr_Occurred())
        PyErr_Print();
    PySide::setNextQObjectMemoryAddr(nullptr);
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

// Check if o inherits from baseClass
static bool inheritsFrom(const QMetaObject *o, const char *baseClass)
{
    for (auto *base = o->superClass(); base ; base = base->superClass()) {
        if (qstrcmp(base->className(), baseClass) == 0)
            return true;
    }
    return false;
}

// Check if o inherits from QPyQmlPropertyValueSource.
static inline bool isQmlPropertyValueSource(const QMetaObject *o)
{
    return inheritsFrom(o, "QPyQmlPropertyValueSource");
}

// Check if o inherits from QQmlParserStatus.
static inline bool isQmlParserStatus(const QMetaObject *o)
{
    return inheritsFrom(o, "QPyQmlParserStatus");
}

static QByteArray getGlobalString(const char *name)
{
    PyObject *globalVar = PyDict_GetItemString(PyEval_GetGlobals(), name);

    if (globalVar == nullptr || PyUnicode_Check(globalVar) == 0)
        return {};

    const char *stringValue = _PepUnicode_AsString(globalVar);
    return stringValue != nullptr ? QByteArray(stringValue) : QByteArray{};
}

static int getGlobalInt(const char *name)
{
    PyObject *globalVar = PyDict_GetItemString(PyEval_GetGlobals(), name);

    if (globalVar == nullptr || PyLong_Check(globalVar) == 0)
        return -1;

    long value = PyLong_AsLong(globalVar);

    if (value > std::numeric_limits<int>::max() || value < std::numeric_limits<int>::min())
        return -1;

    return value;
}

struct ImportData
{
    QByteArray importName;
    int majorVersion = 0;
    int minorVersion = 0;

    QTypeRevision toTypeRevision() const;
};

QTypeRevision ImportData::toTypeRevision() const
{
    return QTypeRevision::fromVersion(majorVersion, minorVersion);
}

std::optional<ImportData> getGlobalImportData(const char *decoratorName)
{
    ImportData result{getGlobalString("QML_IMPORT_NAME"),
                      getGlobalInt("QML_IMPORT_MAJOR_VERSION"),
                      getGlobalInt("QML_IMPORT_MINOR_VERSION")};

    if (result.importName.isEmpty()) {
        PyErr_Format(PyExc_TypeError, "You need specify QML_IMPORT_NAME in order to use %s.",
                     decoratorName);
        return {};
    }

    if (result.majorVersion == -1) {
        PyErr_Format(PyExc_TypeError, "You need specify QML_IMPORT_MAJOR_VERSION in order to use %s.",
                     decoratorName);
        return {};
    }

    // Specifying a minor version is optional
    if (result.minorVersion == -1)
        result.minorVersion = 0;
    return result;
}

static PyTypeObject *checkTypeObject(PyObject *pyObj, const char *what)
{
    if (PyType_Check(pyObj) == 0) {
        PyErr_Format(PyExc_TypeError, "%s can only be used for classes.", what);
        return nullptr;
    }
    return reinterpret_cast<PyTypeObject *>(pyObj);
}

static bool setClassInfo(PyTypeObject *type, const QByteArray &key, const QByteArray &value)
{
    if (!PySide::ClassInfo::setClassInfo(type, key, value)) {
        PyErr_Format(PyExc_TypeError, "Setting class info \"%s\" to \"%s\" on \"%s\" failed.",
                     key.constData(), value.constData(), type->tp_name);
        return false;
    }
    return true;
}

static inline bool setSingletonClassInfo(PyTypeObject *type)
{
    return setClassInfo(type, "QML.Singleton"_ba, "true"_ba);
}

static QQmlCustomParser *defaultCustomParserFactory()
{
    return nullptr;
}

namespace PySide::Qml {

// Modern (6.7) type registration using RegisterTypeAndRevisions
// and information set to QMetaClassInfo.
static int qmlRegisterType(PyObject *pyObj,
                           const ImportData &importData,
                           const QMetaObject *metaObject,
                           const QMetaObject *classInfoMetaObject = nullptr)
{
    PyTypeObject *pyObjType = reinterpret_cast<PyTypeObject *>(pyObj);

    if (classInfoMetaObject == nullptr)
        classInfoMetaObject = metaObject;

    // Register as simple QObject rather than Qt Quick item.
    // Incref the type object, don't worry about decref'ing it because
    // there's no way to unregister a QML type.
    Py_INCREF(pyObj);

    const QByteArray typeName(pyObjType->tp_name);
    QByteArray ptrType = typeName + '*';
    QByteArray listType = QByteArrayLiteral("QQmlListProperty<") + typeName + '>';
    const auto typeId = QMetaType(new QQmlMetaTypeInterface(ptrType));
    const auto listId = QMetaType(new QQmlListMetaTypeInterface(listType, typeId.iface()));
    const int objectSize = static_cast<int>(PySide::getSizeOfQObject(reinterpret_cast<PyTypeObject *>(pyObj)));

    const auto typeInfo = qmlTypeInfo(pyObj);
    const auto attachedInfo = qmlAttachedInfo(pyObjType, typeInfo);
    const auto extendedInfo = qmlExtendedInfo(pyObj, typeInfo);

    QList<int> ids;
    QQmlPrivate::RegisterTypeAndRevisions type {
        QQmlPrivate::RegisterType::StructVersion::Base, // structVersion
        typeId, listId, objectSize,
        createInto, // create
        pyObj, // userdata
        nullptr, // createValueType (Remove in Qt 7)
        importData.importName.constData(),
        importData.toTypeRevision(), // version
        metaObject,
        classInfoMetaObject,
        attachedInfo.factory, // attachedPropertiesFunction
        attachedInfo.metaObject, // attachedPropertiesMetaObject
        0, 0, 0, // parserStatusCast, valueSourceCast, valueInterceptorCast
        extendedInfo.factory, // extensionObjectCreate
        extendedInfo.metaObject, // extensionMetaObject
        defaultCustomParserFactory, // customParser
        &ids, // qmlTypeIds
        0, // finalizerCast
        false, // forceAnonymous
        {} // listMetaSequence
    };

    // Allow registering Qt Quick items.
    const bool isQuickType = quickRegisterItemFunction && quickRegisterItemFunction(pyObj, &type);

    if (!isQuickType) { // values filled by the Quick registration
        // QPyQmlParserStatus inherits QObject, QQmlParserStatus, so,
        // it is found behind the QObject.
        type.parserStatusCast = isQmlParserStatus(metaObject)
            ? int(sizeof(QObject))
            : QQmlPrivate::StaticCastSelector<QObject, QQmlParserStatus>::cast();
        // Similar for QPyQmlPropertyValueSource
        type.valueSourceCast = isQmlPropertyValueSource(metaObject)
            ? int(sizeof(QObject))
            : QQmlPrivate::StaticCastSelector<QObject, QQmlPropertyValueSource>::cast();
        type.valueInterceptorCast =
                QQmlPrivate::StaticCastSelector<QObject, QQmlPropertyValueInterceptor>::cast();
    }

    QQmlPrivate::qmlregister(QQmlPrivate::TypeAndRevisionsRegistration, &type);
    const int qmlTypeId = ids.value(0, -1);
    if (qmlTypeId == -1) {
        PyErr_Format(PyExc_TypeError, "QML meta type registration of \"%s\" failed.",
                     typeName.constData());
    }
    return qmlTypeId;
}

static int qmlRegisterType(PyObject *pyObj, PyObject *pyClassInfoObj,
                           const ImportData &importData)
{
    PyTypeObject *pyObjType = reinterpret_cast<PyTypeObject *>(pyObj);
    if (!isQObjectDerived(pyObjType, true))
        return -1;

    const QMetaObject *metaObject = PySide::retrieveMetaObject(pyObjType);
    Q_ASSERT(metaObject);
    const QMetaObject *classInfoMetaObject = pyObj == pyClassInfoObj
        ? metaObject : PySide::retrieveMetaObject(pyClassInfoObj);
    return qmlRegisterType(pyObj, importData, metaObject, classInfoMetaObject);
}

// Legacy (pre 6.7) compatibility helper for the free register functions.
int qmlRegisterType(PyObject *pyObj, const char *uri, int versionMajor, int versionMinor,
                    const char *qmlName, const char *noCreationReason,
                    bool creatable)
{
    auto *type = checkTypeObject(pyObj, "qmlRegisterType()");
    if (type == nullptr || !PySide::isQObjectDerived(type, true))
        return -1;

    const QMetaObject *metaObject = PySide::retrieveMetaObject(type);
    Q_ASSERT(metaObject);

    // PYSIDE-2709: Use a separate QMetaObject for the class information
    // as modifying metaObject breaks inheritance.
    QMetaObjectBuilder classInfobuilder(&QObject::staticMetaObject);
    classInfobuilder.addClassInfo(qmlElementKey, qmlName);
    if (!creatable)
        setUncreatableClassInfo(&classInfobuilder, noCreationReason);
    auto *classInfoMetaObject = classInfobuilder.toMetaObject();

    const int qmlTypeId = qmlRegisterType(pyObj, {uri, versionMajor, versionMinor},
                                          metaObject, classInfoMetaObject);
    free(classInfoMetaObject);
    return qmlTypeId;
}

// Singleton helpers

// Check the arguments of a singleton callback (C++: "QJSValue cb(QQmlEngine *, QJSEngine *)",
// but we drop the QJSEngine since it will be the same as QQmlEngine when the latter exists.
static bool checkSingletonCallback(PyObject *callback)
{
    if (callback == nullptr) {
        PyErr_SetString(PyExc_TypeError, "No callback specified.");
        return false;
    }
    if (PyCallable_Check(callback) == 0) {
        PyErr_Format(PyExc_TypeError, "Invalid callback specified (%S).", callback);
        return false;
    }
    Shiboken::AutoDecRef funcCode(PyObject_GetAttrString(callback, "__code__"));
    if (funcCode.isNull()) {
        PyErr_Format(PyExc_TypeError, "Cannot retrieve code of callback (%S).", callback);
        return false;
    }
    Shiboken::AutoDecRef argCountAttr(PyObject_GetAttrString(funcCode, "co_argcount"));
    const int argCount = PyLong_AsLong(argCountAttr.object());
    if (argCount != 1) {
        PyErr_Format(PyExc_TypeError, "Callback (%S) has %d parameter(s), expected one.",
                     callback, argCount);
        return false;
    }

    return true;
}

// Shared data of a singleton creation callback which dereferences an object on
// destruction.
class SingletonQObjectCreationSharedData
{
public:
    Q_DISABLE_COPY_MOVE(SingletonQObjectCreationSharedData)

    SingletonQObjectCreationSharedData(PyObject *cb, PyObject *ref = nullptr) noexcept :
        callable(cb), reference(ref)
    {
        Py_XINCREF(ref);
    }

    // FIXME: Currently, the QML registration data are in global static variables
    // and thus cleaned up after Python terminates. Once they are cleaned up
    // by the QML engine, the code can be activated for proper cleanup of the references.
   ~SingletonQObjectCreationSharedData()
#if 0 //
    ~SingletonQObjectCreationSharedData()
    {
        if (reference != nullptr) {
            Shiboken::GilState gil;
            Py_DECREF(reference);
        }
    }
#else
        = default;
#endif

    PyObject *callable{}; // Callback, static method or type object to  be invoked.
    PyObject *reference{}; // Object to dereference when going out scope
};

// Base class for QML singleton creation callbacks with helper for error checking.
class SingletonQObjectCreationBase
{
protected:
    explicit SingletonQObjectCreationBase(PyObject *cb, PyObject *ref = nullptr) :
        m_data(std::make_shared<SingletonQObjectCreationSharedData>(cb, ref))
    {
    }

    static QObject *handleReturnValue(PyObject *retVal);

    std::shared_ptr<SingletonQObjectCreationSharedData> data() const { return m_data; }

private:
    std::shared_ptr<SingletonQObjectCreationSharedData> m_data;
};

QObject *SingletonQObjectCreationBase::handleReturnValue(PyObject *retVal)
{
    using Shiboken::Conversions::isPythonToCppPointerConvertible;
    // Make sure the callback returns something we can convert, else the entire application will crash.
    if (retVal == nullptr) {
        PyErr_Format(PyExc_TypeError, "Callback returns 0 value.");
        return nullptr;
    }
    if (isPythonToCppPointerConvertible(qObjectType(), retVal) == nullptr) {
        PyErr_Format(PyExc_TypeError, "Callback returns invalid value (%S).", retVal);
        return nullptr;
    }

    QObject *obj = nullptr;
    Shiboken::Conversions::pythonToCppPointer(qObjectType(), retVal, &obj);
    return obj;
}

// QML singleton creation callback by invoking a type object
class SingletonQObjectFromTypeCreation : public SingletonQObjectCreationBase
{
public:
    explicit SingletonQObjectFromTypeCreation(PyObject *typeObj) :
        SingletonQObjectCreationBase(typeObj, typeObj) {}

    QObject *operator ()(QQmlEngine *, QJSEngine *) const
    {
        Shiboken::GilState gil;
        Shiboken::AutoDecRef args(PyTuple_New(0));
        PyObject *retVal = PyObject_CallObject(data()->callable, args);
        QObject *result = handleReturnValue(retVal);
        if (result == nullptr)
            Py_XDECREF(retVal);
        return result;
    }
};

// QML singleton creation by invoking a callback, passing QQmlEngine. Keeps a
// references to the the callback.
class SingletonQObjectCallbackCreation : public SingletonQObjectCreationBase
{
public:
    explicit SingletonQObjectCallbackCreation(PyObject *callback) :
        SingletonQObjectCreationBase(callback, callback) {}
    explicit SingletonQObjectCallbackCreation(PyObject *callback, PyObject *ref) :
        SingletonQObjectCreationBase(callback, ref) {}

    QObject *operator ()(QQmlEngine *engine, QJSEngine *) const
    {
        Shiboken::GilState gil;
        Shiboken::AutoDecRef args(PyTuple_New(1));
        PyTuple_SET_ITEM(args, 0,
                         Shiboken::Conversions::pointerToPython(qQmlEngineType(), engine));
        PyObject *retVal = PyObject_CallObject(data()->callable, args);
        QObject *result = handleReturnValue(retVal);
        if (result == nullptr)
            Py_XDECREF(retVal);
        return result;
    }
};

using SingletonQObjectCreation = std::function<QObject*(QQmlEngine *, QJSEngine *)>;

// Modern (6.7) singleton type registration using RegisterSingletonTypeAndRevisions
// and information set to QMetaClassInfo (QObject only pending QTBUG-110467).
static int qmlRegisterSingletonTypeV2(PyObject *pyObj, PyObject *pyClassInfoObj,
                                      const ImportData &importData,
                                      const SingletonQObjectCreation &callback)
{
    PyTypeObject *pyObjType = reinterpret_cast<PyTypeObject *>(pyObj);
    if (!isQObjectDerived(pyObjType, true))
        return -1;

    const QMetaObject *metaObject = PySide::retrieveMetaObject(pyObjType);
    Q_ASSERT(metaObject);
    const QMetaObject *classInfoMetaObject = pyObj == pyClassInfoObj
        ? metaObject : PySide::retrieveMetaObject(pyClassInfoObj);

    QList<int> ids;
    QQmlPrivate::RegisterSingletonTypeAndRevisions type {
        QQmlPrivate::RegisterType::StructVersion::Base, // structVersion
        importData.importName.constData(),
        importData.toTypeRevision(), // version
        callback, // qObjectApi,
        metaObject,
        classInfoMetaObject,
        QMetaType(QMetaType::QObjectStar), // typeId
        nullptr, // extensionMetaObject
        nullptr, // extensionObjectCreate
        &ids
    };

    QQmlPrivate::qmlregister(QQmlPrivate::SingletonAndRevisionsRegistration, &type);
    const int qmlTypeId = ids.value(0, -1);
    if (qmlTypeId == -1) {
        PyErr_Format(PyExc_TypeError, "Singleton QML meta type registration of \"%s\" failed.",
                     pyObjType->tp_name);
    }
    return qmlTypeId;
}

// Legacy (pre 6.7) singleton type registration using RegisterSingletonType
// for QObject and value types. Still used by qmlRegisterSingletonType()
// for the hypothetical case of a value type.
static int qmlRegisterSingletonType(PyObject *pyObj, const ImportData &importData,
                                    const char *qmlName, PyObject *callback,
                                    bool isQObject, bool hasCallback)
{
    if (hasCallback && !checkSingletonCallback(callback))
        return -1;

    const QMetaObject *metaObject = nullptr;

    if (isQObject) {
        PyTypeObject *pyObjType = reinterpret_cast<PyTypeObject *>(pyObj);

        if (!isQObjectDerived(pyObjType, true))
            return -1;

        metaObject = PySide::retrieveMetaObject(pyObjType);
        Q_ASSERT(metaObject);
    }

    QQmlPrivate::RegisterSingletonType type {
        QQmlPrivate::RegisterType::StructVersion::Base, // structVersion
        importData.importName.constData(),
        importData.toTypeRevision(), // version
        qmlName, // typeName
        {}, // scriptApi
        {}, // qObjectApi
        metaObject, // instanceMetaObject
        {}, // typeId
        nullptr, // extensionMetaObject
        nullptr, // extensionObjectCreate
        {} // revision
    };

    if (isQObject) {
        // FIXME: Fix this to assign new type ids each time.
        type.typeId = QMetaType(QMetaType::QObjectStar);

        if (hasCallback)
            type.qObjectApi = SingletonQObjectCallbackCreation(callback);
        else
            type.qObjectApi = SingletonQObjectFromTypeCreation(pyObj);
    } else {
        type.scriptApi =
            [callback](QQmlEngine *engine, QJSEngine *) -> QJSValue {
                using namespace Shiboken;

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

// Legacy (pre 6.7) compatibility helper for the free register functions.
int qmlRegisterSingletonType(PyObject *pyObj,const char *uri,
                             int versionMajor, int versionMinor, const char *qmlName,
                             PyObject *callback, bool isQObject, bool hasCallback)
{
    return qmlRegisterSingletonType(pyObj, {uri, versionMajor, versionMinor}, qmlName,
                                    callback, isQObject, hasCallback);
}

// Modern (6.7) singleton instance registration using RegisterSingletonTypeAndRevisions
// and information set to QMetaClassInfo (QObject only).
static int qmlRegisterSingletonInstance(PyObject *pyObj, const ImportData &importData,
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
    QQmlPrivate::SingletonInstanceFunctor registrationFunctor;
    registrationFunctor.m_object = instanceQObject;

    const QMetaObject *metaObject = PySide::retrieveMetaObject(pyObjType);
    Q_ASSERT(metaObject);

    QList<int> ids;
    QQmlPrivate::RegisterSingletonTypeAndRevisions type {
        QQmlPrivate::RegisterType::StructVersion::Base, // structVersion
        importData.importName.constData(),
        importData.toTypeRevision(), // version
        registrationFunctor, // qObjectApi,
        metaObject,
        metaObject, // classInfoMetaObject
        QMetaType(QMetaType::QObjectStar), // typeId
        nullptr, // extensionMetaObject
        nullptr, // extensionObjectCreate
        &ids
    };

    QQmlPrivate::qmlregister(QQmlPrivate::SingletonAndRevisionsRegistration, &type);
    return ids.value(0, -1);
}

// Legacy (pre 6.7) compatibility helper for the free register functions.
int qmlRegisterSingletonInstance(PyObject *pyObj, const char *uri, int versionMajor,
                                 int versionMinor, const char *qmlName,
                                 PyObject *instanceObject)
{
    auto *type = checkTypeObject(pyObj, "qmlRegisterSingletonInstance()");
    if (type == nullptr || !setClassInfo(type, qmlElementKey, qmlName)
        || !setSingletonClassInfo(type)) {
        return -1;
    }
    return qmlRegisterSingletonInstance(pyObj, {uri, versionMajor, versionMinor},
                                        instanceObject);
}

} // namespace PySide::Qml

enum class RegisterMode {
    Normal,
    Singleton
};

namespace PySide::Qml {

// Check for a static create() method on a decorated singleton.
// Might set a Python error if the check fails.
static std::optional<SingletonQObjectCreation>
    singletonCreateMethod(PyTypeObject *pyObjType)
{
    Shiboken::AutoDecRef tpDict(PepType_GetDict(pyObjType));
    auto *create = PyDict_GetItemString(tpDict.object(), "create");
    // Method decorated by "@staticmethod"
    if (create == nullptr || std::strcmp(Py_TYPE(create)->tp_name, "staticmethod") != 0)
        return std::nullopt;
    // 3.10: "__wrapped__"
    Shiboken::AutoDecRef function(PyObject_GetAttrString(create, "__func__"));
    if (function.isNull()) {
        PyErr_Format(PyExc_TypeError, "Cannot retrieve function of callback (%S).",
                     create);
        return std::nullopt;
    }
    if (!checkSingletonCallback(function.object()))
        return std::nullopt;
    // Reference to the type needs to be kept.
    return SingletonQObjectCallbackCreation(function.object(),
                                            reinterpret_cast<PyObject *>(pyObjType));
}

PyObject *qmlElementMacro(PyObject *pyObj, const char *decoratorName,
                          const QByteArray &typeName)
{
    auto *pyObjType = checkTypeObject(pyObj, decoratorName);
    if (pyObjType == nullptr)
        return nullptr;

    if (!PySide::isQObjectDerived(pyObjType, false)) {
        PyErr_Format(PyExc_TypeError,
                     "%s can only be used with classes inherited from QObject, got %s.",
                     decoratorName, pyObjType->tp_name);
        return nullptr;
    }

    if (!setClassInfo(pyObjType, qmlElementKey, typeName))
        return nullptr;

    RegisterMode mode = RegisterMode::Normal;
    const auto info = PySide::Qml::qmlTypeInfo(pyObj);
    auto *registerObject = pyObj;
    if (info) {
        if (info->flags.testFlag(PySide::Qml::QmlTypeFlag::Singleton)) {
            mode = RegisterMode::Singleton;
            setSingletonClassInfo(pyObjType);
        }
        if (info->foreignType)
            registerObject = reinterpret_cast<PyObject *>(info->foreignType);
    }

    const auto importDataO = getGlobalImportData(decoratorName);
    if (!importDataO.has_value())
        return nullptr;
    const auto importData = importDataO.value();

    int result{};
    if (mode == RegisterMode::Singleton) {
        auto singletonCreateMethodO = singletonCreateMethod(pyObjType);
        if (!singletonCreateMethodO.has_value()) {
            if (PyErr_Occurred() != nullptr)
                return nullptr;
            singletonCreateMethodO = SingletonQObjectFromTypeCreation(pyObj);
        }
        result = PySide::Qml::qmlRegisterSingletonTypeV2(registerObject, pyObj, importData,
                                                         singletonCreateMethodO.value());
    } else {
        result = PySide::Qml::qmlRegisterType(registerObject, pyObj, importData);
    }
    if (result == -1) {
        PyErr_Format(PyExc_TypeError, "%s: Failed to register type %s.",
                     decoratorName, pyObjType->tp_name);
        return nullptr;
    }

    return pyObj;
}

PyObject *qmlElementMacro(PyObject *pyObj)
{
    return qmlElementMacro(pyObj, "QmlElement", "auto"_ba);
}

PyObject *qmlNamedElementMacro(PyObject *pyObj, const QByteArray &typeName)
{
    return qmlElementMacro(pyObj, "QmlNamedElement", typeName);
}

PyObject *qmlAnonymousMacro(PyObject *pyObj)
{
    return qmlElementMacro(pyObj, "QmlAnonymous",  "anonymous"_ba);
}

PyObject *qmlSingletonMacro(PyObject *pyObj)
{
    PySide::Qml::ensureQmlTypeInfo(pyObj)->flags.setFlag(PySide::Qml::QmlTypeFlag::Singleton);
    Py_INCREF(pyObj);
    return pyObj;
}

QuickRegisterItemFunction getQuickRegisterItemFunction()
{
    return quickRegisterItemFunction;
}

void setQuickRegisterItemFunction(QuickRegisterItemFunction function)
{
    quickRegisterItemFunction = function;
}

} // namespace PySide::Qml
