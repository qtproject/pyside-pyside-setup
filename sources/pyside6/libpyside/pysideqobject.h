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

#ifndef PYSIDEQOBJECT_H
#define PYSIDEQOBJECT_H

#include <sbkpython.h>

#include <pysidemacros.h>

#include <QtCore/QtGlobal>

QT_FORWARD_DECLARE_CLASS(QObject)
QT_FORWARD_DECLARE_STRUCT(QMetaObject)
QT_FORWARD_DECLARE_CLASS(QMutex)

namespace PySide
{

/// Fill QObject properties and do signal connections using the values found in \p kwds dictionary.
/// \param qObj PyObject fot the QObject.
/// \param metaObj QMetaObject of \p qObj.
/// \param kwds key->value dictonary.
/// \return True if everything goes well, false with a Python error set otherwise.
PYSIDE_API bool fillQtProperties(PyObject *qObj, const QMetaObject *metaObj, PyObject *kwds);

PYSIDE_API void initDynamicMetaObject(PyTypeObject *type, const QMetaObject *base,
                                      std::size_t cppObjSize);
PYSIDE_API void initQObjectSubType(PyTypeObject *type, PyObject *args, PyObject *kwds);

/// Return the size in bytes of a type that inherits QObject.
PYSIDE_API std::size_t getSizeOfQObject(PyTypeObject *type);

/// Check if a PyTypeObject or its bases contains a QObject
/// \param pyType is the PyTypeObject to check
/// \param raiseError controls if a TypeError is raised when an object does not
/// inherit QObject
PYSIDE_API bool isQObjectDerived(PyTypeObject *pyType, bool raiseError);

/// Convenience to convert a PyObject to QObject
PYSIDE_API QObject *convertToQObject(PyObject *object, bool raiseError);

/// Check for properties and signals registered on MetaObject and return these
/// \param cppSelf Is the QObject which contains the metaobject
/// \param self Python object of cppSelf
/// \param name Name of the argument which the function will try retrieve from MetaData
/// \return The Python object which contains the Data obtained in metaObject or the Python
/// attribute related with name
PYSIDE_API PyObject *getMetaDataFromQObject(QObject *cppSelf, PyObject *self, PyObject *name);

/// Mutex for accessing QObject memory helpers from multiple threads
PYSIDE_API QMutex &nextQObjectMemoryAddrMutex();
PYSIDE_API void *nextQObjectMemoryAddr();
/// Set the address where to allocate the next QObject (for QML)
PYSIDE_API void setNextQObjectMemoryAddr(void *addr);

PYSIDE_API PyObject *getWrapperForQObject(QObject *cppSelf, PyTypeObject *sbk_type);

/// Return the best-matching type for a QObject (Helper for QObject.findType())
/// \param cppSelf QObject instance
/// \return type object
PYSIDE_API PyTypeObject *getTypeForQObject(const QObject *cppSelf);

} //namespace PySide

#endif // PYSIDEQOBJECT_H
