// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDEQMLATTACHED_H
#define PYSIDEQMLATTACHED_H

#include <sbkpython.h>

#include "pysideqmlmacros.h"

#include <QtCore/qtconfigmacros.h>

QT_FORWARD_DECLARE_CLASS(QObject)

namespace PySide::Qml
{

PYSIDEQML_API QObject *qmlAttachedPropertiesObject(PyObject *typeObject, QObject *obj,
                                                   bool create = true);

} // namespace PySide::Qml

#endif // PYSIDEQMLATTACHED_H
