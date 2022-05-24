// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "codesniphelpers.h"

#include <QtCore/QStringList>

#include <algorithm>

static inline int firstNonBlank(QStringView s)
{
    const auto it = std::find_if(s.cbegin(), s.cend(),
                                 [] (QChar c) { return !c.isSpace(); });
    return int(it - s.cbegin());
}

static inline bool isEmpty(QStringView s)
{
    return s.isEmpty()
        || std::all_of(s.cbegin(), s.cend(),
                       [] (QChar c) { return c.isSpace(); });
}

QString CodeSnipHelpers::dedent(const QString &code)
{
    if (code.isEmpty())
        return code;
    // Right trim if indent=0, or trim if single line
    if (!code.at(0).isSpace() || !code.contains(u'\n'))
        return code.trimmed();
    const auto lines = QStringView{code}.split(u'\n');
    int spacesToRemove = std::numeric_limits<int>::max();
    for (const auto &line : lines) {
        if (!isEmpty(line)) {
            const int nonSpacePos = firstNonBlank(line);
            if (nonSpacePos < spacesToRemove)
                spacesToRemove = nonSpacePos;
            if (spacesToRemove == 0)
                return code;
        }
    }
    QString result;
    for (const auto &line : lines) {
        if (!isEmpty(line) && spacesToRemove < line.size())
            result += line.mid(spacesToRemove).toString();
        result += u'\n';
    }
    return result;
}

QString CodeSnipHelpers::fixSpaces(QString code)
{
    code.remove(u'\r');
    // Check for XML <tag>\n<space>bla...
    if (code.startsWith(u"\n "))
        code.remove(0, 1);
    while (!code.isEmpty() && code.back().isSpace())
        code.chop(1);
    code = dedent(code);
    if (!code.isEmpty() && !code.endsWith(u'\n'))
        code.append(u'\n');
    return code;
}

// Prepend a line to the code, observing indentation
void CodeSnipHelpers::prependCode(QString *code, QString firstLine)
{
    while (!code->isEmpty() && code->front() == u'\n')
        code->remove(0, 1);
    if (!code->isEmpty() && code->front().isSpace()) {
        const int indent = firstNonBlank(*code);
        firstLine.prepend(QString(indent, u' '));
    }
    if (!firstLine.endsWith(u'\n'))
        firstLine += u'\n';
    code->prepend(firstLine);
}
