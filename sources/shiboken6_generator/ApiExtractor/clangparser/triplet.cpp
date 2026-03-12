// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "triplet.h"

#include <QtCore/qdebug.h>
#include <QtCore/qlibraryinfo.h>
#include <QtCore/qoperatingsystemversion.h>

using namespace Qt::StringLiterals;

// from CMAKE_SYSTEM_PROCESSOR or target triplet
static Architecture parseArchitecture(QStringView a)
{
    if (a == "AMD64"_L1 || a == "IA64"_L1 // Windows
        || a == "x86_64"_L1) {
        return Architecture::X64;
    }
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
    return Architecture::Unknown;
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
    return Architecture::Unknown;
}

// from CMAKE_SYSTEM_NAME / legacy lower case name or target triplet
static Platform parsePlatform(QStringView name)
{
    if (name.compare("unix"_L1, Qt::CaseInsensitive) == 0)
        return Platform::Unix;
    if (name.compare("linux"_L1, Qt::CaseInsensitive) == 0)
        return Platform::Linux;
    if (name.compare("windows"_L1, Qt::CaseInsensitive) == 0)
        return Platform::Windows;
    if (name.compare("darwin"_L1, Qt::CaseInsensitive) == 0
        || name.compare("macosx"_L1, Qt::CaseInsensitive) == 0) {
        return Platform::macOS;
    }
    if (name.startsWith("android"_L1, Qt::CaseInsensitive))
        return Platform::Android; // "androideabi"
    if (name.compare("ios"_L1, Qt::CaseInsensitive) == 0)
        return Platform::iOS;
    return Platform::Unknown;
}

// CMAKE_CXX_COMPILER_ID or triplet name
static Compiler parseCompiler(QStringView name)
{
    if (name.compare("msvc"_L1, Qt::CaseInsensitive) == 0)
        return Compiler::Msvc;
    if (name.compare("g++"_L1, Qt::CaseInsensitive) == 0 || name.compare("gnu"_L1, Qt::CaseInsensitive) == 0)
        return Compiler::Gpp;
    if (name.compare("clang"_L1, Qt::CaseInsensitive) == 0)
        return Compiler::Clang;
    return Compiler::Unknown;
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

static Platform hostPlatform()
{
#if defined (Q_OS_APPLE)
    return Platform::macOS;
#elif defined (Q_OS_WIN)
    return Platform::Windows;
#elif defined (Q_OS_LINUX)
    return Platform::Linux;
#else
    return Platform::Unix;
#endif
}

static QVersionNumber hostPlatformVersion()
{
    auto ov = QOperatingSystemVersion::current();
    return ov.type() != QOperatingSystemVersionBase::Unknown ? ov.version() : QVersionNumber{};
}

Triplet::Triplet() = default;

bool Triplet::isValid() const
{
    return m_architecture != Architecture::Unknown
           && m_platform != Platform::Unknown;
}

QByteArray Triplet::architectureTripletValue() const
{
    switch (m_architecture) {
    case Architecture::X64:
        return "x86_64"_ba;
    case Architecture::X86:
        return "i586"_ba;
    case Architecture::Arm32:
        return "armv7a"_ba;
    case Architecture::Arm64:
        return m_platform == Platform::Android ? "aarch64"_ba : "arm64"_ba;
    case Architecture::Unknown:
        break;
    }
    return {};
}

void Triplet::setArchitecture(Architecture newArchitecture)
{
    m_architecture = newArchitecture;
}

bool Triplet::setArchitectureString(QStringView v)
{
    const auto arch = parseArchitecture(v);
    const bool ok = arch != Architecture::Unknown;
    if (ok)
        m_architecture = arch;
    return ok;
}

QByteArray Triplet::platformTripletValue() const
{
    switch (m_platform) {
    case Platform::Unix:
        return "unknown-unix"_ba;
    case Platform::Linux:
        return "unknown-linux"_ba;
    case Platform::Windows:
        return "pc-windows"_ba;
    case Platform::macOS:
        return "apple-macosx"_ba;
    case Platform::Android:
        return "unknown-linux-android"_ba;
        break;
    case Platform::iOS:
        return "apple-ios"_ba;
    case Platform::Unknown:
        break;
    }
    return {};
}

void Triplet::setPlatform(Platform newPlatform)
{
    m_platform = newPlatform;
}

QByteArray Triplet::compilerTripletValue() const
{
    switch (m_compiler) {
    case Compiler::Clang:
        return "clang"_ba;
    case Compiler::Msvc:
        return "msvc"_ba;
    case Compiler::Gpp:
        return "gnu"_ba;
        break;
    case Compiler::Unknown:
        break;
    }
    return {};
}

void Triplet::setCompiler(Compiler newCompiler)
{
    m_compiler = newCompiler;
}

bool Triplet::setCompilerString(QStringView v)
{
    const auto comp = parseCompiler(v);
    const bool ok = comp != Compiler::Unknown;
    if (ok)
        m_compiler = comp;
    return ok;
}

bool Triplet::setPlatformString(QStringView v)
{
    const auto p = parsePlatform(v);
    const bool ok = p != Platform::Unknown;
    if (ok)
        m_platform = p;
    return ok;
}

void Triplet::setPlatformVersion(const QVersionNumber &newPlatformVersion)
{
    m_platformVersion = newPlatformVersion;
}

bool Triplet::equals(const Triplet &rhs) const noexcept
{
    if (m_architecture != rhs.m_architecture
        || m_platform != rhs.m_platform
        || m_compiler != rhs.m_compiler) {
        return false;
    }
    const bool lhsHasVersion = hasPlatformVersion();
    const bool rhsHasVersion = rhs.hasPlatformVersion();;
    if (lhsHasVersion != rhsHasVersion)
        return false;
    return !lhsHasVersion || m_platformVersion == rhs.m_platformVersion;
}

QByteArray Triplet::toByteArray() const
{
    if (!isValid())
        return {};

    QByteArray result = architectureTripletValue() + '-' + platformTripletValue();

    if (m_platform != Platform::Unix && m_platform != Platform::Unknown
        && !m_platformVersion.isNull()) {
        result += m_platformVersion.toString().toUtf8();
    }

    switch (m_platform) {
    case Platform::Linux:
    case Platform::Windows:
        if (m_compiler != Compiler::Unknown)
            result += '-' + compilerTripletValue();
        break;
    default:
        break;
    }

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

std::optional<Triplet> Triplet::fromString(QStringView name)
{
    auto values = name.split(u'-');
    if (values.size() < 2)
        return std::nullopt;

    const auto arch = parseArchitecture(values.constFirst());
    if (arch == Architecture::Unknown)
        return std::nullopt;;
    // Try a trailing compiler?
    const Compiler comp = parseCompiler(stripTrailingVersion(values.constLast()));
    if (comp != Compiler::Unknown)
        values.removeLast();

    const QStringView &fullPlatform = values.constLast();
    QStringView platformName = stripTrailingVersion(fullPlatform);
    const Platform platform = parsePlatform(platformName);
    if (platform == Platform::Unknown)
        return std::nullopt;

    Triplet result;
    result.setArchitecture(arch);
    result.setPlatform(platform);
    if (comp != Compiler::Unknown)
        result.setCompiler(comp);

    QVersionNumber platformVersion;
    if (platformName.size() < fullPlatform.size()) {
        const QVersionNumber platformVersion = QVersionNumber::fromString(fullPlatform.sliced(platformName.size()));
        if (!platformVersion.isNull())
            result.setPlatformVersion(platformVersion);
    }

    return result;
}

Triplet Triplet::fromHost()
{
    Triplet result;
    result.setArchitecture(hostArchitecture());
    result.setPlatform(hostPlatform());
    result.setCompiler(hostCompiler());
    const auto hv = hostPlatformVersion();
    if (!hv.isNull())
        result.setPlatformVersion(hv);
    return result;
}

QDebug operator<<(QDebug debug, const Triplet &t)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Triplet(";
    if (t.isValid()) {
        debug << '"' << t.toByteArray() << '"';
    } else {
        debug << "invalid";
    }
    debug << ')';
    return debug;
}
