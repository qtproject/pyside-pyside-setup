// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef QTXMLTOSPHINXINTERFACE_H
#define QTXMLTOSPHINXINTERFACE_H

#include <QtCore/qstringlist.h>

#include <cstdint>

QT_FORWARD_DECLARE_CLASS(QLoggingCategory)
QT_FORWARD_DECLARE_CLASS(QDebug)

struct QtXmlToSphinxImage
{
    QString scope;
    QString href;
};

QDebug operator<<(QDebug debug, const QtXmlToSphinxImage &i);

using QtXmlToSphinxImages = QList<QtXmlToSphinxImage>;

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
    enum Type : std::uint16_t
    {
        Method = 0x1, Function = 0x2,
        FunctionMask = Method | Function,
        Class = 0x4, Attribute = 0x8, Module = 0x10,
        CodeMask = 0xFF,
        Reference = 0x100, External= 0x200
    };

    enum Flags : std::uint8_t { InsideBold = 0x1, InsideItalic = 0x2 };

    explicit QtXmlToSphinxLink(QString ref) : linkRef(std::move(ref)) {}

    QString linkRef;
    QString linkText;
    Type type = Reference;
    std::underlying_type_t<Flags> flags = 0;
};

class QtXmlToSphinxDocGeneratorInterface
{
public:
    Q_DISABLE_COPY_MOVE(QtXmlToSphinxDocGeneratorInterface)

    QtXmlToSphinxDocGeneratorInterface() noexcept = default;

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
