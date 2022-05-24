// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "sourcelocation.h"
#include <QtCore/QDir>
#include <QtCore/QDebug>

SourceLocation::SourceLocation() = default;

SourceLocation::SourceLocation(const QString &file, int l)
    : m_fileName(file), m_lineNumber(l)
{
}

bool SourceLocation::isValid() const
{
    return m_lineNumber >= 0 && !m_fileName.isEmpty();
}

QString SourceLocation::fileName() const
{
    return m_fileName;
}

void SourceLocation::setFileName(const QString &fileName)
{
    m_fileName = fileName;
}

int SourceLocation::lineNumber() const
{
    return m_lineNumber;
}

void SourceLocation::setLineNumber(int lineNumber)
{
    m_lineNumber = lineNumber;
}

QString  SourceLocation::toString() const
{
    QString result;
    QTextStream s(&result);
    format(s);
    return result;
}

template<class Stream>
void SourceLocation::format(Stream &s) const
{
    if (isValid())
        s << QDir::toNativeSeparators(m_fileName) << ':' << m_lineNumber << ':';
    else
        s << "<unknown>";
}

QTextStream &operator<<(QTextStream &s, const SourceLocation &l)
{
    if (l.isValid()) {
        l.format(s);
        s << '\t'; // ":\t" is used by ReportHandler for filtering suppressions
    }
    return s;
}

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const SourceLocation &l)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    l.format(d);
    return d;
}
#endif
