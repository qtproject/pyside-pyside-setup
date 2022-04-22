/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
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

#include "shibokenconfig.h"
#include "cppgenerator.h"
#include "generator.h"
#include "headergenerator.h"
#include "qtdocgenerator.h"

#include <apiextractor.h>
#include <apiextractorresult.h>
#include <fileout.h>
#include <messages.h>
#include <reporthandler.h>
#include <typedatabase.h>

#include <QtCore/QCoreApplication>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QLibrary>
#include <QtCore/QVariant>

#include "qtcompat.h"

#include <exception>
#include <iostream>

using namespace Qt::StringLiterals;

static const QChar clangOptionsSplitter = u',';
static const QChar keywordsSplitter = u',';
static const QChar dropTypeEntriesSplitter = u';';
static const QChar apiVersionSplitter = u'|';

static inline QString keywordsOption() { return QStringLiteral("keywords"); }
static inline QString clangOptionOption() { return QStringLiteral("clang-option"); }
static inline QString clangOptionsOption() { return QStringLiteral("clang-options"); }
static inline QString apiVersionOption() { return QStringLiteral("api-version"); }
static inline QString dropTypeEntriesOption() { return QStringLiteral("drop-type-entries"); }
static inline QString languageLevelOption() { return QStringLiteral("language-level"); }
static inline QString includePathOption() { return QStringLiteral("include-paths"); }
static inline QString frameworkIncludePathOption() { return QStringLiteral("framework-include-paths"); }
static inline QString systemIncludePathOption() { return QStringLiteral("system-include-paths"); }
static inline QString typesystemPathOption() { return QStringLiteral("typesystem-paths"); }
static inline QString helpOption() { return QStringLiteral("help"); }
static inline QString diffOption() { return QStringLiteral("diff"); }
static inline QString useGlobalHeaderOption() { return QStringLiteral("use-global-header"); }
static inline QString dryrunOption() { return QStringLiteral("dry-run"); }
static inline QString skipDeprecatedOption() { return QStringLiteral("skip-deprecated"); }

static const char helpHint[] = "Note: use --help or -h for more information.\n";

using OptionDescriptions = Generator::OptionDescriptions;

struct CommandLineArguments
{
    void addToOptionsList(const QString &option,
                          const QString &value);
    void addToOptionsList(const QString &option,
                          const QStringList &value);
    void addToOptionsList(const QString &option,
                          const QString &listValue,
                          QChar separator);
    void addToOptionsPathList(const QString &option,
                              const QString &pathListValue)
    {
        addToOptionsList(option, pathListValue, QDir::listSeparator());
    }

    QVariantMap options; // string,stringlist for path lists, etc.
    QStringList positionalArguments;
};

void CommandLineArguments::addToOptionsList(const QString &option,
                                            const QString &value)
{
    auto it = options.find(option);
    if (it == options.end()) {
        options.insert(option, QVariant(QStringList(value)));
    } else {
        auto list = it.value().toStringList();
        list += value;
        options[option] = QVariant(list);
    }
}

void CommandLineArguments::addToOptionsList(const QString &option,
                                            const QStringList &value)
{
    auto it = options.find(option);
    if (it == options.end()) {
        options.insert(option, QVariant(value));
    } else {
        auto list = it.value().toStringList();
        list += value;
        options[option] = QVariant(list);
    }
}

void CommandLineArguments::addToOptionsList(const QString &option,
                                            const QString &listValue,
                                            QChar separator)
{
    const auto newValues = listValue.split(separator, Qt::SkipEmptyParts);
    addToOptionsList(option, newValues);
}

static void printOptions(QTextStream &s, const OptionDescriptions &options)
{
    s.setFieldAlignment(QTextStream::AlignLeft);
    for (const auto &od : options) {
        if (!od.first.startsWith(u'-'))
            s << "--";
        s << od.first;
        if (od.second.isEmpty()) {
            s << ", ";
        } else {
            s << Qt::endl;
            const auto lines = QStringView{od.second}.split(u'\n');
            for (const auto &line : lines)
                s << "        " << line << Qt::endl;
            s << Qt::endl;
        }
    }
}

static std::optional<CommandLineArguments>
    processProjectFile(const QString &appName, QFile &projectFile)
{
    QByteArray line = projectFile.readLine().trimmed();
    if (line.isEmpty() || line != "[generator-project]") {
        std::cerr << qPrintable(appName) << ": first line of project file \""
            << qPrintable(projectFile.fileName())
            << "\" must be the string \"[generator-project]\"\n";
        return {};
    }

    CommandLineArguments args;

    while (!projectFile.atEnd()) {
        line = projectFile.readLine().trimmed();
        if (line.isEmpty())
            continue;

        int split = line.indexOf('=');
        QByteArray key;
        QString value;
        if (split > 0) {
            key = line.left(split).trimmed();
            value = QString::fromUtf8(line.mid(split + 1).trimmed());
        } else {
            key = line;
        }

        if (key == "include-path") {
            args.addToOptionsList(includePathOption(),
                                  QDir::toNativeSeparators(value));
        } else if (key == "framework-include-path") {
            args.addToOptionsList(frameworkIncludePathOption(),
                                  QDir::toNativeSeparators(value));
        } else if (key == "system-include-paths") {
            args.addToOptionsList(systemIncludePathOption(),
                                  QDir::toNativeSeparators(value));
        } else if (key == "typesystem-path") {
            args.addToOptionsList(typesystemPathOption(),
                                  QDir::toNativeSeparators(value));
        } else if (key == "language-level") {
            args.options.insert(languageLevelOption(), value);
        } else if (key == "clang-option") {
            args.addToOptionsList(clangOptionsOption(), value);
        } else if (key == "clang-options") {
            args.addToOptionsList(clangOptionsOption(),
                                  value, clangOptionsSplitter);
        } else if (key == "api-version") {
            args.addToOptionsList(apiVersionOption(),
                                  value, apiVersionSplitter);
        } else if (key == "keywords") {
            args.addToOptionsList(keywordsOption(),
                                  value, keywordsSplitter);
        } else if (key == "drop-type-entries") {
            args.addToOptionsList(dropTypeEntriesOption(),
                                  value, dropTypeEntriesSplitter);
        } else if (key == "header-file") {
            args.positionalArguments.prepend(value);
        } else if (key == "typesystem-file") {
            args.positionalArguments.append(value);
        } else {
            args.options.insert(QString::fromUtf8(key), value);
        }
    }

    return args;
}

static std::optional<CommandLineArguments> getProjectFileArguments()
{
    QStringList arguments = QCoreApplication::arguments();
    QString appName = arguments.constFirst();
    arguments.removeFirst();

    QString projectFileName;
    for (const QString &arg : qAsConst(arguments)) {
        if (arg.startsWith(u"--project-file")) {
            int split = arg.indexOf(u'=');
            if (split > 0)
                projectFileName = arg.mid(split + 1).trimmed();
            break;
        }
    }

    if (projectFileName.isEmpty())
        return CommandLineArguments{};

    if (!QFile::exists(projectFileName)) {
        std::cerr << qPrintable(appName) << ": Project file \""
            << qPrintable(projectFileName) << "\" not found.\n";
        return {};
    }

    QFile projectFile(projectFileName);
    if (!projectFile.open(QIODevice::ReadOnly)) {
        std::cerr << qPrintable(appName) << ": Cannot open project file \""
            << qPrintable(projectFileName) << "\" : " << qPrintable(projectFile.errorString())
            << '\n';
        return {};
    }
    return processProjectFile(appName, projectFile);
}

static void getCommandLineArg(QString arg, int &argNum, CommandLineArguments &args)
{
    if (arg.startsWith(u"--")) {
        arg.remove(0, 2);
        const int split = arg.indexOf(u'=');
        if (split < 0) {
            args.options.insert(arg, QString());
            return;
        }
        const QString option = arg.left(split);
        const QString value = arg.mid(split + 1).trimmed();
        if (option == includePathOption() || option == frameworkIncludePathOption()
            || option == systemIncludePathOption() || option == typesystemPathOption()) {
            args.addToOptionsPathList(option, value);
        } else if (option == apiVersionOption()) {
            args.addToOptionsList(apiVersionOption(), value, apiVersionSplitter);
        } else if (option == dropTypeEntriesOption()) {
            args.addToOptionsList(dropTypeEntriesOption(), value, dropTypeEntriesSplitter);
        } else if (option == clangOptionOption()) {
            args.addToOptionsList(clangOptionsOption(), value);
        } else if (option == clangOptionsOption()) {
            args.addToOptionsList(clangOptionsOption(), value, clangOptionsSplitter);
        } else if (option == keywordsOption()) {
            args.addToOptionsList(keywordsOption(), value, keywordsSplitter);
        } else {
            args.options.insert(option, value);
        }
        return;
    }
    if (arg.startsWith(u'-')) {
        arg.remove(0, 1);
        if (arg.startsWith(u'I')) // Shorthand path arguments -I/usr/include...
            args.addToOptionsPathList(includePathOption(), arg.mid(1));
        else if (arg.startsWith(u'F'))
            args.addToOptionsPathList(frameworkIncludePathOption(), arg.mid(1));
        else if (arg.startsWith(u"isystem"))
            args.addToOptionsPathList(systemIncludePathOption(), arg.mid(7));
        else if (arg.startsWith(u'T'))
            args.addToOptionsPathList(typesystemPathOption(), arg.mid(1));
        else if (arg == u"h")
            args.options.insert(helpOption(), QString());
        else if (arg.startsWith(u"std="))
            args.options.insert(languageLevelOption(), arg.mid(4));
        else
            args.options.insert(arg, QString());
        return;
    }
    if (argNum < args.positionalArguments.size())
        args.positionalArguments[argNum] = arg;
    else
        args.positionalArguments.append(arg);
    ++argNum;
}

static void getCommandLineArgs(CommandLineArguments &args)
{
    const QStringList arguments = QCoreApplication::arguments();
    int argNum = 0;
    for (int i = 1, size = arguments.size(); i < size; ++i)
        getCommandLineArg(arguments.at(i).trimmed(), argNum, args);
}

static inline Generators docGenerators()
{
    Generators result;
#ifdef DOCSTRINGS_ENABLED
    result.append(GeneratorPtr(new QtDocGenerator));
#endif
    return result;
}

static inline Generators shibokenGenerators()
{
    Generators result;
    result << GeneratorPtr(new CppGenerator) << GeneratorPtr(new HeaderGenerator);
    return result;
}

static inline QString languageLevelDescription()
{
    return u"C++ Language level (c++11..c++17, default="_s
        + QLatin1StringView(clang::languageLevelOption(clang::emulatedCompilerLanguageLevel()))
        + u')';
}

void printUsage()
{
    const QChar pathSplitter = QDir::listSeparator();
    QTextStream s(stdout);
    s << "Usage:\n  "
      << "shiboken [options] header-file(s) typesystem-file\n\n"
      << "General options:\n";
    QString pathSyntax;
    QTextStream(&pathSyntax) << "<path>[" << pathSplitter << "<path>"
        << pathSplitter << "...]";
    OptionDescriptions generalOptions = {
        {u"api-version=<\"package mask\">,<\"version\">"_s,
         u"Specify the supported api version used to generate the bindings"_s},
        {u"debug-level=[sparse|medium|full]"_s,
         u"Set the debug level"_s},
        {u"documentation-only"_s,
         u"Do not generates any code, just the documentation"_s},
        {u"drop-type-entries=\"<TypeEntry0>[;TypeEntry1;...]\""_s,
         u"Semicolon separated list of type system entries (classes, namespaces,\n"
          "global functions and enums) to be dropped from generation."_s},
        {keywordsOption() + QStringLiteral("=keyword1[,keyword2,...]"),
         u"A comma-separated list of keywords for conditional typesystem parsing"_s},
        {clangOptionOption(),
         u"Option to be passed to clang"_s},
        {clangOptionsOption(),
         u"A comma-separated list of options to be passed to clang"_s},
        {u"-F<path>"_s, {} },
        {u"framework-include-paths="_s + pathSyntax,
         u"Framework include paths used by the C++ parser"_s},
        {u"-isystem<path>"_s, {} },
        {u"system-include-paths="_s + pathSyntax,
         u"System include paths used by the C++ parser"_s},
        {useGlobalHeaderOption(),
         u"Use the global headers in generated code."_s},
        {u"generator-set=<\"generator module\">"_s,
         u"generator-set to be used. e.g. qtdoc"_s},
        {skipDeprecatedOption(),
         u"Skip deprecated functions"_s},
        {diffOption(), u"Print a diff of wrapper files"_s},
        {dryrunOption(), u"Dry run, do not generate wrapper files"_s},
        {u"-h"_s, {} },
        {helpOption(), u"Display this help and exit"_s},
        {u"-I<path>"_s, {} },
        {u"include-paths="_s + pathSyntax,
        u"Include paths used by the C++ parser"_s},
        {languageLevelOption() + u"=, -std=<level>"_s,
         languageLevelDescription()},
        {u"license-file=<license-file>"_s,
         u"File used for copyright headers of generated files"_s},
        {u"no-suppress-warnings"_s,
         u"Show all warnings"_s},
        {u"output-directory=<path>"_s,
         u"The directory where the generated files will be written"_s},
        {u"project-file=<file>"_s,
         u"text file containing a description of the binding project.\n"
          "Replaces and overrides command line arguments"_s},
        {u"silent"_s, u"Avoid printing any message"_s},
        {u"-T<path>"_s, {} },
        {u"typesystem-paths="_s + pathSyntax,
         u"Paths used when searching for typesystems"_s},
        {u"version"_s,
         u"Output version information and exit"_s}
    };
    printOptions(s, generalOptions);

    const Generators generators = shibokenGenerators() + docGenerators();
    for (const GeneratorPtr &generator : generators) {
        const OptionDescriptions options = generator->options();
        if (!options.isEmpty()) {
            s << Qt::endl << generator->name() << " options:\n\n";
            printOptions(s, generator->options());
        }
    }
}

static inline void printVerAndBanner()
{
    std::cout << "shiboken v" SHIBOKEN_VERSION << std::endl;
    std::cout << "Copyright (C) 2016 The Qt Company Ltd." << std::endl;
}

static inline void errorPrint(const QString &s)
{
    QStringList arguments = QCoreApplication::arguments();
    arguments.pop_front();
    std::cerr << "shiboken: " << qPrintable(s) << "\nCommand line:\n";
    for (const auto &argument : arguments)
        std::cerr << "    \"" << qPrintable(argument) << "\"\n";
}

static void parseIncludePathOption(const QString &option, HeaderType headerType,
                                   CommandLineArguments &args,
                                   ApiExtractor &extractor)
{
    const auto it = args.options.find(option);
    if (it != args.options.end()) {
        const auto includePathListList = it.value().toStringList();
        args.options.erase(it);
        for (const QString &s : includePathListList) {
            auto path = QFile::encodeName(QDir::cleanPath(s));
            extractor.addIncludePath(HeaderPath{path, headerType});
        }
    }
}

int shibokenMain(int argc, char *argv[])
{
    // PYSIDE-757: Request a deterministic ordering of QHash in the code model
    // and type system.
    qSetGlobalQHashSeed(0);
    // needed by qxmlpatterns
    QCoreApplication app(argc, argv);
    ReportHandler::install();
    if (ReportHandler::isDebug(ReportHandler::SparseDebug))
        qCInfo(lcShiboken()).noquote().nospace() << QCoreApplication::arguments().join(u' ');

    // Store command arguments in a map
    const auto projectFileArgumentsOptional = getProjectFileArguments();
    if (!projectFileArgumentsOptional.has_value())
        return EXIT_FAILURE;

    const CommandLineArguments projectFileArguments = projectFileArgumentsOptional.value();
    CommandLineArguments args = projectFileArguments;
    getCommandLineArgs(args);
    Generators generators;

    auto ait = args.options.find(u"version"_s);
    if (ait != args.options.end()) {
        args.options.erase(ait);
        printVerAndBanner();
        return EXIT_SUCCESS;
    }

    QString generatorSet;
    ait = args.options.find(u"generator-set"_s);
    if (ait == args.options.end()) // Also check "generatorSet" command line argument for backward compatibility.
        ait = args.options.find(u"generatorSet"_s);
    if (ait != args.options.end()) {
        generatorSet = ait.value().toString();
        args.options.erase(ait);
    }

    // Pre-defined generator sets.
    if (generatorSet == u"qtdoc") {
        generators = docGenerators();
        if (generators.isEmpty()) {
            errorPrint(u"Doc strings extractions was not enabled in this shiboken build."_s);
            return EXIT_FAILURE;
        }
    } else if (generatorSet.isEmpty() || generatorSet == u"shiboken") {
        generators = shibokenGenerators();
    } else {
        errorPrint(u"Unknown generator set, try \"shiboken\" or \"qtdoc\"."_s);
        return EXIT_FAILURE;
    }

    ait = args.options.find(u"help"_s);
    if (ait != args.options.end()) {
        args.options.erase(ait);
        printUsage();
        return EXIT_SUCCESS;
    }

    ait = args.options.find(diffOption());
    if (ait != args.options.end()) {
        args.options.erase(ait);
        FileOut::setDiff(true);
    }

    ait = args.options.find(useGlobalHeaderOption());
    if (ait != args.options.end()) {
        args.options.erase(ait);
        ApiExtractor::setUseGlobalHeader(true);
    }

    ait = args.options.find(dryrunOption());
    if (ait != args.options.end()) {
        args.options.erase(ait);
        FileOut::setDryRun(true);
    }

    QString licenseComment;
    ait = args.options.find(u"license-file"_s);
    if (ait != args.options.end()) {
        QFile licenseFile(ait.value().toString());
        args.options.erase(ait);
        if (licenseFile.open(QIODevice::ReadOnly)) {
            licenseComment = QString::fromUtf8(licenseFile.readAll());
        } else {
            errorPrint(QStringLiteral("Could not open the file \"%1\" containing the license heading: %2").
                       arg(QDir::toNativeSeparators(licenseFile.fileName()), licenseFile.errorString()));
            return EXIT_FAILURE;
        }
    }

    QString outputDirectory = u"out"_s;
    ait = args.options.find(u"output-directory"_s);
    if (ait != args.options.end()) {
        outputDirectory = ait.value().toString();
        args.options.erase(ait);
    }

    if (!QDir(outputDirectory).exists()) {
        if (!QDir().mkpath(outputDirectory)) {
            qCWarning(lcShiboken).noquote().nospace()
                << "Can't create output directory: " << QDir::toNativeSeparators(outputDirectory);
            return EXIT_FAILURE;
        }
    }

    // Create and set-up API Extractor
    ApiExtractor extractor;
    extractor.setLogDirectory(outputDirectory);
    ait = args.options.find(skipDeprecatedOption());
    if (ait != args.options.end()) {
        extractor.setSkipDeprecated(true);
        args.options.erase(ait);
    }

    ait = args.options.find(u"silent"_s);
    if (ait != args.options.end()) {
        extractor.setSilent(true);
        args.options.erase(ait);
    } else {
        ait = args.options.find(u"debug-level"_s);
        if (ait != args.options.end()) {
            const QString value = ait.value().toString();
            if (!ReportHandler::setDebugLevelFromArg(value)) {
                errorPrint(u"Invalid debug level: "_s + value);
                return EXIT_FAILURE;
            }
            args.options.erase(ait);
        }
    }
    ait = args.options.find(u"no-suppress-warnings"_s);
    if (ait != args.options.end()) {
        args.options.erase(ait);
        extractor.setSuppressWarnings(false);
    }
    ait = args.options.find(apiVersionOption());
    if (ait != args.options.end()) {
        const QStringList &versions = ait.value().toStringList();
        args.options.erase(ait);
        for (const QString &fullVersion : versions) {
            QStringList parts = fullVersion.split(u',');
            QString package;
            QString version;
            package = parts.size() == 1 ? u"*"_s : parts.constFirst();
            version = parts.constLast();
            if (!extractor.setApiVersion(package, version)) {
                errorPrint(msgInvalidVersion(package, version));
                return EXIT_FAILURE;
            }
        }
    }

    ait = args.options.find(dropTypeEntriesOption());
    if (ait != args.options.end()) {
        extractor.setDropTypeEntries(ait.value().toStringList());
        args.options.erase(ait);
    }

    ait = args.options.find(keywordsOption());
    if (ait != args.options.end()) {
        extractor.setTypesystemKeywords(ait.value().toStringList());
        args.options.erase(ait);
    }

    ait = args.options.find(typesystemPathOption());
    if (ait != args.options.end()) {
        extractor.addTypesystemSearchPath(ait.value().toStringList());
        args.options.erase(ait);
    }

    ait = args.options.find(clangOptionsOption());
    if (ait != args.options.end()) {
        extractor.setClangOptions(ait.value().toStringList());
        args.options.erase(ait);
    }

    parseIncludePathOption(includePathOption(), HeaderType::Standard,
                           args, extractor);
    parseIncludePathOption(frameworkIncludePathOption(), HeaderType::Framework,
                           args, extractor);
    parseIncludePathOption(systemIncludePathOption(), HeaderType::System,
                           args, extractor);

    if (args.positionalArguments.size() < 2) {
        errorPrint(u"Insufficient positional arguments, specify header-file and typesystem-file."_s);
        std::cout << '\n';
        printUsage();
        return EXIT_FAILURE;
    }

    const QString typeSystemFileName = args.positionalArguments.takeLast();
    QString messagePrefix = QFileInfo(typeSystemFileName).baseName();
    if (messagePrefix.startsWith(u"typesystem_"))
        messagePrefix.remove(0, 11);
    ReportHandler::setPrefix(u'(' + messagePrefix + u')');

    QFileInfoList cppFileNames;
    for (const QString &cppFileName : qAsConst(args.positionalArguments)) {
        const QFileInfo cppFileNameFi(cppFileName);
        if (!cppFileNameFi.isFile() && !cppFileNameFi.isSymLink()) {
            errorPrint(u'"' + cppFileName + u"\" does not exist."_s);
            return EXIT_FAILURE;
        }
        cppFileNames.append(cppFileNameFi);
    }

    // Pass option to all generators (Cpp/Header generator have the same options)
    for (ait = args.options.begin(); ait != args.options.end(); ) {
        bool found = false;
        for (const GeneratorPtr &generator : qAsConst(generators))
            found |= generator->handleOption(ait.key(), ait.value().toString());
        if (found)
            ait = args.options.erase(ait);
        else
            ++ait;
    }

    ait = args.options.find(languageLevelOption());
    if (ait != args.options.end()) {
        const QByteArray languageLevelBA = ait.value().toString().toLatin1();
        args.options.erase(ait);
        const LanguageLevel level = clang::languageLevelFromOption(languageLevelBA.constData());
        if (level == LanguageLevel::Default) {
            std::cout << "Invalid argument for language level: \""
                << languageLevelBA.constData() << "\"\n" << helpHint;
            return EXIT_FAILURE;
        }
        extractor.setLanguageLevel(level);
    }

    /* Make sure to remove the project file's arguments (if any) and
     * --project-file, also the arguments of each generator before
     * checking if there isn't any existing arguments in argsHandler.
     */
    args.options.remove(u"project-file"_s);
    for (auto it = projectFileArguments.options.cbegin(), end = projectFileArguments.options.cend();
         it != end; ++it) {
        args.options.remove(it.key());
    }

    if (!args.options.isEmpty()) {
        errorPrint(msgLeftOverArguments(args.options));
        std::cout << helpHint;
        return EXIT_FAILURE;
    }

    if (typeSystemFileName.isEmpty()) {
        std::cout << "You must specify a Type System file." << std::endl << helpHint;
        return EXIT_FAILURE;
    }

    extractor.setCppFileNames(cppFileNames);
    extractor.setTypeSystem(typeSystemFileName);

    ApiExtractorFlags apiExtractorFlags;
    if (generators.constFirst()->usePySideExtensions())
        apiExtractorFlags.setFlag(ApiExtractorFlag::UsePySideExtensions);
    if (generators.constFirst()->avoidProtectedHack())
        apiExtractorFlags.setFlag(ApiExtractorFlag::AvoidProtectedHack);
    const std::optional<ApiExtractorResult> apiOpt = extractor.run(apiExtractorFlags);

    if (!apiOpt.has_value()) {
        errorPrint(u"Error running ApiExtractor."_s);
        return EXIT_FAILURE;
    }

    if (apiOpt->classes().isEmpty())
        qCWarning(lcShiboken) << "No C++ classes found!";

    if (ReportHandler::isDebug(ReportHandler::FullDebug)
        || qEnvironmentVariableIsSet("SHIBOKEN_DUMP_CODEMODEL")) {
        qCInfo(lcShiboken) << "API Extractor:\n" << extractor
            << "\n\nType datase:\n" << *TypeDatabase::instance();
    }

    for (const GeneratorPtr &g : qAsConst(generators)) {
        g->setOutputDirectory(outputDirectory);
        g->setLicenseComment(licenseComment);
        ReportHandler::startProgress(QByteArray("Running ") + g->name() + "...");
        const bool ok = g->setup(apiOpt.value()) && g->generate();
        ReportHandler::endProgress();
         if (!ok) {
             errorPrint(u"Error running generator: "_s
                        + QLatin1StringView(g->name()) + u'.');
             return EXIT_FAILURE;
         }
    }

    const QByteArray doneMessage = ReportHandler::doneMessage();
    std::cout << doneMessage.constData() << std::endl;

    return EXIT_SUCCESS;
}

int main(int argc, char *argv[])
{
    int ex = EXIT_SUCCESS;
    try {
        ex = shibokenMain(argc, argv);
    }  catch (const std::exception &e) {
        std::cerr << e.what() << std::endl;
        ex = EXIT_FAILURE;
    }
    return ex;
}
