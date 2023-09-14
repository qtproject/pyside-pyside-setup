// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "shibokenconfig.h"
#include "cppgenerator.h"
#include "generator.h"
#include "headergenerator.h"
#include "qtdocgenerator.h"

#include <apiextractor.h>
#include <apiextractorresult.h>
#include <exception.h>
#include <fileout.h>
#include <messages.h>
#include <optionsparser.h>
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

static const char helpHint[] = "Note: use --help or -h for more information.\n";
static const char appName[] = "shiboken";

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

struct CommonOptions
{
    QString generatorSet;
    QString licenseComment;
    QString outputDirectory = u"out"_s;
    QStringList headers;
    QString typeSystemFileName;
    bool help = false;
    bool version = false;
    bool diff = false;
    bool dryRun = false;
    bool logUnmatched = false;
    bool printBuiltinTypes = false;
};

class CommonOptionsParser : public OptionsParser
{
public:
    explicit CommonOptionsParser(CommonOptions *o) : m_options(o) {}

    bool handleBoolOption(const QString &key, OptionSource source) override;
    bool handleOption(const QString &key, const QString &value, OptionSource source) override;

    static OptionDescriptions optionDescriptions();

private:
    CommonOptions *m_options;
};

OptionDescriptions CommonOptionsParser::optionDescriptions()
{
    return {
        {u"debug-level=[sparse|medium|full]"_s,
         u"Set the debug level"_s},
        {u"documentation-only"_s,
         u"Do not generates any code, just the documentation"_s},
        {u"compiler=<type>"_s,
         u"Emulated compiler type (g++, msvc, clang)"_s},
        {u"platform=<name>"_s,
         u"Emulated platform (windows, darwin, unix)"_s},
        {u"compiler-path=<file>"_s,
         u"Path to the compiler for determining builtin include paths"_s},
        {u"generator-set=<\"generator module\">"_s,
         u"generator-set to be used. e.g. qtdoc"_s},
        {u"diff"_s, u"Print a diff of wrapper files"_s},
        {u"dry-run"_s, u"Dry run, do not generate wrapper files"_s},
        {u"-h"_s, {} },
        {u"help"_s, u"Display this help and exit"_s},
        {u"-I<path>"_s, {} },
        {u"include-paths="_s + OptionsParser::pathSyntax(),
        u"Include paths used by the C++ parser"_s},
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
        {u"print-builtin-types"_s,
         u"Print information about builtin types"_s},
        {u"version"_s,
         u"Output version information and exit"_s}
    };
}

bool CommonOptionsParser::handleBoolOption(const QString &key, OptionSource source)
{
    if (source == OptionSource::CommandLineSingleDash) {
        if (key == u"h") {
            m_options->help = true;
            return true;
        }
        return false;
    }

    if (key == u"version") {
        m_options->version = true;
        return true;
    }
    if (key == u"help") {
        m_options->help = true;
        return true;
    }
    if (key == u"diff") {
        FileOut::setDiff(true);
        return true;
    }
    if (key == u"dry-run") {
        FileOut::setDryRun(true);
        return true;
    }
    if (key == u"silent") {
        ReportHandler::setSilent(true);
        return true;
    }
    if (key == u"log-unmatched") {
        m_options->logUnmatched = true;
        return true;
    }
    if (key == u"print-builtin-types") {
        m_options->printBuiltinTypes = true;
        return true;
    }

    return false;
}

bool CommonOptionsParser::handleOption(const QString &key, const QString &value,
                                       OptionSource source)
{
    if (source == OptionSource::CommandLineSingleDash)
        return false;

    if (key == u"generator-set" || key == u"generatorSet" /* legacy */) {
        m_options->generatorSet = value;
        return true;
    }
    if (key == u"license-file") {
        QFile licenseFile(value);
        if (!licenseFile.open(QIODevice::ReadOnly))
            throw Exception(msgCannotOpenForReading(licenseFile));
        m_options->licenseComment = QString::fromUtf8(licenseFile.readAll());
        return true;
    }
    if (key == u"debug-level") {
        if (!ReportHandler::setDebugLevelFromArg(value))
            throw Exception(u"Invalid debug level: "_s + value);
        return true;
    }
    if (key == u"output-directory") {
        m_options->outputDirectory = value;
        return true;
    }
    if (key == u"compiler") {
        if (!clang::setCompiler(value))
            throw Exception(u"Invalid value \""_s + value + u"\" passed to --compiler"_s);
        return true;
    }
    if (key == u"compiler-path") {
        clang::setCompilerPath(value);
        return true;
    }
    if (key == u"platform") {
        if (!clang::setPlatform(value))
            throw Exception(u"Invalid value \""_s + value + u"\" passed to --platform"_s);
        return true;
    }

    if (source == OptionSource::ProjectFile) {
        if (key == u"header-file") {
            m_options->headers.append(value);
            return true;
        }
        if (key == u"typesystem-file") {
            m_options->typeSystemFileName = value;
            return true;
        }
    }

    return false;
}

void printUsage()
{
    const auto generatorOptions = Generator::options();

    QTextStream s(stdout);
    s << "Usage:\n  "
        << "shiboken [options] header-file(s) typesystem-file\n\n"
        << "General options:\n"
        << CommonOptionsParser::optionDescriptions()
        << ApiExtractor::options()
        << TypeDatabase::options()
        << "\nSource generator options:\n\n" << generatorOptions
        << ShibokenGenerator::options();

#ifdef DOCSTRINGS_ENABLED
    s << "\nDocumentation Generator options:\n\n"
        << generatorOptions << QtDocGenerator::options();
#endif
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

int shibokenMain(const QStringList &argV)
{
    // PYSIDE-757: Request a deterministic ordering of QHash in the code model
    // and type system.
    QHashSeed::setDeterministicGlobalSeed();

    ReportHandler::install();
    if (ReportHandler::isDebug(ReportHandler::SparseDebug))
        qCInfo(lcShiboken()).noquote().nospace() << appName << ' ' << argV.join(u' ');

    Options options;
    options.setOptions(argV);

    CommonOptions commonOptions;
    {
        CommonOptionsParser parser(&commonOptions);
        parser.process(&options);
    }
    if (commonOptions.version) {
        printVerAndBanner();
        return EXIT_SUCCESS;
    }
    if (commonOptions.help) {
        printUsage();
        return EXIT_SUCCESS;
    }

    Generators generators;

    OptionsParserList optionParser;
    optionParser.append(Generator::createOptionsParser());
    optionParser.append(TypeDatabase::instance()->createOptionsParser());
    ApiExtractor extractor;
    optionParser.append(extractor.createOptionsParser());

    // Pre-defined generator sets.
    if (commonOptions.generatorSet == u"qtdoc") {
        generators = docGenerators();
        if (generators.isEmpty()) {
            errorPrint(u"Doc strings extractions was not enabled in this shiboken build."_s, argV);
            return EXIT_FAILURE;
        }
#ifdef DOCSTRINGS_ENABLED
        optionParser.append(QtDocGenerator::createOptionsParser());
#endif
    } else if (commonOptions.generatorSet.isEmpty() || commonOptions.generatorSet == u"shiboken") {
        generators = shibokenGenerators();
        optionParser.append(ShibokenGenerator::createOptionsParser());
    } else {
        errorPrint(u"Unknown generator set, try \"shiboken\" or \"qtdoc\"."_s, argV);
        return EXIT_FAILURE;
    }

    if (!QDir(commonOptions.outputDirectory).exists()) {
        if (!QDir().mkpath(commonOptions.outputDirectory)) {
            qCWarning(lcShiboken).noquote().nospace()
                << "Can't create output directory: "
                << QDir::toNativeSeparators(commonOptions.outputDirectory);
            return EXIT_FAILURE;
        }
    }

    // Create and set-up API Extractor
    extractor.setLogDirectory(commonOptions.outputDirectory);

    if (commonOptions.typeSystemFileName.isEmpty() && commonOptions.headers.isEmpty()) {
        if (options.positionalArguments.size() < 2) {
            errorPrint(u"Insufficient positional arguments, specify header-file and typesystem-file."_s,
                       argV);
            std::cout << '\n';
            printUsage();
            return EXIT_FAILURE;
        }

        commonOptions.typeSystemFileName = options.positionalArguments.takeLast();
        commonOptions.headers = options.positionalArguments;
    }

    QString messagePrefix = QFileInfo(commonOptions.typeSystemFileName).baseName();
    if (messagePrefix.startsWith(u"typesystem_"))
        messagePrefix.remove(0, 11);
    ReportHandler::setPrefix(u'(' + messagePrefix + u')');

    QFileInfoList cppFileNames;
    for (const QString &cppFileName : std::as_const(commonOptions.headers)) {
        const QFileInfo cppFileNameFi(cppFileName);
        if (!cppFileNameFi.isFile() && !cppFileNameFi.isSymLink()) {
            errorPrint(u'"' + cppFileName + u"\" does not exist."_s, argV);
            return EXIT_FAILURE;
        }
        cppFileNames.append(cppFileNameFi);
    }

    optionParser.process(&options);
    optionParser.clear();

    if (!options.boolOptions.isEmpty() || !options.valueOptions.isEmpty()) {
        errorPrint(msgLeftOverArguments(options.msgUnprocessedOptions(), argV), argV);
        std::cout << helpHint;
        return EXIT_FAILURE;
    }

    if (commonOptions.typeSystemFileName.isEmpty()) {
        std::cout << "You must specify a Type System file." << std::endl << helpHint;
        return EXIT_FAILURE;
    }

    extractor.setCppFileNames(cppFileNames);
    extractor.setTypeSystem(commonOptions.typeSystemFileName);

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

    if (commonOptions.printBuiltinTypes)
        TypeDatabase::instance()->formatBuiltinTypes(qInfo());

    for (const GeneratorPtr &g : std::as_const(generators)) {
        g->setOutputDirectory(commonOptions.outputDirectory);
        g->setLicenseComment(commonOptions.licenseComment);
        ReportHandler::startProgress("Ran "_ba + g->name() + '.');
        const bool ok = g->setup(apiOpt.value()) && g->generate();
        ReportHandler::endProgress();
         if (!ok) {
             errorPrint(u"Error running generator: "_s
                        + QLatin1StringView(g->name()) + u'.', argV);
             return EXIT_FAILURE;
         }
    }

    if (commonOptions.logUnmatched)
        TypeDatabase::instance()->logUnmatched();

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
