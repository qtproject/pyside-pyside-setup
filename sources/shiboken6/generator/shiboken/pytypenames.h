// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PYTYPENAMES_H
#define PYTYPENAMES_H

#include <QtCore/QString>

constexpr auto pyBoolT = QLatin1StringView ("PyBool");
constexpr auto pyFloatT = QLatin1StringView ("PyFloat");
constexpr auto pyLongT = QLatin1StringView ("PyLong");
constexpr auto pyObjectT = QLatin1StringView ("object");
constexpr auto pyStrT = QLatin1StringView ("str");

// PYSIDE-1499: A custom type determined by existence of an `__fspath__` attribute.
constexpr auto pyPathLikeT = QLatin1StringView ("PyPathLike");

constexpr auto cPyBufferT = QLatin1StringView ("PyBuffer");
constexpr auto cPyListT = QLatin1StringView ("PyList");
constexpr auto cPyObjectT = QLatin1StringView ("PyObject");
constexpr auto cPySequenceT = QLatin1StringView ("PySequence");
constexpr auto cPyTypeObjectT = QLatin1StringView ("PyTypeObject");

// numpy
constexpr auto cPyArrayObjectT = QLatin1StringView ("PyArrayObject");

constexpr auto sbkCharT = QLatin1StringView ("SbkChar");

#endif // PYTYPENAMES_H
