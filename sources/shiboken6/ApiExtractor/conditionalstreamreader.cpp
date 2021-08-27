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

#include "conditionalstreamreader.h"

#include <QtCore/QDebug>
#include <QtCore/QHash>

// ProxyEntityResolver proxies a QXmlStreamEntityResolver set by the user
// on ConditionalStreamReader and stores entity definitions from the
// <?entity name value?> processing instruction in a cache
// (which is also used for the proxied resolver).
class ProxyEntityResolver : public QXmlStreamEntityResolver
{
public:
    QString resolveEntity(const QString& publicId,
                          const QString& systemId) override;
    QString resolveUndeclaredEntity(const QString &name) override;

    QXmlStreamEntityResolver *source() const { return m_source; }
    void setSource(QXmlStreamEntityResolver *s) { m_source = s; }

    void defineEntity(const QString &name, const QString &value)
    {
        m_undeclaredEntityCache.insert(name, value);
    }

private:
    QHash<QString, QString> m_undeclaredEntityCache;
    QXmlStreamEntityResolver *m_source = nullptr;
};

QString ProxyEntityResolver::resolveEntity(const QString &publicId, const QString &systemId)
{
    QString result;
    if (m_source != nullptr)
        result = m_source->resolveEntity(publicId, systemId);
    if (result.isEmpty())
        result = QXmlStreamEntityResolver::resolveEntity(publicId, systemId);
    return result;
}

QString ProxyEntityResolver::resolveUndeclaredEntity(const QString &name)
{
    const auto it = m_undeclaredEntityCache.constFind(name);
    if (it != m_undeclaredEntityCache.constEnd())
        return it.value();
    if (m_source == nullptr)
        return {};
    const QString result = m_source->resolveUndeclaredEntity(name);
   if (!result.isEmpty())
        defineEntity(name, result);
   return result;
}

ConditionalStreamReader::ConditionalStreamReader(QIODevice *iod) :
    m_reader(iod)
{
    init();
}

ConditionalStreamReader::ConditionalStreamReader(const QString &s) :
    m_reader(s)
{
    init();
}

void ConditionalStreamReader::init()
{
    m_proxyEntityResolver = new ProxyEntityResolver;
    m_reader.setEntityResolver(m_proxyEntityResolver);
}

ConditionalStreamReader::~ConditionalStreamReader()
{
    m_reader.setEntityResolver(nullptr);
    delete m_proxyEntityResolver;
}

void ConditionalStreamReader::setEntityResolver(QXmlStreamEntityResolver *resolver)
{
    m_proxyEntityResolver->setSource(resolver);
}

QXmlStreamEntityResolver *ConditionalStreamReader::entityResolver() const
{
    return m_proxyEntityResolver->source();
}

QXmlStreamReader::TokenType ConditionalStreamReader::readNext()
{
    auto exToken = readNextInternal();

    if (exToken.second == PiTokens::EntityDefinition)
        return readEntityDefinitonPi() ? exToken.first : QXmlStreamReader::Invalid;

    if (exToken.second != PiTokens::If || conditionMatches())
        return exToken.first;

    // Condition does not match - search for endif
    int nestingLevel = 1;
    while (true) {
        exToken = readNextInternal();
        if (exToken.first == QXmlStreamReader::NoToken
            || exToken.first == QXmlStreamReader::Invalid
            || exToken.first == QXmlStreamReader::EndDocument) {
            break;
        }

        if (exToken.second == PiTokens::If)
            ++nestingLevel;
        else if (exToken.second == PiTokens::Endif && --nestingLevel == 0)
            break;
    }
    return exToken.first;
}

void ConditionalStreamReader::defineEntity(const QString &name, const QString &value)
{
    m_proxyEntityResolver->defineEntity(name, value);
}

// Read an entity definition: "<?entity name value?>:
bool ConditionalStreamReader::readEntityDefinitonPi()
{
    const auto data = m_reader.processingInstructionData();
    const auto separator = data.indexOf(u' ');
    if (separator <= 0 || separator == data.size() - 1) {
        m_reader.raiseError(u"Malformed entity definition: "_qs + data.toString());
        return false;
    }
    defineEntity(data.left(separator).toString(),
                 data.right(data.size() - separator - 1).toString());
    return true;
}

bool ConditionalStreamReader::conditionMatches() const
{
    const auto keywords = m_reader.processingInstructionData().split(u' ', Qt::SkipEmptyParts);
    if (keywords.isEmpty())
        return false;

    bool matches = false;
    bool exclusionOnly = true;
    for (const auto &keyword : keywords) {
        if (keyword.startsWith(u'!')) { // exclusion '!windows' takes preference
            if (m_conditions.contains(keyword.mid(1)))
                return false;
        } else {
            exclusionOnly = false;
            matches |= m_conditions.contains(keyword);
        }
    }
    return exclusionOnly || matches;
}

void ConditionalStreamReader::setConditions(const QStringList &newConditions)
{
    m_conditions = newConditions + platformConditions();
}

QStringList ConditionalStreamReader::platformConditions()
{
    QStringList result;
#if defined (Q_OS_UNIX)
    result << QStringLiteral("unix");
#endif

#if defined (Q_OS_LINUX)
    result << QStringLiteral("linux");
#elif defined (Q_OS_MACOS)
    result << QStringLiteral("darwin");
#elif defined (Q_OS_WINDOWS)
    result << QStringLiteral("windows");
#endif
    return result;
}

ConditionalStreamReader::ExtendedToken ConditionalStreamReader::readNextInternal()
{
    const auto token = m_reader.readNext();
    PiTokens piToken = PiTokens::None;
    if (token == QXmlStreamReader::ProcessingInstruction) {
        const auto target = m_reader.processingInstructionTarget();
        if (target == u"if")
            piToken = PiTokens::If;
        else if (target == u"endif")
            piToken = PiTokens::Endif;
        else if (target == u"entity")
            piToken = PiTokens::EntityDefinition;
    }
    return {token, piToken};
}

QDebug operator<<(QDebug dbg, const QXmlStreamAttributes &attrs)
{
    QDebugStateSaver saver(dbg);
    dbg.noquote();
    dbg.nospace();
    dbg << "QXmlStreamAttributes(";
    for (qsizetype i = 0, size = attrs.size(); i < size; ++i ) {
        if (i)
            dbg << ", ";
        dbg << attrs.at(i).name() << "=\"" << attrs.at(i).value() << '"';
    }
    dbg << ')';
    return dbg;
}

