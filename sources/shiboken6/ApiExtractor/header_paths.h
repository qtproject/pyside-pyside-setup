// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef HEADER_PATHS_H
#define HEADER_PATHS_H

#include <QtCore/QByteArray>
#include <QtCore/QList>

enum class HeaderType
{
    Standard,
    System,         // -isystem
    Framework,      // macOS framework path
    FrameworkSystem // macOS framework system path
};

class HeaderPath {
public:
    QByteArray path;
    HeaderType type;

    static QByteArray includeOption(const HeaderPath &p)
    {
        QByteArray option;
        switch (p.type) {
        case HeaderType::Standard:
            option = QByteArrayLiteral("-I");
            break;
        case HeaderType::System:
            option = QByteArrayLiteral("-isystem");
            break;
        case HeaderType::Framework:
            option = QByteArrayLiteral("-F");
            break;
        case HeaderType::FrameworkSystem:
            option = QByteArrayLiteral("-iframework");
            break;
        }
        return option + p.path;
    }
};

using HeaderPaths = QList<HeaderPath>;

#endif // HEADER_PATHS_H
