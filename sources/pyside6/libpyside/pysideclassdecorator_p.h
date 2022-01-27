/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
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

#ifndef CLASSDECORATOR_P_H
#define CLASSDECORATOR_P_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <array>
#include <string>

/// Helpers for class decorators with parameters
namespace PySide::ClassDecorator {

/// Base class for private objects of class decorators with parameters
class PYSIDE_API DecoratorPrivate
{
public:
    virtual ~DecoratorPrivate();

    /// Virtual function which is passed the decorated class type
    /// \param args Decorated class type argument
    /// \return class with reference count increased if the call was successful,
    ///         else nullptr
    virtual PyObject *tp_call(PyObject *self, PyObject *args, PyObject * /* kw */) = 0;

    /// Virtual function which is passed the decorator parameters
    /// \param args Decorator arguments
    /// \return 0 if the parameters are correct
    virtual int tp_init(PyObject *self, PyObject *args, PyObject *kwds) = 0;
    virtual const char *name() const = 0;

    /// Helper that returns DecoratorPrivate instance from a PyObject
    template <class DerivedPrivate>
    static DerivedPrivate *get(PyObject *o)
    { return static_cast<DerivedPrivate *>(DecoratorPrivate::getPrivate(o)); }

protected:
    /// Check mode for the arguments of the call operator
    enum class CheckMode { None, WrappedType, QObjectType };

    static DecoratorPrivate *getPrivate(PyObject *o);

    /// Helper for checking the arguments of the call operator
    /// \param args Arguments
    /// \param name Decorator name
    /// \param checkMode Type check mode
    /// \return The type object if the argument is a matching type
    PyObject *tp_call_check(PyObject *args,
                            CheckMode checkMode = CheckMode::QObjectType) const;
};

/// Base class for private objects of class decorator with a string parameter
class PYSIDE_API StringDecoratorPrivate : public DecoratorPrivate
{
public:
    /// Init function that retrieves the string parameter using convertToString()
    int tp_init(PyObject *self, PyObject *args, PyObject *kwds) override;

    const std::string &string() const { return m_string; }

protected:
    /// Helper function that retrieves the string parameter
    /// \param self self
    /// \param args Arguments
    /// \return 0 if the parameter is correct, else -1 (for tp_init())
    int convertToString(PyObject *self, PyObject *args);

private:
    std::string m_string;
};

/// Base class for private objects of class decorator with a type parameter
class PYSIDE_API TypeDecoratorPrivate : public DecoratorPrivate
{
public:
    /// Init function that retrieves the type parameter using convertToType()
    int tp_init(PyObject *self, PyObject *args, PyObject *kwds) override;

    PyTypeObject *type() const { return m_type; }

protected:
    /// Helper function that retrieves the type parameter
    /// \param self self
    /// \param args Arguments
    /// \return 0 if the parameter is correct, else -1 (for tp_init())
    int convertToType(PyObject *self, PyObject *args);

private:
    PyTypeObject *m_type = nullptr;
};

} // namespace PySide::ClassDecorator

extern "C"
{
LIBSHIBOKEN_API void Sbk_object_dealloc(PyObject *self);

/// Python type for class decorators with DecoratorPrivate
struct PYSIDE_API PySideClassDecorator
{
    PyObject_HEAD
    PySide::ClassDecorator::DecoratorPrivate *d;
};
};

namespace PySide::ClassDecorator {

/// Helper template providing the methods (slots) for class decorators
template <class DecoratorPrivate>
struct Methods
{
    static PyObject *tp_new(PyTypeObject *subtype)
    {
        auto *result = reinterpret_cast<PySideClassDecorator *>(subtype->tp_alloc(subtype, 0));
        result->d = new DecoratorPrivate;
        return reinterpret_cast<PyObject *>(result);
    }

    static void tp_free(void *self)
    {
        auto pySelf = reinterpret_cast<PyObject *>(self);
        auto decorator = reinterpret_cast<PySideClassDecorator *>(self);
        delete decorator->d;
        Py_TYPE(pySelf)->tp_base->tp_free(self);
    }

    static PyObject *tp_call(PyObject *self, PyObject *args, PyObject *kwds)
    {
        auto *decorator = reinterpret_cast<PySideClassDecorator *>(self);
        return decorator->d->tp_call(self, args, kwds);
    }

    static int tp_init(PyObject *self, PyObject *args, PyObject *kwds)
    {
        auto *decorator = reinterpret_cast<PySideClassDecorator *>(self);
        return decorator->d->tp_init(self, args, kwds);
    }

    using TypeSlots = std::array<PyType_Slot, 6>;

    static TypeSlots typeSlots()
    {
        return { {{Py_tp_call, reinterpret_cast<void *>(tp_call)},
                  {Py_tp_init, reinterpret_cast<void *>(tp_init)},
                  {Py_tp_new, reinterpret_cast<void *>(tp_new)},
                  {Py_tp_free, reinterpret_cast<void *>(tp_free)},
                  {Py_tp_dealloc, reinterpret_cast<void *>(Sbk_object_dealloc)},
                  {0, nullptr}}
               };
    }
};

} // namespace PySide::ClassDecorator

#endif // CLASSDECORATOR_P_H
