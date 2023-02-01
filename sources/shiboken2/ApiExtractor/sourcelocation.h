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

#ifndef SOURCE_LOCATION_H
#define SOURCE_LOCATION_H

#include <QString>

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
