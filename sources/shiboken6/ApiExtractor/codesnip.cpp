// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "codesnip.h"

#include "qtcompat.h"
#include "exception.h"
#include "typedatabase.h"

#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

QString TemplateInstance::expandCode() const
{
    const auto templateEntry = TypeDatabase::instance()->findTemplate(m_name);
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
