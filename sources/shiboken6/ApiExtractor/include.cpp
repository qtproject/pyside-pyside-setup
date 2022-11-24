// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "include.h"
#include "textstream.h"

#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QHash>
#include <QtCore/QTextStream>

#include "qtcompat.h"

#include <algorithm>

using namespace Qt::StringLiterals;

QString Include::toString() const
{
    if (m_type == IncludePath)
        return u"#include <"_s + m_name + u'>';
    if (m_type == LocalPath)
        return u"#include \""_s + m_name + u'"';
    return u"import "_s + m_name + u';';
}

int Include::compare(const Include &rhs) const
{
    if (m_type < rhs.m_type)
        return -1;
    if (m_type > rhs.m_type)
        return 1;
    return m_name.compare(rhs.m_name);
}

size_t qHash(const Include& inc)
{
    return qHash(inc.m_name);
}

QTextStream& operator<<(QTextStream& out, const Include& g)
{
    if (g.isValid())
        out << g.toString() << Qt::endl;
    return out;
}

TextStream& operator<<(TextStream& out, const Include& include)
{
    if (include.isValid())
        out << include.toString() << '\n';
    return out;
}

TextStream& operator<<(TextStream &out, const IncludeGroup& g)
{
    if (!g.includes.isEmpty()) {
        if (!g.title.isEmpty())
            out << "\n// " << g.title << "\n";
        auto includes = g.includes;
        std::sort(includes.begin(), includes.end());
        for (const Include &inc : std::as_const(includes))
            out << inc.toString() << '\n';
    }
    return out;
}

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const Include &i)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "Include(";
    if (i.isValid())
        d << "type=" << i.type() << ", file=\"" << QDir::toNativeSeparators(i.name()) << '"';
    else
        d << "invalid";
    d << ')';
    return d;
}
#endif // !QT_NO_DEBUG_STREAM
