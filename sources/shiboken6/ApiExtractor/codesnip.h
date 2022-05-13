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

#ifndef CODESNIP_H
#define CODESNIP_H

#include "codesniphelpers.h"
#include "typesystem_enums.h"

#include <QtCore/QList>
#include <QtCore/QHash>
#include <QtCore/QSharedPointer>
#include <QtCore/QString>

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

using TemplateInstancePtr = QSharedPointer<TemplateInstance>;

class CodeSnipFragment
{
public:
    CodeSnipFragment() = default;
    explicit CodeSnipFragment(const QString &code) : m_code(code) {}
    explicit CodeSnipFragment(const TemplateInstancePtr &instance) : m_instance(instance) {}

    bool isEmpty() const { return m_code.isEmpty() && m_instance.isNull(); }

    QString code() const;

    TemplateInstancePtr instance() const { return m_instance; }

private:
    QString m_code;
    QSharedPointer<TemplateInstance> m_instance;
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
