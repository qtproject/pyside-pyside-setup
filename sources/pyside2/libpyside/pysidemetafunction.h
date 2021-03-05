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

#ifndef PYSIDE_METAFUNCTION_H
#define PYSIDE_METAFUNCTION_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <QtCore/QObject>

extern "C"
{
    extern PYSIDE_API PyTypeObject *PySideMetaFunctionTypeF(void);

    struct PySideMetaFunctionPrivate;
    struct PYSIDE_API PySideMetaFunction
    {
        PyObject_HEAD
        PySideMetaFunctionPrivate *d;
    };
}; //extern "C"

namespace PySide { namespace MetaFunction {

/**
 * This function creates a MetaFunction object
 *
 * @param   obj the QObject witch this fuction is part of
 * @param   methodIndex The index of this function on MetaObject
 * @return  Return a new reference of PySideMetaFunction
 **/
PYSIDE_API PySideMetaFunction *newObject(QObject *obj, int methodIndex);

} //namespace MetaFunction
} //namespace PySide

#endif
