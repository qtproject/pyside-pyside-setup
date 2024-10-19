// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "signalmanager.h"
#include "pysidesignal.h"
#include "pysidelogging_p.h"
#include "pysideproperty.h"
#include "pysideproperty_p.h"
#include "pyside_p.h"
#include "dynamicqmetaobject.h"
#include "pysidemetafunction_p.h"

#include <autodecref.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <gilstate.h>
#include <sbkconverter.h>
#include <sbkstring.h>
#include <sbkstaticstrings.h>
#include <sbkerrors.h>

#include <QtCore/QCoreApplication>
#include <QtCore/QByteArrayView>
#include <QtCore/QDebug>
#include <QtCore/QHash>
#include <QtCore/QScopedPointer>
#include <QtCore/QTimerEvent>

#include <memory>

using namespace Qt::StringLiterals;

#if QSLOT_CODE != 1 || QSIGNAL_CODE != 2
#error QSLOT_CODE and/or QSIGNAL_CODE changed! change the hardcoded stuff to the correct value!
#endif

static PyObject *metaObjectAttr = nullptr;

static void destroyMetaObject(PyObject *obj)
{
    void *ptr = PyCapsule_GetPointer(obj, nullptr);
    auto *meta = reinterpret_cast<PySide::MetaObjectBuilder *>(ptr);
    SbkObject *wrapper = Shiboken::BindingManager::instance().retrieveWrapper(meta);
    if (wrapper)
        Shiboken::BindingManager::instance().releaseWrapper(wrapper);
    delete meta;
}

static const char *metaCallName(QMetaObject::Call call)
{
    static const QHash<QMetaObject::Call, const char *> mapping = {
        {QMetaObject::InvokeMetaMethod, "InvokeMetaMethod"},
        {QMetaObject::ReadProperty, "ReadProperty"},
        {QMetaObject::WriteProperty, "WriteProperty"},
        {QMetaObject::ResetProperty, "ResetProperty"},
        {QMetaObject::CreateInstance, "CreateInstance"},
        {QMetaObject::IndexOfMethod, "IndexOfMethod"},
        {QMetaObject::RegisterPropertyMetaType, "RegisterPropertyMetaType"},
        {QMetaObject::RegisterMethodArgumentMetaType, "RegisterMethodArgumentMetaType"},
        {QMetaObject::BindableProperty, "BindableProperty"},
        {QMetaObject::CustomCall, "CustomCall"}
    };
    auto it = mapping.constFind(call);
    return it != mapping.constEnd() ? it.value() : "<Unknown>";
}

static QByteArray methodSignature(const QMetaMethod &method)
{
    QByteArray result;
    if (const auto *t = method.typeName()) {
        result += t;
        result += ' ';
    }
    result += method.methodSignature();
    return result;
}

static QByteArray msgCannotConvertParameter(const QByteArray &parameterTypeName,
                                            const QByteArray &signature, qsizetype p)
{
    return "Cannot call meta function \""_ba + signature
           + "\" because parameter " + QByteArray::number(p) + " of type \""_ba
           + parameterTypeName + "\" cannot be converted."_ba;
}

static inline QByteArray msgCannotConvertParameter(QMetaMethod method, qsizetype p)
{
    return msgCannotConvertParameter(method.parameterTypeName(p),
                                     methodSignature(method), p);
}

static QByteArray msgCannotConvertReturn(const QByteArray &signature)
{
    return "The return value of \""_ba + signature + "\" cannot be converted."_ba;
}

static inline QByteArray msgCannotConvertReturn(QMetaMethod method)
{
    return msgCannotConvertReturn(methodSignature(method));
}

namespace PySide {

PyObjectWrapper::PyObjectWrapper()
    :m_me(Py_None)
{
    // PYSIDE-813: When PYSIDE-164 was solved by adding some thread allowance,
    // this code was no longer protected. It was hard to find this connection.
    // See the website https://bugreports.qt.io/browse/PYSIDE-813 for details.
    Shiboken::GilState gil;
    Py_XINCREF(m_me);
}

PyObjectWrapper::PyObjectWrapper(PyObject *me)
    : m_me(me)
{
    Shiboken::GilState gil;
    Py_XINCREF(m_me);
}

PyObjectWrapper::PyObjectWrapper(const PyObjectWrapper &other)
    : m_me(other.m_me)
{
    Shiboken::GilState gil;
    Py_XINCREF(m_me);
}

PyObjectWrapper::~PyObjectWrapper()
{
    // Check that Python is still initialized as sometimes this is called by a static destructor
    // after Python interpeter is shutdown.
    if (!Py_IsInitialized())
        return;

    Shiboken::GilState gil;
    Py_XDECREF(m_me);
}

void PyObjectWrapper::reset(PyObject *o)
{
    Shiboken::GilState gil;
    Py_XINCREF(o);
    Py_XDECREF(m_me);
    m_me = o;
}

PyObjectWrapper &PyObjectWrapper::operator=(const PySide::PyObjectWrapper &other)
{
    if (this != &other)
        reset(other.m_me);
    return *this;
}

PyObjectWrapper::operator PyObject *() const
{
    return m_me;
}


int PyObjectWrapper::toInt() const
{
    // hold the GIL
    Shiboken::GilState state;
    return Shiboken::Enum::check(m_me) ? Shiboken::Enum::getValue(m_me) : -1;
}

QDataStream &operator<<(QDataStream &out, const PyObjectWrapper &myObj)
{
    if (Py_IsInitialized() == 0) {
        qWarning() << "Stream operator for PyObject called without python interpreter.";
        return out;
    }

    static PyObject *reduce_func = nullptr;

    Shiboken::GilState gil;
    if (!reduce_func) {
        Shiboken::AutoDecRef pickleModule(PyImport_ImportModule("pickle"));
        reduce_func = PyObject_GetAttr(pickleModule, Shiboken::PyName::dumps());
    }
    PyObject *pyObj = myObj;
    Shiboken::AutoDecRef repr(PyObject_CallFunctionObjArgs(reduce_func, pyObj, nullptr));
    if (repr.object()) {
        const char *buff = nullptr;
        Py_ssize_t size  = 0;
        if (PyBytes_Check(repr.object())) {
            buff = PyBytes_AS_STRING(repr.object());
            size = PyBytes_GET_SIZE(repr.object());
        } else if (Shiboken::String::check(repr.object())) {
            buff = Shiboken::String::toCString(repr.object());
            size = Shiboken::String::len(repr.object());
        }
        QByteArray data(buff, size);
        out << data;
    }
    return out;
}

QDataStream &operator>>(QDataStream &in, PyObjectWrapper &myObj)
{
    if (Py_IsInitialized() == 0) {
        qWarning() << "Stream operator for PyObject called without python interpreter.";
        return in;
    }

    static PyObject *eval_func = nullptr;

    Shiboken::GilState gil;
    if (!eval_func) {
        Shiboken::AutoDecRef pickleModule(PyImport_ImportModule("pickle"));
        eval_func = PyObject_GetAttr(pickleModule, Shiboken::PyName::loads());
    }

    QByteArray repr;
    in >> repr;
    Shiboken::AutoDecRef pyCode(PyBytes_FromStringAndSize(repr.data(), repr.size()));
    Shiboken::AutoDecRef value(PyObject_CallFunctionObjArgs(eval_func, pyCode.object(), 0));
    if (!value.object())
        value.reset(Py_None);
    myObj.reset(value);
    return in;
}

};

using namespace PySide;

struct SignalManagerPrivate
{
    static SignalManager::QmlMetaCallErrorHandler m_qmlMetaCallErrorHandler;

    static void handleMetaCallError(QObject *object, int *result);
    static int qtPropertyMetacall(QObject *object, QMetaObject::Call call,
                                  int id, void **args);
    static int qtMethodMetacall(QObject *object, int id, void **args);
};

SignalManager::QmlMetaCallErrorHandler
    SignalManagerPrivate::m_qmlMetaCallErrorHandler = nullptr;

static void PyObject_PythonToCpp_PyObject_PTR(PyObject *pyIn, void *cppOut)
{
    *reinterpret_cast<PyObject **>(cppOut) = pyIn;
}
static PythonToCppFunc is_PyObject_PythonToCpp_PyObject_PTR_Convertible(PyObject * /* pyIn */)
{
    return PyObject_PythonToCpp_PyObject_PTR;
}
static PyObject *PyObject_PTR_CppToPython_PyObject(const void *cppIn)
{
    auto *pyOut = reinterpret_cast<PyObject *>(const_cast<void *>(cppIn));
    if (pyOut)
        Py_INCREF(pyOut);
    return pyOut;
}

void SignalManager::init()
{
    // Register Qt primitive typedefs used on signals.
    using namespace Shiboken;

    // Register PyObject type to use in queued signal and slot connections
    qRegisterMetaType<PyObjectWrapper>("PyObject");
    // Register QVariant(enum) conversion to QVariant(int)
    QMetaType::registerConverter<PyObjectWrapper, int>(&PyObjectWrapper::toInt);

    SbkConverter *converter = Shiboken::Conversions::createConverter(&PyBaseObject_Type, nullptr);
    Shiboken::Conversions::setCppPointerToPythonFunction(converter, PyObject_PTR_CppToPython_PyObject);
    Shiboken::Conversions::setPythonToCppPointerFunctions(converter, PyObject_PythonToCpp_PyObject_PTR, is_PyObject_PythonToCpp_PyObject_PTR_Convertible);
    Shiboken::Conversions::registerConverterName(converter, "PyObject");
    Shiboken::Conversions::registerConverterName(converter, "object");
    Shiboken::Conversions::registerConverterName(converter, "PyObjectWrapper");
    Shiboken::Conversions::registerConverterName(converter, "PySide::PyObjectWrapper");

    if (!metaObjectAttr)
        metaObjectAttr = Shiboken::String::fromCString("__METAOBJECT__");
}

void SignalManager::setQmlMetaCallErrorHandler(QmlMetaCallErrorHandler handler)
{
    SignalManagerPrivate::m_qmlMetaCallErrorHandler = handler;
}

bool SignalManager::emitSignal(QObject *source, const char *signal, PyObject *args)
{
    if (!Signal::checkQtSignal(signal))
        return false;
    signal++;

    int signalIndex = source->metaObject()->indexOfSignal(signal);
    return signalIndex != -1 && MetaFunction::call(source, signalIndex, args);
}

// Handle errors from meta calls. Requires GIL and PyErr_Occurred()
void SignalManagerPrivate::handleMetaCallError(QObject *object, int *result)
{
    // Bubbles Python exceptions up to the Javascript engine, if called from one
    if (m_qmlMetaCallErrorHandler) {
        auto idOpt = m_qmlMetaCallErrorHandler(object);
        if (idOpt.has_value())
            *result = idOpt.value();
    }
    SignalManager::handleMetaCallError();
}

void SignalManager::handleMetaCallError()
{
    const int reclimit = Py_GetRecursionLimit();
    // Inspired by Python's errors.c: PyErr_GivenExceptionMatches() function.
    // Temporarily bump the recursion limit, so that PyErr_Print will not raise a recursion
    // error again. Don't do it when the limit is already insanely high, to avoid overflow.
    if (reclimit < (1 << 30))
        Py_SetRecursionLimit(reclimit + 5);
    PyErr_Print();
    Py_SetRecursionLimit(reclimit);
}

// Handler for QMetaObject::ReadProperty/WriteProperty/ResetProperty:
int SignalManagerPrivate::qtPropertyMetacall(QObject *object,
                                             QMetaObject::Call call,
                                             int id, void **args)
{
    const QMetaObject *metaObject = object->metaObject();
    int result = id - metaObject->propertyCount();

    const QMetaProperty mp = metaObject->property(id);

    qCDebug(lcPySide).noquote().nospace() << __FUNCTION__
        << ' ' << metaCallName(call) << " #" << id << ' ' << mp.typeName()
        << "/\"" << mp.name() << "\" " << object;

    if (!mp.isValid())
        return result;

    Shiboken::GilState gil;
    auto *pySbkSelf = Shiboken::BindingManager::instance().retrieveWrapper(object);
    Q_ASSERT(pySbkSelf);
    auto *pySelf = reinterpret_cast<PyObject *>(pySbkSelf);
    Shiboken::AutoDecRef pp_name(Shiboken::String::fromCString(mp.name()));
    PySideProperty *pp = Property::getObject(pySelf, pp_name);
    if (!pp) {
        qWarning("Invalid property: %s.", mp.name());
        return false;
    }
    pp->d->metaCall(pySelf, call, args);
    Py_DECREF(pp);
    if (PyErr_Occurred()) {
        // PYSIDE-2160: An unknown type was reported. Indicated by StopIteration.
        if (PyErr_ExceptionMatches(PyExc_StopIteration)) {
            PyObject *excType{};
            PyObject *excValue{};
            PyObject *excTraceback{};
            PyErr_Fetch(&excType, &excValue, &excTraceback);
            bool ign = call == QMetaObject::WriteProperty;
            PyErr_WarnFormat(PyExc_RuntimeWarning, 0,
                ign ? "Unknown property type '%s' of QObject '%s' used in fset"
                    : "Unknown property type '%s' of QObject '%s' used in fget with %R",
                pp->d->typeName.constData(), metaObject->className(), excValue);
            if (PyErr_Occurred())
                Shiboken::Errors::storeErrorOrPrint();
            Py_DECREF(excType);
            Py_DECREF(excValue);
            Py_XDECREF(excTraceback);
            return result;
        }

        qWarning().noquote().nospace()
            << "An error occurred executing the property metacall " << call
            << " on property \"" << mp.name() << "\" of " << object;
        handleMetaCallError(object, &result);
    }
    return result;
}

// Handler for QMetaObject::InvokeMetaMethod
int SignalManagerPrivate::qtMethodMetacall(QObject *object,
                                           int id, void **args)
{
    const QMetaObject *metaObject = object->metaObject();
    const QMetaMethod method = metaObject->method(id);
    int result = id - metaObject->methodCount();

    std::unique_ptr<Shiboken::GilState> gil;

    qCDebug(lcPySide).noquote().nospace() << __FUNCTION__ << " #" << id
        << " \"" << method.methodSignature() << '"';

    if (method.methodType() == QMetaMethod::Signal) {
        // emit python signal
        QMetaObject::activate(object, id, args);
    } else {
        gil.reset(new Shiboken::GilState);
        auto *pySbkSelf = Shiboken::BindingManager::instance().retrieveWrapper(object);
        Q_ASSERT(pySbkSelf);
        auto *pySelf = reinterpret_cast<PyObject *>(pySbkSelf);
        QByteArray methodName = method.methodSignature();
        methodName.truncate(methodName.indexOf('('));
        Shiboken::AutoDecRef pyMethod(PyObject_GetAttrString(pySelf, methodName));
        if (pyMethod.isNull()) {
            PyErr_Format(PyExc_AttributeError, "Slot '%s::%s' not found.",
                         metaObject->className(), method.methodSignature().constData());
        } else {
            SignalManager::callPythonMetaMethod(method, args, pyMethod);
        }
    }
    // WARNING Isn't safe to call any metaObject and/or object methods beyond this point
    //         because the object can be deleted inside the called slot.

    if (gil == nullptr)
        gil.reset(new Shiboken::GilState);

    if (PyErr_Occurred())
        handleMetaCallError(object, &result);

    return result;
}

int SignalManager::qt_metacall(QObject *object, QMetaObject::Call call, int id, void **args)
{
    switch (call) {
        case QMetaObject::ReadProperty:
        case QMetaObject::WriteProperty:
        case QMetaObject::ResetProperty:
            id = SignalManagerPrivate::qtPropertyMetacall(object, call, id, args);
            break;
        case QMetaObject::RegisterPropertyMetaType:
        case QMetaObject::BindableProperty:
            id -= object->metaObject()->propertyCount();
            break;
        case QMetaObject::InvokeMetaMethod:
            id = SignalManagerPrivate::qtMethodMetacall(object, id, args);
            break;
        case QMetaObject::CreateInstance:
        case QMetaObject::IndexOfMethod:
        case QMetaObject::RegisterMethodArgumentMetaType:
        case QMetaObject::CustomCall:
            qCDebug(lcPySide).noquote().nospace() << __FUNCTION__ << ' '
                << metaCallName(call) << " #" << id << ' '  << object;
            id -= object->metaObject()->methodCount();
            break;
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        case QMetaObject::ConstructInPlace:
            break;
#endif
    }
    return id;
}

// Helper for calling a Python pyCallable matching a Qt signal / slot.
enum CallResult : int
{
    CallOk,
    CallOtherError, // Python error set
    CallReturnValueError,
    CallArgumentError // Argument (return - CallArgumentError) caused an error
};

static inline bool isNonVoidReturn(const char *returnType)
{
    return returnType != nullptr && returnType[0] != 0 && std::strcmp("void", returnType) != 0;
}

static int callPythonMetaMethodHelper(const QByteArrayList &paramTypes,
                                      const char *returnType /* = nullptr */,
                                      void **args, PyObject *pyCallable)
{
    const qsizetype argsSize = paramTypes.size();
    Shiboken::AutoDecRef preparedArgs(PyTuple_New(argsSize));

    for (qsizetype i = 0; i < argsSize; ++i) {
        void *data = args[i + 1];
        auto param = paramTypes.at(i);
        Shiboken::Conversions::SpecificConverter converter(param.constData());
        if (!converter.isValid())
            return CallResult::CallArgumentError + int(i);
        PyTuple_SET_ITEM(preparedArgs, i, converter.toPython(data));
    }

    QScopedPointer<Shiboken::Conversions::SpecificConverter> retConverter;
    if (isNonVoidReturn(returnType)) {
        retConverter.reset(new Shiboken::Conversions::SpecificConverter(returnType));
        if (!retConverter->isValid())
            return CallResult::CallReturnValueError;
    }

    Shiboken::AutoDecRef retval(PyObject_CallObject(pyCallable, preparedArgs.object()));
    if (PyErr_Occurred() != nullptr || retval.isNull())
        return CallResult::CallOtherError;

    if (retval != Py_None && !retConverter.isNull())
        retConverter->toCpp(retval, args[0]);
    return CallResult::CallOk;
}

int SignalManager::callPythonMetaMethod(QMetaMethod method, void **args,
                                        PyObject *callable)
{
    Q_ASSERT(callable);

    Shiboken::GilState gil;
    int callResult = callPythonMetaMethodHelper(method.parameterTypes(),
                                                method.typeName(), args, callable);
    switch (callResult) {
    case CallOk:
        return 0;
    case CallOtherError:
        return -1;
    case CallReturnValueError:
        PyErr_SetString(PyExc_RuntimeError, msgCannotConvertReturn(method).constData());
        return -1;
    default: { // CallArgumentError + n
        const int arg = callResult - CallArgumentError;
        PyErr_SetString(PyExc_TypeError, msgCannotConvertParameter(method, arg).constData());
        return -1;
    }
    }
    return 0;
}

static QByteArray signature(const char *name, const QByteArrayList &parameterTypes,
                            const char *returnType)
{
    QByteArray result;
    if (isNonVoidReturn(returnType))
        result += QByteArray(returnType) + ' ';
    result += QByteArray(name) + '(' + parameterTypes.join(", ") + ')';
    return result;
}

int SignalManager::callPythonMetaMethod(const QByteArrayList &parameterTypes,
                                        const char *returnType,
                                        void **args, PyObject *callable)
{
    Q_ASSERT(callable);

    Shiboken::GilState gil;
    int callResult = callPythonMetaMethodHelper(parameterTypes, returnType, args, callable);
    switch (callResult) {
    case CallOk:
        return 0;
    case CallOtherError:
        return -1;
    case CallReturnValueError: {
        const auto &sig = signature("slot", parameterTypes, returnType);
        PyErr_SetString(PyExc_RuntimeError, msgCannotConvertReturn(sig).constData());
        return -1;
    }
    default: { // CallArgumentError + n
        const int arg = callResult - CallArgumentError;
        const auto &sig = signature("slot", parameterTypes, returnType);
        const auto &msg = msgCannotConvertParameter(parameterTypes.at(arg), sig, arg);
        PyErr_SetString(PyExc_TypeError, msg.constData());
        return -1;
    }
    }
    return 0;
}

bool SignalManager::registerMetaMethod(QObject *source, const char *signature, QMetaMethod::MethodType type)
{
    int ret = registerMetaMethodGetIndex(source, signature, type);
    return (ret != -1);
}

static MetaObjectBuilder *metaBuilderFromDict(PyObject *dict)
{
    // PYSIDE-803: The dict in this function is the ob_dict of an SbkObject.
    // The "metaObjectAttr" entry is only handled in this file. There is no
    // way in this function to involve the interpreter. Therefore, we need
    // no GIL.
    // Note that "SignalManager::registerMetaMethodGetIndex" has write actions
    // that might involve the interpreter, but in that context the GIL is held.
    if (!dict || !PyDict_Contains(dict, metaObjectAttr))
        return nullptr;

    // PYSIDE-813: The above assumption is not true in debug mode:
    // PyDict_GetItem would touch PyThreadState_GET and the global error state.
    // PyDict_GetItemWithError instead can work without GIL.
    PyObject *pyBuilder = PyDict_GetItemWithError(dict, metaObjectAttr);
    return reinterpret_cast<MetaObjectBuilder *>(PyCapsule_GetPointer(pyBuilder, nullptr));
}

// Helper to format a method signature "foo(QString)" into
// Slot decorator "@Slot(str)"

struct slotSignature
{
    explicit slotSignature(const char *signature) : m_signature(signature) {}

    const char *m_signature;
};

QDebug operator<<(QDebug debug, const slotSignature &sig)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "@Slot(";
    QByteArrayView signature(sig.m_signature);
    const auto len = signature.size();
    auto pos = signature.indexOf('(');
    if (pos != -1 && pos < len - 2) {
        ++pos;
        while (true) {
            auto nextPos = signature.indexOf(',', pos);
            if (nextPos == -1)
                nextPos = len - 1;
            const QByteArrayView parameter = signature.sliced(pos, nextPos - pos);
            if (parameter == "QString") {
                debug << "str";
            } else if (parameter == "double") {
                debug << "float";
            } else {
                const bool hasDelimiter = parameter.contains("::");
                if (hasDelimiter)
                    debug << '"';
                if (!hasDelimiter && parameter.endsWith('*'))
                    debug << parameter.first(parameter.size() - 1);
                else
                    debug << parameter;
                if (hasDelimiter)
                    debug << '"';
            }
            pos = nextPos + 1;
            if (pos >= len)
                break;
            debug << ',';
        }
    }
    debug << ')';
    return debug;
}

static int addMetaMethod(QObject *source, const QByteArray &signature,
                         QMetaMethod::MethodType type)
{
    const QMetaObject *metaObject = source->metaObject();
    SbkObject *self = Shiboken::BindingManager::instance().retrieveWrapper(source);
    if (!Shiboken::Object::hasCppWrapper(self)) {
        qWarning().noquote().nospace() << __FUNCTION__
            << ": Cannot add dynamic method \"" << signature << "\" (" << type
            << ") to " << source << ": No Wrapper found.";
        return -1;
    }

    auto *pySelf = reinterpret_cast<PyObject *>(self);
    auto *dict = SbkObject_GetDict_NoRef(pySelf);
    MetaObjectBuilder *dmo = metaBuilderFromDict(dict);
    // Create a instance meta object
    if (dmo == nullptr) {
        dmo = new MetaObjectBuilder(Py_TYPE(pySelf), metaObject);
        PyObject *pyDmo = PyCapsule_New(dmo, nullptr, destroyMetaObject);
        PyObject_SetAttr(pySelf, metaObjectAttr, pyDmo);
        Py_DECREF(pyDmo);
    }

    if (type == QMetaMethod::Slot) {
        qCWarning(lcPySide).noquote().nospace()
            << "Warning: Registering dynamic slot \""
            << signature << "\" on \"" << source->metaObject()->className()
            << "\". Consider annotating with " << slotSignature(signature);
    }

    return type == QMetaMethod::Signal ? dmo->addSignal(signature) : dmo->addSlot(signature);
}

static inline void warnNullSource(const char *signature)
{
    qWarning("SignalManager::registerMetaMethodGetIndex(\"%s\") called with source=nullptr.",
             signature);
}

int SignalManager::registerMetaMethodGetIndex(QObject *source, const char *signature,
                                              QMetaMethod::MethodType type)
{
    if (source == nullptr) {
        warnNullSource(signature);
        return -1;
    }
    const QMetaObject *metaObject = source->metaObject();
    const int methodIndex = metaObject->indexOfMethod(signature);
    // Create the dynamic signal if needed
    return methodIndex != -1
        ? methodIndex : addMetaMethod(source, QByteArray(signature), type);
}

int SignalManager::registerMetaMethodGetIndexBA(QObject* source, const QByteArray &signature,
                                                QMetaMethod::MethodType type)
{
    if (source == nullptr) {
        warnNullSource(signature.constData());
        return -1;
    }
    const QMetaObject *metaObject = source->metaObject();
    const int methodIndex = metaObject->indexOfMethod(signature.constData());
    // Create the dynamic signal if needed
    return methodIndex != -1
        ? methodIndex : addMetaMethod(source, signature, type);
}

const QMetaObject *SignalManager::retrieveMetaObject(PyObject *self)
{
    // PYSIDE-803: Avoid the GIL in SignalManager::retrieveMetaObject
    // This function had the GIL. We do not use the GIL unless we have to.
    // metaBuilderFromDict accesses a Python dict, but in that context there
    // is no way to reach the interpreter, see "metaBuilderFromDict".
    //
    // The update function is MetaObjectBuilderPrivate::update in
    // dynamicmetaobject.c . That function now uses the GIL when the
    // m_dirty flag is set.
    Q_ASSERT(self);

    auto *ob_dict = SbkObject_GetDict_NoRef(self);
    MetaObjectBuilder *builder = metaBuilderFromDict(ob_dict);
    if (!builder)
        builder = &(retrieveTypeUserData(self)->mo);

    return builder->update();
}
