// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <QtCore>

int main(int argc, char *argv[])
{
    QStringList args;
    args.append("--generator-set=dummy");
    for (int i = 1; i < argc; i++)
        args.append(argv[i]);
    return QProcess::execute("generatorrunner", args);
}

