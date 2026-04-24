// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_QENUM_H
#define PYSIDE_QENUM_H

#include <sbkpython.h>

#include <pysidemacros.h>

#include <vector>

#include <QtCore/qtclasshelpermacros.h>

QT_FORWARD_DECLARE_CLASS(QByteArray)
QT_FORWARD_DECLARE_CLASS(QMetaType)

namespace PySide::QEnum {

// PYSIDE-957: Support the QEnum macro
PYSIDE_API PyObject *QEnumMacro(PyObject *, bool);
PYSIDE_API int isFlag(PyObject *);
PYSIDE_API std::vector<PyObject *> resolveDelayedQEnums(PyTypeObject *);
PYSIDE_API void init();


// PYSIDE-2840: For an enum registered in Qt, return the C++ name.
// Ignore flags here; their underlying enums are of Python type flags anyways.
PYSIDE_API QByteArray getTypeName(PyTypeObject *type);

// Create a QMetaType for a decorated Python enum (int), enabling
// modification of properties by Qt Widgets Designer.
QMetaType createGenericEnumMetaType(const QByteArray &name, PyTypeObject *pyType);

// Like createGenericEnumMetaType(), but for "unsigned long long".
QMetaType createGenericEnum64MetaType(const QByteArray &name, PyTypeObject *pyType);

} // namespace PySide::QEnum

#endif
