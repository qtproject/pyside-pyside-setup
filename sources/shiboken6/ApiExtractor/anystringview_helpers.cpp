// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "anystringview_helpers.h"

#include <QtCore/QAnyStringView>
#include <QtCore/QDebug>
#include <QtCore/QTextStream>

QTextStream &operator<<(QTextStream &str, QAnyStringView asv)
{
    asv.visit([&str](auto s) { str << s; });
    return str;
}

QDebug operator<<(QDebug debug, QAnyStringView asv)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    asv.visit([&debug](auto s) { debug << s; });
    return debug;
}
