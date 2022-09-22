// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "pymethoddefentry.h"
#include "textstream.h"

#include <QtCore/QDebug>

TextStream &operator<<(TextStream &s, const PyMethodDefEntry &e)
{
     s <<  "{\"" << e.name << "\", reinterpret_cast<PyCFunction>("
      << e.function << "), ";
    if (e.methFlags.isEmpty()) {
         s << '0';
    } else {
        for (qsizetype i = 0, size = e.methFlags.size(); i < size; ++i) {
            if (i)
                s << '|';
            s << e.methFlags.at(i);
        }
    }
    if (e.doc.isEmpty())
        s << ", nullptr";
    else
        s << ", R\"(" << e.doc << ")\"";
    s << '}';
    return s;
}

TextStream &operator<<(TextStream &s, const PyMethodDefEntries &entries)
{
    for (const auto &e : entries)
        s << e << ",\n";
    return s;
}

QDebug operator<<(QDebug debug, const PyMethodDefEntry &e)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "PyMethodDefEntry(\"" << e.name << "\", " << e.function
          << ", " << e.methFlags;
    if (!e.doc.isEmpty())
        debug << ", \"" << e.doc << '"';
    debug << ')';
    return debug;
}
