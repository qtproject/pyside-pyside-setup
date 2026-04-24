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

/// Return a QMetaType for a PyTypeObject for purposes of
/// converting to a QVariant.
PYSIDE_API QMetaType resolveMetaType(PyTypeObject *type);

/// Convert a heterogenous Python list to a QVariantList by converting each
/// item using the QVariant converter.
PYSIDE_API std::optional<QVariantList> pyListToVariantList(PyObject *list);

/// Converts a list to a QVariant following the PySide semantics:
/// - A list of strings is returned as QVariant<QStringList>
/// - A list of convertible values is returned as QVariant<QList<Value>>
/// - Remaining types are returned as QVariant(QVariantList)
PYSIDE_API QVariant convertToVariantList(PyObject *list);

/// Converts a map to a QVariantMap (string keys and QVariant values)
PYSIDE_API QVariant convertToVariantMap(PyObject *map);

/// Converts a QVariant parameter of a JavaScript callback to Python
PYSIDE_API PyObject *javascriptVariantToPython(const QVariant &value);

} // namespace PySide::Variant

#endif // PYSIDEVARIANTUTILS_H
