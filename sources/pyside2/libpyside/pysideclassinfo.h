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

#ifndef PYSIDE_CLASSINFO_H
#define PYSIDE_CLASSINFO_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <QtCore/QMap>
#include <QtCore/QByteArray>

extern "C"
{
    extern PYSIDE_API PyTypeObject *PySideClassInfoTypeF(void);

    struct PySideClassInfoPrivate;
    struct PYSIDE_API PySideClassInfo
    {
        PyObject_HEAD
        PySideClassInfoPrivate* d;
    };
};

namespace PySide { namespace ClassInfo {

PYSIDE_API bool checkType(PyObject* pyObj);
PYSIDE_API QMap<QByteArray, QByteArray> getMap(PySideClassInfo* obj);

} //namespace ClassInfo
} //namespace PySide

#endif
