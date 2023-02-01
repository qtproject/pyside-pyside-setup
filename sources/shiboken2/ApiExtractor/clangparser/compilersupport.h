/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef COMPILERSUPPORT_H
#define COMPILERSUPPORT_H

#include <QtCore/QByteArrayList>

QT_FORWARD_DECLARE_CLASS(QVersionNumber)

enum class LanguageLevel {
    Default,
    Cpp11,
    Cpp14,
    Cpp17,
    Cpp20,
    Cpp1Z
};

namespace clang {
QVersionNumber libClangVersion();

QByteArrayList emulatedCompilerOptions();
LanguageLevel emulatedCompilerLanguageLevel();

const char *languageLevelOption(LanguageLevel l);
LanguageLevel languageLevelFromOption(const char *);
} // namespace clang

#endif // COMPILERSUPPORT_H
