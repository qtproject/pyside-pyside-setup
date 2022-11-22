// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CLASSDOCUMENTATION_H
#define CLASSDOCUMENTATION_H

#include <QtCore/QStringList>

QT_FORWARD_DECLARE_CLASS(QDebug)

/// An enumeration in a WebXML/doxygen document
struct EnumDocumentation
{
    QString name;
    QString description;
};

/// A QObject property in a WebXML/doxygen document
struct PropertyDocumentation
{
    QString name;
    QString brief;
    QString description;
};

/// Helper struct for querying a function in a WebXML/doxygen document
struct FunctionDocumentationQuery
{
    QString name;
    QStringList parameters;
    bool constant = false;
};

/// A function in a WebXML/doxygen document
struct FunctionDocumentation : public FunctionDocumentationQuery
{
    QString signature;
    QString returnType;
    QString description;
};

using FunctionDocumentationList = QList<FunctionDocumentation>;

/// A class/namespace in a WebXML/doxygen document
struct ClassDocumentation
{
    qsizetype indexOfEnum(const QString &name) const;
    FunctionDocumentationList findFunctionCandidates(const QString &name,
                                                     bool constant) const;
    static qsizetype indexOfFunction(const FunctionDocumentationList &fl,
                                     const FunctionDocumentationQuery &q);
    qsizetype indexOfProperty(const QString &name) const;

    QString name;
    QString description;

    QList<EnumDocumentation> enums;
    QList<PropertyDocumentation> properties;
    FunctionDocumentationList functions;

    operator bool() const { return !name.isEmpty(); }
};

/// Parse a WebXML class/namespace document
ClassDocumentation parseWebXml(const QString &fileName, QString *errorMessage);

/// Extract the module description from a WebXML module document
QString webXmlModuleDescription(const QString &fileName, QString *errorMessage);

QDebug operator<<(QDebug debug, const EnumDocumentation &e);
QDebug operator<<(QDebug debug, const PropertyDocumentation &p);
QDebug operator<<(QDebug debug, const FunctionDocumentationQuery &q);
QDebug operator<<(QDebug debug, const FunctionDocumentation &f);
QDebug operator<<(QDebug debug, const ClassDocumentation &c);

#endif // CLASSDOCUMENTATION_H
