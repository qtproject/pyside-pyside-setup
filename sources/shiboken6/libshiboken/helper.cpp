/****************************************************************************
**
** Copyright (C) 2020 The Qt Company Ltd.
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

#include "helper.h"
#include "basewrapper_p.h"
#include "sbkstring.h"
#include "sbkstaticstrings.h"

#include <iomanip>
#include <iostream>

#include <cstdarg>

#ifdef _WIN32
#  ifndef NOMINMAX
#    define NOMINMAX
#  endif
#  include <windows.h>
#else
#  include <pthread.h>
#endif

#include <algorithm>

static void formatPyTypeObject(const PyTypeObject *obj, std::ostream &str)
{
    if (obj) {
        str << '"' << obj->tp_name << "\", 0x" << std::hex
            << obj->tp_flags << std::dec;
        if (obj->tp_flags & Py_TPFLAGS_HEAPTYPE)
            str << " [heaptype]";
        if (obj->tp_flags & Py_TPFLAGS_BASETYPE)
            str << " [base]";
        if (obj->tp_flags & Py_TPFLAGS_HAVE_GC)
            str << " [gc]";
        if (obj->tp_flags & Py_TPFLAGS_LONG_SUBCLASS)
            str << " [long]";
        if (obj->tp_flags & Py_TPFLAGS_LIST_SUBCLASS)
            str << " [list]";
        if (obj->tp_flags & Py_TPFLAGS_TUPLE_SUBCLASS)
            str << " [tuple]";
        if (obj->tp_flags & Py_TPFLAGS_BYTES_SUBCLASS)
            str << " [bytes]";
        if (obj->tp_flags & Py_TPFLAGS_UNICODE_SUBCLASS)
            str << " [unicode]";
        if (obj->tp_flags & Py_TPFLAGS_DICT_SUBCLASS)
            str << " [dict]";
        if (obj->tp_flags & Py_TPFLAGS_TYPE_SUBCLASS)
            str << " [type]";
        if (obj->tp_flags & Py_TPFLAGS_IS_ABSTRACT)
            str << " [abstract]";
#if PY_VERSION_HEX >= 0x03080000
        if (obj->tp_flags & Py_TPFLAGS_METHOD_DESCRIPTOR)
            str << " [method_descriptor]";
#  if PY_VERSION_HEX >= 0x03090000
#    ifndef Py_LIMITED_API
        if (obj->tp_flags & Py_TPFLAGS_HAVE_VECTORCALL)
            str << " [vectorcall]";
#    endif // !Py_LIMITED_API
#    if PY_VERSION_HEX >= 0x030A0000
        if (obj->tp_flags & Py_TPFLAGS_IMMUTABLETYPE)
            str << " [immutabletype]";
        if (obj->tp_flags & Py_TPFLAGS_DISALLOW_INSTANTIATION)
            str << " [disallow_instantiation]";
        if (obj->tp_flags & Py_TPFLAGS_MAPPING)
            str << " [mapping]";
        if (obj->tp_flags & Py_TPFLAGS_SEQUENCE)
            str << " [sequence]";
#    endif // 3.10
#  endif // 3.9
#endif // 3.8
    } else {
        str << '0';
    }
}

static void formatPyObject(PyObject *obj, std::ostream &str);

static void formatPySequence(PyObject *obj, std::ostream &str)
{
    const Py_ssize_t size = PySequence_Size(obj);
    const Py_ssize_t printSize = std::min(size, Py_ssize_t(5));
    str << size << " <";
    for (Py_ssize_t i = 0; i < printSize; ++i) {
        if (i)
            str << ", ";
        str << '(';
        PyObject *item = PySequence_GetItem(obj, i);
        formatPyObject(item, str);
        str << ')';
        Py_XDECREF(item);
    }
    if (printSize < size)
        str << ",...";
    str << '>';
}

static void formatPyTuple(PyObject *obj, std::ostream &str)
{

    const Py_ssize_t size = PyTuple_Size(obj);
    str << size << " <";
    for (Py_ssize_t i = 0; i < size; ++i) {
        if (i)
            str << ", ";
        str << '(';
        PyObject *item = PyTuple_GetItem(obj, i);
        formatPyObject(item, str);
        str << ')';
        Py_XDECREF(item);
    }
    str << '>';
}

static void formatPyDict(PyObject *obj, std::ostream &str)
{
    PyObject *key;
    PyObject *value;
    Py_ssize_t pos = 0;
    str << '{';
    while (PyDict_Next(obj, &pos, &key, &value) != 0) {
        if (pos)
            str << ", ";
        str << Shiboken::debugPyObject(key) << '=' << Shiboken::debugPyObject(value);
    }
    str << '}';
}

// Helper to format a 0-terminated character sequence
template <class Char>
static void formatCharSequence(const Char *s, std::ostream &str)
{
    str << '"';
    const auto oldFillC = str.fill('0');
    str << std::hex;
    for (; *s; ++s) {
        const unsigned c = *s;
        if (c < 127)
            str << char(c);
        else
            str << "0x" << std::right << std::setw(sizeof(Char) * 2) << c << std::left;
    }
    str << std::dec;
    str.fill(oldFillC);
    str << '"';
}

static void formatPyUnicode(PyObject *obj, std::ostream &str)
{
    // Note: The below call create the PyCompactUnicodeObject.utf8 representation
    str << '"' << _PepUnicode_AsString(obj) << '"';

    str << " (" << PyUnicode_GetLength(obj) << ')';
    const auto kind = _PepUnicode_KIND(obj);
    switch (kind) {
    case PepUnicode_WCHAR_KIND:
        str << " [wchar]";
        break;
    case PepUnicode_1BYTE_KIND:
        str << " [1byte]";
        break;
    case PepUnicode_2BYTE_KIND:
        str << " [2byte]";
        break;
    case PepUnicode_4BYTE_KIND:
        str << " [4byte]";
        break;
    }

    const bool ascii = _PepUnicode_IS_ASCII(obj);
    if (ascii)
        str << " [ascii]";
    const bool compact = _PepUnicode_IS_COMPACT(obj);
    if (compact)
        str << " [compact]";
    void *data =_PepUnicode_DATA(obj);
    str << ", data=";
    switch (kind) {
    case PepUnicode_WCHAR_KIND:
        formatCharSequence(reinterpret_cast<const wchar_t *>(data), str);
        break;
    case PepUnicode_1BYTE_KIND:
        formatCharSequence(reinterpret_cast<const Py_UCS1 *>(data), str);
        break;
    case PepUnicode_2BYTE_KIND:
        formatCharSequence(reinterpret_cast<const Py_UCS2 *>(data), str);
        break;
    case PepUnicode_4BYTE_KIND:
        formatCharSequence(reinterpret_cast<const Py_UCS4 *>(data), str);
        break;
    }

#ifndef Py_LIMITED_API
    const char *utf8 = nullptr;
    if (!ascii && compact && kind == PepUnicode_1BYTE_KIND) {
        const auto *compactObj = reinterpret_cast<const PyCompactUnicodeObject *>(obj);
        if (compactObj->utf8_length)
            utf8 = compactObj->utf8;
    }
    if (utf8) {
        str << ", utf8=";
        formatCharSequence(reinterpret_cast<const Py_UCS1 *>(utf8), str);
    } else {
        str << ", no-utf8";
    }
#endif // !Py_LIMITED_API
}

static void formatPyObjectHelper(PyObject *obj, std::ostream &str)
{
    str << ", refs=" << obj->ob_refcnt << ", ";
    formatPyTypeObject(obj->ob_type, str);
    str << ", ";
    if (PyLong_Check(obj))
        str << PyLong_AsLong(obj);
    else if (PyFloat_Check(obj))
        str << PyFloat_AsDouble(obj);
    else if (PyUnicode_Check(obj))
        formatPyUnicode(obj, str);
    else if (PySequence_Check(obj))
        formatPySequence(obj, str);
    else if (PyDict_Check(obj))
        formatPyDict(obj, str);
    else if (PyTuple_CheckExact(obj))
        formatPyTuple(obj, str);
    else
        str << "<unknown>";
}

static void formatPyObject(PyObject *obj, std::ostream &str)
{
    str << obj;
    if (obj)
        formatPyObjectHelper(obj, str);
}

namespace Shiboken
{

debugPyObject::debugPyObject(PyObject *o) : m_object(o)
{
}

debugSbkObject::debugSbkObject(SbkObject *o) : m_object(o)
{
}

debugPyTypeObject::debugPyTypeObject(const PyTypeObject *o) : m_object(o)
{
}

debugPyBuffer::debugPyBuffer(const Py_buffer &b) : m_buffer(b)
{
}

std::ostream &operator<<(std::ostream &str, const debugPyTypeObject &o)
{
    str << "PyTypeObject(";
    formatPyTypeObject(o.m_object, str);
    str << ')';
    return str;
}

std::ostream &operator<<(std::ostream &str, const debugSbkObject &o)
{
    str << "SbkObject(" << o.m_object;
    if (o.m_object) {
        Shiboken::Object::_debugFormat(str, o.m_object);
        formatPyObjectHelper(reinterpret_cast<PyObject *>(o.m_object), str);
    }
    str << ')';
    return str;
}

std::ostream &operator<<(std::ostream &str, const debugPyObject &o)
{
    str << "PyObject(";
    formatPyObject(o.m_object, str);
    str << ')';
    return str;
}

std::ostream &operator<<(std::ostream &str, const debugPyBuffer &b)
{
    str << "PyBuffer(buf=" << b.m_buffer.buf << ", len="
        << b.m_buffer.len << ", itemsize=" << b.m_buffer.itemsize
        << ", readonly=" << b.m_buffer.readonly << ", ndim=" << b.m_buffer.ndim;
    if (b.m_buffer.format)
        str << ", format=\"" << b.m_buffer.format << '"';
    str << ", shape=" << b.m_buffer.shape << ", strides=" << b.m_buffer.strides
        << ", suboffsets=" << b.m_buffer.suboffsets << ')';
    return str;
}

#ifdef _WIN32
// Converts a Unicode string to a string encoded in the Windows console's
// code page via wchar_t for use with argv (PYSIDE-1425).
// FIXME: Remove once Windows console uses UTF-8
static char *toWindowsConsoleEncoding(PyObject *unicode)
{
    wchar_t *buf =  PyUnicode_AsWideCharString(unicode, nullptr);
    if (buf == nullptr)
        return nullptr;
    const int required = WideCharToMultiByte(CP_ACP, 0, buf, -1,
                                             nullptr, 0, nullptr, nullptr);
    if (required == 0) {
        PyMem_Free(buf);
        return nullptr;
    }
    char *result = new char[required];
    WideCharToMultiByte(CP_ACP, 0, buf, -1,
                        result, required, nullptr, nullptr);
    PyMem_Free(buf);
    return result;
}
#endif // _WIN32

// PySide-510: Changed from PySequence to PyList, which is correct.
bool listToArgcArgv(PyObject *argList, int *argc, char ***argv, const char *defaultAppName)
{
    if (!PyList_Check(argList))
        return false;

    if (!defaultAppName)
        defaultAppName = "PySideApplication";

    // Check all items
    Shiboken::AutoDecRef args(PySequence_Fast(argList, nullptr));
    int numArgs = int(PySequence_Fast_GET_SIZE(argList));
    for (int i = 0; i < numArgs; ++i) {
        PyObject *item = PyList_GET_ITEM(args.object(), i);
        if (!PyBytes_Check(item) && !PyUnicode_Check(item))
            return false;
    }

    bool hasEmptyArgList = numArgs == 0;
    if (hasEmptyArgList)
        numArgs = 1;

    *argc = numArgs;
    *argv = new char *[*argc];

    if (hasEmptyArgList) {
        // Try to get the script name
        PyObject *globals = PyEval_GetGlobals();
        PyObject *appName = PyDict_GetItem(globals, Shiboken::PyMagicName::file());
        (*argv)[0] = strdup(appName ? Shiboken::String::toCString(appName) : defaultAppName);
    } else {
        for (int i = 0; i < numArgs; ++i) {
            PyObject *item = PyList_GET_ITEM(args.object(), i);
            char *string = nullptr;
            if (Shiboken::String::check(item)) {
#ifdef _WIN32
                string = toWindowsConsoleEncoding(item);
#else
                string = strdup(Shiboken::String::toCString(item));
#endif
            }
            (*argv)[i] = string;
        }
    }

    return true;
}

int *sequenceToIntArray(PyObject *obj, bool zeroTerminated)
{
    AutoDecRef seq(PySequence_Fast(obj, "Sequence of ints expected"));
    if (seq.isNull())
        return nullptr;

    Py_ssize_t size = PySequence_Fast_GET_SIZE(seq.object());
    int *array = new int[size + (zeroTerminated ? 1 : 0)];

    for (int i = 0; i < size; i++) {
        PyObject *item = PySequence_Fast_GET_ITEM(seq.object(), i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "Sequence of ints expected");
            delete[] array;
            return nullptr;
        }
        array[i] = PyLong_AsLong(item);
    }

    if (zeroTerminated)
        array[size] = 0;

    return array;
}


int warning(PyObject *category, int stacklevel, const char *format, ...)
{
    va_list args;
    va_start(args, format);
#ifdef _WIN32
    va_list args2 = args;
#else
    va_list args2;
    va_copy(args2, args);
#endif

    // check the necessary memory
    int size = vsnprintf(nullptr, 0, format, args) + 1;
    auto message = new char[size];
    int result = 0;
    if (message) {
        // format the message
        vsnprintf(message, size, format, args2);
        result = PyErr_WarnEx(category, message, stacklevel);
        delete [] message;
    }
    va_end(args2);
    va_end(args);
    return result;
}

ThreadId currentThreadId()
{
#if defined(_WIN32)
    return GetCurrentThreadId();
#elif defined(__APPLE_CC__)
    return reinterpret_cast<ThreadId>(pthread_self());
#else
    return pthread_self();
#endif
}

// Internal, used by init() from main thread
static ThreadId _mainThreadId{0};
void _initMainThreadId() { _mainThreadId =  currentThreadId(); }

ThreadId mainThreadId()
{
    return _mainThreadId;
}

} // namespace Shiboken
