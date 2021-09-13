/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
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

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet qsignaltransition
if (PyObject_TypeCheck(%1, PySideSignalInstanceTypeF())) {
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
if (!PyObject_TypeCheck(%1, PySideSignalInstanceTypeF()))
    goto Sbk_%TYPEFunc_%FUNCTION_NAME_TypeError;
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
