// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CODESNIP_H
#define CODESNIP_H

#include "codesniphelpers.h"
#include "typesystem_enums.h"

#include <QtCore/qlist.h>
#include <QtCore/qhash.h>
#include <QtCore/qstring.h>

#include <variant>

QT_FORWARD_DECLARE_CLASS(QDebug)

class TemplateInstance
{
public:
    explicit TemplateInstance(QString name) : m_name(std::move(name)) {}

    void addReplaceRule(const QString &name, const QString &value)
    {
        replaceRules.insert(name, value);
    }

    QString expandCode() const;

    QString name() const
    {
        return m_name;
    }

private:
    Q_DECLARE_EQUALITY_COMPARABLE(TemplateInstance)

    friend bool comparesEqual(const TemplateInstance &lhs, const TemplateInstance &rhs) noexcept;
    friend size_t qHash(const TemplateInstance &t, size_t seed = 0) noexcept
    { return qHashMulti(seed, t.m_name, t.replaceRules); }

    QString m_name;
    QHash<QString, QString> replaceRules;
};

using CodeSnipFragment = std::variant<QString, TemplateInstance>;

size_t qHash(const CodeSnipFragment &codeFrag, size_t seed = 0) noexcept;

QDebug operator<<(QDebug d, const CodeSnipFragment &codeFrag);

class CodeSnipAbstract : public CodeSnipHelpers
{
public:
    using CodeSnipFragments = QList<CodeSnipFragment>;

    QString code() const;

    void addCode(const QString &code);
    void addCode(QStringView code) { addCode(code.toString()); }

    void addTemplateInstance(const TemplateInstance &ti)
    {
        m_codeList.emplace_back(CodeSnipFragment{ti});
    }

    bool isEmpty() const { return m_codeList.empty(); }
    void purgeEmptyFragments();

    const CodeSnipFragments &codeList() const { return m_codeList; }

    static QRegularExpression placeHolderRegex(int index);

private:
    CodeSnipFragments m_codeList;
};

class TemplateEntry : public CodeSnipAbstract
{
public:
    const QString &name() const { return m_name; }
    void setName(const QString &n) { m_name = n ;}

private:
    QString m_name;
};

class CodeSnip : public CodeSnipAbstract
{
public:
    CodeSnip() = default;
    explicit CodeSnip(TypeSystem::Language lang) : language(lang) {}

    TypeSystem::Language language = TypeSystem::TargetLangCode;
    TypeSystem::CodeSnipPosition position = TypeSystem::CodeSnipPositionAny;

    Q_DECLARE_EQUALITY_COMPARABLE(CodeSnip)

    friend bool comparesEqual(const CodeSnip &lhs, const CodeSnip &rhs) noexcept;
    friend size_t qHash(const CodeSnip &s, size_t seed = 0) noexcept
    { return qHashMulti(seed, s.position, s.language, s.codeList()); }
};

/// Purge empty fragments and snippets caused by new line characters in
/// conjunction with <insert-template>.
void purgeEmptyCodeSnips(QList<CodeSnip> *list);

#endif // CODESNIP_H
