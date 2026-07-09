// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#include "pymethoddefentry.h"
#include "textstream.h"

#include <QtCore/qdebug.h>

using namespace Qt::StringLiterals;

struct PyMethodMapping
{
    QString name;
    PyMethodFlag flag;
};

static const QList<PyMethodMapping> &pyMethodMapping()
{
    static const QList<PyMethodMapping> result = {
         {u"METH_VARARGS"_s, PyMethodFlag::Varargs},
         {u"METH_KEYWORDS"_s, PyMethodFlag::Keywords},
         {u"METH_NOARGS"_s, PyMethodFlag::NoArgs},
         {u"METH_O"_s, PyMethodFlag::SingleObject},
         {u"METH_CLASS"_s, PyMethodFlag::Class},
         {u"METH_STATIC"_s, PyMethodFlag::Static},
         {u"METH_COEXIST"_s, PyMethodFlag::Coexist},
         {u"METH_FASTCALL"_s, PyMethodFlag::Fastcall},
         {u"METH_STACKLESS"_s, PyMethodFlag::Stackless},
         {u"METH_METHOD"_s, PyMethodFlag::Method}
    };
    return result;
}

std::optional<PyMethodFlags> pyMethodFlagsFromString(QStringView v)
{
    PyMethodFlags result;
    if (!v.isEmpty()) {
        const auto tokens = v.split(u'|', Qt::SkipEmptyParts);
        const auto &mapping = pyMethodMapping();
        for (const auto &tokenV : tokens) {
            const auto token = tokenV.trimmed();
            auto pred = [token](const PyMethodMapping &m) { return m.name == token; };
            auto it = std::find_if(mapping.cbegin(), mapping.cend(), pred);
            if (it == mapping.cend())
                return std::nullopt;
            result.setFlag(it->flag);
        }
    }
    return result;
}

QString pyMethodFlagsToString(PyMethodFlags flags)
{
    QString result;
    if (flags.toInt() == 0) {
        result.append(u'0');
    } else {
        for (const auto &mapping : pyMethodMapping()) {
            if (flags.testFlag(mapping.flag)) {
                if (!result.isEmpty())
                    result += u'|';
                  result += mapping.name;
            }
        }
    }
    return result;
}

TextStream &operator<<(TextStream &str, const castToPyCFunction &c)
{
    str << "reinterpret_cast<PyCFunction>(" << c.m_function << ')';
    return str;
}

TextStream &operator<<(TextStream &s, const PyMethodDefEntry &e)
{

    const bool signatureMismatch = e.flags.testFlag(PyMethodFlag::NoArgs)
                                   || e.flags.testFlag(PyMethodFlag::Keywords);
    s <<  "{\"" << e.name << "\", ";
    if (signatureMismatch)
        s << castToPyCFunction(e.function);
    else
        s << e.function;
    s << ", " << pyMethodFlagsToString(e.flags);
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
          << ", " << e.flags;
    if (!e.doc.isEmpty())
        debug << ", \"" << e.doc << '"';
    debug << ')';
    return debug;
}
