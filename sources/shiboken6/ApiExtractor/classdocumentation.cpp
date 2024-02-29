// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "classdocumentation.h"
#include "messages.h"
#include "debughelpers_p.h"

#include <QtCore/QDebug>
#include <QtCore/QBuffer>
#include <QtCore/QFile>
#include <QtCore/QXmlStreamReader>
#include <QtCore/QXmlStreamAttributes>
#include <QtCore/QXmlStreamWriter>

#include <algorithm>

using namespace Qt::StringLiterals;

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

enum class WebXmlCodeTag
{
    Class, Description, Enum, Function, Header, Parameter, Property, Typedef, Other
};

static WebXmlCodeTag tag(QStringView name)
{
    if (name == u"class" || name == u"namespace")
        return WebXmlCodeTag::Class;
    if (name == u"enum")
        return WebXmlCodeTag::Enum;
    if (name == u"function")
        return WebXmlCodeTag::Function;
    if (name == u"description")
        return WebXmlCodeTag::Description;
    if (name == u"header")
        return WebXmlCodeTag::Header;
    if (name == u"parameter")
        return WebXmlCodeTag::Parameter;
    if (name == u"property")
        return WebXmlCodeTag::Property;
    if (name == u"typedef")
        return WebXmlCodeTag::Typedef;
    return WebXmlCodeTag::Other;
}

static void parseWebXmlElement(WebXmlCodeTag tag, const QXmlStreamAttributes &attributes,
                               ClassDocumentation *cd)
{
    switch (tag) {
    case WebXmlCodeTag::Class:
        cd->name = attributes.value(u"name"_s).toString();
        cd->type = ClassDocumentation::Class;
        break;
    case WebXmlCodeTag::Header:
        cd->name = attributes.value(u"name"_s).toString();
        cd->type = ClassDocumentation::Header;
        break;
    case WebXmlCodeTag::Enum: {
        EnumDocumentation ed;
        ed.name = attributes.value(u"name"_s).toString();
        cd->enums.append(ed);
    }
        break;
    case WebXmlCodeTag::Function: {
        FunctionDocumentation fd;
        fd.name = attributes.value(u"name"_s).toString();
        fd.signature = attributes.value(u"signature"_s).toString();
        fd.returnType = attributes.value(u"type"_s).toString();
        fd.constant = attributes.value(u"const"_s) == u"true";
        cd->functions.append(fd);
    }
        break;
    case WebXmlCodeTag::Parameter:
        Q_ASSERT(!cd->functions.isEmpty());
        cd->functions.last().parameters.append(attributes.value(u"type"_s).toString());
        break;
    case WebXmlCodeTag::Property: {
        PropertyDocumentation pd;
        pd.name = attributes.value(u"name"_s).toString();
        pd.brief = attributes.value(u"brief"_s).toString();
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

std::optional<ClassDocumentation> parseWebXml(const QString &fileName, QString *errorMessage)
{
    ClassDocumentation result;

    QFile file(fileName);
    if (!file.open(QIODevice::Text | QIODevice::ReadOnly)) {
        *errorMessage = msgCannotOpenForReading(file);
        return std::nullopt;
    }

    WebXmlCodeTag lastTag = WebXmlCodeTag::Other;
    QXmlStreamReader reader(&file);
    while (!reader.atEnd()) {
        switch (reader.readNext()) {
        case QXmlStreamReader::StartElement: {
            const auto currentTag = tag(reader.name());
            parseWebXmlElement(currentTag, reader.attributes(), &result);
            switch (currentTag) { // Store relevant tags in lastTag
            case WebXmlCodeTag::Class:
            case WebXmlCodeTag::Function:
            case WebXmlCodeTag::Enum:
            case WebXmlCodeTag::Header:
            case WebXmlCodeTag::Property:
            case WebXmlCodeTag::Typedef:
                lastTag = currentTag;
                break;
            case WebXmlCodeTag::Description: { // Append the description to the element
                QString *target = nullptr;
                switch (lastTag) {
                case WebXmlCodeTag::Class:
                    target = &result.description;
                    break;
                case WebXmlCodeTag::Function:
                    target = &result.functions.last().description;
                    break;
                case WebXmlCodeTag::Enum:
                    target = &result.enums.last().description;
                    break;
                case WebXmlCodeTag::Property:
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
        return std::nullopt;
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
        formatList(debug, ", parameters", f.parameters, ", ");
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
    debug << "Class(" << c.name << ", ";
    formatDescription(debug, c.description);
    formatList(debug, ", enums", c.enums);
    formatList(debug, ", properties", c.properties);
    formatList(debug, ", functions", c.functions);
    debug << ')';
    return debug;
}
