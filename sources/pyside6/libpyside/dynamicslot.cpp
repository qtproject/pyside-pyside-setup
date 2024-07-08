// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "dynamicslot_p.h"
#include "globalreceiverv2.h" // for GlobalReceiverMethodSlot
#include "pysidestaticstrings.h"
#include "pysideutils.h"
#include "pysideweakref.h"
#include "signalmanager.h"

#include <autodecref.h>
#include <gilstate.h>
#include <pep384ext.h>

#include <QtCore/QDebug>

namespace PySide
{

DynamicSlot::SlotType DynamicSlot::slotType(PyObject *callback)
{
    if (PyMethod_Check(callback) != 0)
        return SlotType::Method;
    if (PySide::isCompiledMethod(callback) != 0)
        return SlotType::CompiledMethod;
    return SlotType::Callable;
}

// Simple callable slot.
class CallbackDynamicSlot : public DynamicSlot
{
    Q_DISABLE_COPY_MOVE(CallbackDynamicSlot)
public:
    explicit CallbackDynamicSlot(PyObject *callback) noexcept;
    ~CallbackDynamicSlot() override;

    void call(const QByteArrayList &parameterTypes, const char *returnType,
              void **cppArgs) override;
    void formatDebug(QDebug &debug) const override;

private:
    PyObject *m_callback;
};

CallbackDynamicSlot::CallbackDynamicSlot(PyObject *callback) noexcept :
    m_callback(callback)
{
    Py_INCREF(m_callback);
}

CallbackDynamicSlot::~CallbackDynamicSlot()
{
    Shiboken::GilState gil;
    Py_DECREF(m_callback);
}

void CallbackDynamicSlot::call(const QByteArrayList &parameterTypes, const char *returnType,
                               void **cppArgs)
{
    SignalManager::callPythonMetaMethod(parameterTypes, returnType, cppArgs, m_callback);
}

void CallbackDynamicSlot::formatDebug(QDebug &debug) const
{
    debug << "CallbackDynamicSlot(" << PySide::debugPyObject(m_callback) << ')';
}

// A method given by "signal.connect(foo.method)" is a temporarily created
// callable/partial function where self is bound as a first parameter.
// It can be split into self and the function. Keeping a reference on
// the callable itself would prevent object deletion. Instead, keep a
// reference on the function.
class MethodDynamicSlot : public DynamicSlot
{
    Q_DISABLE_COPY_MOVE(MethodDynamicSlot)
public:

    explicit MethodDynamicSlot(PyObject *function, PyObject *pythonSelf);
    ~MethodDynamicSlot() override;

    void call(const QByteArrayList &parameterTypes, const char *returnType,
              void **cppArgs) override;
    void formatDebug(QDebug &debug) const override;

private:
    PyObject *m_function;
    PyObject *m_pythonSelf;
};

MethodDynamicSlot::MethodDynamicSlot(PyObject *function, PyObject *pythonSelf) :
    m_function(function),
    m_pythonSelf(pythonSelf)
{
}

MethodDynamicSlot::~MethodDynamicSlot()
{
    Shiboken::GilState gil;
    Py_DECREF(m_function);
}

void MethodDynamicSlot::call(const QByteArrayList &parameterTypes, const char *returnType,
                             void **cppArgs)
{
    // create a callback based on method data
    Shiboken::AutoDecRef callable(PepExt_Type_CallDescrGet(m_function,
                                                           m_pythonSelf, nullptr));
    SignalManager::callPythonMetaMethod(parameterTypes, returnType,
                                        cppArgs, callable.object());
}

void MethodDynamicSlot::formatDebug(QDebug &debug) const
{
    debug << "MethodDynamicSlot(self=" << PySide::debugPyObject(m_pythonSelf)
        << ", function=" << PySide::debugPyObject(m_function) << ')';
}

// Store a weak reference on pythonSelf.
class TrackingMethodDynamicSlot : public MethodDynamicSlot
{
    Q_DISABLE_COPY_MOVE(TrackingMethodDynamicSlot)
public:
    explicit TrackingMethodDynamicSlot(PyObject *function, PyObject *pythonSelf,
                                       PyObject *weakRef);
    ~TrackingMethodDynamicSlot() override;

    void releaseWeakRef() { m_weakRef = nullptr; }

private:
    PyObject *m_weakRef;
};

TrackingMethodDynamicSlot::TrackingMethodDynamicSlot(PyObject *function, PyObject *pythonSelf,
                                                     PyObject *weakRef) :
    MethodDynamicSlot(function, pythonSelf),
    m_weakRef(weakRef)
{
}

TrackingMethodDynamicSlot::~TrackingMethodDynamicSlot()
{
    Shiboken::GilState gil;
    Py_XDECREF(m_weakRef);
    m_weakRef = nullptr;
}

// Delete the GlobalReceiver on pythonSelf deletion
class GlobalReceiverMethodSlot : public TrackingMethodDynamicSlot
{
    Q_DISABLE_COPY_MOVE(GlobalReceiverMethodSlot)
public:
    explicit GlobalReceiverMethodSlot(PyObject *function, PyObject *pythonSelf,
                                      GlobalReceiverV2 *parent);
    ~GlobalReceiverMethodSlot() override = default;

    GlobalReceiverV2 *parent() const { return m_parent; }

private:
    GlobalReceiverV2 *m_parent;
};

static void onGlobalReceiverSlotDestroyed(void *data)
{
    auto *self = reinterpret_cast<GlobalReceiverMethodSlot *>(data);
    self->releaseWeakRef();
    Py_BEGIN_ALLOW_THREADS
    SignalManager::deleteGlobalReceiver(self->parent());
    Py_END_ALLOW_THREADS
}

// monitor class from method lifetime
GlobalReceiverMethodSlot::GlobalReceiverMethodSlot(PyObject *function, PyObject *pythonSelf,
                                                   GlobalReceiverV2 *parent) :
    TrackingMethodDynamicSlot(function, pythonSelf,
                               WeakRef::create(pythonSelf, onGlobalReceiverSlotDestroyed, this)),
    m_parent(parent)
{
}

DynamicSlot* DynamicSlot::create(PyObject *callback, GlobalReceiverV2 *parent)
{
    Shiboken::GilState gil;
    switch (slotType(callback)) {
    case SlotType::Method: {
        PyObject *function = PyMethod_GET_FUNCTION(callback);
        Py_INCREF(function);
        PyObject *pythonSelf = PyMethod_GET_SELF(callback);
        if (parent != nullptr)
            return new GlobalReceiverMethodSlot(function, pythonSelf, parent);
        return new MethodDynamicSlot(function, pythonSelf);
    }
    case SlotType::CompiledMethod: {
        // PYSIDE-1523: PyMethod_Check is not accepting compiled form, we just go by attributes.
        PyObject *function = PyObject_GetAttr(callback, PySide::PySideName::im_func());
        Py_DECREF(function);
        PyObject *pythonSelf = PyObject_GetAttr(callback, PySide::PySideName::im_self());
        Py_DECREF(pythonSelf);
        if (parent != nullptr)
            return new GlobalReceiverMethodSlot(function, pythonSelf, parent);
        return new MethodDynamicSlot(function, pythonSelf);
    }
    case SlotType::Callable:
        break;
    }
    return new CallbackDynamicSlot(callback);
}

QDebug operator<<(QDebug debug, const DynamicSlot *ds)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    if (ds != nullptr)
        ds->formatDebug(debug);
    else
        debug << "DynamicSlot(0";
    return debug;
}

} // namespace PySide
