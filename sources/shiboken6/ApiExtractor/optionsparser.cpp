// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "optionsparser.h"
#include "messages.h"
#include "exception.h"

#include <QtCore/QDir>
#include <QtCore/QTextStream>

using namespace Qt::StringLiterals;

template <class Stream> void formatBoolOption(Stream &s, const BoolOption &bo)
{
    switch (bo.source) {
    case OptionSource::CommandLine:
        s << "--";
        break;
    case OptionSource::CommandLineSingleDash:
        s << '-';
        break;
    default:
        break;
    }
    s << bo.option;
    if (bo.source == OptionSource::ProjectFile)
        s << " (project)";
}

template <class Stream> void formatOptionValue(Stream &s, const OptionValue &ov)
{
    switch (ov.source) {
    case OptionSource::CommandLine:
        s << "--";
        break;
    case OptionSource::CommandLineSingleDash:
        s << '-';
        break;
    default:
        break;
    }
    s << ov.option << '=' << ov.value;
    if (ov.source == OptionSource::ProjectFile)
        s << " (project)";
}

QTextStream &operator<<(QTextStream &s, const BoolOption &bo)
{
    formatBoolOption(s, bo);
    return s;
}

QTextStream &operator<<(QTextStream &s, const OptionValue &ov)
{
    formatOptionValue(s, ov);
    return s;
}

QDebug operator<<(QDebug debug, const BoolOption &bo)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    formatBoolOption(debug, bo);
    return debug;
}

QDebug operator<<(QDebug debug, const OptionValue &v)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    formatOptionValue(debug, v);
    return debug;
}

QDebug operator<<(QDebug debug, const Options &v)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Options(";
    if (!v.boolOptions.isEmpty())
        debug << "bools=" << v.boolOptions;
    if (!v.valueOptions.isEmpty())
        debug << ", option values=" << v.valueOptions;
    if (!v.positionalArguments.isEmpty())
        debug << ", pos=" << v.positionalArguments;
    debug << ')';
    return debug;
}

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

void OptionsParser::process(Options *o)
{
    for (auto i = o->boolOptions.size() - 1; i >= 0; --i) {
        const auto &opt = o->boolOptions.at(i);
        if (handleBoolOption(opt.option, opt.source))
            o->boolOptions.removeAt(i);
    }
    for (auto i = o->valueOptions.size() - 1; i >= 0; --i) {
        const auto &opt = o->valueOptions.at(i);
        if (handleOption(opt.option, opt.value, opt.source))
            o->valueOptions.removeAt(i);
    }
}

bool OptionsParserList::handleBoolOption(const QString &key, OptionSource source)
{
    for (const auto &p : std::as_const(m_parsers)) {
        if (p->handleBoolOption(key, source))
            return true;
    }
    return false;
}

bool OptionsParserList::handleOption(const QString &key, const QString &value, OptionSource source)
{
    for (const auto &p : std::as_const(m_parsers)) {
        if (p->handleOption(key, value, source))
            return true;
    }
    return false;
}

static void processOption(const QString &o, OptionSource source,
                          BoolOptions *bools, OptionValues *values)
{
    const auto equals = o.indexOf(u'=');
    if (equals == -1) {
        bools->append({o.trimmed(), source});
    } else {
        QString key = o.left(equals).trimmed();
        QString value = o.mid(equals + 1).trimmed();
        if (!value.isEmpty())
            values->append({key, value, source});
    }
}

static void readProjectFile(const QString &name, Options *o)
{
    const auto startMarker = "[generator-project]"_ba;

    QFile file(name);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
        throw Exception(msgCannotOpenForReading(file));

    if (file.atEnd() || file.readLine().trimmed() != startMarker)
        throw Exception(msgMissingProjectFileMarker(name, startMarker));

    while (!file.atEnd()) {
        const QByteArray lineB = file.readLine().trimmed();
        if (!lineB.isEmpty() && !lineB.startsWith('#')) {
            processOption(QString::fromUtf8(lineB), OptionSource::ProjectFile,
                          &o->boolOptions, &o->valueOptions);
        }
    }
}

void Options::setOptions(const QStringList &argv)
{
    const auto projectFileOption = "--project-file="_L1;
    for (const auto &o : argv) {
        if (o.startsWith(projectFileOption)) {
            readProjectFile(o.sliced(projectFileOption.size()), this);
        } else if (o.startsWith(u"--")) {
            processOption(o.sliced(2), OptionSource::CommandLine,
                          &boolOptions, &valueOptions);
        } else if (o.startsWith(u'-')) {
            processOption(o.sliced(1), OptionSource::CommandLineSingleDash,
                          &boolOptions, &valueOptions);
        } else {
            positionalArguments.append(o);
        }
    }
}

QString Options::msgUnprocessedOptions() const
{
    QString result;
    QTextStream str(&result);
    for (const auto &b : boolOptions)
        str << b << ' ';
    for (const auto &v : valueOptions)
        str << v << ' ';
    return result.trimmed();
}
