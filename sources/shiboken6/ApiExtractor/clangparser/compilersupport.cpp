// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "compilersupport.h"
#include "header_paths.h"
#include "clangutils.h"

#include <reporthandler.h>

#include "qtcompat.h"

#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QFileInfo>
#include <QtCore/QProcess>
#include <QtCore/QStandardPaths>
#include <QtCore/QStringList>
#include <QtCore/QVersionNumber>

#include <clang-c/Index.h>

#include <algorithm>
#include <iterator>

using namespace Qt::StringLiterals;

namespace clang {

QVersionNumber libClangVersion()
{
    return QVersionNumber(CINDEX_VERSION_MAJOR, CINDEX_VERSION_MINOR);
}

static Compiler _compiler =
#if defined (Q_CC_CLANG)
    Compiler::Clang;
#elif defined (Q_CC_MSVC)
    Compiler::Msvc;
#else
    Compiler::Gpp;
#endif

Compiler compiler() { return _compiler; }

bool setCompiler(const QString &name)
{
    bool result = true;
    if (name == u"msvc")
        _compiler = Compiler::Msvc;
    else if (name == u"g++")
        _compiler = Compiler::Gpp;
    else if (name == u"clang")
        _compiler = Compiler::Clang;
    else
        result = false;
    return result;
}

QString _compilerPath; // Pre-defined compiler path (from command line)

const QString &compilerPath()
{
    return _compilerPath;
}

void setCompilerPath(const QString &name)
{
    _compilerPath = name;
}

static Platform _platform =
#if defined (Q_OS_DARWIN)
    Platform::macOS;
#elif defined (Q_OS_WIN)
    Platform::Windows;
#else
    Platform::Unix;
#endif

Platform platform() { return _platform; }

bool setPlatform(const QString &name)
{
    bool result = true;
    if (name == u"windows")
        _platform = Platform::Windows;
    else if (name == u"darwin")
        _platform = Platform::macOS;
    else if (name == u"unix")
        _platform = Platform::Unix;
    else
        result = false;
    return result;
}

static bool runProcess(const QString &program, const QStringList &arguments,
                       QByteArray *stdOutIn = nullptr, QByteArray *stdErrIn = nullptr)
{
    QProcess process;
    process.start(program, arguments, QProcess::ReadWrite);
    if (!process.waitForStarted()) {
        qWarning().noquote().nospace() << "Unable to start "
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
        qWarning().noquote().nospace() << process.program() << " timed out: " << stdErr;
        process.kill();
        return false;
    }

    if (process.exitStatus() != QProcess::NormalExit) {
        qWarning().noquote().nospace() << process.program() << " crashed: " << stdErr;
        return false;
    }

    if (process.exitCode() != 0) {
        qWarning().noquote().nospace() <<  process.program() << " exited "
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

    qCInfo(lcShiboken) << "Found HOMEBREW_OPT with value:" << homebrewPrefix
                       << "Assuming homebrew build environment.";

    HeaderPaths::iterator it = headerPaths.begin();
    while (it != headerPaths.end()) {
        if (it->path.startsWith(homebrewPrefix)) {
            qCInfo(lcShiboken) << "Filtering out homebrew include path: "
                               << it->path;
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
static HeaderPaths gppInternalIncludePaths(const QString &compiler)
{
    HeaderPaths result;
    QStringList arguments{u"-E"_s, u"-x"_s, u"c++"_s, u"-"_s, u"-v"_s};
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
        } else if (line.startsWith(QByteArrayLiteral("#include <...> search starts here"))) {
            isIncludeDir = true;
        }
    }

    if (platform() == Platform::macOS)
        filterHomebrewHeaderPaths(result);

    return result;
}

// Detect Vulkan as supported from Qt 5.10 by checking the environment variables.
QByteArrayList detectVulkan()
{
    static const char *vulkanVariables[] = {"VULKAN_SDK", "VK_SDK_PATH"};
    for (const char *vulkanVariable : vulkanVariables) {
        if (qEnvironmentVariableIsSet(vulkanVariable)) {
            const auto option = QByteArrayLiteral("-isystem")
                                + qgetenv(vulkanVariable)
                                + QByteArrayLiteral("/include");
            return {option};
        }
    }
    return {};
}

// For MSVC, we set the MS compatibility version and let Clang figure out its own
// options and include paths.
// For the others, we pass "-nostdinc" since libclang tries to add it's own system
// include paths, which together with the clang compiler paths causes some clash
// which causes std types not being found and construct -I/-F options from the
// include paths of the host compiler.

static QByteArray noStandardIncludeOption() { return QByteArrayLiteral("-nostdinc"); }

// The clang builtin includes directory is used to find the definitions for
// intrinsic functions and builtin types. It is necessary to use the clang
// includes to prevent redefinition errors. The default toolchain includes
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
        qWarning(R"(%s: "%s" as returned by llvm-config "%s" does not exist.)",
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
            qWarning("%s: %s as pointed to by %s does not exist.", __FUNCTION__, qPrintable(path), envVar);
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
        QVersionNumber lastVersionNumber(1, 0, 0);
        const QString clangDirName = clangPathLibDir + u"/clang"_s;
        QDir clangDir(clangDirName);
        const QFileInfoList versionDirs =
            clangDir.entryInfoList(QDir::Dirs | QDir::NoDotAndDotDot);
        if (versionDirs.isEmpty())
            qWarning("%s: No subdirectories found in %s.", __FUNCTION__, qPrintable(clangDirName));
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
            return candidate + QStringLiteral("/include");
    }
    return queryLlvmConfigDir(u"--includedir"_s);
}

static QString compilerFromCMake(const QString &defaultCompiler)
{
    if (!compilerPath().isEmpty())
        return compilerPath();
// Added !defined(Q_OS_DARWIN) due to PYSIDE-1032
    QString result = defaultCompiler;
#ifdef CMAKE_CXX_COMPILER
    if (platform() != Platform::macOS)
        result = QString::fromLocal8Bit(CMAKE_CXX_COMPILER);
#endif
    return result;
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
        qCInfo(lcShiboken, "CLANG v%d.%d, builtins includes directory: %s",
               CINDEX_VERSION_MAJOR, CINDEX_VERSION_MINOR,
               qPrintable(clangBuiltinIncludesDir));
        p->append(HeaderPath{QFile::encodeName(clangBuiltinIncludesDir),
                             HeaderType::System});
    }
}

// Returns clang options needed for emulating the host compiler
QByteArrayList emulatedCompilerOptions()
{
    QByteArrayList result;
    HeaderPaths headerPaths;
    switch (compiler()) {
    case Compiler::Msvc:
        result.append(QByteArrayLiteral("-fms-compatibility-version=19.26.28806"));
        result.append(QByteArrayLiteral("-fdelayed-template-parsing"));
        result.append(QByteArrayLiteral("-Wno-microsoft-enum-value"));
        // Fix yvals_core.h:  STL1000: Unexpected compiler version, expected Clang 7 or newer (MSVC2017 update)
        result.append(QByteArrayLiteral("-D_ALLOW_COMPILER_AND_STL_VERSION_MISMATCH"));
        if (needsClangBuiltinIncludes())
            appendClangBuiltinIncludes(&headerPaths);
        break;
    case Compiler::Clang:
        headerPaths.append(gppInternalIncludePaths(compilerFromCMake(u"clang++"_s)));
        result.append(noStandardIncludeOption());
        break;
    case Compiler::Gpp:
        if (needsClangBuiltinIncludes())
            appendClangBuiltinIncludes(&headerPaths);

        // Append the c++ include paths since Clang is unable to find
        // <type_traits> etc (g++ 11.3).
        const HeaderPaths gppPaths = gppInternalIncludePaths(compilerFromCMake(u"g++"_s));
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
        if (!strcmp(m.option, o))
            return m.level;
    }
    return LanguageLevel::Default;
}

} // namespace clang
