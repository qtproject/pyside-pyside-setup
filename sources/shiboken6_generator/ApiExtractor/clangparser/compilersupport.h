// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef COMPILERSUPPORT_H
#define COMPILERSUPPORT_H

#include "triplet.h"

#include <QtCore/qbytearraylist.h>
#include <QtCore/qversionnumber.h>

QT_FORWARD_DECLARE_CLASS(QString)

enum class LanguageLevel : std::uint8_t {
    Default,
    Cpp11,
    Cpp14,
    Cpp17,
    Cpp20,
    Cpp1Z
};

namespace clang {
QVersionNumber libClangVersion();

QByteArrayList emulatedCompilerOptions(LanguageLevel level);
LanguageLevel emulatedCompilerLanguageLevel();

const char *languageLevelOption(LanguageLevel l);
LanguageLevel languageLevelFromOption(const char *);

QByteArrayList detectVulkan();

// The triplet set by options and heuristics and setters
const Triplet &optionsTriplet();

bool setArchitecture(QStringView name);
bool setCompiler(QStringView name);
bool setPlatform(QStringView name);
bool setPlatformVersion(QAnyStringView name);

bool isCrossCompilation();

const QString &compilerPath();
void setCompilerPath(const QString &name);
void addCompilerArgument(const QString &arg);

QString compilerFromCMake();

// Are there any options specifying a target
bool hasTargetOption(const QByteArrayList &clangOptions);

// Unless the platform/architecture/compiler options were set, try to find
// values based on a --target option in clangOptions and the compiler path.
void setHeuristicOptions(const QByteArrayList &clangOptions);

// Parse a triplet "x86_64-unknown-linux-gnu" (for testing). Note the
// compiler might not be present and defaults to host
bool parseTriplet(QStringView name, Architecture *a, Platform *p, Compiler *c,
                  QVersionNumber *version);

} // namespace clang

#endif // COMPILERSUPPORT_H
