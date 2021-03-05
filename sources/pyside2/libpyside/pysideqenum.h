/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef PYSIDE_QENUM_H
#define PYSIDE_QENUM_H

#include <pysidemacros.h>
#include <vector>

namespace PySide { namespace QEnum {

// PYSIDE-957: Support the QEnum macro
PYSIDE_API PyObject *QEnumMacro(PyObject *, bool);
PYSIDE_API int isFlag(PyObject *);
PYSIDE_API std::vector<PyObject *> resolveDelayedQEnums(PyTypeObject *);
PYSIDE_API void init();

} // namespace QEnum
} // namespace PySide

#endif
