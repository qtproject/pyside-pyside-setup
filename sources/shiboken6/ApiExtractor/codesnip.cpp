/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
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

#include "codesnip.h"

#include "qtcompat.h"
#include "exception.h"
#include "typedatabase.h"

#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

static inline QString callOperator() { return QStringLiteral("operator()"); }

QString TemplateInstance::expandCode() const
{
    TemplateEntry *templateEntry = TypeDatabase::instance()->findTemplate(m_name);
    if (!templateEntry) {
        const QString m = u"<insert-template> referring to non-existing template '"_s
                          + m_name + u"'."_s;
        throw Exception(m);
    }

    QString code = templateEntry->code();
    for (auto it = replaceRules.cbegin(), end = replaceRules.cend(); it != end; ++it)
        code.replace(it.key(), it.value());
    while (!code.isEmpty() && code.at(code.size() - 1).isSpace())
        code.chop(1);
    QString result = u"// TEMPLATE - "_s + m_name + u" - START"_s;
    if (!code.startsWith(u'\n'))
        result += u'\n';
    result += code;
    result += u"\n// TEMPLATE - "_s + m_name + u" - END\n"_s;
    return result;
}

// ---------------------- CodeSnipFragment
QString CodeSnipFragment::code() const
{
    return m_instance ? m_instance->expandCode() : m_code;
}

// ---------------------- CodeSnipAbstract
QString CodeSnipAbstract::code() const
{
    QString res;
    for (const CodeSnipFragment &codeFrag : codeList)
        res.append(codeFrag.code());

    return res;
}

void CodeSnipAbstract::addCode(const QString &code)
{
    codeList.append(CodeSnipFragment(fixSpaces(code)));
}

void CodeSnipAbstract::purgeEmptyFragments()
{
    auto end = std::remove_if(codeList.begin(), codeList.end(),
                              [](const CodeSnipFragment &f) { return f.isEmpty(); });
    codeList.erase(end, codeList.end());
}

QRegularExpression CodeSnipAbstract::placeHolderRegex(int index)
{
    return QRegularExpression(u'%' + QString::number(index) + QStringLiteral("\\b"));
}

void purgeEmptyCodeSnips(QList<CodeSnip> *list)
{
    for (auto it = list->begin(); it != list->end(); ) {
        it->purgeEmptyFragments();
        if (it->isEmpty())
            it = list->erase(it);
        else
            ++it;
    }
}
