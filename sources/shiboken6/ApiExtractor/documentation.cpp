/****************************************************************************
**
** Copyright (C) 2020 The Qt Company Ltd.
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

#include "documentation.h"

Documentation::Documentation(const QString &detailed,
                             const QString &brief,
                             Format fmt) :
    m_detailed(detailed.trimmed()), m_brief(brief.trimmed()), m_format(fmt)
{
}

bool Documentation::isEmpty() const
{
    return m_detailed.isEmpty() && m_brief.isEmpty();
}

Documentation::Format Documentation::format() const
{
    return m_format;
}

void Documentation::setValue(const QString &value, Documentation::Type t)
{
    if (t == Brief)
        setBrief(value);
    else
        setDetailed(value);
}

void Documentation::setFormat(Documentation::Format f)
{
    m_format = f;
}

bool Documentation::equals(const Documentation &rhs) const
{
    return m_format == rhs.m_format && m_detailed == rhs.m_detailed
        && m_brief == rhs.m_brief;
}

void Documentation::setDetailed(const QString &detailed)
{
    m_detailed = detailed.trimmed();
}

void Documentation::setBrief(const QString &brief)
{
    m_brief = brief.trimmed();
}
