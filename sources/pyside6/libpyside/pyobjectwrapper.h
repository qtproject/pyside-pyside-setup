// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:critical reason:handling-untrusted-data

#ifndef PYOBJECTWRAPPER
#define PYOBJECTWRAPPER

#include "pysidemacros.h"

#include <sbkpython.h>

#include <QtCore/qtclasshelpermacros.h>
#include <QtCore/qmetatype.h>

QT_FORWARD_DECLARE_CLASS(QDataStream)
QT_FORWARD_DECLARE_CLASS(QDebug)

namespace PySide
{

class PYSIDE_API PyObjectWrapper
{
public:

    PyObjectWrapper();
    explicit PyObjectWrapper(PyObject* me);
    PyObjectWrapper(const PyObjectWrapper &other);
    PyObjectWrapper& operator=(const PyObjectWrapper &other);
    PyObjectWrapper(PyObjectWrapper&&) noexcept;
    PyObjectWrapper &operator=(PyObjectWrapper &&) noexcept;

    void reset(PyObject *o);

    ~PyObjectWrapper();
    operator PyObject*() const;

    // FIXME: To be removed in Qt7
    // This was done to make QAbstractItemModel::data() work without explicit conversion of
    // QVariant(PyObjectWrapper) to QVariant(int). This works because QAbstractItemModel::data()
    // inturn calls legacyEnumValueFromModelData(const QVariant &data). But this function will
    // be removed in Qt7.
    // The proper fix would be to associate PyObjectWrapper to the corresponding C++ Enum.
    int toInt() const;

    static int metaTypeId();
    static void registerMetaType();

    /*!
        Returns true (and clears the per-thread flag) if \c{operator>>}
        blocked a deserialization attempt. Call with the GIL held, after
        \c Py_END_ALLOW_THREADS.
    */
    static bool checkAndClearPickleRejected();

private:
    PyObject* m_me;
};

PYSIDE_API QDataStream &operator<<(QDataStream& out, const PyObjectWrapper& myObj);
PYSIDE_API QDataStream &operator>>(QDataStream& in, PyObjectWrapper& myObj);
PYSIDE_API QDebug operator<<(QDebug debug, const PyObjectWrapper &myObj);

} // namespace PySide

Q_DECLARE_METATYPE(PySide::PyObjectWrapper)

#endif // PYOBJECTWRAPPER
