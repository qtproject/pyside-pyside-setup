// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef QTXMLTOSPHINXINTERFACE_H
#define QTXMLTOSPHINXINTERFACE_H

#include <QtCore/QStringList>

QT_FORWARD_DECLARE_CLASS(QLoggingCategory)

struct QtXmlToSphinxParameters
{
    QString moduleName;
    QString docDataDir;
    QString outputDirectory;
    QString libSourceDir;
    QStringList codeSnippetDirs;
    QString codeSnippetRewriteOld;
    QString codeSnippetRewriteNew;
    bool snippetComparison = false;
};

struct QtXmlToSphinxLink
{
    enum Type
    {
        Method = 0x1, Function = 0x2,
        FunctionMask = Method | Function,
        Class = 0x4, Attribute = 0x8, Module = 0x10,
        Reference = 0x20, External= 0x40
    };

    enum Flags { InsideBold = 0x1, InsideItalic = 0x2 };

    explicit QtXmlToSphinxLink(const QString &ref) : linkRef(ref) {}

    QString linkRef;
    QString linkText;
    Type type = Reference;
    int flags = 0;
};

class QtXmlToSphinxDocGeneratorInterface
{
public:
    virtual QString expandFunction(const QString &function) const = 0;
    virtual QString expandClass(const QString &context,
                                const QString &name) const = 0;
    virtual QString resolveContextForMethod(const QString &context,
                                            const QString &methodName) const = 0;

    virtual const QLoggingCategory &loggingCategory() const = 0;

    virtual QtXmlToSphinxLink resolveLink(const QtXmlToSphinxLink &) const = 0;

    virtual ~QtXmlToSphinxDocGeneratorInterface() = default;
};

#endif // QTXMLTOSPHINXINTERFACE_H
