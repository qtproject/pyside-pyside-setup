// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "codesnip.h"

#include "exception.h"
#include "typedatabase.h"

#include <QtCore/qdebug.h>

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

bool comparesEqual(const TemplateInstance &lhs, const TemplateInstance &rhs) noexcept
{
    return lhs.m_name == rhs.m_name && lhs.replaceRules == rhs.replaceRules;
}

// ---------------------- CodeSnipFragment

static QString fragmentToCodeHelper(const QString &c)
{
    return c;
}

static QString fragmentToCodeHelper(const TemplateInstance &p)
{
    return p.expandCode();
}

static QString fragmentToCode(const CodeSnipFragment &codeFrag)
{
    return std::visit([](auto f) { return fragmentToCodeHelper(f); }, codeFrag);
}

static bool isEmptyFragmentHelper(const QString &c)
{
    return c.isEmpty();
}

static bool isEmptyFragmentHelper(const TemplateInstance &)
{
    return false;
}

static bool isEmptyFragment(const CodeSnipFragment &codeFrag)
{
    return std::visit([](auto f) { return isEmptyFragmentHelper(f); }, codeFrag);
}

static size_t hashHelper(const QString &c, size_t seed) noexcept
{
    return qHash(c, seed);
}

static size_t hashHelper(const TemplateInstance &t, size_t seed) noexcept
{
    return qHash(t, seed);
}

size_t qHash(const CodeSnipFragment &codeFrag, size_t seed) noexcept
{
    return std::visit([seed](auto f) { return hashHelper(f, seed); }, codeFrag);
}

static void formatDebugHelper(QDebug &d, const QString &code)
{
    const auto lines = QStringView{code}.split(u'\n');
    for (qsizetype i = 0, size = lines.size(); i < size; ++i) {
        if (i)
            d << "\\n";
        d << lines.at(i).trimmed();
    }
}

static void formatDebugHelper(QDebug &d, const TemplateInstance &t)
{
     d << "template=\"" << t.name() << '"';
}

QDebug operator<<(QDebug d, const CodeSnipFragment &codeFrag)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    std::visit([&d](auto f) { formatDebugHelper(d, f); }, codeFrag);
    return d;
}

// ---------------------- CodeSnipAbstract

void CodeSnipAbstract::addCode(const QString &code)
{
    m_codeList.emplace_back(CodeSnipFragment(fixSpaces(code)));
}

QString CodeSnipAbstract::code() const
{
    QString res;
    for (const auto &codeFrag : m_codeList)
        res.append(fragmentToCode(codeFrag));
    return res;
}

void CodeSnipAbstract::purgeEmptyFragments()
{
    auto end = std::remove_if(m_codeList.begin(), m_codeList.end(), isEmptyFragment);
    m_codeList.erase(end, m_codeList.end());
}

QRegularExpression CodeSnipAbstract::placeHolderRegex(int index)
{
    return QRegularExpression(u'%' + QString::number(index) + "\\b"_L1);
}

bool comparesEqual(const CodeSnip &lhs, const CodeSnip &rhs) noexcept
{
    return lhs.language == rhs.language && lhs.position == rhs.position
        && lhs.codeList() == rhs.codeList();
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
