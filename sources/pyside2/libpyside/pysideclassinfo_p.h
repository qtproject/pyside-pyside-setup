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

#ifndef PYSIDE_CLASSINFO_P_H
#define PYSIDE_CLASSINFO_P_H

#include <sbkpython.h>
#include <QMetaObject>
#include "pysideclassinfo.h"

struct PySideClassInfo;

extern "C"
{

struct PySideClassInfoPrivate {
    QMap<QByteArray, QByteArray> m_data;
    bool m_alreadyWrapped;
};

} // extern "C"

namespace PySide { namespace ClassInfo {

/**
 * Init PySide QProperty support system
 */
void init(PyObject* module);


} // namespace ClassInfo
} // namespace PySide

#endif
