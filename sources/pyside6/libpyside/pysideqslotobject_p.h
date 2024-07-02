// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQSLOTOBJECT_P_H
#define PYSIDEQSLOTOBJECT_P_H

#include "pysidemacros.h"
#include <sbkpython.h>

#include <QtCore/QObject>
#include <QtCore/qobjectdefs.h>

namespace PySide
{

class PySideQSlotObject : public QtPrivate::QSlotObjectBase
{
public:
    explicit PySideQSlotObject(PyObject *callable, const QByteArrayList &parameterTypes,
                               const char *returnType  = nullptr);
    ~PySideQSlotObject();

private:
    static void impl(int which, QSlotObjectBase *this_, QObject *receiver, void **args, bool *ret);
    void call(void **args);

    PyObject *m_callable;
    const QByteArrayList m_parameterTypes;
    const char *m_returnType;
};


} // namespace PySide

#endif // PYSIDEQSLOTOBJECT_P_H
