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

#ifndef FEATURE_SELECT_H
#define FEATURE_SELECT_H

#include "pysidemacros.h"
#include <sbkpython.h>

namespace PySide {
namespace Feature {

PYSIDE_API void init();
PYSIDE_API void Select(PyObject *obj);

} // namespace Feature
} // namespace PySide

#endif // FEATURE_SELECT_H
