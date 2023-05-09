// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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
static inline QString compilerOption() { return QStringLiteral("compiler"); }
static inline QString compilerPathOption() { return QStringLiteral("compiler-path"); }
static inline QString platformOption() { return QStringLiteral("platform"); }
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
static inline QString printBuiltinTypesOption() { return QStringLiteral("print-builtin-types"); }

static const char helpHint[] = "Note: use --help or -h for more information.\n";
static const char appName[] = "shiboken";

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

    bool addCommonOption(const QString &option, const QString &value);

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

// Add options common to project file and command line
bool CommandLineArguments::addCommonOption(const QString &option,
                                           const QString &value)
{
    bool result = true;
    if (option == compilerOption() || option == compilerPathOption()
        || option == platformOption()) {
        options.insert(option, value);
    } else if (option == clangOptionOption()) {
        options.insert(option, QStringList(value));
    } else if (option == clangOptionsOption()) {
        addToOptionsList(option, value, clangOptionsSplitter);
    } else if (option == apiVersionOption()) {
        addToOptionsList(option, value, apiVersionSplitter);
    } else if (option == keywordsOption()) {
        addToOptionsList(option, value, keywordsSplitter);
    } else if (option == dropTypeEntriesOption()) {
        addToOptionsList(option, value, dropTypeEntriesSplitter);
    } else {
        result = false;
    }
    return result;
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

// Return the file command line option matching a project file keyword
static QString projectFileKeywordToCommandLineOption(const QString &p)
{
    if (p == u"include-path")
        return includePathOption(); // "include-paths", ...
    if (p == u"framework-include-path")
        return frameworkIncludePathOption();
    if (p == u"typesystem-path")
        return typesystemPathOption();
    if (p == u"system-include-paths")
        return systemIncludePathOption();
    return {};
}

static void processProjectFileLine(const QByteArray &line, CommandLineArguments &args)
{
    if (line.isEmpty())
        return;
    const QString lineS = QString::fromUtf8(line);
    const auto split = line.indexOf(u'=');
    if (split < 0) {
        args.options.insert(lineS, QString{});
        return;
    }

    const QString key = lineS.left(split).trimmed();
    const QString value = lineS.mid(split + 1).trimmed();
    const QString fileOption = projectFileKeywordToCommandLineOption(key);
    if (fileOption.isEmpty()) {
        if (key == u"header-file") {
            args.positionalArguments.prepend(value);
        } else if (key == u"typesystem-file") {
            args.positionalArguments.append(value);
        } else {
            args.options.insert(key, value);
        }
    } else {
        // Add single line value to the path list
        args.addToOptionsList(fileOption, QDir::toNativeSeparators(value));
    }
}

static std::optional<CommandLineArguments>
    processProjectFile(const char *appName, QFile &projectFile)
{
    QByteArray line = projectFile.readLine().trimmed();
    if (line.isEmpty() || line != "[generator-project]") {
        std::cerr << appName << ": first line of project file \""
            << qPrintable(projectFile.fileName())
            << "\" must be the string \"[generator-project]\"\n";
        return {};
    }

    CommandLineArguments args;
    while (!projectFile.atEnd())
        processProjectFileLine(projectFile.readLine().trimmed(), args);
    return args;
}

static std::optional<CommandLineArguments> getProjectFileArguments(const QStringList &arguments)
{
    QString projectFileName;
    for (const QString &arg : std::as_const(arguments)) {
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
        std::cerr << appName << ": Project file \""
            << qPrintable(projectFileName) << "\" not found.\n";
        return {};
    }

    QFile projectFile(projectFileName);
    if (!projectFile.open(QIODevice::ReadOnly)) {
        std::cerr << appName << ": Cannot open project file \""
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
        const auto split = arg.indexOf(u'=');
        if (split < 0) {
            args.options.insert(arg, QString());
            return;
        }
        const QString option = arg.left(split);
        const QString value = arg.mid(split + 1).trimmed();
        if (args.addCommonOption(option, value)) {
        } else if (option == includePathOption() || option == frameworkIncludePathOption()
                   || option == systemIncludePathOption() || option == typesystemPathOption()) {
            // Add platform path-separator separated list value to path list
            args.addToOptionsPathList(option, value);
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

static void getCommandLineArgs(CommandLineArguments &args, const QStringList &arguments)
{
    int argNum = 0;
    for (const QString &argument : arguments)
        getCommandLineArg(argument.trimmed(), argNum, args);
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
        {compilerOption() + u"=<type>"_s,
         u"Emulated compiler type (g++, msvc, clang)"_s},
        {platformOption() + u"=<name>"_s,
         u"Emulated platform (windows, darwin, unix)"_s},
        {compilerPathOption() + u"=<file>"_s,
         u"Path to the compiler for determining builtin include paths"_s},
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
        {printBuiltinTypesOption(),
         u"Print information about builtin types"_s},
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
    std::cout << appName << " v" << SHIBOKEN_VERSION << std::endl;
    std::cout << "Copyright (C) 2016 The Qt Company Ltd." << std::endl;
}

static inline void errorPrint(const QString &s, const QStringList &arguments)
{
    std::cerr << appName << ": " << qPrintable(s) << "\nCommand line:\n";
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

int shibokenMain(const QStringList &argV)
{
    // PYSIDE-757: Request a deterministic ordering of QHash in the code model
    // and type system.
    QHashSeed::setDeterministicGlobalSeed();

    ReportHandler::install();
    if (ReportHandler::isDebug(ReportHandler::SparseDebug))
        qCInfo(lcShiboken()).noquote().nospace() << appName << ' ' << argV.join(u' ');

    // Store command arguments in a map
    const auto projectFileArgumentsOptional = getProjectFileArguments(argV);
    if (!projectFileArgumentsOptional.has_value())
        return EXIT_FAILURE;

    const CommandLineArguments projectFileArguments = projectFileArgumentsOptional.value();
    CommandLineArguments args = projectFileArguments;
    getCommandLineArgs(args, argV);
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
            errorPrint(u"Doc strings extractions was not enabled in this shiboken build."_s, argV);
            return EXIT_FAILURE;
        }
    } else if (generatorSet.isEmpty() || generatorSet == u"shiboken") {
        generators = shibokenGenerators();
    } else {
        errorPrint(u"Unknown generator set, try \"shiboken\" or \"qtdoc\"."_s, argV);
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
                       arg(QDir::toNativeSeparators(licenseFile.fileName()), licenseFile.errorString()), argV);
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
                errorPrint(u"Invalid debug level: "_s + value, argV);
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
                errorPrint(msgInvalidVersion(package, version), argV);
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

    ait = args.options.find(compilerOption());
    if (ait != args.options.end()) {
        const QString name = ait.value().toString();
        if (!clang::setCompiler(name)) {
            errorPrint(u"Invalid value \""_s + name + u"\" passed to --compiler"_s, argV);
            return EXIT_FAILURE;
        }
        args.options.erase(ait);
    }

    ait = args.options.find(printBuiltinTypesOption());
    const bool printBuiltinTypes = ait != args.options.end();
    if (printBuiltinTypes)
        args.options.erase(ait);

    ait = args.options.find(compilerPathOption());
    if (ait != args.options.end()) {
        clang::setCompilerPath(ait.value().toString());
        args.options.erase(ait);
    }

    ait = args.options.find(platformOption());
    if (ait != args.options.end()) {
        const QString name = ait.value().toString();
        if (!clang::setPlatform(name)) {
            errorPrint(u"Invalid value \""_s + name + u"\" passed to --platform"_s, argV);
            return EXIT_FAILURE;
        }
        args.options.erase(ait);
    }

    parseIncludePathOption(includePathOption(), HeaderType::Standard,
                           args, extractor);
    parseIncludePathOption(frameworkIncludePathOption(), HeaderType::Framework,
                           args, extractor);
    parseIncludePathOption(systemIncludePathOption(), HeaderType::System,
                           args, extractor);

    if (args.positionalArguments.size() < 2) {
        errorPrint(u"Insufficient positional arguments, specify header-file and typesystem-file."_s,
                  argV);
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
    for (const QString &cppFileName : std::as_const(args.positionalArguments)) {
        const QFileInfo cppFileNameFi(cppFileName);
        if (!cppFileNameFi.isFile() && !cppFileNameFi.isSymLink()) {
            errorPrint(u'"' + cppFileName + u"\" does not exist."_s, argV);
            return EXIT_FAILURE;
        }
        cppFileNames.append(cppFileNameFi);
    }

    // Pass option to all generators (Cpp/Header generator have the same options)
    for (ait = args.options.begin(); ait != args.options.end(); ) {
        bool found = false;
        for (const GeneratorPtr &generator : std::as_const(generators))
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
        errorPrint(msgLeftOverArguments(args.options), argV);
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
        errorPrint(u"Error running ApiExtractor."_s, argV);
        return EXIT_FAILURE;
    }

    if (apiOpt->classes().isEmpty())
        qCWarning(lcShiboken) << "No C++ classes found!";

    if (ReportHandler::isDebug(ReportHandler::FullDebug)
        || qEnvironmentVariableIsSet("SHIBOKEN_DUMP_CODEMODEL")) {
        qCInfo(lcShiboken) << "API Extractor:\n" << extractor
            << "\n\nType datase:\n" << *TypeDatabase::instance();
    }

    if (printBuiltinTypes)
        TypeDatabase::instance()->formatBuiltinTypes(qInfo());

    for (const GeneratorPtr &g : std::as_const(generators)) {
        g->setOutputDirectory(outputDirectory);
        g->setLicenseComment(licenseComment);
        ReportHandler::startProgress(QByteArray("Running ") + g->name() + "...");
        const bool ok = g->setup(apiOpt.value()) && g->generate();
        ReportHandler::endProgress();
         if (!ok) {
             errorPrint(u"Error running generator: "_s
                        + QLatin1StringView(g->name()) + u'.', argV);
             return EXIT_FAILURE;
         }
    }

    const QByteArray doneMessage = ReportHandler::doneMessage();
    std::cout << doneMessage.constData() << std::endl;

    return EXIT_SUCCESS;
}

#ifndef Q_OS_WIN

static inline QString argvToString(const char *arg)
{
    return QString::fromLocal8Bit(arg);
}

int main(int argc, char *argv[])
#else

static inline QString argvToString(const  wchar_t *arg)
{
    return QString::fromWCharArray(arg);
}

int wmain(int argc, wchar_t *argv[])
#endif
{
    int ex = EXIT_SUCCESS;

    QStringList argV;
    argV.reserve(argc - 1);
    std::transform(argv + 1, argv + argc, std::back_inserter(argV), argvToString);

    try {
        ex = shibokenMain(argV);
    }  catch (const std::exception &e) {
        std::cerr << appName << " error: " << e.what() << std::endl;
        ex = EXIT_FAILURE;
    }
    return ex;
}
