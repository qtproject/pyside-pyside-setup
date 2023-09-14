// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OPTIONSPARSER_H
#define OPTIONSPARSER_H

#include <QtCore/QString>
#include <QtCore/QStringList>

#include <memory>

QT_FORWARD_DECLARE_CLASS(QTextStream)

enum class OptionSource
{
    CommandLine, // "--option"
    CommandLineSingleDash, // "-o"
    ProjectFile
};

struct BoolOption
{
    QString option;
    OptionSource source = OptionSource::CommandLine;
};

struct OptionValue // --option=value pair
{
    QString option;
    QString value;
    OptionSource source = OptionSource::CommandLine;
};

using BoolOptions = QList<BoolOption>;
using OptionValues = QList<OptionValue>;

struct Options // Options from command line and project file
{
    void setOptions(const QStringList &argv);
    QString msgUnprocessedOptions() const;

    BoolOptions boolOptions;
    OptionValues valueOptions;
    QStringList positionalArguments;
};

struct OptionDescription // For help formatting
{
    QString name;
    QString description;
};

using OptionDescriptions = QList<OptionDescription>;

QTextStream &operator<<(QTextStream &s, const BoolOption &bo);
QTextStream &operator<<(QTextStream &s, const OptionValue &ov);
QTextStream &operator<<(QTextStream &s, const OptionDescription &od);
QTextStream &operator<<(QTextStream &s, const OptionDescriptions &options);

class OptionsParser
{
public:
    Q_DISABLE_COPY_MOVE(OptionsParser)

    virtual ~OptionsParser();

    // Return true to indicate the option was processed.
    virtual bool handleBoolOption(const QString &key, OptionSource source);
    virtual bool handleOption(const QString &key, const QString &value, OptionSource source);

    void process(Options *);

    static const QString &pathSyntax();

protected:
    OptionsParser() noexcept;
};

class OptionsParserList : public OptionsParser
{
public:
    using OptionsParserPtr = std::shared_ptr<OptionsParser>;

    void append(const OptionsParserPtr &parser) { m_parsers.append(parser); }
    void clear() { m_parsers.clear(); }

    bool handleBoolOption(const QString &key, OptionSource source) override;
    bool handleOption(const QString &key, const QString &value, OptionSource source) override;

private:
    QList<OptionsParserPtr> m_parsers;
};

QDebug operator<<(QDebug debug, const BoolOption &bo);
QDebug operator<<(QDebug debug, const OptionValue &v);
QDebug operator<<(QDebug debug, const Options &v);

#endif // OPTIONSPARSER_H
