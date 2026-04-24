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

/**
 * Init PySide QProperty support system
 */
void init(PyObject* module);

/**
 * This function call reset property function
 * This function does not check the property object type
 *
 * @param   self The property object
 * @param   source The QObject witch has the property
 * @return  Return 0 if ok or -1 if this function fail
 **/
int reset(PySideProperty* self, PyObject* source);


/**
 * This function return the property type
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return the property type name
 **/
const char* getTypeName(const PySideProperty* self);

/// This function returns the type object of the property. It is either a real
/// PyTypeObject ("@Property(int)") or a string "@Property('QVariant')".
/// @param  self The property object
/// @return type object
PyObject *getTypeObject(const PySideProperty* self);

} // namespace PySide::Property

#endif
