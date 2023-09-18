// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_CLASSINFO_P_H
#define PYSIDE_CLASSINFO_P_H

#include <sbkpython.h>

#include "pysideclassdecorator_p.h"
#include "pysideclassinfo.h"

#include <QtCore/QMetaObject>

struct PySideClassInfo;

extern "C"
{
extern PYSIDE_API PyTypeObject *PySideClassInfo_TypeF(void);

} // extern "C"

namespace PySide { namespace ClassInfo {

class ClassInfoPrivate : public PySide::ClassDecorator::DecoratorPrivate
{
public:
    PyObject *tp_call(PyObject *self, PyObject *args, PyObject * /* kw */) override;
    int tp_init(PyObject *self, PyObject *args, PyObject *kwds) override;
    const char *name() const override;

    QMap<QByteArray, QByteArray> m_data;
    bool m_alreadyWrapped = false;
};

/**
 * Init PySide QProperty support system
 */
void init(PyObject* module);


} // namespace ClassInfo
} // namespace PySide

#endif
