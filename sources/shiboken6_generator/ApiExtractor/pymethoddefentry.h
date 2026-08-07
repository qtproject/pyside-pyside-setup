// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:build-tool

#ifndef PYMETHODDEFENTRY_H
#define PYMETHODDEFENTRY_H

#include <QtCore/qbytearraylist.h>
#include <QtCore/qflags.h>
#include <QtCore/qstring.h>

#include <optional>

QT_FORWARD_DECLARE_CLASS(QDebug)

class TextStream;

enum class PyMethodFlag : int
{
    Varargs      = 0x0001, // METH_VARARGS
    Keywords     = 0x0002, // METH_KEYWORDS
    NoArgs       = 0x0004, // METH_NOARGS
    SingleObject = 0x0008, // METH_O
    Class        = 0x0010, // METH_CLASS
    Static       = 0x0020, // METH_STATIC
    Coexist      = 0x0040, // METH_COEXIST
    Fastcall     = 0x0080, // METH_FASTCALL
    Stackless    = 0x0100, // METH_STACKLESS
    Method       = 0x0200, // METH_METHOD
};

Q_DECLARE_FLAGS(PyMethodFlags,PyMethodFlag)
Q_DECLARE_OPERATORS_FOR_FLAGS(PyMethodFlags)

std::optional<PyMethodFlags> pyMethodFlagsFromString(QStringView v);
QString pyMethodFlagsToString(PyMethodFlags flags);

struct castToPyCFunction
{
    explicit castToPyCFunction(QAnyStringView function) noexcept :
        m_function(function) {}

    QAnyStringView m_function;
};

struct PyMethodDefEntry
{
    QString name;
    QString function;
    PyMethodFlags flags;
    QString doc;
};

using PyMethodDefEntries = QList<PyMethodDefEntry>;

TextStream &operator<<(TextStream &str, const castToPyCFunction &c);
TextStream &operator<<(TextStream &s, const PyMethodDefEntry &e);
TextStream &operator<<(TextStream &s, const PyMethodDefEntries &e);

QDebug operator<<(QDebug debug, const PyMethodDefEntry &e);

#endif // PYMETHODDEFENTRY_H
