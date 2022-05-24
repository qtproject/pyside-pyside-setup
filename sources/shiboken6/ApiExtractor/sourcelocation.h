// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SOURCE_LOCATION_H
#define SOURCE_LOCATION_H

#include <QtCore/QString>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QTextStream)

class SourceLocation
{
public:
    explicit SourceLocation(const QString &file, int l);
    SourceLocation();

    bool isValid() const;

    QString fileName() const;
    void setFileName(const QString &fileName);

    int lineNumber() const;
    void setLineNumber(int lineNumber);

    QString toString() const;

    template<class Stream>
    void format(Stream &s) const;

private:
    QString m_fileName;
    int m_lineNumber = 0;
};

QTextStream &operator<<(QTextStream &s, const SourceLocation &l);

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const SourceLocation &l);
#endif

#endif // SOURCE_LOCATION_H
