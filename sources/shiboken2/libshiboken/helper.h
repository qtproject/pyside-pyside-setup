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

#ifndef HELPER_H
#define HELPER_H

#include "sbkpython.h"
#include "shibokenmacros.h"
#include "autodecref.h"

#include <iosfwd>

#define SBK_UNUSED(x)   (void)(x);

namespace Shiboken
{

/**
* It transforms a python sequence into two C variables, argc and argv.
* This function tries to find the application (script) name and put it into argv[0], if
* the application name can't be guessed, defaultAppName will be used.
*
* No memory is allocated is an error occur.
*
* \note argc must be a valid address.
* \note The argv array is allocated using new operator and each item is allocated using malloc.
* \returns True on sucess, false otherwise.
*/
LIBSHIBOKEN_API bool listToArgcArgv(PyObject *argList, int *argc, char ***argv, const char *defaultAppName = nullptr);

/**
 * Convert a python sequence into a heap-allocated array of ints.
 *
 * \returns The newly allocated array or NULL in case of error or empty sequence. Check with PyErr_Occurred
 *          if it was successfull.
 */
LIBSHIBOKEN_API int *sequenceToIntArray(PyObject *obj, bool zeroTerminated = false);

/**
 *  Creates and automatically deallocates C++ arrays.
 */
template<class T>
class AutoArrayPointer
{
    public:
        AutoArrayPointer(const AutoArrayPointer &) = delete;
        AutoArrayPointer(AutoArrayPointer &&) = delete;
        AutoArrayPointer &operator=(const AutoArrayPointer &) = delete;
        AutoArrayPointer &operator=(AutoArrayPointer &&) = delete;

        explicit AutoArrayPointer(int size) { data = new T[size]; }
        T &operator[](int pos) { return data[pos]; }
        operator T *() const { return data; }
        ~AutoArrayPointer() { delete[] data; }
    private:
        T *data;
};

using ThreadId = unsigned long long;
LIBSHIBOKEN_API ThreadId currentThreadId();
LIBSHIBOKEN_API ThreadId mainThreadId();

/**
 * An utility function used to call PyErr_WarnEx with a formatted message.
 */
LIBSHIBOKEN_API int warning(PyObject *category, int stacklevel, const char *format, ...);

struct LIBSHIBOKEN_API debugPyObject
{
    explicit debugPyObject(PyObject *o);

    PyObject *m_object;
};

struct LIBSHIBOKEN_API debugPyTypeObject
{
    explicit debugPyTypeObject(const PyTypeObject *o);

    const PyTypeObject *m_object;
};

LIBSHIBOKEN_API std::ostream &operator<<(std::ostream &str, const debugPyObject &o);
LIBSHIBOKEN_API std::ostream &operator<<(std::ostream &str, const debugPyTypeObject &o);

} // namespace Shiboken


#endif // HELPER_H
