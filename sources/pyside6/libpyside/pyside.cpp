// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pyside.h"
#include "pysideinit.h"
#include "pysidecleanup.h"
#include "pysidemetatype.h"
#include "pysideqapp.h"
#include "pysideqobject.h"
#include "pysideutils.h"
#include "pyside_p.h"
#include "signalmanager.h"
#include "pysideclassinfo_p.h"
#include "pysideproperty_p.h"
#include "class_property.h"
#include "pysideproperty.h"
#include "pysidesignal.h"
#include "pysidesignal_p.h"
#include "pysidestaticstrings.h"
#include "pysideslot_p.h"
#include "pysidemetafunction_p.h"
#include "pysidemetafunction.h"
#include "dynamicqmetaobject.h"
#include "feature_select.h"
#include "pysidelogging_p.h"

#include <autodecref.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <gilstate.h>
#include <sbkconverter.h>
#include <sbkstring.h>
#include <sbkstaticstrings.h>
#include <sbkfeature_base.h>

#include <QtCore/QByteArray>
#include <QtCore/QCoreApplication>
#include <QtCore/QDir>
#include <QtCore/QFileInfo>
#include <QtCore/QMetaMethod>
#include <QtCore/QMutex>
#include <QtCore/QStack>
#include <QtCore/QThread>

#include <algorithm>
#include <cstring>
#include <cctype>
#include <memory>
#include <optional>
#include <typeinfo>

using namespace Qt::StringLiterals;

static QStack<PySide::CleanupFunction> cleanupFunctionList;
static void *qobjectNextAddr;

QT_BEGIN_NAMESPACE
extern bool qRegisterResourceData(int, const unsigned char *, const unsigned char *,
        const unsigned char *);
QT_END_NAMESPACE

Q_LOGGING_CATEGORY(lcPySide, "qt.pyside.libpyside", QtCriticalMsg)

namespace PySide
{

void init(PyObject *module)
{
    qobjectNextAddr = nullptr;
    ClassInfo::init(module);
    Signal::init(module);
    Slot::init(module);
    Property::init(module);
    ClassProperty::init(module);
    MetaFunction::init(module);
    // Init signal manager, so it will register some meta types used by QVariant.
    SignalManager::instance();
    initQApp();
}

static const QByteArray _sigWithMangledName(const QByteArray &signature, bool mangle)
{
    if (!mangle)
        return signature;
    auto bracePos = signature.indexOf('(');
    auto limit = bracePos >= 0 ? bracePos : signature.size();
    if (limit < 3)
        return signature;
    QByteArray result;
    result.reserve(signature.size() + 4);
    for (auto i = 0; i < limit; ++i) {
        const char c = signature.at(i);
        if (std::isupper(c)) {
            if (i > 0) {
                if (std::isupper(signature.at(i - 1)))
                    return signature; // Give up at consecutive upper chars
                 result.append('_');
            }
            result.append(std::tolower(c));
        } else {
            result.append(c);
        }
    }
    // Copy the rest after the opening brace (if any)
    result.append(signature.mid(limit));
    return result;
}

static const QByteArray _sigWithOrigName(const QByteArray &signature, bool mangle)
{
    if (!mangle)
        return signature;
    auto bracePos = signature.indexOf('(');
    auto limit = bracePos >= 0 ? bracePos : signature.size();
    QByteArray result;
    result.reserve(signature.size());
    for (auto i = 0; i < limit; ++i) {
        const char c = signature.at(i);
        if (std::isupper(c)) {
            if (i > 0) {
                if (std::isupper(signature.at(i - 1)))
                    return signature;       // Give up at consecutive upper chars
                return QByteArray{};        // Error, this was not converted!
            }
        }
        if (std::islower(c) && i > 0 && signature.at(i - 1) == '_') {
            result.chop(1);
            result.append(std::toupper(c));
        } else {
            result.append(c);
        }
    }
    // Copy the rest after the opening brace (if any)
    result.append(signature.mid(limit));
    return result;
}

/*****************************************************************************
 *
 * How do we find a property?
 * --------------------------
 *
 * There are methods which are truly parts of properties, and there are
 * other property-like methods which are not. True properties can be
 * found by inspecting `SbkObjectType_GetPropertyStrings(type)`.
 *
 * Pseudo-properties have only a getter and a setter, and we must assume that
 * the name of the getter is the property name, and the name of the setter
 * is the uppercase of the getter with "set" prepended.
 *
 * We first walk the mro and search the property name and get the setter
 * name. If that doesn't work, we use the heuristics for the setter.
 * We then do the final mro lookup.
 *
 * Note that the true property lists have the original names, while the
 * dict entries in the mro are already mangled.
 */

static const QByteArrayList parseFields(const char *propStr, int flags, bool *stdWrite)
{
    /*
     * Break the string into subfields at ':' and add defaults.
     */
    if (stdWrite)
        *stdWrite = true;
    QByteArray s = QByteArray(propStr);
    auto list = s.split(':');
    assert(list.size() == 2 || list.size() == 3);
    auto name = list[0];
    auto read = list[1];
    if (read.isEmpty())
        list[1] = name;
    if (list.size() == 2)
        return list;
    auto write = list[2];
    if (stdWrite)
        *stdWrite = write.isEmpty();
    if (write.isEmpty()) {
        auto snake_flag = flags & 0x01;
        if (snake_flag) {
            list[2] = ("set_") + name;
        } else {
            list[2] = QByteArray("set") + name;
            list[2][3] = std::toupper(list[2][3]);
        }
    }
    return list;
}

static QByteArrayList _SbkType_LookupProperty(PyTypeObject *type,
                                              const QByteArray &name, int flags)
{
    /*
     * Looks up a property and returns all fields.
     */
    int snake_flag = flags & 0x01;
    QByteArray origName(_sigWithOrigName(name, snake_flag));
    if (origName.isEmpty())
        return QByteArrayList{};
    PyObject *mro = type->tp_mro;
    auto n = PyTuple_GET_SIZE(mro);
    auto len = std::strlen(origName);
    for (Py_ssize_t idx = 0; idx < n; idx++) {
        PyTypeObject *base = reinterpret_cast<PyTypeObject *>(PyTuple_GET_ITEM(mro, idx));
        auto props = SbkObjectType_GetPropertyStrings(base);
        if (props == nullptr || *props == nullptr)
            continue;
        for (; *props != nullptr; ++props) {
            QByteArray propStr(*props);
            if (std::strncmp(propStr, origName, len) == 0) {
                if (propStr[len] != ':')
                    continue;
                // We found the property. Return the parsed fields.
                propStr = _sigWithMangledName(propStr, snake_flag);
                return parseFields(propStr, flags, nullptr);
            }
        }
    }
    return QByteArrayList{};
}

static QByteArrayList _SbkType_FakeProperty(const QByteArray &name, int flags)
{
    /*
     * Handle a pseudo.property and return all fields.
     */
    int snake_flag = flags & 0x01;
    QByteArray propStr(name);
    propStr += "::";
    propStr = _sigWithMangledName(propStr, snake_flag);
    return parseFields(propStr, snake_flag, nullptr);
}

static bool _setProperty(PyObject *qObj, PyObject *name, PyObject *value, bool *accept)
{
    using Shiboken::AutoDecRef;

    QByteArray propName(Shiboken::String::toCString(name));
    auto type = Py_TYPE(qObj);
    int flags = currentSelectId(type);
    int prop_flag = flags & 0x02;
    auto found = false;
    QByteArray getterName{}, setterName{};

    auto fields = _SbkType_LookupProperty(type, propName, flags);
    if (!fields.isEmpty()) {
        found = true;
        bool haveWrite = fields.size() == 3;
        if (!haveWrite)
            return false;
    } else {
        fields = _SbkType_FakeProperty(propName, flags);
    }

    propName = fields[0];
    getterName = fields[1];
    setterName = fields[2];

    // PYSIDE-1702: We do not use getattr, since that could trigger an action
    //              if we have a true property. Better to look inside the mro.
    //              That should return a descriptor or a property.
    PyObject *look{};

    if (found && prop_flag) {
        // We have a property, and true_property is active.
        // There must be a property object and we use it's fset.
        AutoDecRef pyPropName(Shiboken::String::fromCString(propName.constData()));
        look = _PepType_Lookup(Py_TYPE(qObj), pyPropName);
    } else {
        // We have a pseudo property or true_property is off, looking for a setter.
        AutoDecRef pySetterName(Shiboken::String::fromCString(setterName.constData()));
        look = _PepType_Lookup(Py_TYPE(qObj), pySetterName);
    }

    if (look) {
        AutoDecRef propSetter{};
        static PyObject *magicGet = Shiboken::PyMagicName::get();
        if (found && prop_flag) {
            // the indirection of the setter descriptor in a true property
            AutoDecRef descr(PyObject_GetAttr(look, PySideName::fset()));
            propSetter.reset(PyObject_CallMethodObjArgs(descr, magicGet, qObj, nullptr));
        } else {
            // look is already the descriptor
            propSetter.reset(PyObject_CallMethodObjArgs(look, magicGet, qObj, nullptr));
        }
        *accept = true;
        AutoDecRef args(PyTuple_Pack(1, value));
        AutoDecRef retval(PyObject_CallObject(propSetter, args));
        if (retval.isNull())
            return false;
    } else {
        PyErr_Clear();
        AutoDecRef attr(PyObject_GenericGetAttr(qObj, name));
        if (PySide::Property::checkType(attr)) {
            *accept = true;
            if (PySide::Property::setValue(reinterpret_cast<PySideProperty *>(
                    attr.object()), qObj, value) < 0)
                return false;
        }
    }
    return true;
}

// PYSIDE-2329: Search a signal by name (Note: QMetaObject::indexOfSignal()
// searches by signature).
static std::optional<QMetaMethod> findSignal(const QMetaObject *mo,
                                             const QByteArray &name)
{
    const auto count = mo->methodCount();
    for (int i = mo->methodOffset(); i < count; ++i) {
        const auto method = mo->method(i);
        if (method.methodType() == QMetaMethod::Signal && method.name() == name)
            return method;
    }
    auto *base = mo->superClass();
    return base != nullptr ? findSignal(base, name) : std::nullopt;
}

bool fillQtProperties(PyObject *qObj, const QMetaObject *metaObj,
                      PyObject *kwds, bool allowErrors)
{

    PyObject *key, *value;
    Py_ssize_t pos = 0;
    int flags = currentSelectId(Py_TYPE(qObj));
    int snake_flag = flags & 0x01;

    while (PyDict_Next(kwds, &pos, &key, &value)) {
        const QByteArray propName = Shiboken::String::toCString(key);
        QByteArray unmangledName = _sigWithOrigName(propName, snake_flag);
        bool accept = false;
        // PYSIDE-1705: Make sure that un-mangled names are not recognized in snake_case mode.
        if (!unmangledName.isEmpty()) {
            if (metaObj->indexOfProperty(unmangledName) != -1) {
                if (!_setProperty(qObj, key, value, &accept))
                    return false;
            } else {
                const auto methodO = findSignal(metaObj, propName);
                if (methodO.has_value()) {
                    const auto signature = "2"_ba + methodO->methodSignature();
                    accept = true;
                    if (!PySide::Signal::connect(qObj, signature, value))
                        return false;
                }
            }
            if (!accept) {
                // PYSIDE-1019: Allow any existing attribute in the constructor.
                if (!_setProperty(qObj, key, value, &accept))
                    return false;
            }
        }
        if (allowErrors) {
            PyErr_Clear();
            continue;
        }
        if (!accept) {
            PyErr_Format(PyExc_AttributeError, "'%s' is not a Qt property or a signal",
                         propName.constData());
            return false;
        }
    }
    return true;
}

void registerCleanupFunction(CleanupFunction func)
{
    cleanupFunctionList.push(func);
}

void runCleanupFunctions()
{
    while (!cleanupFunctionList.isEmpty()) {
        CleanupFunction f = cleanupFunctionList.pop();
        f();
    }
}

static void destructionVisitor(SbkObject *pyObj, void *data)
{
    auto realData = reinterpret_cast<void **>(data);
    auto pyQApp = reinterpret_cast<SbkObject *>(realData[0]);
    auto pyQObjectType = reinterpret_cast<PyTypeObject *>(realData[1]);

    if (pyObj != pyQApp && PyObject_TypeCheck(pyObj, pyQObjectType)) {
        if (Shiboken::Object::hasOwnership(pyObj) && Shiboken::Object::isValid(pyObj, false)) {
            Shiboken::Object::setValidCpp(pyObj, false);

            Py_BEGIN_ALLOW_THREADS
            Shiboken::callCppDestructor<QObject>(Shiboken::Object::cppPointer(pyObj, pyQObjectType));
            Py_END_ALLOW_THREADS
        }
    }

};

void destroyQCoreApplication()
{
    QCoreApplication *app = QCoreApplication::instance();
    if (!app)
        return;
    SignalManager::instance().clear();

    Shiboken::BindingManager &bm = Shiboken::BindingManager::instance();
    SbkObject *pyQApp = bm.retrieveWrapper(app);
    PyTypeObject *pyQObjectType = Shiboken::Conversions::getPythonTypeObject("QObject*");
    assert(pyQObjectType);

    void *data[2] = {pyQApp, pyQObjectType};
    bm.visitAllPyObjects(&destructionVisitor, &data);

    // in the end destroy app
    // Allow threads because the destructor calls
    // QThreadPool::globalInstance().waitForDone() which may deadlock on the GIL
    // if there is a worker working with python objects.
    Py_BEGIN_ALLOW_THREADS
    delete app;
    Py_END_ALLOW_THREADS
    // PYSIDE-571: make sure to create a singleton deleted qApp.
    Py_DECREF(MakeQAppWrapper(nullptr));
}

std::size_t getSizeOfQObject(PyTypeObject *type)
{
    return retrieveTypeUserData(type)->cppObjSize;
}

void initDynamicMetaObject(PyTypeObject *type, const QMetaObject *base, std::size_t cppObjSize)
{
    //create DynamicMetaObject based on python type
    auto userData = new TypeUserData(reinterpret_cast<PyTypeObject *>(type), base, cppObjSize);
    userData->mo.update();
    Shiboken::ObjectType::setTypeUserData(type, userData, Shiboken::callCppDestructor<TypeUserData>);

    //initialize staticQMetaObject property
    void *metaObjectPtr = const_cast<QMetaObject *>(userData->mo.update());
    static SbkConverter *converter = Shiboken::Conversions::getConverter("QMetaObject");
    if (!converter)
        return;
    Shiboken::AutoDecRef pyMetaObject(Shiboken::Conversions::pointerToPython(converter, metaObjectPtr));
    PyObject_SetAttr(reinterpret_cast<PyObject *>(type),
                     Shiboken::PyName::qtStaticMetaObject(), pyMetaObject);
}

TypeUserData *retrieveTypeUserData(PyTypeObject *pyTypeObj)
{
    return reinterpret_cast<TypeUserData *>(Shiboken::ObjectType::getTypeUserData(pyTypeObj));
}

TypeUserData *retrieveTypeUserData(PyObject *pyObj)
{
    auto pyTypeObj = PyType_Check(pyObj)
        ? reinterpret_cast<PyTypeObject *>(pyObj) : Py_TYPE(pyObj);
    return retrieveTypeUserData(pyTypeObj);
}

const QMetaObject *retrieveMetaObject(PyTypeObject *pyTypeObj)
{
    TypeUserData *userData = retrieveTypeUserData(pyTypeObj);
    return userData ? userData->mo.update() : nullptr;
}

const QMetaObject *retrieveMetaObject(PyObject *pyObj)
{
    auto pyTypeObj = PyType_Check(pyObj)
        ? reinterpret_cast<PyTypeObject *>(pyObj) : Py_TYPE(pyObj);
    return retrieveMetaObject(pyTypeObj);
}

void initQObjectSubType(PyTypeObject *type, PyObject *args, PyObject * /* kwds */)
{
    PyTypeObject *qObjType = Shiboken::Conversions::getPythonTypeObject("QObject*");
    QByteArray className(Shiboken::String::toCString(PyTuple_GET_ITEM(args, 0)));

    PyObject *bases = PyTuple_GET_ITEM(args, 1);
    int numBases = PyTuple_GET_SIZE(bases);

    TypeUserData *userData = nullptr;

    for (int i = 0; i < numBases; ++i) {
        auto base = reinterpret_cast<PyTypeObject *>(PyTuple_GET_ITEM(bases, i));
        if (PyType_IsSubtype(base, qObjType)) {
            userData = retrieveTypeUserData(base);
            break;
        }
    }
    if (!userData) {
        qWarning("Sub class of QObject not inheriting QObject!? Crash will happen when using %s.", className.constData());
        return;
    }
    // PYSIDE-1463: Don't change feature selection durin subtype initialization.
    // This behavior is observed with PySide 6.
    PySide::Feature::Enable(false);
    initDynamicMetaObject(type, userData->mo.update(), userData->cppObjSize);
    PySide::Feature::Enable(true);
}

void initQApp()
{
    /*
     * qApp will not be initialized when embedding is active.
     * That means that qApp exists already when PySide is initialized.
     * We could solve that by creating a qApp variable, but in embedded
     * mode, we also have the effect that the first assignment to qApp
     * is persistent! Therefore, we can never be sure to have created
     * qApp late enough to get the right type for the instance.
     *
     * I would appreciate very much if someone could explain or even fix
     * this issue. It exists only when a pre-existing application exists.
     */
    if (!qApp)
        Py_DECREF(MakeQAppWrapper(nullptr));

    // PYSIDE-1470: Register a function to destroy an application from shiboken.
    setDestroyQApplication(destroyQCoreApplication);
}

PyObject *getHiddenDataFromQObject(QObject *cppSelf, PyObject *self, PyObject *name)
{
    using Shiboken::AutoDecRef;

    // PYSIDE-68-bis: This getattr finds signals early by `signalDescrGet`.
    PyObject *attr = PyObject_GenericGetAttr(self, name);
    if (!Shiboken::Object::isValid(reinterpret_cast<SbkObject *>(self), false))
        return attr;

    if (attr && Property::checkType(attr)) {
        PyObject *value = Property::getValue(reinterpret_cast<PySideProperty *>(attr), self);
        Py_DECREF(attr);
        if (!value)
            return nullptr;
        attr = value;
    }

    // Search on metaobject (avoid internal attributes started with '__')
    if (!attr) {
        PyObject *type, *value, *traceback;
        PyErr_Fetch(&type, &value, &traceback);     // This was omitted for a loong time.

        int flags = currentSelectId(Py_TYPE(self));
        int snake_flag = flags & 0x01;
        int propFlag = flags & 0x02;

        if (propFlag) {
            // PYSIDE-1889: If we have actually a Python property, return f(get|set|del).
            //              Do not store this attribute in the instance dict, because this
            //              would create confusion with overload.
            // Note: before implementing this property handling, the meta function code
            // below created meta functions which was quite wrong.
            auto *subdict = _PepType_Lookup(Py_TYPE(self), PySideMagicName::property_methods());
            PyObject *propName = PyDict_GetItem(subdict, name);
            if (propName) {
                // We really have a property name and need to fetch the fget or fset function.
                static PyObject *const _fget = Shiboken::String::createStaticString("fget");
                static PyObject *const _fset = Shiboken::String::createStaticString("fset");
                static PyObject *const _fdel = Shiboken::String::createStaticString("fdel");
                static PyObject *const arr[3] = {_fget, _fset, _fdel};
                auto prop = _PepType_Lookup(Py_TYPE(self), propName);
                for (int idx = 0; idx < 3; ++idx) {
                    auto *trial = arr[idx];
                    auto *res = PyObject_GetAttr(prop, trial);
                    if (res) {
                        AutoDecRef elemName(PyObject_GetAttr(res, PySideMagicName::name()));
                        // Note: This comparison works because of interned strings.
                        if (elemName == name)
                            return res;
                        Py_DECREF(res);
                    }
                    PyErr_Clear();
                }
            }
        }

        const char *cname = Shiboken::String::toCString(name);
        uint cnameLen = qstrlen(cname);
        if (std::strncmp("__", cname, 2)) {
            const QMetaObject *metaObject = cppSelf->metaObject();
            QList<QMetaMethod> signalList;
            // Caution: This inserts a meta function or a signal into the instance dict.
            for (int i=0, imax = metaObject->methodCount(); i < imax; i++) {
                QMetaMethod method = metaObject->method(i);
                // PYSIDE-1753: Snake case names must be renamed here too, or they will be
                // found unexpectedly when forgetting to rename them.
                auto origSignature = method.methodSignature();
                // Currently, we rename only methods but no signals. This might change.
                bool use_lower = snake_flag and method.methodType() != QMetaMethod::Signal;
                const QByteArray methSig_ = _sigWithMangledName(origSignature, use_lower);
                const char *methSig = methSig_.constData();
                bool methMatch = std::strncmp(cname, methSig, cnameLen) == 0
                                 && methSig[cnameLen] == '(';
                if (methMatch) {
                    if (method.methodType() == QMetaMethod::Signal) {
                        signalList.append(method);
                    } else {
                        PySideMetaFunction *func = MetaFunction::newObject(cppSelf, i);
                        if (func) {
                            PyObject *result = reinterpret_cast<PyObject *>(func);
                            PyObject_SetAttr(self, name, result);
                            return result;
                        }
                    }
                }
            }
            if (!signalList.isEmpty()) {
                PyObject *pySignal = reinterpret_cast<PyObject *>(
                    Signal::newObjectFromMethod(self, signalList));
                PyObject_SetAttr(self, name, pySignal);
                return pySignal;
            }
        }
        PyErr_Restore(type, value, traceback);
    }
    return attr;
}

bool inherits(PyTypeObject *objType, const char *class_name)
{
    if (strcmp(objType->tp_name, class_name) == 0)
        return true;

    PyTypeObject *base = objType->tp_base;
    if (base == nullptr)
        return false;

    return inherits(base, class_name);
}

QMutex &nextQObjectMemoryAddrMutex()
{
    static QMutex mutex;
    return mutex;
}

void *nextQObjectMemoryAddr()
{
    return qobjectNextAddr;
}

void setNextQObjectMemoryAddr(void *addr)
{
    qobjectNextAddr = addr;
}

} // namespace PySide

// A std::shared_ptr is used with a deletion function to invalidate a pointer
// when the property value is cleared.  This should be a QSharedPointer with
// a void *pointer, but that isn't allowed
typedef char any_t;
Q_DECLARE_METATYPE(std::shared_ptr<any_t>);


namespace PySide
{

static void invalidatePtr(any_t *object)
{
    // PYSIDE-2254: Guard against QObjects outliving Python, for example the
    // adopted main thread as returned by QObjects::thread().
    if (Py_IsInitialized() == 0)
        return;

    Shiboken::GilState state;

    SbkObject *wrapper = Shiboken::BindingManager::instance().retrieveWrapper(object);
    if (wrapper != nullptr)
        Shiboken::BindingManager::instance().releaseWrapper(wrapper);
}

static const char invalidatePropertyName[] = "_PySideInvalidatePtr";

// PYSIDE-1214, when creating new wrappers for classes inheriting QObject but
// not exposed to Python, try to find the best-matching (most-derived) Qt
// class by walking up the meta objects.
static const char *typeName(const QObject *cppSelf)
{
    const char *typeName = typeid(*cppSelf).name();
    if (!Shiboken::Conversions::getConverter(typeName)) {
        for (auto metaObject = cppSelf->metaObject(); metaObject; metaObject = metaObject->superClass()) {
            const char *name = metaObject->className();
            if (Shiboken::Conversions::getConverter(name)) {
                typeName = name;
                break;
            }
        }
    }
    return typeName;
}

PyTypeObject *getTypeForQObject(const QObject *cppSelf)
{
    // First check if there are any instances of Python implementations
    // inheriting a PySide class.
    auto *existing = Shiboken::BindingManager::instance().retrieveWrapper(cppSelf);
    if (existing != nullptr)
        return reinterpret_cast<PyObject *>(existing)->ob_type;
    // Find the best match (will return a PySide type)
    auto *sbkObjectType = Shiboken::ObjectType::typeForTypeName(typeName(cppSelf));
    if (sbkObjectType != nullptr)
        return reinterpret_cast<PyTypeObject *>(sbkObjectType);
    return nullptr;
}

PyObject *getWrapperForQObject(QObject *cppSelf, PyTypeObject *sbk_type)
{
    PyObject *pyOut = reinterpret_cast<PyObject *>(Shiboken::BindingManager::instance().retrieveWrapper(cppSelf));
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }

    // Setting the property will trigger an QEvent notification, which may call into
    // code that creates the wrapper so only set the property if it isn't already
    // set and check if it's created after the set call
    QVariant existing = cppSelf->property(invalidatePropertyName);
    if (!existing.isValid()) {
        if (cppSelf->thread() == QThread::currentThread()) {
            std::shared_ptr<any_t> shared_with_del(reinterpret_cast<any_t *>(cppSelf), invalidatePtr);
            cppSelf->setProperty(invalidatePropertyName, QVariant::fromValue(shared_with_del));
        }
        pyOut = reinterpret_cast<PyObject *>(Shiboken::BindingManager::instance().retrieveWrapper(cppSelf));
        if (pyOut) {
            Py_INCREF(pyOut);
            return pyOut;
        }
    }

    pyOut = Shiboken::Object::newObject(sbk_type, cppSelf, false, false, typeName(cppSelf));

    return pyOut;
}

QString pyUnicodeToQString(PyObject *str)
{
    Q_ASSERT(PyUnicode_Check(str) != 0);

    const void *data = _PepUnicode_DATA(str);
    const Py_ssize_t len = PyUnicode_GetLength(str);
    switch (_PepUnicode_KIND(str)) {
    case PepUnicode_1BYTE_KIND:
        return QString::fromLatin1(reinterpret_cast<const char *>(data), len);
    case PepUnicode_2BYTE_KIND:
        return QString::fromUtf16(reinterpret_cast<const char16_t *>(data), len);
    case PepUnicode_4BYTE_KIND:
        break;
    }
    return QString::fromUcs4(reinterpret_cast<const char32_t *>(data), len);
}

PyObject *qStringToPyUnicode(QStringView s)
{
    const QByteArray ba = s.toUtf8();
    return PyUnicode_FromStringAndSize(ba.constData(), ba.size());
}

// Inspired by Shiboken::String::toCString;
QString pyStringToQString(PyObject *str)
{
    if (str == Py_None)
        return QString();

    if (PyUnicode_Check(str) != 0)
        return pyUnicodeToQString(str);

    if (PyBytes_Check(str)) {
        const char *asciiBuffer = PyBytes_AS_STRING(str);
        if (asciiBuffer)
            return QString::fromLatin1(asciiBuffer);
    }
    return QString();
}

// PySide-1499: Provide an efficient, correct PathLike interface
QString pyPathToQString(PyObject *path)
{
    // For empty constructors path can be nullptr
    // fallback to an empty QString in that case.
    if (!path)
        return QString();

    // str or bytes pass through
    if (PyUnicode_Check(path) || PyBytes_Check(path))
        return pyStringToQString(path);

    // Let PyOS_FSPath do its work and then fix the result for Windows.
    Shiboken::AutoDecRef strPath(PyOS_FSPath(path));
    if (strPath.isNull())
        return QString();
    return QDir::fromNativeSeparators(pyStringToQString(strPath));
}

bool isCompiledMethod(PyObject *callback)
{
    return PyObject_HasAttr(callback, PySide::PySideName::im_func())
           && PyObject_HasAttr(callback, PySide::PySideName::im_self())
           && PyObject_HasAttr(callback, PySide::PySideMagicName::code());
}

static const unsigned char qt_resource_name[] = {
  // qt
  0x0,0x2,
  0x0,0x0,0x7,0x84,
  0x0,0x71,
  0x0,0x74,
    // etc
  0x0,0x3,
  0x0,0x0,0x6c,0xa3,
  0x0,0x65,
  0x0,0x74,0x0,0x63,
    // qt.conf
  0x0,0x7,
  0x8,0x74,0xa6,0xa6,
  0x0,0x71,
  0x0,0x74,0x0,0x2e,0x0,0x63,0x0,0x6f,0x0,0x6e,0x0,0x66
};

static const unsigned char qt_resource_struct[] = {
  // :
  0x0,0x0,0x0,0x0,0x0,0x2,0x0,0x0,0x0,0x1,0x0,0x0,0x0,0x1,
  // :/qt
  0x0,0x0,0x0,0x0,0x0,0x2,0x0,0x0,0x0,0x1,0x0,0x0,0x0,0x2,
  // :/qt/etc
  0x0,0x0,0x0,0xa,0x0,0x2,0x0,0x0,0x0,0x1,0x0,0x0,0x0,0x3,
  // :/qt/etc/qt.conf
  0x0,0x0,0x0,0x16,0x0,0x0,0x0,0x0,0x0,0x1,0x0,0x0,0x0,0x0
};

bool registerInternalQtConf()
{
    // Guard to ensure single registration.
#ifdef PYSIDE_QT_CONF_PREFIX
    static bool registrationAttempted = false;
#else
    static bool registrationAttempted = true;
#endif
    static bool isRegistered = false;
    if (registrationAttempted)
        return isRegistered;
    registrationAttempted = true;

    // Support PyInstaller case when a qt.conf file might be provided next to the generated
    // PyInstaller executable.
    // This will disable the internal qt.conf which points to the PySide6 subdirectory (due to the
    // subdirectory not existing anymore).
#ifndef PYPY_VERSION
    QString executablePath = QString::fromWCharArray(Py_GetProgramFullPath());
#else
    // PYSIDE-535: FIXME: Add this function when available.
    QString executablePath = QLatin1String("missing Py_GetProgramFullPath");
#endif // PYPY_VERSION

    QString appDirPath = QFileInfo(executablePath).absolutePath();

    QString maybeQtConfPath = QDir(appDirPath).filePath(u"qt.conf"_s);
    maybeQtConfPath = QDir::toNativeSeparators(maybeQtConfPath);
    bool executableQtConfAvailable = QFileInfo::exists(maybeQtConfPath);

    QString maybeQt6ConfPath = QDir(appDirPath).filePath(u"qt6.conf"_s);
    maybeQt6ConfPath = QDir::toNativeSeparators(maybeQt6ConfPath);
    bool executableQt6ConfAvailable = QFileInfo::exists(maybeQt6ConfPath);

    // Allow disabling the usage of the internal qt.conf. This is necessary for tests to work,
    // because tests are executed before the package is installed, and thus the Prefix specified
    // in qt.conf would point to a not yet existing location.
    bool disableInternalQtConf =
        qEnvironmentVariableIntValue("PYSIDE_DISABLE_INTERNAL_QT_CONF") > 0;
    bool runsInConda =
        qEnvironmentVariableIsSet("CONDA_DEFAULT_ENV") || qEnvironmentVariableIsSet("CONDA_PREFIX");

    if ((!runsInConda && (disableInternalQtConf || executableQtConfAvailable))
        || (runsInConda && executableQt6ConfAvailable)) {
        registrationAttempted = true;
        return false;
    }

    PyObject *pysideModule = PyImport_ImportModule("PySide6");
    if (!pysideModule)
        return false;

    // Querying __file__ should be done only for modules that have finished their initialization.
    // Thus querying for the top-level PySide6 package works for us whenever any Qt-wrapped module
    // is loaded.
    PyObject *pysideInitFilePath = PyObject_GetAttr(pysideModule, Shiboken::PyMagicName::file());
    Py_DECREF(pysideModule);
    if (!pysideInitFilePath)
        return false;

    QString initPath = pyStringToQString(pysideInitFilePath);
    Py_DECREF(pysideInitFilePath);
    if (initPath.isEmpty())
        return false;

    // pysideDir - absolute path to the directory containing the init file, which also contains
    // the rest of the PySide6 modules.
    // prefixPath - absolute path to the directory containing the installed Qt (prefix).
    QDir pysideDir = QFileInfo(QDir::fromNativeSeparators(initPath)).absoluteDir();
    QString setupPrefix;
#ifdef PYSIDE_QT_CONF_PREFIX
    setupPrefix = QStringLiteral(PYSIDE_QT_CONF_PREFIX);
#endif
    const QByteArray prefixPath = pysideDir.absoluteFilePath(setupPrefix).toUtf8();

    // rccData needs to be static, otherwise when it goes out of scope, the Qt resource system
    // will point to invalid memory.
    static QByteArray rccData = QByteArrayLiteral("[Paths]\nPrefix = ") + prefixPath + "\n";
#ifdef Q_OS_WIN
    // LibraryExecutables needs to point to Prefix instead of ./bin because we don't
    // currently conform to the Qt default directory layout on Windows. This is necessary
    // for QtWebEngineCore to find the location of QtWebEngineProcess.exe.
    rccData += QByteArrayLiteral("LibraryExecutables = ") + prefixPath + "\n";
#endif

    // The RCC data structure expects a 4-byte size value representing the actual data.
    qsizetype size = rccData.size();

    for (int i = 0; i < 4; ++i) {
        rccData.prepend((size & 0xff));
        size >>= 8;
    }

    const int version = 0x01;
    isRegistered = qRegisterResourceData(version, qt_resource_struct, qt_resource_name,
                                         reinterpret_cast<const unsigned char *>(
                                             rccData.constData()));

    return isRegistered;
}

static PyTypeObject *qobjectType()
{
    static PyTypeObject * const result = Shiboken::Conversions::getPythonTypeObject("QObject*");
    return result;
}

bool isQObjectDerived(PyTypeObject *pyType, bool raiseError)
{
    const bool result = PyType_IsSubtype(pyType, qobjectType());
    if (!result && raiseError) {
        PyErr_Format(PyExc_TypeError, "A type inherited from %s expected, got %s.",
                     qobjectType()->tp_name, pyType->tp_name);
    }
    return result;
}

QObject *convertToQObject(PyObject *object, bool raiseError)
{
    if (object == nullptr) {
        if (raiseError)
            PyErr_Format(PyExc_TypeError, "None passed for QObject");
        return nullptr;
    }

    if (!isQObjectDerived(Py_TYPE(object), raiseError))
        return nullptr;

    auto *sbkObject = reinterpret_cast<SbkObject*>(object);
    auto *ptr = Shiboken::Object::cppPointer(sbkObject, qobjectType());
    if (ptr == nullptr) {
        if (raiseError) {
            PyErr_Format(PyExc_TypeError, "Conversion of %s to QObject failed.",
                         Py_TYPE(object)->tp_name);
        }
        return nullptr;
    }
    return reinterpret_cast<QObject*>(ptr);
}

QMetaType qMetaTypeFromPyType(PyTypeObject *pyType)
{
    if (Shiboken::String::checkType(pyType))
        return QMetaType(QMetaType::QString);
    if (pyType == &PyFloat_Type)
        return QMetaType(QMetaType::Double);
    if (pyType == &PyLong_Type)
        return QMetaType(QMetaType::Int);
    if (Shiboken::ObjectType::checkType(pyType))
        return QMetaType::fromName(Shiboken::ObjectType::getOriginalName(pyType));
    return QMetaType::fromName(pyType->tp_name);
}

} //namespace PySide

