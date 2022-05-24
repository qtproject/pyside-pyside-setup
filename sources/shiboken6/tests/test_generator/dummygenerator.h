// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
#ifndef DUMMYGENERATOR_H
#define DUMMYGENERATOR_H

#include "generator.h"

class GENRUNNER_API DummyGenerator : public Generator
{
public:
    DummyGenerator() {}
    ~DummyGenerator() {}
    bool doSetup(const QMap<QString, QString>& args);
    const char* name() const { return "DummyGenerator"; }

protected:
    void writeFunctionArguments(QTextStream&, const AbstractMetaFunction*, Options) const {}
    void writeArgumentNames(QTextStream&, const AbstractMetaFunction*, Options) const {}
    QString fileNameForClass(const AbstractMetaClass* metaClass) const;
    void generateClass(QTextStream& s, const AbstractMetaClass* metaClass);
    void finishGeneration() {}
};

#endif // DUMMYGENERATOR_H
