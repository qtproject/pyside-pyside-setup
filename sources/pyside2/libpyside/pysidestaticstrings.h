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

#ifndef PYSIDESTRINGS_H
#define PYSIDESTRINGS_H

#include <sbkpython.h>

namespace PySide
{
namespace PyName
{
PyObject *qtStaticMetaObject();
PyObject *qtConnect();
PyObject *qtDisconnect();
PyObject *qtEmit();
PyObject *dict_ring();
PyObject *name();
PyObject *property();
PyObject *select_id();
} // namespace PyName
namespace PyMagicName
{
PyObject *doc();
PyObject *name();
PyObject *property_methods();
} // namespace PyMagicName
} // namespace PySide

#endif // PYSIDESTRINGS_H
