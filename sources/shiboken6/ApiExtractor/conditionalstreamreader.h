// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CONDITIONALSTREAMREADER_H
#define CONDITIONALSTREAMREADER_H

#include <QtCore/QXmlStreamReader>

#include <utility>

QT_FORWARD_DECLARE_CLASS(QDebug)

class ProxyEntityResolver;

/// ConditionalStreamReader encapsulates QXmlStreamReader, offering the same
/// API (except readNextStartElement() and similar conveniences) and internally
/// uses Processing Instructions like:
///   <?if keyword1 !keyword2?> ... <?endif?>
/// to exclude/include sections depending on a list of condition keywords,
/// containing for example the OS.
/// It should be possible to use it as a drop-in replacement for
/// QXmlStreamReader for any parsing code based on readNext().
/// It also allows for specifying entities using a Processing Instruction:
/// <?entity name value?>
/// which can be used in conjunction with conditional processing.
class ConditionalStreamReader
{
public:
    using TokenType = QXmlStreamReader::TokenType;
    explicit ConditionalStreamReader(QIODevice *iod);
    explicit ConditionalStreamReader(const QString &s);
    ~ConditionalStreamReader();

    QIODevice *device() const { return m_reader.device(); }

    // Note: Caching of entity values is done internally by
    // ConditionalStreamReader.
    void setEntityResolver(QXmlStreamEntityResolver *resolver);
    QXmlStreamEntityResolver *entityResolver() const;

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

    // Additional functions (not delegating to QXmlStreamReader)
    void defineEntity(const QString &name, const QString &value);

    const QStringList &conditions() const { return m_conditions; }
    void setConditions(const QStringList &newConditions);

    static QStringList platformConditions();

private:
    enum class PiTokens { None, If, Endif, EntityDefinition };

    using ExtendedToken = std::pair<TokenType, PiTokens>;
    ExtendedToken readNextInternal();
    void init();
    bool conditionMatches() const;
    bool readEntityDefinitonPi();

    QXmlStreamReader m_reader;
    ProxyEntityResolver *m_proxyEntityResolver = nullptr;
    QStringList m_conditions = ConditionalStreamReader::platformConditions();
};

QDebug operator<<(QDebug dbg, const QXmlStreamAttributes &a);

#endif // CONDITIONALSTREAMREADER_H
