// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_METAFUNCTION_H
#define PYSIDE_METAFUNCTION_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <QtCore/qtclasshelpermacros.h>

QT_FORWARD_DECLARE_CLASS(QObject)

extern "C"
{
    extern PYSIDE_API PyTypeObject *PySideMetaFunction_TypeF(void);

    struct PySideMetaFunctionPrivate;
    struct PYSIDE_API PySideMetaFunction
    {
        PyObject_HEAD
        PySideMetaFunctionPrivate *d;
    };
}; //extern "C"

namespace PySide::MetaFunction {

/*!
    Creates a MetaFunction object for the method \a methodIndex
    of the meta object of the QObject \a source.
    Returns a new reference to the PySideMetaFunction.
*/
PYSIDE_API PySideMetaFunction *newObject(QObject *source, int methodIndex);

} //namespace PySide::MetaFunction

#endif
