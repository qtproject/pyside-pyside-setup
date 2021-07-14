/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef SBK_CONTAINER_H
#define SBK_CONTAINER_H

#include "sbkpython.h"
#include "shibokenmacros.h"

#include <algorithm>
#include <iterator>
#include <optional>

extern "C"
{
struct LIBSHIBOKEN_API ShibokenContainer
{
    PyObject_HEAD
    void *d;
};

} // extern "C"

// Conversion helper traits for container values (Keep it out of namespace as
// otherwise clashes occur).
template <class Value>
struct ShibokenContainerValueConverter
{
    static bool checkValue(PyObject *pyArg);
    static PyObject *convertValueToPython(Value v);
    static std::optional<Value> convertValueToCpp(PyObject pyArg);
};

template <class SequenceContainer>
class ShibokenSequenceContainerPrivate // Helper for sequence type containers
{
public:
    using value_type = typename SequenceContainer::value_type;
    using OptionalValue = typename std::optional<value_type>;

    SequenceContainer *m_list{};
    bool m_ownsList = false;

    static PyObject *tpNew(PyTypeObject *subtype, PyObject * /* args */, PyObject * /* kwds */)
    {
        auto *me = reinterpret_cast<ShibokenContainer *>(subtype->tp_alloc(subtype, 0));
        auto *d = new ShibokenSequenceContainerPrivate;
        d->m_list = new SequenceContainer;
        d->m_ownsList = true;
        me->d = d;
        return reinterpret_cast<PyObject *>(me);
    }

    static int tpInit(PyObject * /* self */, PyObject * /* args */, PyObject * /* kwds */)
    {
        return 0;
    }

    static void tpFree(void *self)
    {
        auto *pySelf = reinterpret_cast<PyObject *>(self);
        auto *d = get(pySelf);
        if (d->m_ownsList)
            delete d->m_list;
        delete d;
        Py_TYPE(pySelf)->tp_base->tp_free(self);
    }

    static Py_ssize_t sqLen(PyObject *self)
    {
        return get(self)->m_list->size();
    }

    static PyObject *sqGetItem(PyObject *self, Py_ssize_t i)
    {
        auto *d = get(self);
        if (i < 0 || i >= Py_ssize_t(d->m_list->size())) {
            PyErr_SetString(PyExc_IndexError, "index out of bounds");
            return nullptr;
        }
        auto it = d->m_list->cbegin();
        std::advance(it, i);
        return ShibokenContainerValueConverter<value_type>::convertValueToPython(*it);
    }

    static int sqSetItem(PyObject *self, Py_ssize_t i, PyObject *pyArg)
    {
        auto *d = get(self);
        if (i < 0 || i >= Py_ssize_t(d->m_list->size())) {
            PyErr_SetString(PyExc_IndexError, "index out of bounds");
            return -1;
        }
        auto it = d->m_list->begin();
        std::advance(it, i);
        OptionalValue value = ShibokenContainerValueConverter<value_type>::convertValueToCpp(pyArg);
        if (!value.has_value())
            return -1;
        *it = value.value();
        return 0;
    }

    static PyObject *push_back(PyObject *self, PyObject *pyArg)
    {
        if (!ShibokenContainerValueConverter<value_type>::checkValue(pyArg)) {
            PyErr_SetString(PyExc_TypeError, "wrong type passed to append.");
            return nullptr;
        }

        auto *d = get(self);
        OptionalValue value = ShibokenContainerValueConverter<value_type>::convertValueToCpp(pyArg);
        if (!value.has_value())
            return nullptr;
        d->m_list->push_back(value.value());
        Py_RETURN_NONE;
    }

    static PyObject *push_front(PyObject *self, PyObject *pyArg)
    {
        if (!ShibokenContainerValueConverter<value_type>::checkValue(pyArg)) {
            PyErr_SetString(PyExc_TypeError, "wrong type passed to append.");
            return nullptr;
        }

        auto *d = get(self);
        OptionalValue value = ShibokenContainerValueConverter<value_type>::convertValueToCpp(pyArg);
        if (!value.has_value())
            return nullptr;
        d->m_list->push_front(value.value());
        Py_RETURN_NONE;
    }

    static PyObject *clear(PyObject *self)
    {
        auto *d = get(self);
        d->m_list->clear();
        Py_RETURN_NONE;
    }

    static PyObject *pop_back(PyObject *self)
    {
        auto *d = get(self);
        d->m_list->pop_back();
        Py_RETURN_NONE;
    }

    static PyObject *pop_front(PyObject *self)
    {
        auto *d = get(self);
        d->m_list->pop_front();
        Py_RETURN_NONE;
    }

    static ShibokenSequenceContainerPrivate *get(PyObject *self)
    {
        auto *data = reinterpret_cast<ShibokenContainer *>(self);
        return reinterpret_cast<ShibokenSequenceContainerPrivate *>(data->d);
    }
};

namespace Shiboken
{
LIBSHIBOKEN_API bool isOpaqueContainer(PyObject *o);
}

#endif // SBK_CONTAINER_H
