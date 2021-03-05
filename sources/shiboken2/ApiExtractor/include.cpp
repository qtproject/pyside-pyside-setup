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

#include "include.h"
#include <QDebug>
#include <QDir>
#include <QTextStream>
#include <QHash>

QString Include::toString() const
{
    if (m_type == IncludePath)
        return QLatin1String("#include <") + m_name + QLatin1Char('>');
    if (m_type == LocalPath)
        return QLatin1String("#include \"") + m_name + QLatin1Char('"');
    return QLatin1String("import ") + m_name + QLatin1Char(';');
}

QtCompatHashFunctionType qHash(const Include& inc)
{
    return qHash(inc.m_name);
}

QTextStream& operator<<(QTextStream& out, const Include& include)
{
    if (include.isValid())
        out << include.toString() << Qt::endl;
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
