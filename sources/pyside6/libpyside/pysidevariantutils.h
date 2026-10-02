// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDEVARIANTUTILS_H
#define PYSIDEVARIANTUTILS_H

#include <sbkpython.h>

#include <pysidemacros.h>

#include <QtCore/qvariant.h>
#include <QtCore/qvariantlist.h>

#include <optional>

namespace PySide::Variant
{

/*!
    Returns a QMetaType for the PyTypeObject \a type for purposes of
    converting to a QVariant.
*/
PYSIDE_API QMetaType resolveMetaType(PyTypeObject *type);

/*!
    Converts a heterogeneous Python \a list to a QVariantList by converting
    each item using the QVariant converter.
*/
PYSIDE_API std::optional<QVariantList> pyListToVariantList(PyObject *list);

/*!
    Converts a \a list to a QVariant following the PySide semantics:

    \list
        \li A list of strings is returned as \c{QVariant<QStringList>}
        \li A list of convertible values is returned as \c{QVariant<QList<Value>>}
        \li Remaining types are returned as \c{QVariant(QVariantList)}
    \endlist
*/
PYSIDE_API QVariant convertToVariantList(PyObject *list);

/*!
    Converts a \a map to a QVariantMap (string keys and QVariant values).
*/
PYSIDE_API QVariant convertToVariantMap(PyObject *map);

/*!
    Converts a QVariant parameter \a value of a JavaScript callback to Python.
*/
PYSIDE_API PyObject *javascriptVariantToPython(const QVariant &value);

} // namespace PySide::Variant

#endif // PYSIDEVARIANTUTILS_H
