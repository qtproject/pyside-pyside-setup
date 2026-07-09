// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef TYPESYSTEMPARSER_CHECKS_H
#define TYPESYSTEMPARSER_CHECKS_H

#include <QtCore/qstringview.h>

bool isValidIdentifier(QStringView input);
bool isValidPackageName(QStringView input);
bool isValidClassName(QStringView input);

#endif // TYPESYSTEMPARSER_CHECKS_H
