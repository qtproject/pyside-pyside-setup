// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "optionsparser.h"

#include <QtCore/QDir>
#include <QtCore/QTextStream>

using namespace Qt::StringLiterals;

QTextStream &operator<<(QTextStream &s, const OptionDescription &od)
{
    if (!od.name.startsWith(u'-'))
        s << "--";
    s << od.name;
    if (od.description.isEmpty()) { // For formatting {{"-s", ""}, {"--short", "descr"}}
        s << ", ";
    } else {
        s << '\n';
        const auto lines = QStringView{od.description}.split(u'\n');
        for (const auto &line : lines)
            s << "        " << line << '\n';
        s << '\n';
    }
    return s;
}

QTextStream &operator<<(QTextStream &s, const OptionDescriptions &options)
{
    s.setFieldAlignment(QTextStream::AlignLeft);
    for (const auto &od : options)
        s << od;
    return s;
}

OptionsParser::OptionsParser() noexcept = default;
OptionsParser::~OptionsParser() = default;

const QString &OptionsParser::pathSyntax()
{
    static const QString result =
        u"<path>["_s + QDir::listSeparator() + u"<path>"_s
        + QDir::listSeparator() + u"...]"_s;
    return result;
}

bool OptionsParser::handleBoolOption(const QString &, OptionSource)
{
    return false;
}

bool OptionsParser::handleOption(const QString &, const QString &, OptionSource)
{
    return false;
}
