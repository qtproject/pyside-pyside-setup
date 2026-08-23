// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDEUTILS_H
#define PYSIDEUTILS_H

#include <sbkpython.h>

#include <pysidemacros.h>

#include <QtCore/qtclasshelpermacros.h>
#include <QtCore/qtversionchecks.h>

// The free-threading work is developed on dev and is not meant for a release
// branch. A Pick-to that lands it on one should fail here rather than produce
// a build nobody has tested. Only for that build: a plain build with a GIL
// keeps working against the Qt versions it always did.
#ifdef Py_GIL_DISABLED
#  if QT_VERSION < QT_VERSION_CHECK(6, 12, 0)
#    error "PySide free-threading is developed on dev; do not pick it to a release branch."
#  endif
#endif

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QString)
QT_FORWARD_DECLARE_CLASS(QStringView)

namespace PySide
{

/// Check if self inherits from class_name
/// \param self Python object
/// \param class_name strict with the class name
/// \return Returns true if self object inherits from class_name, otherwise returns false
PYSIDE_API bool inherits(PyTypeObject *self, const char *class_name);
#ifdef Py_GIL_DISABLED
/// The same asked about the Python wrapper of a C++ object, for the
/// generated qt_metacast(). False when there is no wrapper. Takes a void
/// pointer, not a QObject one: it is a wrapper map key, and under multiple
/// inheritance the QObject subobject is not at the registered address.
/// \param cppSelf the C++ pointer the wrapper was registered with
/// \param class_name strict with the class name
PYSIDE_API bool wrapperInherits(const void *cppSelf, const char *class_name);
#endif

/// Given A PyObject representing Unicode data, returns an equivalent QString.
PYSIDE_API QString pyUnicodeToQString(PyObject *str);

/// Given a QString, return the PyObject repeesenting Unicode data.
PYSIDE_API PyObject *qStringToPyUnicode(QStringView s);

/// Given A PyObject representing ASCII or Unicode data, returns an equivalent QString.
PYSIDE_API QString pyStringToQString(PyObject *str);

/// Provide an efficient, correct PathLike interface.
PYSIDE_API QString pyPathToQString(PyObject *path);

/// Returns whether \a method is a compiled method (Nuitka).
/// \sa Shiboken::isCompiledMethod()
PYSIDE_API bool isCompiledMethod(PyObject *callback);

/// Returns the Python binary (value of sys.executable).
PYSIDE_API QString sysExecutable();

/// Returns whether name is a valid class name in a .ui file (C++ or Python)
PYSIDE_API bool isUiClassName(QStringView name);

struct debugPyTypeObject
{
    PYSIDE_API explicit debugPyTypeObject(PyTypeObject *o) noexcept;

    PyTypeObject *m_object;
};

PYSIDE_API QDebug operator<<(QDebug debug, const debugPyTypeObject &o);

struct debugPyObject
{
    PYSIDE_API explicit debugPyObject(PyObject *o) noexcept;

    PyObject *m_object;
};

PYSIDE_API QDebug operator<<(QDebug debug, const debugPyObject &o);

#if !defined(Py_LIMITED_API) || Py_LIMITED_API >= 0x030B0000
struct debugPyBuffer
{
    PYSIDE_API explicit debugPyBuffer(Py_buffer *b) noexcept;

    Py_buffer *m_buffer;
};

PYSIDE_API QDebug operator<<(QDebug debug, const debugPyBuffer &b);
#endif // !Py_LIMITED_API || >= 3.11

// Shared deprecation message for exec_() → exec() across all Qt module bindings.
extern PYSIDE_API const char *const execDeprecatedMsg;

} //namespace PySide

#endif // PYSIDESTRING_H
