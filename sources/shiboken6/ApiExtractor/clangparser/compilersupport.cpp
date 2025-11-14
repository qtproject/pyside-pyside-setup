// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "compilersupport.h"
#include "header_paths.h"
#include "clangutils.h"

#include <reporthandler.h>

#include "qtcompat.h"

#include <QtCore/qdebug.h>
#include <QtCore/qdir.h>
#include <QtCore/qfile.h>
#include <QtCore/qfileinfo.h>
#include <QtCore/qlibraryinfo.h>
#include <QtCore/qoperatingsystemversion.h>
#include <QtCore/qprocess.h>
#include <QtCore/qstandardpaths.h>
#include <QtCore/qstringlist.h>

#include <clang-c/Index.h>

#include <algorithm>
#include <cstring>
#include <iterator>
#include <string_view>

using namespace Qt::StringLiterals;

namespace clang {

// The command line options set
enum OptionSetFlag : unsigned
{
    CompilerOption = 0x1,
    CompilerPathOption = 0x2,
    PlatformOption = 0x4,
    PlatformVersionOption = 0x8,
    ArchitectureOption = 0x10
};

Q_DECLARE_FLAGS(OptionsSet, OptionSetFlag)
Q_DECLARE_OPERATORS_FOR_FLAGS(OptionsSet)

static OptionsSet setOptions;

QVersionNumber libClangVersion()
{
    return QVersionNumber(CINDEX_VERSION_MAJOR, CINDEX_VERSION_MINOR);
}

static Compiler hostCompiler()
{
#if defined (Q_CC_CLANG)
    return Compiler::Clang;
#elif defined (Q_CC_MSVC)
    return Compiler::Msvc;
#else
    return Compiler::Gpp;
#endif
}

static Compiler _compiler = hostCompiler();

Compiler compiler() { return _compiler; }

// CMAKE_CXX_COMPILER_ID or triplet name
bool parseCompiler(QStringView name, Compiler *c)
{
    bool result = true;
    *c = hostCompiler();
    if (name.compare("msvc"_L1, Qt::CaseInsensitive) == 0)
        *c = Compiler::Msvc;
    else if (name.compare("g++"_L1, Qt::CaseInsensitive) == 0 || name.compare("gnu"_L1, Qt::CaseInsensitive) == 0)
        *c = Compiler::Gpp;
    else if (name.compare("clang"_L1, Qt::CaseInsensitive) == 0)
        *c = Compiler::Clang;
    else
        result = false;
    return result;
}

bool setCompiler(const QString &name)
{
    setOptions.setFlag(CompilerOption);
    return parseCompiler(name, &_compiler);
}

QString _compilerPath; // Pre-defined compiler path (from command line)
QStringList _compilerArguments; // Arguments

static unsigned _pointerSize = QT_POINTER_SIZE * 8;
static QString _targetTriple;

const QString &compilerPath()
{
    return _compilerPath;
}

void setCompilerPath(const QString &name)
{
    setOptions.setFlag(CompilerPathOption);
    _compilerPath = name;
}

void addCompilerArgument(const QString &arg)
{
    _compilerArguments.append(arg);
}

static Platform hostPlatform()
{
#if defined (Q_OS_DARWIN)
    return Platform::macOS;
#elif defined (Q_OS_WIN)
    return Platform::Windows;
#elif defined (Q_OS_LINUX)
    return Platform::Linux;
#else
    return Platform::Unix;
#endif
}

static Platform _platform = hostPlatform();

Platform platform() { return _platform; }

// from CMAKE_SYSTEM_NAME / legacy lower case name or target triplet
static bool parsePlatform(QStringView name, Platform *p)
{
    *p = hostPlatform();
    bool result = true;
    if (name.compare("unix"_L1, Qt::CaseInsensitive) == 0) {
        *p = Platform::Unix;
    } else if (name.compare("linux"_L1, Qt::CaseInsensitive) == 0) {
        *p = Platform::Linux;
    } else if (name.compare("windows"_L1, Qt::CaseInsensitive) == 0) {
        *p = Platform::Windows;
    } else if (name.compare("darwin"_L1, Qt::CaseInsensitive) == 0
               || name.compare("macosx"_L1, Qt::CaseInsensitive) == 0) {
        *p = Platform::macOS;
    } else if (name.startsWith("android"_L1, Qt::CaseInsensitive)) {
        *p = Platform::Android; // "androideabi"
    } else if (name.compare("ios"_L1, Qt::CaseInsensitive) == 0) {
        *p = Platform::iOS;
    } else {
        result = false;
    }
    return result;
}

bool setPlatform(const QString &name)
{
    setOptions.setFlag(PlatformOption);
    return parsePlatform(name, &_platform);
}

static QVersionNumber hostPlatformVersion()
{
    auto ov = QOperatingSystemVersion::current();
    return ov.type() != QOperatingSystemVersionBase::Unknown ? ov.version() : QVersionNumber{};
}

// Version is not initialized from host since it is optional and the host version
// should not interfere with cross build targets
static QVersionNumber _platformVersion;

QVersionNumber platformVersion()
{
    return _platformVersion;
}

bool setPlatformVersion(const QString &name)
{
    auto v = QVersionNumber::fromString(name);
    setOptions.setFlag(PlatformVersionOption);
    const bool result = !v.isNull();
    if (result)
        _platformVersion = v;
    return result;
}

static Architecture hostArchitecture()
{
    // src/corelib/global/archdetect.cpp, "Qt 6.9.2 (x86_64-little_endian-lp64..."
    std::string_view build = QLibraryInfo::build();
    auto startPos = build.find('(');
    auto dashPos = build.find('-');
    if (startPos != std::string_view::npos && dashPos != std::string_view::npos) {
        ++startPos;
        build = build.substr(startPos, dashPos - startPos);
        if (build == "x86_64")
            return Architecture::X64;
        if (build == "i386")
            return Architecture::X86;
        if (build == "arm64")
            return Architecture::Arm64;
        if (build == "arm")
            return Architecture::Arm32;
    }
    return Architecture::Other;
}

// from CMAKE_SYSTEM_PROCESSOR or target triplet
static Architecture parseArchitecture(QStringView a)
{
    if (a == "AMD64"_L1 || a == "IA64"_L1 // Windows
        || a == "x86_64"_L1)
        return Architecture::X64;
    if (a.compare("x86"_L1, Qt::CaseInsensitive) == 0
        || a.compare("i386"_L1, Qt::CaseInsensitive) == 0
        || a.compare("i486"_L1, Qt::CaseInsensitive) == 0
        || a.compare("i586"_L1, Qt::CaseInsensitive) == 0
        || a.compare("i686"_L1, Qt::CaseInsensitive) == 0) {
        return Architecture::X86;
    }
    if (a.startsWith("armv7"_L1, Qt::CaseInsensitive))
        return Architecture::Arm32;
    if (a.startsWith("arm"_L1, Qt::CaseInsensitive)
        || a.startsWith("aarch64"_L1, Qt::CaseInsensitive)) {
        return Architecture::Arm64;
    }
    return Architecture::Other;
}

static Architecture _architecture = hostArchitecture();

Architecture architecture()
{
    return _architecture;
}

bool setArchitecture(const QString &name)
{
    setOptions.setFlag(ArchitectureOption);
    auto newArchitecture = parseArchitecture(name);
    const bool result = newArchitecture != Architecture::Other;
    if (result)
        _architecture = newArchitecture;
    return result;
}

// Parsing triplets
static inline bool isVersionChar(QChar c)
{
    return c.isDigit() || c == u'.';
}

// "macosx15.0" -> "macosx"
QStringView stripTrailingVersion(QStringView s)
{
    while (!s.isEmpty() && isVersionChar(s.at(s.size() - 1)))
        s.chop(1);
    return s;
}

bool parseTriplet(QStringView name, Architecture *a, Platform *p, Compiler *c,
                  QVersionNumber *version)
{
    *a = hostArchitecture();
    *p = hostPlatform();
    *c = hostCompiler();
    *version = hostPlatformVersion();
    auto values = name.split(u'-');
    if (values.size() < 2)
        return false;
    *a = parseArchitecture(values.constFirst());
    if (*a == Architecture::Other)
        return false;
    // Try a trailing compiler?
    Compiler comp{};
    if (parseCompiler(stripTrailingVersion(values.constLast()), &comp)) {
        *c = comp;
        values.removeLast();
    }
    const QStringView &fullPlatform = values.constLast();
    QStringView platformName = stripTrailingVersion(fullPlatform);
    if (platformName.size() < fullPlatform.size()) {
        if (auto vn = QVersionNumber::fromString(fullPlatform.sliced(platformName.size())); !vn.isNull())
            *version = vn;
    }
    return parsePlatform(platformName, p);
}

const char *compilerTripletValue(Compiler c)
{
    switch (c) {
    case Compiler::Clang:
        return "clang";
    case Compiler::Msvc:
        return "msvc";
    case Compiler::Gpp:
        break;
    }
    return "gnu";
}

QByteArray targetTripletForPlatform(Platform p, Architecture a, Compiler c,
                                    const QVersionNumber &platformVersion)
{
    QByteArray result;
    if (p == Platform::Unix || a == Architecture::Other)
        return result; // too unspecific

    switch (a) {
    case Architecture::Other:
        break;
    case Architecture::X64:
        result += "x86_64";
        break;
    case Architecture::X86:
        result += "i586";
        break;
    case Architecture::Arm32:
        result += "armv7a";
        break;
    case Architecture::Arm64:
        result += p == Platform::Android ? "aarch64" : "arm64";
        break;
    }

    result += '-';

    const QByteArray platformVersionB = platformVersion.isNull()
        ? QByteArray{} : platformVersion.toString().toUtf8();
    switch (p) {
    case Platform::Unix:
        break;
    case Platform::Linux:
        result += "unknown-linux"_ba + platformVersionB + '-' + compilerTripletValue(c);
        break;
    case Platform::Windows:
        result += "pc-windows"_ba + platformVersionB + '-' + compilerTripletValue(c);
        break;
    case Platform::macOS:
        result += "apple-macosx"_ba + platformVersionB;
        break;
    case Platform::Android:
        result += "unknown-linux-android"_ba + platformVersionB;
        break;
    case Platform::iOS:
        result += "apple-ios"_ba + platformVersionB;
        break;
    }
    return result;
}

// 3/2024: Use a recent MSVC2022 for libclang 18.X
static QByteArray msvcCompatVersion()
{
    return libClangVersion() >= QVersionNumber(0, 64) ? "19.39"_ba : "19.26"_ba;
}

static bool runProcess(const QString &program, const QStringList &arguments,
                       QByteArray *stdOutIn = nullptr, QByteArray *stdErrIn = nullptr)
{
    QProcess process;
    process.start(program, arguments, QProcess::ReadWrite);
    if (!process.waitForStarted()) {
        qCWarning(lcShiboken).noquote().nospace() << "Unable to start "
            << process.program() << ": " << process.errorString();
        return false;
    }
    process.closeWriteChannel();
    const bool finished = process.waitForFinished();
    const QByteArray stdErr = process.readAllStandardError();
    if (stdErrIn)
        *stdErrIn = stdErr;
    if (stdOutIn)
        *stdOutIn = process.readAllStandardOutput();

    if (!finished) {
        qCWarning(lcShiboken).noquote().nospace() << process.program() << " timed out: " << stdErr;
        process.kill();
        return false;
    }

    if (process.exitStatus() != QProcess::NormalExit) {
        qCWarning(lcShiboken).noquote().nospace() << process.program() << " crashed: " << stdErr;
        return false;
    }

    if (process.exitCode() != 0) {
        qCWarning(lcShiboken).noquote().nospace() <<  process.program() << " exited "
            << process.exitCode() << ": " << stdErr;
        return false;
    }

    return true;
}

static QByteArray frameworkPath() { return QByteArrayLiteral(" (framework directory)"); }

static void filterHomebrewHeaderPaths(HeaderPaths &headerPaths)
{
    QByteArray homebrewPrefix = qgetenv("HOMEBREW_OPT");

    // If HOMEBREW_OPT is found we assume that the build is happening
    // inside a brew environment, which means we need to filter out
    // the -isystem flags added by the brew clang shim. This is needed
    // because brew passes the Qt include paths as system include paths
    // and because our parser ignores system headers, Qt classes won't
    // be found and thus compilation errors will occur.
    if (homebrewPrefix.isEmpty())
        return;

    ReportHandler::addGeneralMessage("Found HOMEBREW_OPT with value:"_L1
                                     + QString::fromUtf8(homebrewPrefix)
                                     + "\nAssuming homebrew build environment."_L1);

    HeaderPaths::iterator it = headerPaths.begin();
    while (it != headerPaths.end()) {
        if (it->path.startsWith(homebrewPrefix)) {
            ReportHandler::addGeneralMessage("Filtering out homebrew include path: "_L1
                                             + QString::fromUtf8(it->path));
            it = headerPaths.erase(it);
        } else {
            ++it;
        }
    }
}

// Determine g++'s internal include paths from the output of
// g++ -E -x c++ - -v </dev/null
// Output looks like:
// #include <...> search starts here:
// /usr/local/include
// /System/Library/Frameworks (framework directory)
// End of search list.
static HeaderPaths gppInternalIncludePaths(const QString &compiler,
                                           const QStringList &args)
{
    HeaderPaths result;
    QStringList arguments{u"-E"_s, u"-x"_s, u"c++"_s, u"-"_s, u"-v"_s};
    arguments.append(args);
    QByteArray stdOut;
    QByteArray stdErr;
    if (!runProcess(compiler, arguments, &stdOut, &stdErr))
        return result;
    const QByteArrayList stdErrLines = stdErr.split('\n');
    bool isIncludeDir = false;

    for (const QByteArray &line : stdErrLines) {
        if (isIncludeDir) {
            if (line.startsWith(QByteArrayLiteral("End of search list"))) {
                isIncludeDir = false;
            } else {
                HeaderPath headerPath{line.trimmed(), HeaderType::System};
                if (headerPath.path.endsWith(frameworkPath())) {
                    headerPath.type = HeaderType::FrameworkSystem;
                    headerPath.path.truncate(headerPath.path.size() - frameworkPath().size());
                }
                result.append(headerPath);
            }
        } else if (line.startsWith("#include <...> search starts here"_ba)) {
            isIncludeDir = true;
        }
    }

    if (platform() == Platform::macOS)
        filterHomebrewHeaderPaths(result);

    QString message;
    {
        QTextStream str(&message);
        str << "gppInternalIncludePaths:\n    compiler: " << compiler
            << arguments.join(u' ') << '\n';
        for (const auto &h : result)
            str << "    " << h.path << '\n';
        if (ReportHandler::isDebug(ReportHandler::MediumDebug))
            str << "    stdOut: " << stdOut << "\n    stdErr: " << stdErr;
    }
    ReportHandler::addGeneralMessage(message);

    return result;
}

// Detect Vulkan as supported from Qt 5.10 by checking the environment variables.
QByteArrayList detectVulkan()
{
    static const char *vulkanVariables[] = {"VULKAN_SDK", "VK_SDK_PATH"};
    for (const char *vulkanVariable : vulkanVariables) {
        if (qEnvironmentVariableIsSet(vulkanVariable)) {
            const auto option = "-isystem"_ba + qgetenv(vulkanVariable) + "/include"_ba;
            return {option};
        }
    }
    return {};
}

// For MSVC, we set the MS compatibility version and let Clang figure out its own
// options and include paths.

// The clang builtin includes directory is used to find the definitions for
// intrinsic functions and builtin types. It is necessary to use the clang
// includes to prevent rqedefinition errors. The default toolchain includes
// should be picked up automatically by clang without specifying
// them implicitly.

// Besides g++/Linux, as of MSVC 19.28.29334, MSVC needs clang includes
// due to PYSIDE-1433, LLVM-47099

static bool needsClangBuiltinIncludes()
{
    return platform() != Platform::macOS;
}

static QString queryLlvmConfigDir(const QString &arg)
{
    static const QString llvmConfig = QStandardPaths::findExecutable(u"llvm-config"_s);
    if (llvmConfig.isEmpty())
        return {};
    QByteArray stdOut;
    if (!runProcess(llvmConfig, QStringList{arg}, &stdOut))
        return {};
    const QString path = QFile::decodeName(stdOut.trimmed());
    if (!QFileInfo::exists(path)) {
        qCWarning(lcShiboken, R"(%s: "%s" as returned by llvm-config "%s" does not exist.)",
                  __FUNCTION__, qPrintable(QDir::toNativeSeparators(path)), qPrintable(arg));
        return {};
    }
    return path;
}

static QString findClangLibDir()
{
    for (const char *envVar : {"LLVM_INSTALL_DIR", "CLANG_INSTALL_DIR"}) {
        if (qEnvironmentVariableIsSet(envVar)) {
            const QString path = QFile::decodeName(qgetenv(envVar)) + u"/lib"_s;
            if (QFileInfo::exists(path))
                return path;
            qCWarning(lcShiboken, "%s: %s as pointed to by %s does not exist.",
                      __FUNCTION__, qPrintable(path), envVar);
        }
    }
    return queryLlvmConfigDir(u"--libdir"_s);
}

static QString findClangBuiltInIncludesDir()
{
    // Find the include directory of the highest version.
    const QString clangPathLibDir = findClangLibDir();
    if (!clangPathLibDir.isEmpty()) {
        QString candidate;
        QString clangDirName = clangPathLibDir + u"/clang"_s;
        // PYSIDE-2769: llvm-config --libdir may report /usr/lib64 on manylinux_2_28_x86_64
        // whereas the includes are under /usr/lib/clang/../include.
        if (!QFileInfo::exists(clangDirName) && clangPathLibDir.endsWith("64"_L1)) {
            const QString fallback = clangPathLibDir.sliced(0, clangPathLibDir.size() - 2);
            clangDirName = fallback + u"/clang"_s;
            qCWarning(lcShiboken, "%s: Falling back from %s to %s.",
                      __FUNCTION__, qPrintable(clangPathLibDir), qPrintable(fallback));
        }

        QVersionNumber lastVersionNumber(1, 0, 0);
        QDir clangDir(clangDirName);
        const QFileInfoList versionDirs =
            clangDir.entryInfoList(QDir::Dirs | QDir::NoDotAndDotDot);
        if (versionDirs.isEmpty())
            qCWarning(lcShiboken, "%s: No subdirectories found in %s.",
                      __FUNCTION__, qPrintable(clangDirName));
        for (const QFileInfo &fi : versionDirs) {
            const QString fileName = fi.fileName();
            if (fileName.at(0).isDigit()) {
                const QVersionNumber versionNumber = QVersionNumber::fromString(fileName);
                if (!versionNumber.isNull() && versionNumber > lastVersionNumber) {
                    candidate = fi.absoluteFilePath();
                    lastVersionNumber = versionNumber;
                }
            }
        }
        if (!candidate.isEmpty())
            return candidate + "/include"_L1;
    }
    return queryLlvmConfigDir(u"--includedir"_s);
}

QString compilerFromCMake()
{
#ifdef CMAKE_CXX_COMPILER
    return QString::fromLocal8Bit(CMAKE_CXX_COMPILER);
#else
    return {};
#endif
}

// Return a compiler suitable for determining the internal include paths
static QString compilerFromCMake(const QString &defaultCompiler)
{
    if (!compilerPath().isEmpty())
        return compilerPath();
    // Exclude macOS since cmakeCompiler returns the full path instead of the
    // /usr/bin/clang shim, which results in the default SDK sysroot path
    // missing (PYSIDE-1032)
    if (platform() == Platform::macOS)
        return defaultCompiler;
    QString cmakeCompiler = compilerFromCMake();
    if (cmakeCompiler.isEmpty())
        return defaultCompiler;
    QFileInfo fi(cmakeCompiler);
    // Should be absolute by default, but a user may specify -DCMAKE_CXX_COMPILER=cl.exe
    if (fi.isRelative())
        return cmakeCompiler;
    if (fi.exists())
        return fi.absoluteFilePath();
    // The compiler may not exist in case something like icecream or
    // a non-standard-path was used on the build machine. Check
    // the executable.
    cmakeCompiler = QStandardPaths::findExecutable(fi.fileName());
    return cmakeCompiler.isEmpty() ? defaultCompiler : cmakeCompiler;
}

static void appendClangBuiltinIncludes(HeaderPaths *p)
{
    const QString clangBuiltinIncludesDir =
        QDir::toNativeSeparators(findClangBuiltInIncludesDir());
    if (clangBuiltinIncludesDir.isEmpty()) {
        qCWarning(lcShiboken, "Unable to locate Clang's built-in include directory "
                  "(neither by checking the environment variables LLVM_INSTALL_DIR, CLANG_INSTALL_DIR "
                  " nor running llvm-config). This may lead to parse errors.");
    } else {
        p->append(HeaderPath{QFile::encodeName(clangBuiltinIncludesDir),
                             HeaderType::System});
        ReportHandler::addGeneralMessage("CLANG builtins includes directory: "_L1
                                         + clangBuiltinIncludesDir);
    }
}

// Returns clang options needed for emulating the host compiler
QByteArrayList emulatedCompilerOptions(LanguageLevel level)
{
    QByteArrayList result;
    HeaderPaths headerPaths;
    switch (compiler()) {
    case Compiler::Msvc:
        result.append("-fms-compatibility-version="_ba + msvcCompatVersion());
        if (level < LanguageLevel::Cpp20)
            result.append("-fdelayed-template-parsing"_ba);
        result.append(QByteArrayLiteral("-Wno-microsoft-enum-value"));
        result.append("/Zc:__cplusplus"_ba);
        // Fix yvals_core.h:  STL1000: Unexpected compiler version, expected Clang 7 or newer (MSVC2017 update)
        result.append(QByteArrayLiteral("-D_ALLOW_COMPILER_AND_STL_VERSION_MISMATCH"));
        if (needsClangBuiltinIncludes())
            appendClangBuiltinIncludes(&headerPaths);
        break;
    case Compiler::Clang:
        headerPaths.append(gppInternalIncludePaths(compilerFromCMake(u"clang++"_s),
                                                   _compilerArguments));
        break;
    case Compiler::Gpp:
        if (needsClangBuiltinIncludes())
            appendClangBuiltinIncludes(&headerPaths);

        // Append the c++ include paths since Clang is unable to find
        // <type_traits> etc (g++ 11.3).
        const HeaderPaths gppPaths = gppInternalIncludePaths(compilerFromCMake(u"g++"_s),
                                                             _compilerArguments);
        for (const HeaderPath &h : gppPaths) {
            if (h.path.contains("c++") || h.path.contains("sysroot"))
                headerPaths.append(h);
        }
        break;
    }

    std::transform(headerPaths.cbegin(), headerPaths.cend(),
                   std::back_inserter(result), HeaderPath::includeOption);
    return result;
}

LanguageLevel emulatedCompilerLanguageLevel()
{
    return LanguageLevel::Cpp17;
}

struct LanguageLevelMapping
{
    const char *option;
    LanguageLevel level;
};

static const LanguageLevelMapping languageLevelMapping[] =
{
    {"c++11", LanguageLevel::Cpp11},
    {"c++14", LanguageLevel::Cpp14},
    {"c++17", LanguageLevel::Cpp17},
    {"c++20", LanguageLevel::Cpp20},
    {"c++1z", LanguageLevel::Cpp1Z}
};

const char *languageLevelOption(LanguageLevel l)
{
    for (const LanguageLevelMapping &m : languageLevelMapping) {
        if (m.level == l)
            return m.option;
    }
    return nullptr;
}

LanguageLevel languageLevelFromOption(const char *o)
{
    for (const LanguageLevelMapping &m : languageLevelMapping) {
        if (!std::strcmp(m.option, o))
            return m.level;
    }
    return LanguageLevel::Default;
}

unsigned pointerSize()
{
    return _pointerSize;
}

void setPointerSize(unsigned ps)
{
    _pointerSize = ps;
}

QString targetTriple()
{
    return _targetTriple;

}
void setTargetTriple(const QString &t)
{
    _targetTriple = t;
}

bool isCrossCompilation()
{
    return platform() != hostPlatform() || architecture() != hostArchitecture()
           || compiler() != hostCompiler();
}

static const char targetOptionC[] = "--target=";

static inline bool isTargetOption(const QByteArray &o)
{
    return o.startsWith(targetOptionC);
}

static bool isTargetArchOption(const QByteArray &o)
{
    return isTargetOption(o)
           || o.startsWith("-march=") || o.startsWith("-meabi");
}

bool hasTargetOption(const QByteArrayList &clangOptions)
{
    return std::any_of(clangOptions.cbegin(), clangOptions.cend(),
                       isTargetArchOption);
}

void setHeuristicOptions(const QByteArrayList &clangOptions)
{
    // Figure out compiler type from the binary set
    if (!setOptions.testFlag(CompilerOption) && setOptions.testFlag(CompilerPathOption)) {
        const QString name = QFileInfo(_compilerPath).baseName().toLower();
        if (name.contains("clang"_L1))
            _compiler = Compiler::Clang;
        else if (name.contains("cl"_L1))
            _compiler = Compiler::Msvc;
        else if (name.contains("gcc"_L1) || name.contains("g++"_L1))
            _compiler = Compiler::Gpp;
    }

    // Figure out platform/arch from "--target" triplet
    if (!setOptions.testFlag(PlatformOption) && !setOptions.testFlag(ArchitectureOption)) {
        auto it = std::find_if(clangOptions.cbegin(), clangOptions.cend(), isTargetOption);
        if (it != clangOptions.cend()) {
            const QString triplet = QLatin1StringView(it->sliced(qstrlen(targetOptionC)));
            Architecture arch{};
            Platform platform{};
            Compiler comp{};
            QVersionNumber platformVersion;
            if (parseTriplet(triplet, &arch, &platform, &comp, &platformVersion)) {
                if (!setOptions.testFlag(ArchitectureOption))
                    _architecture = arch;
                if (!setOptions.testFlag(PlatformOption))
                    _platform = platform;
                if (!setOptions.testFlag(PlatformVersionOption))
                    _platformVersion = platformVersion;
            } else {
                qCWarning(lcShiboken, "Unable to parse triplet \"%s\".", qPrintable(triplet));
            }
        }
    }
}

} // namespace clang
