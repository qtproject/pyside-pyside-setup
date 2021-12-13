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

#include "classdocumentation.h"
#include "messages.h"

#include <QtCore/QDebug>
#include <QtCore/QBuffer>
#include <QtCore/QFile>
#include <QtCore/QXmlStreamReader>
#include <QtCore/QXmlStreamAttributes>
#include <QtCore/QXmlStreamWriter>

#include <algorithm>

// Sort functions by name and argument count
static bool functionDocumentationLessThan(const FunctionDocumentation &f1,
                                          const FunctionDocumentation &f2)
{
    const int nc = f1.name.compare(f2.name);
    if (nc != 0)
        return nc < 0;
    return f1.parameters.size() < f2.parameters.size();
}

static void sortDocumentation(ClassDocumentation *cd)
{
    std::stable_sort(cd->enums.begin(), cd->enums.end(),
                     [] (const EnumDocumentation &e1, const EnumDocumentation &e2) {
                         return e1.name < e2.name; });
    std::stable_sort(cd->properties.begin(), cd->properties.end(),
                     [] (const PropertyDocumentation &p1, const PropertyDocumentation &p2) {
                         return p1.name < p2.name; });
    std::stable_sort(cd->functions.begin(), cd->functions.end(),
                     functionDocumentationLessThan);
}

qsizetype ClassDocumentation::indexOfEnum(const QString &name) const
{
    for (qsizetype i = 0, size = enums.size(); i < size; ++i) {
        if (enums.at(i).name == name)
            return i;
    }
    return -1;
}

FunctionDocumentationList ClassDocumentation::findFunctionCandidates(const QString &name,
                                                                     bool constant) const
{
    FunctionDocumentationList result;
    std::copy_if(functions.cbegin(), functions.cend(),
                 std::back_inserter(result),
                 [name, constant](const FunctionDocumentation &fd) {
                     return fd.constant == constant && fd.name == name;
                 });
    return result;
}

static bool matches(const FunctionDocumentation &fd, const FunctionDocumentationQuery &q)
{
    return fd.name == q.name && fd.constant == q.constant && fd.parameters == q.parameters;
}

qsizetype ClassDocumentation::indexOfFunction(const FunctionDocumentationList &fl,
                                              const FunctionDocumentationQuery &q)
{
    for (qsizetype i = 0, size = fl.size(); i < size; ++i) {
        if (matches(fl.at(i), q))
            return i;
    }
    return -1;
}

qsizetype ClassDocumentation::indexOfProperty(const QString &name) const
{
    for (qsizetype i = 0, size = properties.size(); i < size; ++i) {
        if (properties.at(i).name == name)
            return i;
    }
    return -1;
}

enum class WebXmlTag
{
    Class, Description, Enum, Function, Parameter, Property, Typedef, Other
};

static WebXmlTag tag(QStringView name)
{
    if (name == u"class" || name == u"namespace")
        return WebXmlTag::Class;
    if (name == u"enum")
        return WebXmlTag::Enum;
    if (name == u"function")
        return WebXmlTag::Function;
    if (name == u"description")
        return WebXmlTag::Description;
    if (name == u"parameter")
        return WebXmlTag::Parameter;
    if (name == u"property")
        return WebXmlTag::Property;
    if (name == u"typedef")
        return WebXmlTag::Typedef;
    return WebXmlTag::Other;
}

static void parseWebXmlElement(WebXmlTag tag, const QXmlStreamAttributes &attributes,
                               ClassDocumentation *cd)
{
    switch (tag) {
    case WebXmlTag::Class:
        cd->name = attributes.value(u"name"_qs).toString();
        break;
    case WebXmlTag::Enum: {
        EnumDocumentation ed;
        ed.name = attributes.value(u"name"_qs).toString();
        cd->enums.append(ed);
    }
        break;
    case WebXmlTag::Function: {
        FunctionDocumentation fd;
        fd.name = attributes.value(u"name"_qs).toString();
        fd.signature = attributes.value(u"signature"_qs).toString();
        fd.returnType = attributes.value(u"type"_qs).toString();
        fd.constant = attributes.value(u"const"_qs) == u"true";
        cd->functions.append(fd);
    }
        break;
    case WebXmlTag::Parameter:
        Q_ASSERT(!cd->functions.isEmpty());
        cd->functions.last().parameters.append(attributes.value(u"type"_qs).toString());
        break;
    case WebXmlTag::Property: {
        PropertyDocumentation pd;
        pd.name = attributes.value(u"name"_qs).toString();
        cd->properties.append(pd);
    }
        break;
    default:
        break;
    }
}

// Retrieve the contents of <description>
static QString extractWebXmlDescription(QXmlStreamReader &reader)
{
    QBuffer buffer;
    buffer.open(QIODeviceBase::WriteOnly);
    QXmlStreamWriter writer(&buffer);

    do {
        switch (reader.tokenType()) {
        case QXmlStreamReader::StartElement:
            writer.writeStartElement(reader.name().toString());
            writer.writeAttributes(reader.attributes());
            break;
        case QXmlStreamReader::Characters:
            writer.writeCharacters(reader.text().toString());
            break;
        case QXmlStreamReader::EndElement:
            writer.writeEndElement();
            if (reader.name() == u"description") {
                buffer.close();
                return QString::fromUtf8(buffer.buffer()).trimmed();
            }
            break;
        default:
            break;
        }
        reader.readNext();
    } while (!reader.atEnd());

    return {};
}

static QString msgXmlError(const QString &fileName, const QXmlStreamReader &reader)
{
    QString result;
    QTextStream(&result) << fileName << ':' << reader.lineNumber() << ':'
        << reader.columnNumber() << ':' << reader.errorString();
    return result;
}

ClassDocumentation parseWebXml(const QString &fileName, QString *errorMessage)
{
    ClassDocumentation result;

    QFile file(fileName);
    if (!file.open(QIODevice::Text | QIODevice::ReadOnly)) {
        *errorMessage = msgCannotOpenForReading(file);
        return result;
    }

    WebXmlTag lastTag = WebXmlTag::Other;
    QXmlStreamReader reader(&file);
    while (!reader.atEnd()) {
        switch (reader.readNext()) {
        case QXmlStreamReader::StartElement: {
            const auto currentTag = tag(reader.name());
            parseWebXmlElement(currentTag, reader.attributes(), &result);
            switch (currentTag) { // Store relevant tags in lastTag
            case WebXmlTag::Class:
            case WebXmlTag::Function:
            case WebXmlTag::Enum:
            case WebXmlTag::Property:
            case WebXmlTag::Typedef:
                lastTag = currentTag;
                break;
            case WebXmlTag::Description: { // Append the description to the element
                QString *target = nullptr;
                switch (lastTag) {
                case WebXmlTag::Class:
                    target = &result.description;
                    break;
                case WebXmlTag::Function:
                    target = &result.functions.last().description;
                    break;
                case WebXmlTag::Enum:
                    target = &result.enums.last().description;
                    break;
                case WebXmlTag::Property:
                    target = &result.properties.last().description;
                default:
                    break;
                }
                if (target != nullptr && target->isEmpty())
                    *target = extractWebXmlDescription(reader);
                }
                break;
            default:
                break;
            }
        }
        default:
            break;
        }
    }

    if (reader.error() != QXmlStreamReader::NoError) {
        *errorMessage= msgXmlError(fileName, reader);
        return {};
    }

    sortDocumentation(&result);
    return result;
}

QString webXmlModuleDescription(const QString &fileName, QString *errorMessage)
{
    QFile file(fileName);
    if (!file.open(QIODevice::Text | QIODevice::ReadOnly)) {
        *errorMessage = msgCannotOpenForReading(file);
        return {};
    }

    QString result;
    QXmlStreamReader reader(&file);
    while (!reader.atEnd()) {
        switch (reader.readNext()) {
        case QXmlStreamReader::StartElement:
            if (reader.name() == u"description")
                result = extractWebXmlDescription(reader);
            break;
        default:
            break;
        }
    }

    if (reader.error() != QXmlStreamReader::NoError) {
        *errorMessage= msgXmlError(fileName, reader);
        return {};
    }

    return result;
}

// Debug helpers
template <class T>
static void formatList(QDebug &debug, const char *title, const QList<T> &l)
{
    if (const qsizetype size = l.size()) {
        debug << title << '[' << size << "]=(";
        for (qsizetype i = 0; i < size; ++i) {
            if (i)
                debug << ", ";
            debug << l.at(i);
        }
        debug << ')';
    }
}

static void formatDescription(QDebug &debug, const QString &desc)
{
    debug << "description=";
    if (desc.isEmpty()) {
        debug << "<empty>";
        return;
    }
    if (debug.verbosity() < 3)
        debug << desc.size() << " chars";
    else
        debug << '"' << desc << '"';
}

QDebug operator<<(QDebug debug, const EnumDocumentation &e)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Enum(";
    if (e.name.isEmpty()) {
        debug << "invalid";
    } else {
        debug << e.name << ", ";
        formatDescription(debug, e.description);
    }
    debug << ')';
    return debug;
}

QDebug operator<<(QDebug debug, const PropertyDocumentation &p)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Property(";
    if (p.name.isEmpty()) {
        debug << "invalid";
    } else {
        debug << p.name << ", ";
        formatDescription(debug, p.description);
    }
    debug << ')';
    return debug;
}

QDebug operator<<(QDebug debug, const FunctionDocumentation &f)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Function(";
    if (f.name.isEmpty()) {
        debug << "invalid";
    } else {
        debug << f.name;
        if (!f.returnType.isEmpty())
            debug << ", returns " << f.returnType;
        if (f.constant)
            debug << ", const";
        formatList(debug, ", parameters", f.parameters);
        debug << ", signature=\"" << f.signature << "\", ";
        formatDescription(debug, f.description);
    }
    debug << ')';
    return debug;
}

QDebug operator<<(QDebug debug, const FunctionDocumentationQuery &q)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "FunctionQuery(" << q.name;
    if (q.constant)
        debug << ", const";
    formatList(debug, ", parameters", q.parameters);
    debug << ')';
    return debug;
}

QDebug operator<<(QDebug debug, const ClassDocumentation &c)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "Class(";
    if (c) {
        debug << c.name << ", ";
        formatDescription(debug, c.description);
        formatList(debug, ", enums", c.enums);
        formatList(debug, ", properties", c.properties);
        formatList(debug, ", functions", c.functions);
    } else {
        debug << "invalid";
    }
    debug << ')';
    return debug;
}
