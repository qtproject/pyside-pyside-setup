/****************************************************************************
**
** Copyright (C) 2020 The Qt Company Ltd.
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
#include "pysidesignal.h"
#include "pysidesignal_p.h"
#include "pyside_p.h"
#include "pysidestaticstrings.h"
#include "signalmanager.h"

#include <shiboken.h>

#include <QtCore/QObject>
#include <QtCore/QMetaMethod>
#include <QtCore/QMetaObject>
#include <signature.h>

#include <algorithm>
#include <utility>
#include <cstring>

#define QT_SIGNAL_SENTINEL '2'

static bool connection_Check(PyObject *o)
{
    if (o == nullptr || o == Py_None)
        return false;
    static QByteArray typeName = QByteArrayLiteral("PySide")
        + QByteArray::number(QT_VERSION_MAJOR)
        + QByteArrayLiteral(".QtCore.QMetaObject.Connection");
    return std::strcmp(o->ob_type->tp_name, typeName.constData()) == 0;
}

namespace PySide {
namespace Signal {
    //aux
    class SignalSignature {
    public:
        SignalSignature() = default;
        explicit SignalSignature(QByteArray parameterTypes) :
            m_parameterTypes(std::move(parameterTypes)) {}
        explicit SignalSignature(QByteArray parameterTypes, QMetaMethod::Attributes attributes) :
            m_parameterTypes(std::move(parameterTypes)),
            m_attributes(attributes) {}

        QByteArray m_parameterTypes;
        QMetaMethod::Attributes m_attributes = QMetaMethod::Compatibility;
    };

    static QByteArray buildSignature(const QByteArray &, const QByteArray &);
    static void appendSignature(PySideSignal *, const SignalSignature &);
    static void instanceInitialize(PySideSignalInstance *, PyObject *, PySideSignal *, PyObject *, int);
    static QByteArray parseSignature(PyObject *);
    static PyObject *buildQtCompatible(const QByteArray &);
}
}

extern "C"
{

// Signal methods
static int signalTpInit(PyObject *, PyObject *, PyObject *);
static void signalFree(void *);
static void signalInstanceFree(void *);
static PyObject *signalGetItem(PyObject *self, PyObject *key);
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


static PyMethodDef MetaSignal_methods[] = {
    {"__instancecheck__", reinterpret_cast<PyCFunction>(metaSignalCheck),
                          METH_O|METH_STATIC, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static PyType_Slot PySideMetaSignalType_slots[] = {
    {Py_tp_methods, reinterpret_cast<void *>(MetaSignal_methods)},
    {Py_tp_base,    reinterpret_cast<void *>(&PyType_Type)},
    {Py_tp_free,    reinterpret_cast<void *>(PyObject_GC_Del)},
    {Py_tp_dealloc, reinterpret_cast<void *>(Sbk_object_dealloc)},
    {0, nullptr}
};
static PyType_Spec PySideMetaSignalType_spec = {
    "2:PySide6.QtCore.MetaSignal",
    0,
    // sizeof(PyHeapTypeObject) is filled in by SbkType_FromSpec
    // which calls PyType_Ready which calls inherit_special.
    0,
    Py_TPFLAGS_DEFAULT,
    PySideMetaSignalType_slots,
};


static PyTypeObject *PySideMetaSignalTypeF(void)
{
    static auto *type = SbkType_FromSpec(&PySideMetaSignalType_spec);
    return type;
}

static PyType_Slot PySideSignalType_slots[] = {
    {Py_mp_subscript,   reinterpret_cast<void *>(signalGetItem)},
    {Py_tp_descr_get,   reinterpret_cast<void *>(signalDescrGet)},
    {Py_tp_call,        reinterpret_cast<void *>(signalCall)},
    {Py_tp_str,         reinterpret_cast<void *>(signalToString)},
    {Py_tp_init,        reinterpret_cast<void *>(signalTpInit)},
    {Py_tp_new,         reinterpret_cast<void *>(PyType_GenericNew)},
    {Py_tp_free,        reinterpret_cast<void *>(signalFree)},
    {Py_tp_dealloc,     reinterpret_cast<void *>(Sbk_object_dealloc)},
    {0, nullptr}
};
static PyType_Spec PySideSignalType_spec = {
    "2:PySide6.QtCore.Signal",
    sizeof(PySideSignal),
    0,
    Py_TPFLAGS_DEFAULT,
    PySideSignalType_slots,
};


PyTypeObject *PySideSignalTypeF(void)
{
    static auto *type = SbkType_FromSpecWithMeta(&PySideSignalType_spec, PySideMetaSignalTypeF());
    return type;
}

static PyObject *signalInstanceRepr(PyObject *self)
{
    auto *data = reinterpret_cast<PySideSignalInstance *>(self);
    auto *typeName = Py_TYPE(self)->tp_name;
    return Shiboken::String::fromFormat("<%s %s at %p>", typeName,
                                        data->d->signature.constData(), self);
}

static PyMethodDef SignalInstance_methods[] = {
    {"connect", reinterpret_cast<PyCFunction>(signalInstanceConnect),
                METH_VARARGS|METH_KEYWORDS, nullptr},
    {"disconnect", signalInstanceDisconnect, METH_VARARGS, nullptr},
    {"emit", signalInstanceEmit, METH_VARARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}  /* Sentinel */
};

static PyType_Slot PySideSignalInstanceType_slots[] = {
    {Py_mp_subscript,   reinterpret_cast<void *>(signalInstanceGetItem)},
    {Py_tp_call,        reinterpret_cast<void *>(signalInstanceCall)},
    {Py_tp_methods,     reinterpret_cast<void *>(SignalInstance_methods)},
    {Py_tp_repr,        reinterpret_cast<void *>(signalInstanceRepr)},
    {Py_tp_new,         reinterpret_cast<void *>(PyType_GenericNew)},
    {Py_tp_free,        reinterpret_cast<void *>(signalInstanceFree)},
    {Py_tp_dealloc,     reinterpret_cast<void *>(Sbk_object_dealloc)},
    {0, nullptr}
};
static PyType_Spec PySideSignalInstanceType_spec = {
    "2:PySide6.QtCore.SignalInstance",
    sizeof(PySideSignalInstance),
    0,
    Py_TPFLAGS_DEFAULT,
    PySideSignalInstanceType_slots,
};


PyTypeObject *PySideSignalInstanceTypeF(void)
{
    static auto *type = SbkType_FromSpec(&PySideSignalInstanceType_spec);
    return type;
}

static int signalTpInit(PyObject *self, PyObject *args, PyObject *kwds)
{
    static PyObject * const emptyTuple = PyTuple_New(0);
    static const char *kwlist[] = {"name", "arguments", nullptr};
    char *argName = nullptr;
    PyObject *argArguments = nullptr;

    if (!PyArg_ParseTupleAndKeywords(emptyTuple, kwds,
        "|sO:QtCore.Signal", const_cast<char **>(kwlist), &argName, &argArguments))
        return -1;

    bool tupledArgs = false;
    PySideSignal *data = reinterpret_cast<PySideSignal *>(self);
    if (!data->data)
        data->data = new PySideSignalData;
    if (argName)
        data->data->signalName = argName;

    const Py_ssize_t argument_size =
        argArguments != nullptr && PySequence_Check(argArguments)
        ? PySequence_Size(argArguments) : 0;
    if (argument_size > 0) {
        data->data->signalArguments = new QByteArrayList();
        data->data->signalArguments->reserve(argument_size);
        for (Py_ssize_t i = 0; i < argument_size; ++i) {
            Shiboken::AutoDecRef item(PySequence_GetItem(argArguments, i));
            Shiboken::AutoDecRef strObj(PyUnicode_AsUTF8String(item));
            if (char *s = PyBytes_AsString(strObj))
                data->data->signalArguments->append(QByteArray(s));
        }
    }

    for (Py_ssize_t i = 0, i_max = PyTuple_Size(args); i < i_max; i++) {
        PyObject *arg = PyTuple_GET_ITEM(args, i);
        if (PySequence_Check(arg) && !Shiboken::String::check(arg) && !PyEnumMeta_Check(arg)) {
            tupledArgs = true;
            const auto sig = PySide::Signal::parseSignature(arg);
            PySide::Signal::appendSignature(
                        data,
                        PySide::Signal::SignalSignature(sig));
        }
    }

    if (!tupledArgs) {
        const auto sig = PySide::Signal::parseSignature(args);
        PySide::Signal::appendSignature(
                    data,
                    PySide::Signal::SignalSignature(sig));
    }

    return 0;
}

static void signalFree(void *self)
{
    auto pySelf = reinterpret_cast<PyObject *>(self);
    auto data = reinterpret_cast<PySideSignal *>(self);
    delete data->data->signalArguments;
    delete data->data;
    data->data = nullptr;
    Py_XDECREF(data->homonymousMethod);
    data->homonymousMethod = nullptr;

    Py_TYPE(pySelf)->tp_base->tp_free(self);
}

static PyObject *signalGetItem(PyObject *self, PyObject *key)
{
    auto data = reinterpret_cast<PySideSignal *>(self);
    QByteArray sigKey;
    if (key) {
        sigKey = PySide::Signal::parseSignature(key);
    } else {
        sigKey = data->data == nullptr || data->data->signatures.isEmpty()
            ? PySide::Signal::voidType() : data->data->signatures.constFirst().signature;
    }
    auto sig = PySide::Signal::buildSignature(data->data->signalName, sigKey);
    return Shiboken::String::fromCString(sig.constData());
}


static PyObject *signalToString(PyObject *self)
{
    return signalGetItem(self, nullptr);
}

static void signalInstanceFree(void *self)
{
    auto pySelf = reinterpret_cast<PyObject *>(self);
    auto data = reinterpret_cast<PySideSignalInstance *>(self);

    PySideSignalInstancePrivate *dataPvt = data->d;

    Py_XDECREF(dataPvt->homonymousMethod);

    if (dataPvt->next) {
        Py_DECREF(dataPvt->next);
        dataPvt->next = nullptr;
    }
    delete dataPvt;
    data->d = nullptr;
    Py_TYPE(pySelf)->tp_base->tp_free(self);
}

// PYSIDE-1523: PyFunction_Check is not accepting compiled functions and
// PyMethod_Check is not allowing compiled methods, therefore also lookup
// "im_func" and "__code__" attributes, we allow for that with a dedicated
// function handling both.
static void extractFunctionArgumentsFromSlot(PyObject *slot,
                                             PyObject *& function,
                                             PepCodeObject *& objCode,
                                             bool &isMethod,
                                             QByteArray *functionName)
{
    isMethod = PyMethod_Check(slot);
    bool isFunction = PyFunction_Check(slot);

    function = nullptr;
    objCode = nullptr;

    if (isMethod || isFunction) {
        function = isMethod ? PyMethod_GET_FUNCTION(slot) : slot;
        objCode = reinterpret_cast<PepCodeObject *>(PyFunction_GET_CODE(function));

        if (functionName != nullptr) {
            *functionName = Shiboken::String::toCString(PepFunction_GetName(function));
        }
    } else if (PySide::_isCompiledMethod(slot)) {
        // PYSIDE-1523: PyFunction_Check and PyMethod_Check are not accepting compiled forms, we
        // just go by attributes.
        isMethod = true;

        function = PyObject_GetAttr(slot, PySide::PyName::im_func());

        // Not retaining a reference inline with what PyMethod_GET_FUNCTION does.
        Py_DECREF(function);

        if (functionName != nullptr) {
            PyObject *name = PyObject_GetAttr(function, PySide::PyMagicName::name());
            *functionName = Shiboken::String::toCString(name);
            // Not retaining a reference inline with what PepFunction_GetName does.
            Py_DECREF(name);
        }

        objCode = reinterpret_cast<PepCodeObject *>(
                    PyObject_GetAttr(function, PySide::PyMagicName::code()));
        // Not retaining a reference inline with what PyFunction_GET_CODE does.
        Py_XDECREF(objCode);

        if (objCode == nullptr) {
            // Should not happen, but lets handle it gracefully, maybe Nuitka one day
            // makes these optional, or somebody defined a type named like it without
            // it being actually being that.
            function = nullptr;
        }
    } else if (strcmp(Py_TYPE(slot)->tp_name, "compiled_function") == 0) {
        isMethod = false;
        function = slot;

        if (functionName != nullptr) {
            PyObject *name = PyObject_GetAttr(function, PySide::PyMagicName::name());
            *functionName = Shiboken::String::toCString(name);
            // Not retaining a reference inline with what PepFunction_GetName does.
            Py_DECREF(name);
        }

        objCode = reinterpret_cast<PepCodeObject *>(
                    PyObject_GetAttr(function, PySide::PyMagicName::code()));
        // Not retaining a reference inline with what PyFunction_GET_CODE does.
        Py_XDECREF(objCode);

        if (objCode == nullptr) {
            // Should not happen, but lets handle it gracefully, maybe Nuitka one day
            // makes these optional, or somebody defined a type named like it without
            // it being actually being that.
            function = nullptr;
        }
    }
    // any other callback
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
    Shiboken::AutoDecRef pyArgs(PyList_New(0));

    bool match = false;
    if (Py_TYPE(slot) == PySideSignalInstanceTypeF()) {
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
        int slotArgs = -1;
        bool matchedSlot = false;

        PySideSignalInstance *it = source;

        PyObject *function = nullptr;
        PepCodeObject *objCode = nullptr;
        bool useSelf = false;

        extractFunctionArgumentsFromSlot(slot, function, objCode, useSelf, nullptr);

        if (function != nullptr) {
            slotArgs = PepCode_GET_FLAGS(objCode) & CO_VARARGS ? -1 : PepCode_GET_ARGCOUNT(objCode);
            if (useSelf)
                slotArgs -= 1;

            // Get signature args
            bool isShortCircuit = false;
            int signatureArgs = 0;
            QStringList argsSignature;

            argsSignature = PySide::Signal::getArgsFromSignature(it->d->signature,
                &isShortCircuit);
            signatureArgs = argsSignature.length();

            // Iterate the possible types of connection for this signal and compare
            // it with slot arguments
            if (signatureArgs != slotArgs) {
                while (it->d->next != nullptr) {
                    it = it->d->next;
                    argsSignature = PySide::Signal::getArgsFromSignature(it->d->signature,
                        &isShortCircuit);
                    signatureArgs = argsSignature.length();
                    if (signatureArgs == slotArgs) {
                        matchedSlot = true;
                        break;
                    }
                }
            }
        }

        // Adding references to pyArgs
        PyList_Append(pyArgs, source->d->source);

        if (matchedSlot) {
            // If a slot matching the same number of arguments was found,
            // include signature to the pyArgs
            Shiboken::AutoDecRef signature(PySide::Signal::buildQtCompatible(it->d->signature));
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
                                                       PySide::PyName::qtConnect()));
        if (pyMethod.isNull()) { // PYSIDE-79: check if pyMethod exists.
            PyErr_SetString(PyExc_RuntimeError, "method 'connect' vanished!");
            return nullptr;
        }
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
                                                   PySide::PyName::qtEmit()));

    Shiboken::AutoDecRef tupleArgs(PyList_AsTuple(pyArgs));
    return PyObject_CallObject(pyMethod.object(), tupleArgs);
}

static PyObject *signalInstanceGetItem(PyObject *self, PyObject *key)
{
    auto data = reinterpret_cast<PySideSignalInstance *>(self);
    const auto sigName = data->d->signalName;
    const auto sigKey = PySide::Signal::parseSignature(key);
    const auto sig = PySide::Signal::buildSignature(sigName, sigKey);
    while (data) {
        if (data->d->signature == sig) {
            PyObject *result = reinterpret_cast<PyObject *>(data);
            Py_INCREF(result);
            return result;
        }
        data = data->d->next;
    }

    PyErr_Format(PyExc_IndexError, "Signature %s not found for signal: %s",
                 sig.constData(), sigName.constData());
    return nullptr;
}

static PyObject *signalInstanceDisconnect(PyObject *self, PyObject *args)
{
    auto source = reinterpret_cast<PySideSignalInstance *>(self);
    Shiboken::AutoDecRef pyArgs(PyList_New(0));

    PyObject *slot = Py_None;
    if (PyTuple_Check(args) && PyTuple_GET_SIZE(args))
        slot = PyTuple_GET_ITEM(args, 0);

    bool match = false;
    if (Py_TYPE(slot) == PySideSignalInstanceTypeF()) {
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
                                                       PySide::PyName::qtDisconnect()));
        PyObject *result = PyObject_CallObject(pyMethod, tupleArgs);
        if (!result || result == Py_True)
            return result;
        Py_DECREF(result);
    }

    PyErr_Format(PyExc_RuntimeError, "Failed to disconnect signal %s.",
                 source->d->signature.constData());
    return nullptr;
}

// PYSIDE-68: Supply the missing __get__ function
static PyObject *signalDescrGet(PyObject *self, PyObject *obj, PyObject * /*type*/)
{
    auto signal = reinterpret_cast<PySideSignal *>(self);
    // Return the unbound signal if there is nothing to bind it to.
    if (obj == nullptr || obj == Py_None) {
        Py_INCREF(self);
        return self;
    }
    Shiboken::AutoDecRef name(Py_BuildValue("s", signal->data->signalName.data()));
    return reinterpret_cast<PyObject *>(PySide::Signal::initialize(signal, name, obj));
}

static PyObject *signalCall(PyObject *self, PyObject *args, PyObject *kw)
{
    auto signal = reinterpret_cast<PySideSignal *>(self);

    // Native C++ signals can't be called like functions, thus we throw an exception.
    // The only way calling a signal can succeed (the Python equivalent of C++'s operator() )
    // is when a method with the same name as the signal is attached to an object.
    // An example is QProcess::error() (don't check the docs, but the source code of qprocess.h).
    if (!signal->homonymousMethod) {
        PyErr_SetString(PyExc_TypeError, "native Qt signal is not callable");
        return nullptr;
    }

    descrgetfunc getDescriptor = Py_TYPE(signal->homonymousMethod)->tp_descr_get;

    // Check if there exists a method with the same name as the signal, which is also a static
    // method in C++ land.
    Shiboken::AutoDecRef homonymousMethod(getDescriptor(signal->homonymousMethod,
                                                        nullptr, nullptr));
    if (PyCFunction_Check(homonymousMethod.object())
            && (PyCFunction_GET_FLAGS(homonymousMethod.object()) & METH_STATIC))
        return PyObject_Call(homonymousMethod, args, kw);

    // Assumes homonymousMethod is not a static method.
    ternaryfunc callFunc = Py_TYPE(signal->homonymousMethod)->tp_call;
    return callFunc(homonymousMethod, args, kw);
}

// This function returns a borrowed reference.
static inline PyObject *_getRealCallable(PyObject *func)
{
    static const auto *SignalType = PySideSignalTypeF();
    static const auto *SignalInstanceType = PySideSignalInstanceTypeF();

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
    Py_ssize_t idx, n = PyTuple_GET_SIZE(mro);

    for (idx = 0; idx < n; idx++) {
        auto *sub_type = reinterpret_cast<PyTypeObject *>(PyTuple_GET_ITEM(mro, idx));
        auto *hom = PyDict_GetItem(sub_type->tp_dict, name);
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

    descrgetfunc getDescriptor = Py_TYPE(hom)->tp_descr_get;
    Shiboken::AutoDecRef homonymousMethod(getDescriptor(hom, PySideSignal->d->source, nullptr));
    return PyObject_Call(homonymousMethod, args, kw);
}

static PyObject *metaSignalCheck(PyObject * /* klass */, PyObject *arg)
{
    if (PyType_IsSubtype(Py_TYPE(arg), PySideSignalInstanceTypeF()))
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

} // extern "C"

namespace PySide {
namespace Signal {

static const char *MetaSignal_SignatureStrings[] = {
    "PySide6.QtCore.MetaSignal.__instancecheck__(self,object:object)->bool",
    nullptr}; // Sentinel

static const char *Signal_SignatureStrings[] = {
    "PySide6.QtCore.Signal(self,*types:type,name:str=nullptr,arguments:str=nullptr)",
    "1:PySide6.QtCore.Signal.__get__(self,instance:None,owner:Optional[typing.Any])->PySide6.QtCore.Signal",
    "0:PySide6.QtCore.Signal.__get__(self,instance:PySide6.QtCore.QObject,owner:Optional[typing.Any])->PySide6.QtCore.SignalInstance",
    nullptr}; // Sentinel

static const char *SignalInstance_SignatureStrings[] = {
    "PySide6.QtCore.SignalInstance.connect(self,slot:object,type:type=nullptr)",
    "PySide6.QtCore.SignalInstance.disconnect(self,slot:object=nullptr)",
    "PySide6.QtCore.SignalInstance.emit(self,*args:typing.Any)",
    nullptr}; // Sentinel

void init(PyObject *module)
{
    if (InitSignatureStrings(PySideMetaSignalTypeF(), MetaSignal_SignatureStrings) < 0)
        return;
    Py_INCREF(PySideMetaSignalTypeF());
    PyModule_AddObject(module, "MetaSignal", reinterpret_cast<PyObject *>(PySideMetaSignalTypeF()));

    if (InitSignatureStrings(PySideSignalTypeF(), Signal_SignatureStrings) < 0)
        return;
    Py_INCREF(PySideSignalTypeF());
    PyModule_AddObject(module, "Signal", reinterpret_cast<PyObject *>(PySideSignalTypeF()));

    if (InitSignatureStrings(PySideSignalInstanceTypeF(), SignalInstance_SignatureStrings) < 0)
        return;
    Py_INCREF(PySideSignalInstanceTypeF());
    PyModule_AddObject(module, "SignalInstance", reinterpret_cast<PyObject *>(PySideSignalInstanceTypeF()));
}

bool checkType(PyObject *pyObj)
{
    if (pyObj)
        return PyType_IsSubtype(Py_TYPE(pyObj), PySideSignalTypeF());
    return false;
}

bool checkInstanceType(PyObject *pyObj)
{
    return pyObj != nullptr
        && PyType_IsSubtype(Py_TYPE(pyObj), PySideSignalInstanceTypeF()) != 0;
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

    while ((mroItem.reset(PyIter_Next(mroIterator))), mroItem.object()) {
        Py_ssize_t pos = 0;
        PyObject *key, *value;
        auto *type = reinterpret_cast<PyTypeObject *>(mroItem.object());

        while (PyDict_Next(type->tp_dict, &pos, &key, &value)) {
            if (PyObject_TypeCheck(value, PySideSignalTypeF())) {
                auto *inst = PyObject_New(PySideSignalInstance, PySideSignalInstanceTypeF());
                Shiboken::AutoDecRef signalInstance(reinterpret_cast<PyObject *>(inst));
                instanceInitialize(signalInstance.cast<PySideSignalInstance *>(),
                                   key, reinterpret_cast<PySideSignal *>(value), source, 0);
                if (PyObject_SetAttr(source, key, signalInstance) == -1)
                    return;     // An error occurred while setting the attribute
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
        if (Py_TYPE(type) == SbkEnumType_TypeF())
            return Shiboken::Enum::getCppName(type);
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

static QByteArray parseSignature(PyObject *args)
{
    if (args && (Shiboken::String::check(args) || !PySequence_Check(args)))
        return getTypeName(args);

    QByteArray signature;
    for (Py_ssize_t i = 0, i_max = PySequence_Size(args); i < i_max; i++) {
        Shiboken::AutoDecRef arg(PySequence_GetItem(args, i));
        const auto typeName = getTypeName(arg);
        if (!typeName.isEmpty()) {
            if (!signature.isEmpty())
                signature += ',';
            signature += typeName;
        }
    }
    return signature;
}

static void appendSignature(PySideSignal *self, const SignalSignature &signature)
{
    self->data->signatures.append({signature.m_parameterTypes, signature.m_attributes});
}

static void instanceInitialize(PySideSignalInstance *self, PyObject *name, PySideSignal *data, PyObject *source, int index)
{
    self->d = new PySideSignalInstancePrivate;
    PySideSignalInstancePrivate *selfPvt = self->d;
    selfPvt->next = nullptr;
    if (data->data->signalName.isEmpty())
        data->data->signalName = Shiboken::String::toCString(name);
    selfPvt->signalName = data->data->signalName;

    selfPvt->source = source;
    const auto &signature = data->data->signatures.at(index);
    selfPvt->signature = buildSignature(self->d->signalName, signature.signature);
    selfPvt->attributes = signature.attributes;
    selfPvt->homonymousMethod = nullptr;
    if (data->homonymousMethod) {
        selfPvt->homonymousMethod = data->homonymousMethod;
        Py_INCREF(selfPvt->homonymousMethod);
    }
    index++;

    if (index < data->data->signatures.size()) {
        selfPvt->next = PyObject_New(PySideSignalInstance, PySideSignalInstanceTypeF());
        instanceInitialize(selfPvt->next, name, data, source, index);
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
                                                  PySideSignalInstanceTypeF());
    instanceInitialize(instance, name, self, object, 0);
    auto sbkObj = reinterpret_cast<SbkObject *>(object);
    if (!Shiboken::Object::wasCreatedByPython(sbkObj))
        Py_INCREF(object); // PYSIDE-79: this flag was crucial for a wrapper call.
    return instance;
}

bool connect(PyObject *source, const char *signal, PyObject *callback)
{
    Shiboken::AutoDecRef pyMethod(PyObject_GetAttr(source,
                                                   PySide::PyName::qtConnect()));
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
        PySideSignalInstance *item = PyObject_New(PySideSignalInstance, PySideSignalInstanceTypeF());
        if (!root)
            root = item;

        if (previous)
            previous->d->next = item;

        item->d = new PySideSignalInstancePrivate;
        PySideSignalInstancePrivate *selfPvt = item->d;
        selfPvt->source = source;
        Py_INCREF(selfPvt->source); // PYSIDE-79: an INCREF is missing.
        QByteArray cppName(m.methodSignature());
        cppName.truncate(cppName.indexOf('('));
        // separe SignalName
        selfPvt->signalName = cppName;
        selfPvt->signature = m.methodSignature();
        selfPvt->attributes = m.attributes();
        selfPvt->homonymousMethod = nullptr;
        selfPvt->next = nullptr;
    }
    return root;
}

template<typename T>
static typename T::value_type join(T t, const char *sep)
{
    typename T::value_type res;
    if (t.isEmpty())
        return res;

    typename T::const_iterator it = t.begin();
    typename T::const_iterator end = t.end();
    res += *it;
    ++it;

    while (it != end) {
        res += sep;
        res += *it;
        ++it;
    }
    return res;
}

static void _addSignalToWrapper(PyTypeObject *wrapperType, const char *signalName, PySideSignal *signal)
{
    auto typeDict = wrapperType->tp_dict;
    PyObject *homonymousMethod;
    if ((homonymousMethod = PyDict_GetItemString(typeDict, signalName))) {
        Py_INCREF(homonymousMethod);
        signal->homonymousMethod = homonymousMethod;
    }
    PyDict_SetItemString(typeDict, signalName, reinterpret_cast<PyObject *>(signal));
}

// This function is used by qStableSort to promote empty signatures
static bool compareSignals(const SignalSignature &sig1, const SignalSignature &)
{
    return sig1.m_parameterTypes.isEmpty();
}

static PyObject *buildQtCompatible(const QByteArray &signature)
{
    const auto ba = QT_SIGNAL_SENTINEL + signature;
    return Shiboken::String::fromStringAndSize(ba, ba.size());
}

void registerSignals(PyTypeObject *pyObj, const QMetaObject *metaObject)
{
    using SignalSigMap = QHash<QByteArray, QList<SignalSignature> >;
    SignalSigMap signalsFound;
    for (int i = metaObject->methodOffset(), max = metaObject->methodCount(); i < max; ++i) {
        QMetaMethod method = metaObject->method(i);

        if (method.methodType() == QMetaMethod::Signal) {
            QByteArray methodName(method.methodSignature());
            methodName.chop(methodName.size() - methodName.indexOf('('));
            SignalSignature signature;
            signature.m_parameterTypes = join(method.parameterTypes(), ",");
            if (method.attributes() & QMetaMethod::Cloned)
                signature.m_attributes = QMetaMethod::Cloned;
            signalsFound[methodName] << signature;
        }
    }

    SignalSigMap::Iterator it = signalsFound.begin();
    SignalSigMap::Iterator end = signalsFound.end();
    for (; it != end; ++it) {
        PySideSignal *self = PyObject_New(PySideSignal, PySideSignalTypeF());
        self->data = new PySideSignalData;
        self->data->signalName = it.key();
        self->homonymousMethod = nullptr;

        // Empty signatures comes first! So they will be the default signal signature
        std::stable_sort(it.value().begin(), it.value().end(), &compareSignals);
        const auto endJ = it.value().cend();
        for (auto j = it.value().cbegin(); j != endJ; ++j) {
            const SignalSignature &sig = *j;
            appendSignature(self, sig);
        }

        _addSignalToWrapper(pyObj, it.key(), self);
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

QStringList getArgsFromSignature(const char *signature, bool *isShortCircuit)
{
    QString qsignature = QString::fromLatin1(signature).trimmed();
    QStringList result;

    if (isShortCircuit)
        *isShortCircuit = !qsignature.contains(u'(');
    if (qsignature.contains(u"()") || qsignature.contains(u"(void)"))
        return result;
    if (qsignature.endsWith(u')')) {
        const int paren = qsignature.indexOf(u'(');
        if (paren >= 0) {
            qsignature.chop(1);
            qsignature.remove(0, paren + 1);
            result = qsignature.split(u',');
            for (QString &type : result)
                type = type.trimmed();
        }
    }
    return result;
}

QString getCallbackSignature(const char *signal, QObject *receiver, PyObject *callback, bool encodeName)
{
    QByteArray functionName;
    qsizetype numArgs = -1;

    PyObject *function = nullptr;
    PepCodeObject *objCode = nullptr;
    bool useSelf = false;

    extractFunctionArgumentsFromSlot(callback, function, objCode, useSelf, &functionName);

    if (function != nullptr) {
        numArgs = PepCode_GET_FLAGS(objCode) & CO_VARARGS ? -1 : PepCode_GET_ARGCOUNT(objCode);
    } else if (PyCFunction_Check(callback)) {
        const PyCFunctionObject *funcObj = reinterpret_cast<const PyCFunctionObject *>(callback);
        functionName = PepCFunction_GET_NAMESTR(funcObj);
        useSelf = PyCFunction_GET_SELF(funcObj);
        const int flags = PyCFunction_GET_FLAGS(funcObj);

        if (receiver) {
            //Search for signature on metaobject
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

        if (numArgs == -1) {
            if (flags & METH_VARARGS)
                numArgs = -1;
            else if (flags & METH_NOARGS)
                numArgs = 0;
        }
    } else if (PyCallable_Check(callback)) {
        functionName = "__callback" + QByteArray::number((qlonglong)callback);
    }

    Q_ASSERT(!functionName.isEmpty());

    bool isShortCircuit = false;

    const QString functionNameS = QLatin1String(functionName);
    QString signature = encodeName ? codeCallbackName(callback, functionNameS) : functionNameS;
    QStringList args = getArgsFromSignature(signal, &isShortCircuit);

    if (!isShortCircuit) {
        signature.append(u'(');
        if (numArgs == -1)
            numArgs = std::numeric_limits<qsizetype>::max();
        while (!args.isEmpty() && (args.size() > (numArgs - useSelf)))
            args.removeLast();
        signature.append(args.join(u','));
        signature.append(u')');
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

QString codeCallbackName(PyObject *callback, const QString &funcName)
{
    if (PyMethod_Check(callback)) {
        PyObject *self = PyMethod_GET_SELF(callback);
        PyObject *func = PyMethod_GET_FUNCTION(callback);
        return funcName + QString::number(quint64(self), 16) + QString::number(quint64(func), 16);
    }
    // PYSIDE-1523: Handle the compiled case.
    if (PySide::_isCompiledMethod(callback)) {
        // Not retaining references inline with what PyMethod_GET_(SELF|FUNC) does.
        Shiboken::AutoDecRef self(PyObject_GetAttr(callback, PySide::PyName::im_self()));
        Shiboken::AutoDecRef func(PyObject_GetAttr(callback, PySide::PyName::im_func()));
        return funcName + QString::number(quint64(self), 16) + QString::number(quint64(func), 16);
    }
    return funcName + QString::number(quint64(callback), 16);
}

QByteArray voidType()
{
    return QByteArrayLiteral("void");
}

} //namespace Signal
} //namespace PySide

