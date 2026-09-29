// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef HELPER_H
#define HELPER_H

#include "sbkpython.h"
#include "shibokenmacros.h"
#include "shibokenclasshelpermacros.h"

#include <iosfwd>

#define SBK_UNUSED(x)   (void)(x);

extern "C"
{
struct SbkObject;
}

namespace Shiboken
{

LIBSHIBOKEN_API bool listToArgcArgv(PyObject *argList, int *argc, char ***argv, const char *defaultAppName = nullptr);

/*!
    Deletes a list of arguments \a argv of size \a argc created by
    listToArgcArgv().
*/
LIBSHIBOKEN_API void deleteArgv(int argc, char **argv);

LIBSHIBOKEN_API int *sequenceToIntArray(PyObject *obj, bool zeroTerminated = false);

/*!
    Fixes a type name \a typeIdName returned by \c typeid(t).name(),
    depending on compiler, and returns the fixed name (allocated).
*/
LIBSHIBOKEN_API const char *typeNameOf(const char *typeIdName);

/*!
    Returns whether \a method is a compiled method (Nuitka).
*/
LIBSHIBOKEN_API bool isCompiledMethod(PyObject *method);

/*!
    \class Shiboken::ArrayPointer
    \inmodule libshiboken

    \brief Creates and automatically deallocates C++ arrays.
*/
template<class T>
class ArrayPointer
{
    public:
        LIBSHIBOKEN_DISABLE_COPY_MOVE(ArrayPointer)

        explicit ArrayPointer(Py_ssize_t size) : data(new T[size]) {}
        T &operator[](Py_ssize_t pos) { return data[pos]; }
        operator T *() const { return data; }
        ~ArrayPointer() { delete[] data; }
    private:
        T *data;
};

template <class T>
using AutoArrayPointer = ArrayPointer<T>; // deprecated

using ThreadId = unsigned long long;
LIBSHIBOKEN_API ThreadId currentThreadId();
LIBSHIBOKEN_API ThreadId mainThreadId();

LIBSHIBOKEN_API int pyVerbose();

/*!
    A utility function used to call \c PyErr_WarnEx with the warning
    \a category, the \a stacklevel and a message formatted from \a format.
*/
LIBSHIBOKEN_API int warning(PyObject *category, int stacklevel, const char *format, ...);

struct LIBSHIBOKEN_API debugPyObject
{
    explicit debugPyObject(PyObject *o);

    PyObject *m_object;
};

struct LIBSHIBOKEN_API debugSbkObject
{
    explicit debugSbkObject(SbkObject *o);

    SbkObject *m_object;
};

struct LIBSHIBOKEN_API debugPyTypeObject
{
    explicit debugPyTypeObject(PyTypeObject *o);

    PyTypeObject *m_object;
};

struct debugPyBuffer;

struct debugPyArrayObject
{
    explicit debugPyArrayObject(PyObject *object) : m_object(object) {}

    PyObject *m_object;
};

LIBSHIBOKEN_API std::ostream &operator<<(std::ostream &str, const debugPyObject &o);
LIBSHIBOKEN_API std::ostream &operator<<(std::ostream &str, const debugSbkObject &o);
LIBSHIBOKEN_API std::ostream &operator<<(std::ostream &str, const debugPyTypeObject &o);
LIBSHIBOKEN_API std::ostream &operator<<(std::ostream &str, const debugPyBuffer &b);
LIBSHIBOKEN_API std::ostream &operator<<(std::ostream &str, const debugPyArrayObject &b);
LIBSHIBOKEN_API std::ios_base &debugVerbose(std::ios_base &s);
LIBSHIBOKEN_API std::ios_base &debugBrief(std::ios_base &s);
} // namespace Shiboken


#endif // HELPER_H
