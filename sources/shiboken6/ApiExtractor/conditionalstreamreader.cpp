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

QXmlStreamReader::TokenType ConditionalStreamReader::readNext()
{
    auto exToken = readNextInternal();
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

bool ConditionalStreamReader::conditionMatches() const
{
    const auto keywords = m_reader.processingInstructionData().split(u' ', Qt::SkipEmptyParts);

    bool matches = false;
    for (const auto &keyword : keywords) {
        if (keyword.startsWith(u'!')) { // exclusion '!windows' takes preference
            if (m_conditions.contains(keyword.mid(1)))
                return false;
        } else {
            matches |= m_conditions.contains(keyword);
        }
    }
    return matches;
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
