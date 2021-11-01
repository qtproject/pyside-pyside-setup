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

#ifndef AUTODECREF_H
#define AUTODECREF_H

#include "sbkpython.h"
#include "basewrapper.h"

struct SbkObject;
namespace Shiboken
{

/**
 *  AutoDecRef holds a PyObject pointer and decrement its reference counter when destroyed.
 */
struct LIBSHIBOKEN_API AutoDecRef
{
public:
    AutoDecRef(const AutoDecRef &) = delete;
    AutoDecRef(AutoDecRef &&) = delete;
    AutoDecRef &operator=(const AutoDecRef &) = delete;
    AutoDecRef &operator=(AutoDecRef &&) = delete;

    /**
     * AutoDecRef constructor.
     * \param pyobj A borrowed reference to a Python object
     */
    explicit AutoDecRef(PyObject *pyObj) : m_pyObj(pyObj) {}
    /**
     * AutoDecRef constructor.
     * \param pyobj A borrowed reference to a Python object
     */
    explicit AutoDecRef(SbkObject *pyObj) : m_pyObj(reinterpret_cast<PyObject *>(pyObj)) {}

    /// Decref the borrowed python reference
    ~AutoDecRef()
    {
        Py_XDECREF(m_pyObj);
    }

    inline bool isNull() const { return m_pyObj == nullptr; }
    /// Returns the pointer of the Python object being held.
    inline PyObject *object() { return m_pyObj; }
    inline operator PyObject *() { return m_pyObj; }
#ifndef Py_LIMITED_API
    inline operator PyTupleObject *() { return reinterpret_cast<PyTupleObject *>(m_pyObj); }
#endif
    inline operator bool() const { return m_pyObj != nullptr; }
    inline PyObject *operator->() { return m_pyObj; }

    template<typename T>
    T cast()
    {
        return reinterpret_cast<T>(m_pyObj);
    }

    /**
     * Decref the current borrowed python reference and borrow \p other.
     */
    void reset(PyObject *other)
    {
        // Safely decref m_pyObj. See Py_XSETREF in object.h .
        PyObject *_py_tmp = m_pyObj;
        m_pyObj = other;
        Py_XDECREF(_py_tmp);
    }

    PyObject *release()
    {
        PyObject *result = m_pyObj;
        m_pyObj = nullptr;
        return result;
    }

private:
    PyObject *m_pyObj;
};

} // namespace Shiboken

#endif // AUTODECREF_H

