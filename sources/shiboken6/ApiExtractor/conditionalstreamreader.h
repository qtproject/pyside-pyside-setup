/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef CONDITIONALSTREAMREADER_H
#define CONDITIONALSTREAMREADER_H

#include <QtCore/QXmlStreamReader>

#include <utility>

QT_FORWARD_DECLARE_CLASS(QDebug)

/// ConditionalStreamReader encapsulates QXmlStreamReader, offering the same
/// API (except readNextStartElement() and similar conveniences) and internally
/// uses Processing Instructions like:
///   <?if keyword1 !keyword2?> ... <?endif?>
/// to exclude/include sections depending on a list of condition keywords,
/// containing for example the OS.
/// It should be possible to use it as a drop-in replacement for
/// QXmlStreamReader for any parsing code based on readNext().
class ConditionalStreamReader
{
public:
    using TokenType = QXmlStreamReader::TokenType;
    explicit ConditionalStreamReader(QIODevice *iod) : m_reader(iod) { }
    explicit ConditionalStreamReader(const QString &s) : m_reader(s) { }

    QIODevice *device() const { return m_reader.device(); }

    void setEntityResolver(QXmlStreamEntityResolver *resolver) { m_reader.setEntityResolver(resolver); }
    QXmlStreamEntityResolver *entityResolver() const { return m_reader.entityResolver(); }

    bool atEnd() const { return m_reader.atEnd(); }
    TokenType readNext();

    TokenType tokenType() const { return  m_reader.tokenType(); }

    qint64 lineNumber() const { return m_reader.lineNumber(); }
    qint64 columnNumber() const { return m_reader.columnNumber(); }

    QXmlStreamAttributes attributes() const { return m_reader.attributes(); }

    QString readElementText(QXmlStreamReader::ReadElementTextBehaviour behaviour = QXmlStreamReader::ErrorOnUnexpectedElement)
    { return m_reader.readElementText(behaviour); }

    QStringView name() const { return m_reader.name(); }
    QStringView qualifiedName() const { return m_reader.qualifiedName(); }

    QStringView text() const { return m_reader.text(); }

    QString errorString() const { return m_reader.errorString(); }
    QXmlStreamReader::Error error() const { return m_reader.error(); }

    bool hasError() const { return m_reader.hasError(); }

    const QStringList &conditions() const { return m_conditions; }
    void setConditions(const QStringList &newConditions);

    static QStringList platformConditions();

private:
    enum class PiTokens { None, If, Endif };

    using ExtendedToken = std::pair<TokenType, PiTokens>;
    ExtendedToken readNextInternal();

    bool conditionMatches() const;

    QXmlStreamReader m_reader;
    QStringList m_conditions = ConditionalStreamReader::platformConditions();
};

QDebug operator<<(QDebug dbg, const QXmlStreamAttributes &a);

#endif // CONDITIONALSTREAMREADER_H
