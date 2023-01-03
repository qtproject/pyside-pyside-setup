// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CODESNIP_H
#define CODESNIP_H

#include "codesniphelpers.h"
#include "typesystem_enums.h"

#include <QtCore/QList>
#include <QtCore/QHash>
#include <QtCore/QString>

#include <memory>

class TemplateInstance
{
public:
    explicit TemplateInstance(const QString &name) : m_name(name) {}

    void addReplaceRule(const QString &name, const QString &value)
    {
        replaceRules[name] = value;
    }

    QString expandCode() const;

    QString name() const
    {
        return m_name;
    }

private:
    const QString m_name;
    QHash<QString, QString> replaceRules;
};

using TemplateInstancePtr = std::shared_ptr<TemplateInstance>;

class CodeSnipFragment
{
public:
    CodeSnipFragment() = default;
    explicit CodeSnipFragment(const QString &code) : m_code(code) {}
    explicit CodeSnipFragment(const TemplateInstancePtr &instance) : m_instance(instance) {}

    bool isEmpty() const { return m_code.isEmpty() && !m_instance; }

    QString code() const;

    TemplateInstancePtr instance() const { return m_instance; }

private:
    QString m_code;
    std::shared_ptr<TemplateInstance> m_instance;
};

class CodeSnipAbstract : public CodeSnipHelpers
{
public:
    QString code() const;

    void addCode(const QString &code);
    void addCode(QStringView code) { addCode(code.toString()); }

    void addTemplateInstance(const TemplateInstancePtr &ti)
    {
        codeList.append(CodeSnipFragment(ti));
    }

    bool isEmpty() const { return codeList.isEmpty(); }
    void purgeEmptyFragments();

    QList<CodeSnipFragment> codeList;

    static QRegularExpression placeHolderRegex(int index);
};

class TemplateEntry : public CodeSnipAbstract
{
public:
    explicit TemplateEntry(const QString &name) : m_name(name) {}

    QString name() const
    {
        return m_name;
    }

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
};

/// Purge empty fragments and snippets caused by new line characters in
/// conjunction with <insert-template>.
void purgeEmptyCodeSnips(QList<CodeSnip> *list);

#endif // CODESNIP_H
