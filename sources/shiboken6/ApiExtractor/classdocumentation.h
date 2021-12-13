/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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
