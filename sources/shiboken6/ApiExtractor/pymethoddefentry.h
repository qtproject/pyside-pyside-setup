// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PYMETHODDEFENTRY_H
#define PYMETHODDEFENTRY_H

#include <QtCore/QByteArrayList>
#include <QtCore/QString>

QT_FORWARD_DECLARE_CLASS(QDebug)

class TextStream;

struct PyMethodDefEntry
{
    QString name;
    QString function;
    QByteArrayList methFlags; // "METH_O" etc.
    QString doc;
};

using PyMethodDefEntries = QList<PyMethodDefEntry>;

TextStream &operator<<(TextStream &s, const PyMethodDefEntry &e);
TextStream &operator<<(TextStream &s, const PyMethodDefEntries &e);

QDebug operator<<(QDebug debug, const PyMethodDefEntry &e);

#endif // PYMETHODDEFENTRY_H
