// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef CLASSDECORATOR_P_H
#define CLASSDECORATOR_P_H

#include <pysidemacros.h>

#include <sbkpython.h>
#include <basewrapper.h>
#include <pep384ext.h>

#include <QtCore/qbytearray.h>

#include <array>

namespace PySide::ClassDecorator {

class PYSIDE_API DecoratorPrivate
{
public:
     Q_DISABLE_COPY_MOVE(DecoratorPrivate)

    virtual ~DecoratorPrivate();

    /*!
        Virtual function which is passed the decorated class type in \a args
        for the decorator \a self.
        Returns the class with reference count increased if the call was
        successful, else \nullptr.
    */
    virtual PyObject *tp_call(PyObject *self, PyObject *args, PyObject * /* kw */) = 0;

    /*!
        Virtual function which is passed the decorator parameters in \a args
        and \a kwds for the decorator \a self.
        Returns 0 if the parameters are correct.
    */
    virtual int tp_init(PyObject *self, PyObject *args, PyObject *kwds) = 0;
    virtual const char *name() const = 0;

    /*!
        Helper that returns the DecoratorPrivate instance from a PyObject \a o.
    */
    template <class DerivedPrivate>
    static DerivedPrivate *get(PyObject *o)
    { return static_cast<DerivedPrivate *>(DecoratorPrivate::getPrivate(o)); }

protected:
    /*!
        \enum PySide::ClassDecorator::DecoratorPrivate::CheckMode
        Check mode for the arguments of the call operator.
        \value None
        \value WrappedType
        \value QObjectType
    */
    enum class CheckMode : std::uint8_t { None, WrappedType, QObjectType };

    DecoratorPrivate() noexcept;
    static DecoratorPrivate *getPrivate(PyObject *o);

    /*!
        Helper for checking the arguments \a args of the call operator
        according to \a checkMode.
        Returns the type object extracted from the \a args tuple
        (borrowed reference) if the argument is a matching type.
    */
    PyObject *tp_call_check(PyObject *args,
                            CheckMode checkMode = CheckMode::QObjectType) const;
};

class PYSIDE_API StringDecoratorPrivate : public DecoratorPrivate
{
public:
    /*!
        Init function that retrieves the string parameter from \a args for
        \a self using convertToString(); \a kwds is ignored.
    */
    int tp_init(PyObject *self, PyObject *args, PyObject *kwds) override;

    QByteArray string() const { return m_string; }

protected:
    /*!
        Helper function that retrieves the string parameter from \a args
        for \a self.
        Returns 0 if the parameter is correct, else -1 (for tp_init()).
    */
    static int convertToString(PyObject *self, PyObject *args);

private:
    QByteArray m_string;
};

class PYSIDE_API TypeDecoratorPrivate : public DecoratorPrivate
{
public:
    /*!
        Init function that retrieves the type parameter from \a args for
        \a self using convertToType(); \a kwds is ignored.
    */
    int tp_init(PyObject *self, PyObject *args, PyObject *kwds) override;

    PyTypeObject *type() const { return m_type; }

protected:
    /*!
        Helper function that retrieves the type parameter from \a args
        for \a self.
        Returns 0 if the parameter is correct, else -1 (for tp_init()).
    */
    static int convertToType(PyObject *self, PyObject *args);

private:
    PyTypeObject *m_type = nullptr;
};

} // namespace PySide::ClassDecorator

extern "C"
{

// Python type for class decorators with DecoratorPrivate
struct PYSIDE_API PySideClassDecorator
{
    PyObject_HEAD
    PySide::ClassDecorator::DecoratorPrivate *d;
};
};

namespace PySide::ClassDecorator {

/*!
    \class PySide::ClassDecorator::Methods
    \brief Helper template providing the methods (slots) for class decorators.
    \inmodule libpyside
*/
template <class DecoratorPrivate>
struct Methods
{
    static PyObject *tp_new(PyTypeObject *subtype)
    {
        auto *result = PepExt_TypeCallAlloc<PySideClassDecorator>(subtype, 0);
        result->d = new DecoratorPrivate;
        return reinterpret_cast<PyObject *>(result);
    }

    static void tp_free(void *self)
    {
        auto *pySelf = reinterpret_cast<PyObject *>(self);
        auto *decorator = reinterpret_cast<PySideClassDecorator *>(self);
        delete decorator->d;
        PepExt_TypeCallFree(Py_TYPE(pySelf)->tp_base, self);
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
