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

#ifndef SIGNATURE_H
#define SIGNATURE_H

extern "C"
{

LIBSHIBOKEN_API int InitSignatureStrings(PyTypeObject *, const char *[]);
LIBSHIBOKEN_API void FinishSignatureInitialization(PyObject *, const char *[]);
LIBSHIBOKEN_API void SetError_Argument(PyObject *, const char *, PyObject *);
LIBSHIBOKEN_API PyObject *Sbk_TypeGet___signature__(PyObject *, PyObject *);
LIBSHIBOKEN_API PyObject *Sbk_TypeGet___doc__(PyObject *);
LIBSHIBOKEN_API PyObject *GetFeatureDict();

} // extern "C"

#endif // SIGNATURE_H
