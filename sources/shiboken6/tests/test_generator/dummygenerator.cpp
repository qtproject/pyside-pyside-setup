// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <iostream>
#include "dummygenerator.h"

EXPORT_GENERATOR_PLUGIN(new DummyGenerator)

using namespace std;

QString
DummyGenerator::fileNameForClass(const AbstractMetaClass* metaClass) const
{
    return metaClass->name().toLower() + u"_generated.txt"_qs;
}

void
DummyGenerator::generateClass(QTextStream& s, const AbstractMetaClass* metaClass)
{
    s << "// Generated code for class: " << qPrintable(metaClass->name()) << endl;
}

bool
DummyGenerator::doSetup(const QMap<QString, QString>& args)
{
    if (args.contains("dump-arguments") && !args["dump-arguments"].isEmpty()) {
        QFile logFile(args["dump-arguments"]);
        logFile.open(QIODevice::WriteOnly | QIODevice::Text);
        QTextStream out(&logFile);
        for (QMap<QString, QString>::const_iterator it = args.cbegin(), end = args.cend(); it != end; ++it) {
            const QString& key = it.key();
            if (key == "arg-1")
                out << "header-file";
            else if (key == "arg-2")
                out << "typesystem-file";
            else
                out << key;
            if (!args[key].isEmpty())
                out << " = " << args[key];
            out << endl;
        }
    }
    return true;
}

