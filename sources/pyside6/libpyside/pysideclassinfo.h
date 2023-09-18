// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_CLASSINFO_H
#define PYSIDE_CLASSINFO_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <QtCore/QMap>
#include <QtCore/QByteArray>

namespace PySide::ClassInfo {

PYSIDE_API bool checkType(PyObject* pyObj);
PYSIDE_API QMap<QByteArray, QByteArray> getMap(PyObject *obj);

} // namespace PySide::ClassInfo

#endif
