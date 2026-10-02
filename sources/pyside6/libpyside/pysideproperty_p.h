// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_QPROPERTY_P_H
#define PYSIDE_QPROPERTY_P_H

#include <sbkpython.h>

#include "pysideproperty.h"
#include "pysidepropertybase_p.h"
#include <pysidemacros.h>

#include <QtCore/qtclasshelpermacros.h>
#include <QtCore/qmetaobject.h>

struct PySideProperty;

class PYSIDE_API PySidePropertyPrivate : public PySidePropertyBase
{
public:
    PySidePropertyPrivate(const PySidePropertyPrivate &) = default;
    PySidePropertyPrivate &operator=(const PySidePropertyPrivate &) = delete;
    PySidePropertyPrivate(PySidePropertyPrivate &&) = delete;
    PySidePropertyPrivate &operator=(PySidePropertyPrivate &&) = delete;

    PySidePropertyPrivate() : PySidePropertyBase(Type::Property) {}
    ~PySidePropertyPrivate() override = default;

    [[nodiscard]] PySidePropertyPrivate *clone() const override;

    void metaCall(PyObject *source, QMetaObject::Call call, void **args) override;

    void tp_clear();
    int tp_traverse(visitproc visit, void *arg);
    void incref();

    PyObject *getValue(PyObject *source) const;
    int setValue(PyObject *source, PyObject *value);
    int reset(PyObject *source);

    PyObject *fget = nullptr;
    PyObject *fset = nullptr;
    PyObject *freset = nullptr;
    PyObject *fdel = nullptr;
    bool getter_doc = false;
};

namespace PySide::Property {

/*!
    Initializes the PySide QProperty support system in \a module.
*/
void init(PyObject* module);

/*!
    Calls the reset function of the property \a self on the QObject
    \a source. This function does not check the property object type.
    Returns 0 on success or -1 on failure.
*/
int reset(PySideProperty* self, PyObject* source);


/*!
    Returns the type name of the property \a self.
    This function does not check the property object type.
*/
const char* getTypeName(const PySideProperty* self);

/*!
    Returns the type object of the property \a self. It is either a real
    PyTypeObject (\c{@Property(int)}) or a string (\c{@Property('QVariant')}).
*/
PyObject *getTypeObject(const PySideProperty* self);

} // namespace PySide::Property

#endif
