// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include <sbkpython.h>
#include "pysidesignal.h"
#include "pysidesignal_p.h"
#include "pysideqobject.h"
#include "pysideutils.h"
#include "pysidestaticstrings.h"
#include "pysideweakref.h"
#include "signalmanager.h"

#include <shiboken.h>

#include <QtCore/QByteArray>
#include <QtCore/QDebug>
#include <QtCore/QHash>
#include <QtCore/QObject>
#include <QtCore/QMetaMethod>
#include <QtCore/QMetaObject>
#include <pep384ext.h>
#include <signature.h>

#include <algorithm>
#include <optional>
#include <utility>
#include <cstring>

#define QT_SIGNAL_SENTINEL '2'

using namespace Qt::StringLiterals;

QDebug operator<<(QDebug debug, const PySideSignalData::Signature &s)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Signature(\"" << s.signature << '"';
    if (s.attributes)
        debug << ", attributes=" << s.attributes;
    debug << ')';
    return debug;
}

QDebug operator<<(QDebug debug, const PySideSignalData &d)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "PySideSignalData(\"" << d.signalName << "\", "
          << d.signatures;
    if (!d.signalArguments.isEmpty())
        debug << ", signalArguments=" << d.signalArguments;
    debug << ')';
    return debug;
}

QDebug operator<<(QDebug debug, const PySideSignalInstancePrivate &d)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "PySideSignalInstancePrivate(\"" << d.signalName
          << "\", \"" << d.signature << '"';
    if (d.attributes)
        debug << ", attributes=" << d.attributes;
    if (d.homonymousMethod)
        debug << ", homonymousMethod=" << d.homonymousMethod;
    debug << ')';
    return debug;
}

static bool connection_Check(PyObject *o)
{
    if (o == nullptr || o == Py_None)
        return false;
    static QByteArray typeName = QByteArrayLiteral("PySide")
        + QByteArray::number(QT_VERSION_MAJOR)
        + QByteArrayLiteral(".QtCore.QMetaObject.Connection");
    return std::strcmp(o->ob_type->tp_name, typeName.constData()) == 0;
}

static std::optional<QByteArrayList> parseArgumentNames(PyObject *argArguments)
{
    QByteArrayList result;
    if (argArguments == nullptr)
        return result;
    // Prevent a string from being split into a sequence of characters
    if (PySequence_Check(argArguments) == 0 || PyUnicode_Check(argArguments) != 0)
        return std::nullopt;
    const Py_ssize_t argumentSize = PySequence_Size(argArguments);
    result.reserve(argumentSize);
    for (Py_ssize_t i = 0; i < argumentSize; ++i) {
        Shiboken::AutoDecRef item(PySequence_GetItem(argArguments, i));
        if (PyUnicode_Check(item.object()) == 0)
            return std::nullopt;
        Shiboken::AutoDecRef strObj(PyUnicode_AsUTF8String(item));
        const char *s = PyBytes_AsString(strObj);
        if (s == nullptr)
            return std::nullopt;
        result.append(QByteArray(s));
    }
    return result;
}

namespace PySide::Signal {
    static QByteArray buildSignature(const QByteArray &, const QByteArray &);
    static void instanceInitialize(PySideSignalInstance *, PyObject *, PySideSignal *, PyObject *, int);
    static PySideSignalData::Signature parseSignature(PyObject *);
    static PyObject *buildQtCompatible(const QByteArray &);
} // PySide::Signal

extern "C"
{

// Signal methods
static int signalTpInit(PyObject *, PyObject *, PyObject *);
static void signalFree(void *);
static void signalInstanceFree(void *);
static PyObject *signalGetItem(PyObject *self, PyObject *key);
static PyObject *signalGetAttr(PyObject *self, PyObject *name);
static PyObject *signalToString(PyObject *self);
static PyObject *signalDescrGet(PyObject *self, PyObject *obj, PyObject *type);

// Signal Instance methods
static PyObject *signalInstanceConnect(PyObject *, PyObject *, PyObject *);
static PyObject *signalInstanceDisconnect(PyObject *, PyObject *);
static PyObject *signalInstanceEmit(PyObject *, PyObject *);
static PyObject *signalInstanceGetItem(PyObject *, PyObject *);

static PyObject *signalInstanceCall(PyObject *self, PyObject *args, PyObject *kw);
static PyObject *signalCall(PyObject *, PyObject *, PyObject *);

static PyObject *metaSignalCheck(PyObject *, PyObject *);


static PyMethodDef MetaSignal_tp_methods[] = {
    {"__instancecheck__", reinterpret_cast<PyCFunction>(metaSignalCheck),
                          METH_O|METH_STATIC, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static PyTypeObject *createMetaSignalType()
{
    PyType_Slot PySideMetaSignalType_slots[] = {
        {Py_tp_methods, reinterpret_cast<void *>(MetaSignal_tp_methods)},
        {Py_tp_base,    reinterpret_cast<void *>(&PyType_Type)},
        {Py_tp_free,    reinterpret_cast<void *>(PyObject_GC_Del)},
        {Py_tp_dealloc, reinterpret_cast<void *>(Sbk_object_dealloc)},
        {0, nullptr}
    };

    PyType_Spec PySideMetaSignalType_spec = {
        "2:PySide6.QtCore.MetaSignal",
        0,
        // sizeof(PyHeapTypeObject) is filled in by SbkType_FromSpec
        // which calls PyType_Ready which calls inherit_special.
        0,
        Py_TPFLAGS_DEFAULT,
        PySideMetaSignalType_slots,
    };

    return SbkType_FromSpec(&PySideMetaSignalType_spec);
}

static PyTypeObject *PySideMetaSignal_TypeF(void)
{
    static auto *type = createMetaSignalType();
    return type;
}

static PyTypeObject *createSignalType()
{
    PyType_Slot PySideSignalType_slots[] = {
        {Py_mp_subscript,   reinterpret_cast<void *>(signalGetItem)},
        {Py_tp_getattro,    reinterpret_cast<void *>(signalGetAttr)},
        {Py_tp_descr_get,   reinterpret_cast<void *>(signalDescrGet)},
        {Py_tp_call,        reinterpret_cast<void *>(signalCall)},
        {Py_tp_str,         reinterpret_cast<void *>(signalToString)},
        {Py_tp_init,        reinterpret_cast<void *>(signalTpInit)},
        {Py_tp_new,         reinterpret_cast<void *>(PyType_GenericNew)},
        {Py_tp_free,        reinterpret_cast<void *>(signalFree)},
        {Py_tp_dealloc,     reinterpret_cast<void *>(Sbk_object_dealloc)},
        {0, nullptr}
    };

    PyType_Spec PySideSignalType_spec = {
        "2:PySide6.QtCore.Signal",
        sizeof(PySideSignal),
        0,
        Py_TPFLAGS_DEFAULT,
        PySideSignalType_slots,
    };

    return SbkType_FromSpecWithMeta(&PySideSignalType_spec, PySideMetaSignal_TypeF());
}

PyTypeObject *PySideSignal_TypeF(void)
{
    static auto *type = createSignalType();
    return type;
}

static PyObject *signalInstanceRepr(PyObject *obSelf)
{
    auto *self = reinterpret_cast<PySideSignalInstance *>(obSelf);
    auto *typeName = Py_TYPE(obSelf)->tp_name;
    return Shiboken::String::fromFormat("<%s %s at %p>", typeName,
                                        self->d ? self->d->signature.constData()
                                                : "(no signature)", obSelf);
}

static PyMethodDef SignalInstance_methods[] = {
    {"connect", reinterpret_cast<PyCFunction>(signalInstanceConnect),
                METH_VARARGS|METH_KEYWORDS, nullptr},
    {"disconnect", signalInstanceDisconnect, METH_VARARGS, nullptr},
    {"emit", signalInstanceEmit, METH_VARARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}  /* Sentinel */
};

static PyTypeObject *createSignalInstanceType()
{
    PyType_Slot PySideSignalInstanceType_slots[] = {
        {Py_mp_subscript,   reinterpret_cast<void *>(signalInstanceGetItem)},
        {Py_tp_call,        reinterpret_cast<void *>(signalInstanceCall)},
        {Py_tp_methods,     reinterpret_cast<void *>(SignalInstance_methods)},
        {Py_tp_repr,        reinterpret_cast<void *>(signalInstanceRepr)},
        {Py_tp_new,         reinterpret_cast<void *>(PyType_GenericNew)},
        {Py_tp_free,        reinterpret_cast<void *>(signalInstanceFree)},
        {Py_tp_dealloc,     reinterpret_cast<void *>(Sbk_object_dealloc)},
        {0, nullptr}
    };

    PyType_Spec PySideSignalInstanceType_spec = {
        "2:PySide6.QtCore.SignalInstance",
        sizeof(PySideSignalInstance),
        0,
        Py_TPFLAGS_DEFAULT,
        PySideSignalInstanceType_slots,
    };

    return SbkType_FromSpec(&PySideSignalInstanceType_spec);
}

PyTypeObject *PySideSignalInstance_TypeF(void)
{
    static auto *type = createSignalInstanceType();
    return type;
}

static int signalTpInit(PyObject *obSelf, PyObject *args, PyObject *kwds)
{
    static PyObject * const emptyTuple = PyTuple_New(0);
    static const char *kwlist[] = {"name", "arguments", nullptr};
    char *argName = nullptr;
    PyObject *argArguments = nullptr;

    if (!PyArg_ParseTupleAndKeywords(emptyTuple, kwds,
            "|sO:QtCore.Signal{name, arguments}",
            const_cast<char **>(kwlist), &argName, &argArguments))
        return -1;

    bool tupledArgs = false;
    PySideSignal *self = reinterpret_cast<PySideSignal *>(obSelf);
    if (!self->data)
        self->data = new PySideSignalData;
    if (argName)
        self->data->signalName = argName;

    auto argumentNamesOpt = parseArgumentNames(argArguments);
    if (!argumentNamesOpt.has_value()) {
        PyErr_SetString(PyExc_TypeError, "'arguments' must be a sequence of strings.");
        return -1;
    }
    self->data->signalArguments = argumentNamesOpt.value();

    for (Py_ssize_t i = 0, i_max = PyTuple_Size(args); i < i_max; i++) {
        PyObject *arg = PyTuple_GET_ITEM(args, i);
        if (PySequence_Check(arg) && !Shiboken::String::check(arg) && !PyEnumMeta_Check(arg)) {
            tupledArgs = true;
            self->data->signatures.append(PySide::Signal::parseSignature(arg));
        }
    }

    if (!tupledArgs)
        self->data->signatures.append(PySide::Signal::parseSignature(args));

    return 0;
}

static void signalFree(void *vself)
{
    auto pySelf = reinterpret_cast<PyObject *>(vself);
    auto self = reinterpret_cast<PySideSignal *>(vself);
    if (self->data) {
        delete self->data;
        self->data = nullptr;
    }
    Py_XDECREF(self->homonymousMethod);
    self->homonymousMethod = nullptr;

    PepExt_TypeCallFree(Py_TYPE(pySelf)->tp_base, self);
}

static PyObject *signalGetItem(PyObject *obSelf, PyObject *key)
{
    auto self = reinterpret_cast<PySideSignal *>(obSelf);
    QByteArray sigKey;
    if (key) {
        sigKey = PySide::Signal::parseSignature(key).signature;
    } else {
        sigKey = self->data == nullptr || self->data->signatures.isEmpty()
            ? PySide::Signal::voidType() : self->data->signatures.constFirst().signature;
    }
    auto sig = PySide::Signal::buildSignature(self->data->signalName, sigKey);
    return Shiboken::String::fromCString(sig.constData());
}

static PyObject *signalToString(PyObject *obSelf)
{
    auto self = reinterpret_cast<PySideSignal *>(obSelf);
    QByteArray result;
    if (self->data == nullptr || self->data->signatures.isEmpty()) {
        result = "<invalid>"_ba;
    } else {
        for (const auto &signature : std::as_const(self->data->signatures)) {
            if (!result.isEmpty())
                result += "; "_ba;
            result += PySide::Signal::buildSignature(self->data->signalName,
                                                     signature.signature);
        }
    }
    return Shiboken::String::fromCString(result.constData());
}

static PyObject *signalGetAttr(PyObject *obSelf, PyObject *name)
{
    auto self = reinterpret_cast<PySideSignal *>(obSelf);

    if (PyUnicode_CompareWithASCIIString(name, "signatures") != 0)
        return PyObject_GenericGetAttr(obSelf, name);

    auto nelems = self->data->signatures.count();
    PyObject *tuple = PyTuple_New(nelems);

    for (Py_ssize_t idx = 0; idx < nelems; ++idx) {
        QByteArray sigKey = self->data->signatures.at(idx).signature;
        auto sig = PySide::Signal::buildSignature(self->data->signalName, sigKey);
        PyObject *entry = Shiboken::String::fromCString(sig.constData());
        PyTuple_SetItem(tuple, idx, entry);
    }
    return tuple;
}

static void signalInstanceFree(void *vself)
{
    auto pySelf = reinterpret_cast<PyObject *>(vself);
    auto self = reinterpret_cast<PySideSignalInstance *>(vself);

    PySideSignalInstancePrivate *dataPvt = self->d;
    if (dataPvt) {
        Py_XDECREF(dataPvt->homonymousMethod);

        if (dataPvt->next) {
            Py_DECREF(dataPvt->next);
            dataPvt->next = nullptr;
        }
        delete dataPvt;
        self->d = nullptr;
    }
    self->deleted = true;
    PepExt_TypeCallFree(Py_TYPE(pySelf)->tp_base, self);
}

// PYSIDE-1523: PyFunction_Check is not accepting compiled functions and
// PyMethod_Check is not allowing compiled methods, therefore also lookup
// "im_func" and "__code__" attributes, we allow for that with a dedicated
// function handling both.

struct FunctionArgumentsResult
{
    PyObject *function = nullptr;
    PepCodeObject *objCode = nullptr;
    PyObject *functionName = nullptr;
    bool isMethod = false;
};

static FunctionArgumentsResult extractFunctionArgumentsFromSlot(PyObject *slot)
{
    FunctionArgumentsResult ret;
    ret.isMethod = PyMethod_Check(slot);
    const bool isFunction = PyFunction_Check(slot);

    if (ret.isMethod || isFunction) {
        ret.function = ret.isMethod ? PyMethod_GET_FUNCTION(slot) : slot;
        ret.objCode = reinterpret_cast<PepCodeObject *>(PyFunction_GET_CODE(ret.function));
        ret.functionName = PepFunction_GetName(ret.function);

    } else if (PySide::isCompiledMethod(slot)) {
        // PYSIDE-1523: PyFunction_Check and PyMethod_Check are not accepting compiled forms, we
        // just go by attributes.
        ret.isMethod = true;

        ret.function = PyObject_GetAttr(slot, PySide::PySideName::im_func());
        // Not retaining a reference inline with what PyMethod_GET_FUNCTION does.
        Py_DECREF(ret.function);

        ret.functionName = PyObject_GetAttr(ret.function, PySide::PySideMagicName::name());
        // Not retaining a reference inline with what PepFunction_GetName does.
        Py_DECREF(ret.functionName);

        ret.objCode = reinterpret_cast<PepCodeObject *>(
                    PyObject_GetAttr(ret.function, PySide::PySideMagicName::code()));
        // Not retaining a reference inline with what PyFunction_GET_CODE does.
        Py_XDECREF(ret.objCode);

        // Should not happen, but lets handle it gracefully, maybe Nuitka one day
        // makes these optional, or somebody defined a type named like it without
        // it being actually being that.
        if (ret.objCode == nullptr)
            ret.function = nullptr;
    } else if (strcmp(Py_TYPE(slot)->tp_name, "compiled_function") == 0) {
        ret.isMethod = false;
        ret.function = slot;

        ret.functionName = PyObject_GetAttr(ret.function, PySide::PySideMagicName::name());
        // Not retaining a reference inline with what PepFunction_GetName does.
        Py_DECREF(ret.functionName);

        ret.objCode = reinterpret_cast<PepCodeObject *>(
                    PyObject_GetAttr(ret.function, PySide::PySideMagicName::code()));
        // Not retaining a reference inline with what PyFunction_GET_CODE does.
        Py_XDECREF(ret.objCode);

        // Should not happen, but lets handle it gracefully, maybe Nuitka one day
        // makes these optional, or somebody defined a type named like it without
        // it being actually being that.
        if (ret.objCode == nullptr)
            ret.function = nullptr;
    }
    // any other callback
    return ret;
}

struct ArgCount
{
    int min;
    int max;
};

// Return a pair of minimum / arg count "foo(p1, p2=0)" -> {1, 2}
ArgCount argCount(const FunctionArgumentsResult &args)
{
    Q_ASSERT(args.objCode);
    ArgCount result{-1, -1};
    if ((PepCode_GET_FLAGS(args.objCode) & CO_VARARGS) == 0) {
        result.min = result.max = PepCode_GET_ARGCOUNT(args.objCode);
        if (args.function != nullptr) {
            if (auto *defaultArgs = PepFunction_GetDefaults(args.function))
                result.min -= PyTuple_Size(defaultArgs);
        }
    }
    return result;
}

// Find Signal Instance for argument count.
static PySideSignalInstance *findSignalInstance(PySideSignalInstance *source, int argCount)
{
    for (auto *si = source; si != nullptr; si = si->d->next) {
        if (si->d->argCount == argCount)
            return si;
    }
    return nullptr;
}

static PyObject *signalInstanceConnect(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *slot = nullptr;
    PyObject *type = nullptr;
    static const char *kwlist[] = {"slot", "type", nullptr};

    if (!PyArg_ParseTupleAndKeywords(args, kwds,
        "O|O:SignalInstance", const_cast<char **>(kwlist), &slot, &type))
        return nullptr;

    PySideSignalInstance *source = reinterpret_cast<PySideSignalInstance *>(self);
    if (!source->d)
        return PyErr_Format(PyExc_RuntimeError, "cannot connect uninitialized SignalInstance");
    if (source->deleted)
        return PyErr_Format(PyExc_RuntimeError, "Signal source has been deleted");

    Shiboken::AutoDecRef pyArgs(PyList_New(0));

    bool match = false;
    if (Py_TYPE(slot) == PySideSignalInstance_TypeF()) {
        PySideSignalInstance *sourceWalk = source;

        //find best match
        while (sourceWalk && !match) {
            auto targetWalk = reinterpret_cast<PySideSignalInstance *>(slot);
            while (targetWalk && !match) {
                if (QMetaObject::checkConnectArgs(sourceWalk->d->signature,
                                                  targetWalk->d->signature)) {
                    PyList_Append(pyArgs, sourceWalk->d->source);
                    Shiboken::AutoDecRef sourceSignature(PySide::Signal::buildQtCompatible(sourceWalk->d->signature));
                    PyList_Append(pyArgs, sourceSignature);

                    PyList_Append(pyArgs, targetWalk->d->source);
                    Shiboken::AutoDecRef targetSignature(PySide::Signal::buildQtCompatible(targetWalk->d->signature));
                    PyList_Append(pyArgs, targetSignature);

                    match = true;
                }
                targetWalk = reinterpret_cast<PySideSignalInstance *>(targetWalk->d->next);
            }
            sourceWalk = reinterpret_cast<PySideSignalInstance *>(sourceWalk->d->next);
        }
    } else {
        // Check signature of the slot (method or function) to match signal
        const auto args = extractFunctionArgumentsFromSlot(slot);
        PySideSignalInstance *matchedSlot = nullptr;

        if (args.function != nullptr) {
            auto slotArgRange = argCount(args);
            if (args.isMethod) {
                slotArgRange.min -= 1;
                slotArgRange.max -= 1;
            }

            // Get signature args
            // Iterate the possible types of connection for this signal and compare
            // it with slot arguments
            for (int slotArgs = slotArgRange.max;
                 slotArgs >= slotArgRange.min && matchedSlot == nullptr; --slotArgs) {
                 matchedSlot = findSignalInstance(source, slotArgs);
            }
        }

        // Adding references to pyArgs
        PyList_Append(pyArgs, source->d->source);

        if (matchedSlot != nullptr) {
            // If a slot matching the same number of arguments was found,
            // include signature to the pyArgs
            Shiboken::AutoDecRef signature(PySide::Signal::buildQtCompatible(matchedSlot->d->signature));
            PyList_Append(pyArgs, signature);
        } else {
            // Try the first by default if the slot was not found
            Shiboken::AutoDecRef signature(PySide::Signal::buildQtCompatible(source->d->signature));
            PyList_Append(pyArgs, signature);
        }
        PyList_Append(pyArgs, slot);
        match = true;
    }

    if (type)
        PyList_Append(pyArgs, type);

    if (match) {
        Shiboken::AutoDecRef tupleArgs(PyList_AsTuple(pyArgs));
        Shiboken::AutoDecRef pyMethod(PyObject_GetAttr(source->d->source,
                                                       PySide::PySideName::qtConnect()));
        if (pyMethod.isNull())  // PYSIDE-79: check if pyMethod exists.
            return PyErr_Format(PyExc_RuntimeError, "method 'connect' vanished!");
        PyObject *result = PyObject_CallObject(pyMethod, tupleArgs);
        if (connection_Check(result))
            return result;
        Py_XDECREF(result);
    }
    if (!PyErr_Occurred()) // PYSIDE-79: inverse the logic. A Null return needs an error.
        PyErr_Format(PyExc_RuntimeError, "Failed to connect signal %s.",
                     source->d->signature.constData());
    return nullptr;
}

static int argCountInSignature(const char *signature)
{
    return QByteArray(signature).count(",") + 1;
}

static PyObject *signalInstanceEmit(PyObject *self, PyObject *args)
{
    PySideSignalInstance *source = reinterpret_cast<PySideSignalInstance *>(self);
    if (!source->d)
        return PyErr_Format(PyExc_RuntimeError, "cannot emit uninitialized SignalInstance");

    // PYSIDE-2201: Check if the object has vanished meanwhile.
    //              Tried to revive it without exception, but this gives problems.
    if (source->deleted)
        return PyErr_Format(PyExc_RuntimeError, "The SignalInstance object was already deleted");

    Shiboken::AutoDecRef pyArgs(PyList_New(0));
    int numArgsGiven = PySequence_Fast_GET_SIZE(args);
    int numArgsInSignature = argCountInSignature(source->d->signature);

    // If number of arguments given to emit is smaller than the first source signature expects,
    // it is possible it's a case of emitting a signal with default parameters.
    // Search through all the overloaded signals with the same name, and try to find a signature
    // with the same number of arguments as given to emit, and is also marked as a cloned method
    // (which in metaobject parlance means a signal with default parameters).
    // @TODO: This should be improved to take into account argument types as well. The current
    // assumption is there are no signals which are both overloaded on argument types and happen to
    // have signatures with default parameters.
    if (numArgsGiven < numArgsInSignature) {
        PySideSignalInstance *possibleDefaultInstance = source;
        while ((possibleDefaultInstance = possibleDefaultInstance->d->next)) {
            if (possibleDefaultInstance->d->attributes & QMetaMethod::Cloned
                    && argCountInSignature(possibleDefaultInstance->d->signature) == numArgsGiven) {
                source = possibleDefaultInstance;
                break;
            }
        }
    }
    Shiboken::AutoDecRef sourceSignature(PySide::Signal::buildQtCompatible(source->d->signature));

    PyList_Append(pyArgs, sourceSignature);
    for (Py_ssize_t i = 0, max = PyTuple_Size(args); i < max; i++)
        PyList_Append(pyArgs, PyTuple_GetItem(args, i));

    Shiboken::AutoDecRef pyMethod(PyObject_GetAttr(source->d->source,
                                                   PySide::PySideName::qtEmit()));

    Shiboken::AutoDecRef tupleArgs(PyList_AsTuple(pyArgs));
    return PyObject_CallObject(pyMethod.object(), tupleArgs);
}

static PyObject *signalInstanceGetItem(PyObject *self, PyObject *key)
{
    auto *firstSignal = reinterpret_cast<PySideSignalInstance *>(self);
    const auto &sigName = firstSignal->d->signalName;
    const auto sigKey = PySide::Signal::parseSignature(key).signature;
    const auto sig = PySide::Signal::buildSignature(sigName, sigKey);
    for (auto *data = firstSignal; data != nullptr; data = data->d->next) {
        if (data->d->signature == sig) {
            PyObject *result = reinterpret_cast<PyObject *>(data);
            Py_INCREF(result);
            return result;
        }
    }

    // Build error message with candidates
    QByteArray message = "Signature \"" + sig + "\" not found for signal: \""
                         + sigName + "\". Available candidates: ";
    for (auto *data = firstSignal; data != nullptr; data = data->d->next) {
        if (data != firstSignal)
            message += ", ";
        message += '"' + data->d->signature + '"';
    }

    return PyErr_Format(PyExc_IndexError, message.constData());
}

static inline void warnDisconnectFailed(PyObject *aSlot, const QByteArray &signature)
{
    if (PyErr_Occurred() != nullptr) { // avoid "%S" invoking str() when an error is set.
        PyObject *exc{}, *inst{}, *tb{};
        PyErr_Fetch(&exc, &inst, &tb);
        PyErr_WarnFormat(PyExc_RuntimeWarning, 0, "Failed to disconnect (%s) from signal \"%s\".",
                         Py_TYPE(aSlot)->tp_name, signature.constData());
        PyErr_Restore(exc, inst, tb);
    } else {
        PyErr_WarnFormat(PyExc_RuntimeWarning, 0, "Failed to disconnect (%S) from signal \"%s\".",
                         aSlot, signature.constData());
    }
}

static PyObject *signalInstanceDisconnect(PyObject *self, PyObject *args)
{
    auto source = reinterpret_cast<PySideSignalInstance *>(self);
    if (!source->d)
        return PyErr_Format(PyExc_RuntimeError, "cannot disconnect uninitialized SignalInstance");

    Shiboken::AutoDecRef pyArgs(PyList_New(0));

    PyObject *slot = Py_None;
    if (PyTuple_Check(args) && PyTuple_GET_SIZE(args))
        slot = PyTuple_GET_ITEM(args, 0);

    bool match = false;
    if (Py_TYPE(slot) == PySideSignalInstance_TypeF()) {
        PySideSignalInstance *target = reinterpret_cast<PySideSignalInstance *>(slot);
        if (QMetaObject::checkConnectArgs(source->d->signature, target->d->signature)) {
            PyList_Append(pyArgs, source->d->source);
            Shiboken::AutoDecRef source_signature(PySide::Signal::buildQtCompatible(source->d->signature));
            PyList_Append(pyArgs, source_signature);

            PyList_Append(pyArgs, target->d->source);
            Shiboken::AutoDecRef target_signature(PySide::Signal::buildQtCompatible(target->d->signature));
            PyList_Append(pyArgs, target_signature);
            match = true;
        }
    } else if (connection_Check(slot)) {
        PyList_Append(pyArgs, slot);
        match = true;
    } else {
        //try the first signature
        PyList_Append(pyArgs, source->d->source);
        Shiboken::AutoDecRef signature(PySide::Signal::buildQtCompatible(source->d->signature));
        PyList_Append(pyArgs, signature);

        // disconnect all, so we need to use the c++ signature disconnect(qobj, signal, 0, 0)
        if (slot == Py_None)
            PyList_Append(pyArgs, slot);
        PyList_Append(pyArgs, slot);
        match = true;
    }

    if (match) {
        Shiboken::AutoDecRef tupleArgs(PyList_AsTuple(pyArgs));
        Shiboken::AutoDecRef pyMethod(PyObject_GetAttr(source->d->source,
                                                       PySide::PySideName::qtDisconnect()));
        PyObject *result = PyObject_CallObject(pyMethod, tupleArgs);
        if (result != Py_True)
            warnDisconnectFailed(slot, source->d->signature);
        return result;
    }

    warnDisconnectFailed(slot, source->d->signature);
    Py_RETURN_FALSE;
}

// PYSIDE-68: Supply the missing __get__ function
static PyObject *signalDescrGet(PyObject *self, PyObject *obj, PyObject * /*type*/)
{
    auto signal = reinterpret_cast<PySideSignal *>(self);
    // Return the unbound signal if there is nothing to bind it to.
    if (obj == nullptr || obj == Py_None
        || !PySide::isQObjectDerived(Py_TYPE(obj), true)) {
        Py_INCREF(self);
        return self;
    }

    // PYSIDE-68-bis: It is important to respect the already cached instance.
    Shiboken::AutoDecRef name(Py_BuildValue("s", signal->data->signalName.data()));
    auto *dict = SbkObject_GetDict_NoRef(obj);
    auto *inst = PyDict_GetItem(dict, name);
    if (inst) {
        Py_INCREF(inst);
        return inst;
    }
    inst = reinterpret_cast<PyObject *>(PySide::Signal::initialize(signal, name, obj));
    PyObject_SetAttr(obj, name, inst);
    return inst;
}

static PyObject *signalCall(PyObject *self, PyObject *args, PyObject *kw)
{
    auto signal = reinterpret_cast<PySideSignal *>(self);

    // Native C++ signals can't be called like functions, thus we throw an exception.
    // The only way calling a signal can succeed (the Python equivalent of C++'s operator() )
    // is when a method with the same name as the signal is attached to an object.
    // An example is QProcess::error() (don't check the docs, but the source code of qprocess.h).
    if (!signal->homonymousMethod)
        return PyErr_Format(PyExc_TypeError, "native Qt signal is not callable");

    // Check if there exists a method with the same name as the signal, which is also a static
    // method in C++ land.
    Shiboken::AutoDecRef homonymousMethod(PepExt_Type_CallDescrGet(signal->homonymousMethod,
                                                                   nullptr, nullptr));
    if (PyCFunction_Check(homonymousMethod.object())
            && (PyCFunction_GET_FLAGS(homonymousMethod.object()) & METH_STATIC))
        return PyObject_Call(homonymousMethod, args, kw);

    // Assumes homonymousMethod is not a static method.
    ternaryfunc callFunc = PepExt_Type_GetCallSlot(Py_TYPE(signal->homonymousMethod));
    return callFunc(homonymousMethod, args, kw);
}

// This function returns a borrowed reference.
static inline PyObject *_getRealCallable(PyObject *func)
{
    static const auto *SignalType = PySideSignal_TypeF();
    static const auto *SignalInstanceType = PySideSignalInstance_TypeF();

    // If it is a signal, use the (maybe empty) homonymous method.
    if (Py_TYPE(func) == SignalType) {
        auto *signal = reinterpret_cast<PySideSignal *>(func);
        return signal->homonymousMethod;
    }
    // If it is a signal instance, use the (maybe empty) homonymous method.
    if (Py_TYPE(func) == SignalInstanceType) {
        auto *signalInstance = reinterpret_cast<PySideSignalInstance *>(func);
        return signalInstance->d->homonymousMethod;
    }
    return func;
}

// This function returns a borrowed reference.
static PyObject *_getHomonymousMethod(PySideSignalInstance *inst)
{
    if (inst->d->homonymousMethod)
        return inst->d->homonymousMethod;

    // PYSIDE-1730: We are searching methods with the same name not only at the same place,
    // but walk through the whole mro to find a hidden method with the same name.
    auto signalName = inst->d->signalName;
    Shiboken::AutoDecRef name(Shiboken::String::fromCString(signalName));
    auto *mro = Py_TYPE(inst->d->source)->tp_mro;
    const Py_ssize_t n = PyTuple_GET_SIZE(mro);

    for (Py_ssize_t idx = 0; idx < n; idx++) {
        auto *sub_type = reinterpret_cast<PyTypeObject *>(PyTuple_GET_ITEM(mro, idx));
        Shiboken::AutoDecRef tpDict(PepType_GetDict(sub_type));
        auto *hom = PyDict_GetItem(tpDict, name);
        PyObject *realFunc{};
        if (hom && PyCallable_Check(hom) && (realFunc = _getRealCallable(hom)))
            return realFunc;
    }
    return nullptr;
}

static PyObject *signalInstanceCall(PyObject *self, PyObject *args, PyObject *kw)
{
    auto *PySideSignal = reinterpret_cast<PySideSignalInstance *>(self);
    auto *hom = _getHomonymousMethod(PySideSignal);
    if (!hom) {
        PyErr_Format(PyExc_TypeError, "native Qt signal instance '%s' is not callable",
                     PySideSignal->d->signalName.constData());
        return nullptr;
    }

    Shiboken::AutoDecRef homonymousMethod(PepExt_Type_CallDescrGet(hom, PySideSignal->d->source,
                                                                   nullptr));
    return PyObject_Call(homonymousMethod, args, kw);
}

static PyObject *metaSignalCheck(PyObject * /* klass */, PyObject *arg)
{
    if (PyType_IsSubtype(Py_TYPE(arg), PySideSignalInstance_TypeF()))
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

} // extern "C"

namespace PySide::Signal {

static const char *MetaSignal_SignatureStrings[] = {
    "PySide6.QtCore.MetaSignal.__instancecheck__(self,object:object)->bool",
    nullptr}; // Sentinel

static const char *Signal_SignatureStrings[] = {
    "PySide6.QtCore.Signal(self,*types:type,name:str=nullptr,arguments:typing.List[str]=nullptr)",
    "1:PySide6.QtCore.Signal.__get__(self,instance:None,owner:Optional[typing.Any])->"
        "PySide6.QtCore.Signal",
    "0:PySide6.QtCore.Signal.__get__(self,instance:PySide6.QtCore.QObject,"
        "owner:Optional[typing.Any])->PySide6.QtCore.SignalInstance",
    nullptr}; // Sentinel

static const char *SignalInstance_SignatureStrings[] = {
    "PySide6.QtCore.SignalInstance.connect(self,slot:object,"
        "type:PySide6.QtCore.Qt.ConnectionType=PySide6.QtCore.Qt.ConnectionType.AutoConnection)"
        "->PySide6.QtCore.QMetaObject.Connection",
    "PySide6.QtCore.SignalInstance.disconnect(self,slot:object=nullptr)->bool",
    "PySide6.QtCore.SignalInstance.emit(self,*args:typing.Any)",
    nullptr}; // Sentinel

void init(PyObject *module)
{
    if (InitSignatureStrings(PySideMetaSignal_TypeF(), MetaSignal_SignatureStrings) < 0)
        return;
    Py_INCREF(PySideMetaSignal_TypeF());
    auto *obMetaSignal_Type = reinterpret_cast<PyObject *>(PySideMetaSignal_TypeF());
    PyModule_AddObject(module, "MetaSignal", obMetaSignal_Type);

    if (InitSignatureStrings(PySideSignal_TypeF(), Signal_SignatureStrings) < 0)
        return;
    Py_INCREF(PySideSignal_TypeF());
    auto *obSignal_Type = reinterpret_cast<PyObject *>(PySideSignal_TypeF());
    PyModule_AddObject(module, "Signal", obSignal_Type);

    if (InitSignatureStrings(PySideSignalInstance_TypeF(), SignalInstance_SignatureStrings) < 0)
        return;
    Py_INCREF(PySideSignalInstance_TypeF());
    auto *obSignalInstance_Type = reinterpret_cast<PyObject *>(PySideSignalInstance_TypeF());
    PyModule_AddObject(module, "SignalInstance", obSignalInstance_Type);
}

bool checkType(PyObject *pyObj)
{
    if (pyObj)
        return PyType_IsSubtype(Py_TYPE(pyObj), PySideSignal_TypeF());
    return false;
}

bool checkInstanceType(PyObject *pyObj)
{
    return pyObj != nullptr
        && PyType_IsSubtype(Py_TYPE(pyObj), PySideSignalInstance_TypeF()) != 0;
}

void updateSourceObject(PyObject *source)
{
    // TODO: Provide for actual upstream exception handling.
    //       For now we'll just return early to avoid further issues.

    if (source == nullptr)      // Bad input
       return;

    Shiboken::AutoDecRef mroIterator(PyObject_GetIter(source->ob_type->tp_mro));

    if (mroIterator.isNull())   // Not iterable
       return;

    Shiboken::AutoDecRef mroItem{};
    auto *dict = SbkObject_GetDict_NoRef(source);

    // PYSIDE-1431: Walk the mro and update. But see PYSIDE-1751 below.
    while ((mroItem.reset(PyIter_Next(mroIterator))), mroItem.object()) {
        Py_ssize_t pos = 0;
        PyObject *key, *value;
        auto *type = reinterpret_cast<PyTypeObject *>(mroItem.object());
        Shiboken::AutoDecRef tpDict(PepType_GetDict(type));
        while (PyDict_Next(tpDict, &pos, &key, &value)) {
            if (PyObject_TypeCheck(value, PySideSignal_TypeF())) {
                // PYSIDE-1751: We only insert an instance into the instance dict, if a signal
                //              of the same name is in the mro. This is the equivalent action
                //              as PyObject_SetAttr, but filtered by existing signal names.
                if (!PyDict_GetItem(dict, key)) {
                    auto *inst = PyObject_New(PySideSignalInstance, PySideSignalInstance_TypeF());
                    Shiboken::AutoDecRef signalInstance(reinterpret_cast<PyObject *>(inst));
                    auto *si = reinterpret_cast<PySideSignalInstance *>(signalInstance.object());
                    instanceInitialize(si, key, reinterpret_cast<PySideSignal *>(value),
                                       source, 0);
                    if (PyDict_SetItem(dict, key, signalInstance) == -1)
                        return;     // An error occurred while setting the attribute
                }
            }
        }
    }

    if (PyErr_Occurred())       // An iteration error occurred
        return;
}

QByteArray getTypeName(PyObject *obType)
{
    if (PyType_Check(obType)) {
        auto *type = reinterpret_cast<PyTypeObject *>(obType);
        if (PyType_IsSubtype(type, SbkObject_TypeF()))
            return Shiboken::ObjectType::getOriginalName(type);
        // Translate Python types to Qt names
        if (Shiboken::String::checkType(type))
            return QByteArrayLiteral("QString");
        if (type == &PyLong_Type)
            return QByteArrayLiteral("int");
        if (type == &PyFloat_Type)
            return QByteArrayLiteral("double");
        if (type == &PyBool_Type)
            return QByteArrayLiteral("bool");
        if (type == &PyList_Type)
            return QByteArrayLiteral("QVariantList");
        if (type == &PyDict_Type)
            return QByteArrayLiteral("QVariantMap");
        return QByteArrayLiteral("PyObject");
    }
    if (obType == Py_None) // Must be checked before as Shiboken::String::check accepts Py_None
        return voidType();
    if (Shiboken::String::check(obType)) {
        QByteArray result = Shiboken::String::toCString(obType);
        if (result == "qreal")
            result = sizeof(qreal) == sizeof(double) ? "double" : "float";
        return result;
    }
    return QByteArray();
}

static QByteArray buildSignature(const QByteArray &name, const QByteArray &signature)
{
    return QMetaObject::normalizedSignature(name + '(' + signature + ')');
}

static PySideSignalData::Signature parseSignature(PyObject *args)
{
    PySideSignalData::Signature result{{}, QMetaMethod::Compatibility, 0};
    if (args && (Shiboken::String::check(args) || !PyTuple_Check(args))) {
        result.signature = getTypeName(args);
        result.argCount = 1;
        return result;
    }

    for (Py_ssize_t i = 0, i_max = PySequence_Size(args); i < i_max; i++) {
        Shiboken::AutoDecRef arg(PySequence_GetItem(args, i));
        const auto typeName = getTypeName(arg);
        if (!typeName.isEmpty()) {
            if (!result.signature.isEmpty())
                result.signature += ',';
            result.signature += typeName;
            ++result.argCount;
        }
    }
    return result;
}

static void sourceGone(void *data)
{
    auto *self = reinterpret_cast<PySideSignalInstance *>(data);
    self->deleted = true;
}

static void instanceInitialize(PySideSignalInstance *self, PyObject *name, PySideSignal *signal, PyObject *source, int index)
{
    self->d = new PySideSignalInstancePrivate;
    self->deleted = false;
    PySideSignalInstancePrivate *selfPvt = self->d;
    selfPvt->next = nullptr;
    if (signal->data->signalName.isEmpty())
        signal->data->signalName = Shiboken::String::toCString(name);
    selfPvt->signalName = signal->data->signalName;

    selfPvt->source = source;
    const auto &signature = signal->data->signatures.at(index);
    selfPvt->signature = buildSignature(self->d->signalName, signature.signature);
    selfPvt->argCount = signature.argCount;
    selfPvt->attributes = signature.attributes;
    selfPvt->homonymousMethod = nullptr;
    if (signal->homonymousMethod) {
        selfPvt->homonymousMethod = signal->homonymousMethod;
        Py_INCREF(selfPvt->homonymousMethod);
    }
    // PYSIDE-2201: We have no reference to source. Let's take a weakref to get
    //              notified when source gets deleted.
    PySide::WeakRef::create(source, sourceGone, self);

    index++;

    if (index < signal->data->signatures.size()) {
        selfPvt->next = PyObject_New(PySideSignalInstance, PySideSignalInstance_TypeF());
        instanceInitialize(selfPvt->next, name, signal, source, index);
    }
}

PySideSignalInstance *initialize(PySideSignal *self, PyObject *name, PyObject *object)
{
    static PyTypeObject *pyQObjectType = Shiboken::Conversions::getPythonTypeObject("QObject*");
    assert(pyQObjectType);

    if (!PyObject_TypeCheck(object, pyQObjectType)) {
        PyErr_Format(PyExc_TypeError, "%s cannot be converted to %s",
                                      Py_TYPE(object)->tp_name, pyQObjectType->tp_name);
        return nullptr;
    }

    PySideSignalInstance *instance = PyObject_New(PySideSignalInstance,
                                                  PySideSignalInstance_TypeF());
    instanceInitialize(instance, name, self, object, 0);
    auto sbkObj = reinterpret_cast<SbkObject *>(object);
    if (!Shiboken::Object::wasCreatedByPython(sbkObj))
        Py_INCREF(object); // PYSIDE-79: this flag was crucial for a wrapper call.
    return instance;
}

bool connect(PyObject *source, const char *signal, PyObject *callback)
{
    Shiboken::AutoDecRef pyMethod(PyObject_GetAttr(source,
                                                   PySide::PySideName::qtConnect()));
    if (pyMethod.isNull())
        return false;

    Shiboken::AutoDecRef pySignature(Shiboken::String::fromCString(signal));
    Shiboken::AutoDecRef pyArgs(PyTuple_Pack(3, source, pySignature.object(), callback));
    PyObject *result =  PyObject_CallObject(pyMethod, pyArgs);
    if (result == Py_False) {
        PyErr_Format(PyExc_RuntimeError, "Failed to connect signal %s, to python callable object.", signal);
        Py_DECREF(result);
        result = nullptr;
    }
    return result;
}

PySideSignalInstance *newObjectFromMethod(PyObject *source, const QList<QMetaMethod>& methodList)
{
    PySideSignalInstance *root = nullptr;
    PySideSignalInstance *previous = nullptr;
    for (const QMetaMethod &m : methodList) {
        PySideSignalInstance *item = PyObject_New(PySideSignalInstance, PySideSignalInstance_TypeF());
        if (!root)
            root = item;

        if (previous)
            previous->d->next = item;

        item->d = new PySideSignalInstancePrivate;
        item->deleted = false;
        PySideSignalInstancePrivate *selfPvt = item->d;
        selfPvt->source = source;
        QByteArray cppName(m.methodSignature());
        cppName.truncate(cppName.indexOf('('));
        // separate SignalName
        selfPvt->signalName = cppName;
        selfPvt->signature = m.methodSignature();
        selfPvt->argCount = int(m.parameterCount());
        selfPvt->attributes = m.attributes();
        selfPvt->homonymousMethod = nullptr;
        selfPvt->next = nullptr;
    }
    return root;
}

static void _addSignalToWrapper(PyTypeObject *wrapperType, const char *signalName, PySideSignal *signal)
{
    Shiboken::AutoDecRef tpDict(PepType_GetDict(wrapperType));
    auto typeDict = tpDict.object();
    PyObject *homonymousMethod;
    if ((homonymousMethod = PyDict_GetItemString(typeDict, signalName))) {
        Py_INCREF(homonymousMethod);
        signal->homonymousMethod = homonymousMethod;
    }
    PyDict_SetItemString(typeDict, signalName, reinterpret_cast<PyObject *>(signal));
}

// This function is used by qStableSort to promote empty signatures
static bool compareSignals(const PySideSignalData::Signature &sig1,
                           const PySideSignalData::Signature &sig2)
{
    return sig1.signature.isEmpty() && !sig2.signature.isEmpty();
}

static PyObject *buildQtCompatible(const QByteArray &signature)
{
    const auto ba = QT_SIGNAL_SENTINEL + signature;
    return Shiboken::String::fromStringAndSize(ba, ba.size());
}

void registerSignals(PyTypeObject *pyObj, const QMetaObject *metaObject)
{
    using Signature = PySideSignalData::Signature;
    struct MetaSignal
    {
        QByteArray methodName;
        QList<Signature> signatures;
    };

    QList<MetaSignal> signalsFound;
    for (int i = metaObject->methodOffset(), max = metaObject->methodCount(); i < max; ++i) {
        QMetaMethod method = metaObject->method(i);

        if (method.methodType() == QMetaMethod::Signal) {
            QByteArray methodName(method.methodSignature());
            methodName.truncate(methodName.indexOf('('));
            Signature signature{method.parameterTypes().join(','), {},
                                short(method.parameterCount())};
            if (method.attributes() & QMetaMethod::Cloned)
                signature.attributes = QMetaMethod::Cloned;
            auto it = std::find_if(signalsFound.begin(), signalsFound.end(),
                                   [methodName](const MetaSignal &ms)
                                   { return ms.methodName == methodName; });
            if (it != signalsFound.end())
                it->signatures << signature;
            else
                signalsFound.append(MetaSignal{methodName, {signature}});
        }
    }

    for (const auto &metaSignal : std::as_const(signalsFound)) {
        PySideSignal *self = PyObject_New(PySideSignal, PySideSignal_TypeF());
        self->data = new PySideSignalData;
        self->data->signalName = metaSignal.methodName;
        self->homonymousMethod = nullptr;

        // Empty signatures comes first! So they will be the default signal signature
        self->data->signatures = metaSignal.signatures;
        std::stable_sort(self->data->signatures.begin(),
                         self->data->signatures.end(), &compareSignals);

        _addSignalToWrapper(pyObj, metaSignal.methodName, self);
        Py_DECREF(reinterpret_cast<PyObject *>(self));
    }
}

PyObject *getObject(PySideSignalInstance *signal)
{
    return signal->d->source;
}

const char *getSignature(PySideSignalInstance *signal)
{
    return signal->d->signature;
}

EmitterData getEmitterData(PySideSignalInstance *signal)
{
    EmitterData result;
    result.emitter = PySide::convertToQObject(getObject(signal), false);
    if (result.emitter != nullptr) {
        auto *mo = result.emitter->metaObject();
        result.methodIndex = mo->indexOfMethod(getSignature(signal));
    }
    return result;
}

QByteArrayList getArgsFromSignature(const char *signature, bool *isShortCircuit)
{
    QByteArray qsignature = QByteArray(signature).trimmed();
    QByteArrayList result;

    if (isShortCircuit)
        *isShortCircuit = !qsignature.contains(u'(');
    if (qsignature.contains("()") || qsignature.contains("(void)"))
        return result;
    if (qsignature.endsWith(')')) {
        const auto paren = qsignature.indexOf('(');
        if (paren >= 0) {
            qsignature.chop(1);
            qsignature.remove(0, paren + 1);
            result = qsignature.split(u',');
            for (auto &type : result)
                type = type.trimmed();
        }
    }
    return result;
}

QByteArray getCallbackSignature(const char *signal, QObject *receiver,
                                PyObject *callback, bool encodeName)
{
    QByteArray functionName;
    qsizetype numArgs = -1;

    const auto slotArgs = extractFunctionArgumentsFromSlot(callback);
    qsizetype useSelf = slotArgs.isMethod ? 1 : 0;

    if (slotArgs.function != nullptr) {
        numArgs = argCount(slotArgs).max;
#ifdef PYPY_VERSION
    } else if (Py_TYPE(callback) == PepBuiltinMethod_TypePtr) {
        // PYSIDE-535: PyPy has a special builtin method that acts almost like PyCFunction.
        Shiboken::AutoDecRef temp(PyObject_GetAttr(callback, Shiboken::PyMagicName::name()));
        functionName = Shiboken::String::toCString(temp);
        useSelf = true;

        if (receiver) {
            // Search for signature on metaobject
            const QMetaObject *mo = receiver->metaObject();
            QByteArray prefix(functionName);
            prefix += '(';
            for (int i = 0; i < mo->methodCount(); i++) {
                QMetaMethod me = mo->method(i);
                if ((strncmp(me.methodSignature(), prefix, prefix.size()) == 0) &&
                    QMetaObject::checkConnectArgs(signal, me.methodSignature())) {
                    numArgs = me.parameterTypes().size() + useSelf;
                    break;
                }
           }
        }
#endif
    } else if (PyCFunction_Check(callback)) {
        const PyCFunctionObject *funcObj = reinterpret_cast<const PyCFunctionObject *>(callback);
        functionName = PepCFunction_GET_NAMESTR(funcObj);
        useSelf = PyCFunction_GET_SELF(funcObj) != nullptr ? 1 : 0;
        const int flags = PyCFunction_GET_FLAGS(funcObj);

        if (receiver) {
            // Search for signature on metaobject
            const QMetaObject *mo = receiver->metaObject();
            QByteArray prefix(functionName);
            prefix += '(';
            for (int i = 0, count = mo->methodCount(); i < count; ++i) {
                QMetaMethod me = mo->method(i);
                if ((strncmp(me.methodSignature(), prefix, prefix.size()) == 0) &&
                    QMetaObject::checkConnectArgs(signal, me.methodSignature())) {
                    numArgs = me.parameterTypes().size() + useSelf;
                    break;
                }
           }
        }

        if (numArgs == -1) {
            if (flags & METH_VARARGS)
                numArgs = -1;
            else if (flags & METH_NOARGS)
                numArgs = 0;
        }
    } else if (PyCallable_Check(callback)) {
        functionName = "__callback" + QByteArray::number(quintptr(callback));
    }

    if (functionName.isEmpty() && slotArgs.functionName != nullptr)
        functionName = Shiboken::String::toCString(slotArgs.functionName);
    Q_ASSERT(!functionName.isEmpty());

    bool isShortCircuit = false;

    if (functionName.startsWith('<') && functionName.endsWith('>')) { // fix "<lambda>"
        functionName[0] = '_';
        functionName[functionName.size() - 1] = '_';
    }
    QByteArray signature = encodeName ? codeCallbackName(callback, functionName) : functionName;
    QByteArrayList args = getArgsFromSignature(signal, &isShortCircuit);

    if (!isShortCircuit) {
        signature.append(u'(');
        if (numArgs == -1)
            numArgs = std::numeric_limits<qsizetype>::max();
        while (!args.isEmpty() && (args.size() > (numArgs - useSelf)))
            args.removeLast();
        signature.append(args.join(','));
        signature.append(')');
    }
    return signature;
}

bool isQtSignal(const char *signal)
{
    return (signal && signal[0] == QT_SIGNAL_SENTINEL);
}

bool checkQtSignal(const char *signal)
{
    if (!isQtSignal(signal)) {
        PyErr_SetString(PyExc_TypeError, "Use the function PySide6.QtCore.SIGNAL on signals");
        return false;
    }
    return true;
}

QByteArray codeCallbackName(PyObject *callback, const QByteArray &funcName)
{
    if (PyMethod_Check(callback)) {
        PyObject *self = PyMethod_GET_SELF(callback);
        PyObject *func = PyMethod_GET_FUNCTION(callback);
        return funcName + QByteArray::number(quint64(self), 16) + QByteArray::number(quint64(func), 16);
    }
    // PYSIDE-1523: Handle the compiled case.
    if (PySide::isCompiledMethod(callback)) {
        // Not retaining references inline with what PyMethod_GET_(SELF|FUNC) does.
        Shiboken::AutoDecRef self(PyObject_GetAttr(callback, PySide::PySideName::im_self()));
        Shiboken::AutoDecRef func(PyObject_GetAttr(callback, PySide::PySideName::im_func()));
        return funcName + QByteArray::number(quint64(self), 16) + QByteArray::number(quint64(func), 16);
    }
    return funcName + QByteArray::number(quint64(callback), 16);
}

QByteArray voidType()
{
    return QByteArrayLiteral("void");
}

} //namespace PySide::Signal
