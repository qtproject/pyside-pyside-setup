// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TRIPLET_H
#define TRIPLET_H

#include <cstdint>

#include <QtCore/qstring.h>
#include <QtCore/qstringview.h>
#include <QtCore/qversionnumber.h>

#include <optional>

QT_FORWARD_DECLARE_CLASS(QDebug)

enum class Compiler : std::uint8_t {
    Unknown,
    Msvc,
    Gpp,
    Clang
};

enum class Platform : std::uint8_t {
    Unknown,
    Unix,
    Linux,
    Windows,
    macOS,
    Android,
    iOS
};

enum class Architecture : std::uint8_t {
    Unknown,
    X64,
    X86,
    Arm64,
    Arm32
};

class Triplet
{
public:
    Q_DECLARE_EQUALITY_COMPARABLE(Triplet)

    Triplet();

    bool isValid() const;

    Architecture architecture() const { return m_architecture; }
    QByteArray architectureTripletValue() const;
    void setArchitecture(Architecture newArchitecture);
    bool setArchitectureString(QStringView v);

    Platform platform() const { return m_platform; }
    QByteArray platformTripletValue() const;
    void setPlatform(Platform newPlatform);
    bool setPlatformString(QStringView v);

    Compiler compiler() const { return m_compiler; }
    QByteArray compilerTripletValue() const;
    void setCompiler(Compiler newCompiler);
    bool setCompilerString(QStringView v);

    bool hasPlatformVersion() const { return !m_platformVersion.isNull(); }
    QVersionNumber platformVersion() const { return m_platformVersion; }
    void setPlatformVersion(const QVersionNumber &newPlatformVersion);

    QByteArray toByteArray() const;
    QString toString() const { return QLatin1StringView(toByteArray()); }

    static Triplet fromHost(bool detectVersion);
    static std::optional<Triplet> fromString(QStringView name);

private:
    friend bool comparesEqual(const Triplet &lhs, const Triplet &rhs) noexcept
    {  return lhs.equals(rhs); }

    bool equals(const Triplet &rhs) const noexcept;

    Architecture m_architecture = Architecture::Unknown;
    Platform m_platform = Platform::Unknown;
    Compiler m_compiler = Compiler::Unknown;
    QVersionNumber m_platformVersion;
};

QDebug operator<<(QDebug d, const Triplet &t);

#endif // TRIPLET_H
