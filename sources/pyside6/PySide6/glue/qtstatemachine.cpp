// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet qsignaltransition
if (PyObject_TypeCheck(%1, PySideSignalInstance_TypeF())) {
    auto *signalInstance = reinterpret_cast<PySideSignalInstance *>(%PYARG_1);
    PyObject *dataSource = PySide::Signal::getObject(signalInstance);
    Shiboken::AutoDecRef obType(PyObject_Type(dataSource));
    QObject * sender = %CONVERTTOCPP[QObject *](dataSource);
    //XXX   /|\ omitting this space crashes shiboken!
    if (sender) {
        const char *dataSignature = PySide::Signal::getSignature(signalInstance);
        QByteArray signature(dataSignature); // Append SIGNAL flag (2)
        signature.prepend('2');
        %0 = new QSignalTransitionWrapper(sender, signature, %2);
    }
}
// @snippet qsignaltransition

// @snippet qstate-addtransition-1
QByteArray signalName(%2);
signalName.remove(0, 1);
if (PySide::SignalManager::registerMetaMethod(%1, signalName.constData(),
                                              QMetaMethod::Signal)) {
    QSignalTransition *%0 = %CPPSELF->addTransition(%1, %2, %3);
    %PYARG_0 = %CONVERTTOPYTHON[QSignalTransition *](%0);
} else {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet qstate-addtransition-1

// @snippet qstate-addtransition-2
// Obviously the label used by the following goto is a very awkward solution,
// since it refers to a name very tied to the generator implementation.
// Check bug #362 for more information on this
// http://bugs.openbossa.org/show_bug.cgi?id=362
// PYSIDE-2256: The label was removed
if (!PyObject_TypeCheck(%1, PySideSignalInstance_TypeF()))
    return Shiboken::returnWrongArguments(args, fullName, errInfo);
PySideSignalInstance *signalInstance = reinterpret_cast<PySideSignalInstance *>(%1);
auto sender = %CONVERTTOCPP[QObject *](PySide::Signal::getObject(signalInstance));
QSignalTransition *%0 = %CPPSELF->%FUNCTION_NAME(sender, PySide::Signal::getSignature(signalInstance),%2);
%PYARG_0 = %CONVERTTOPYTHON[QSignalTransition *](%0);
// @snippet qstate-addtransition-2

// @snippet qstatemachine-configuration
%PYARG_0 = PySet_New(0);
for (auto *abs_state : %CPPSELF.configuration()) {
        Shiboken::AutoDecRef obj(%CONVERTTOPYTHON[QAbstractState *](abs_state));
        Shiboken::Object::setParent(self, obj);
        PySet_Add(%PYARG_0, obj);
}
// @snippet qstatemachine-configuration

// @snippet qstatemachine-defaultanimations
%PYARG_0 = PyList_New(0);
for (auto *abs_anim : %CPPSELF.defaultAnimations()) {
        Shiboken::AutoDecRef obj(%CONVERTTOPYTHON[QAbstractAnimation *](abs_anim));
        Shiboken::Object::setParent(self, obj);
        PyList_Append(%PYARG_0, obj);
}
// @snippet qstatemachine-defaultanimations
