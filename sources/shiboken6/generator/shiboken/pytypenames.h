// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PYTYPENAMES_H
#define PYTYPENAMES_H

#include <QtCore/QString>

static inline QString pyBoolT() { return QStringLiteral("PyBool"); }
static inline QString pyFloatT() { return QStringLiteral("PyFloat"); }
static inline QString pyLongT() { return QStringLiteral("PyLong"); }
static inline QString pyObjectT() { return QStringLiteral("object"); }
static inline QString pyStrT() { return QStringLiteral("str"); }

// PYSIDE-1499: A custom type determined by existence of an `__fspath__` attribute.
static inline QString pyPathLikeT() { return QStringLiteral("PyPathLike"); }

static inline QString cPyBufferT() { return QStringLiteral("PyBuffer"); }
static inline QString cPyListT() { return QStringLiteral("PyList"); }
static inline QString cPyObjectT() { return QStringLiteral("PyObject"); }
static inline QString cPySequenceT() { return QStringLiteral("PySequence"); }
static inline QString cPyTypeObjectT() { return QStringLiteral("PyTypeObject"); }

// numpy
static inline QString cPyArrayObjectT() { return QStringLiteral("PyArrayObject"); }

static inline QString sbkCharT() { return QStringLiteral("SbkChar"); }

#endif // PYTYPENAMES_H
