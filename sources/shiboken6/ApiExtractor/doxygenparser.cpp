// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "doxygenparser.h"
#include "abstractmetaargument.h"
#include "abstractmetalang.h"
#include "abstractmetafield.h"
#include "abstractmetafunction.h"
#include "abstractmetaenum.h"
#include "abstractmetatype.h"
#include "documentation.h"
#include "messages.h"
#include "modifications.h"
#include "propertyspec.h"
#include "reporthandler.h"
#include "complextypeentry.h"
#include "xmlutils.h"

#include "qtcompat.h"

#include <QtCore/QFile>
#include <QtCore/QDir>

using namespace Qt::StringLiterals;

static QString getSectionKindAttr(const AbstractMetaFunctionCPtr &func)
{
    if (func->isSignal())
        return u"signal"_s;
    QString kind = func->isPublic()
        ? u"public"_s : u"protected"_s;
    if (func->isStatic())
        kind += u"-static"_s;
    else if (func->isSlot())
        kind += u"-slot"_s;
    return kind;
}

Documentation DoxygenParser::retrieveModuleDocumentation()
{
        return retrieveModuleDocumentation(packageName());
}

void DoxygenParser::fillDocumentation(const AbstractMetaClassPtr &metaClass)
{
    if (!metaClass)
        return;

    QString doxyFileSuffix;
    if (metaClass->enclosingClass()) {
        doxyFileSuffix += metaClass->enclosingClass()->name();
        doxyFileSuffix += u"_1_1"_s; // FIXME: Check why _1_1!!
    }
    doxyFileSuffix += metaClass->name();
    doxyFileSuffix += u".xml"_s;

    const char* prefixes[] = { "class", "struct", "namespace" };
    bool isProperty = false;

    QString doxyFilePath;
    for (const char *prefix : prefixes) {
        doxyFilePath = documentationDataDirectory() + u'/'
                       + QLatin1StringView(prefix) + doxyFileSuffix;
        if (QFile::exists(doxyFilePath))
            break;
        doxyFilePath.clear();
    }

    if (doxyFilePath.isEmpty()) {
        qCWarning(lcShibokenDoc).noquote().nospace()
            << "Can't find doxygen file for class " << metaClass->name() << ", tried: "
            << QDir::toNativeSeparators(documentationDataDirectory())
            <<  "/{struct|class|namespace}"<< doxyFileSuffix;
        return;
    }

    QString errorMessage;
    XQueryPtr xquery = XQuery::create(doxyFilePath, &errorMessage);
    if (!xquery) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return;
    }

    static const QList<QPair<Documentation::Type, QString>> docTags = {
        { Documentation::Brief,  u"briefdescription"_s },
        { Documentation::Detailed,  u"detaileddescription"_s }
    };
    // Get class documentation
    Documentation classDoc;

    for (const auto &tag : docTags) {
        const QString classQuery = u"/doxygen/compounddef/"_s + tag.second;
        QString doc = getDocumentation(xquery, classQuery,
                                            metaClass->typeEntry()->docModifications());
        if (doc.isEmpty())
            qCWarning(lcShibokenDoc, "%s",
                      qPrintable(msgCannotFindDocumentation(doxyFilePath, "class", metaClass->name(),
                                                            classQuery)));
        else
            classDoc.setValue(doc, tag.first);
    }
    metaClass->setDocumentation(classDoc);

    //Functions Documentation
    const auto &funcs = DocParser::documentableFunctions(metaClass);
    for (const auto &func : funcs) {
        QString query = u"/doxygen/compounddef/sectiondef"_s;
        // properties
        if (func->isPropertyReader() || func->isPropertyWriter()
            || func->isPropertyResetter()) {
            const auto prop = metaClass->propertySpecs().at(func->propertySpecIndex());
            query += u"[@kind=\"property\"]/memberdef/name[text()=\""_s
                     + prop.name() + u"\"]"_s;
            isProperty = true;
        } else { // normal methods
            QString kind = getSectionKindAttr(func);
            query += u"[@kind=\""_s + kind
                     + u"-func\"]/memberdef/name[text()=\""_s
                     + func->originalName() + u"\"]"_s;

            if (func->arguments().isEmpty()) {
                QString args = func->isConstant() ? u"() const "_s : u"()"_s;
                query += u"/../argsstring[text()=\""_s + args + u"\"]"_s;
            } else {
                int i = 1;
                const AbstractMetaArgumentList &arguments = func->arguments();
                for (const AbstractMetaArgument &arg : arguments) {
                    if (!arg.type().isPrimitive()) {
                        query += u"/../param["_s + QString::number(i)
                                 + u"]/type/ref[text()=\""_s
                                 + arg.type().cppSignature().toHtmlEscaped()
                                 + u"\"]/../.."_s;
                    } else {
                        query += u"/../param["_s + QString::number(i)
                                 + u"]/type[text(), \""_s
                                 + arg.type().cppSignature().toHtmlEscaped()
                                 + u"\"]/.."_s;
                    }
                    ++i;
                }
            }
        }
        Documentation funcDoc;
        for (const auto &tag : docTags) {
            QString funcQuery(query);
            if (!isProperty) {
                funcQuery += u"/../"_s + tag.second;
            } else {
                funcQuery = u'(' + funcQuery;
                funcQuery += u"/../"_s + tag.second + u")[1]"_s;
            }

            QString doc = getDocumentation(xquery, funcQuery,
                                           DocParser::getDocModifications(metaClass, func));
            if (doc.isEmpty()) {
                qCWarning(lcShibokenDoc, "%s",
                          qPrintable(msgCannotFindDocumentation(doxyFilePath, func.get(),
                                                                funcQuery)));
            } else {
                funcDoc.setValue(doc, tag.first);
            }
        }
        std::const_pointer_cast<AbstractMetaFunction>(func)->setDocumentation(funcDoc);
        isProperty = false;
    }

    //Fields
    for (AbstractMetaField &field : metaClass->fields()) {
        if (field.isPrivate())
            return;

        Documentation fieldDoc;
        for (const auto &tag : docTags) {
            QString query = u"/doxygen/compounddef/sectiondef/memberdef/name[text()=\""_s
                            + field.name() + u"\"]/../"_s + tag.second;
            QString doc = getDocumentation(xquery, query, DocModificationList());
            if (doc.isEmpty()) {
                qCWarning(lcShibokenDoc, "%s",
                          qPrintable(msgCannotFindDocumentation(doxyFilePath, metaClass, field,
                                                                query)));
            } else {
                fieldDoc.setValue(doc, tag.first);
            }
        }
        field.setDocumentation(fieldDoc);
    }

    //Enums
    for (AbstractMetaEnum &meta_enum : metaClass->enums()) {
        QString query = u"/doxygen/compounddef/sectiondef/memberdef[@kind=\"enum\"]/name[text()=\""_s
            + meta_enum.name() + u"\"]/.."_s;
        QString doc = getDocumentation(xquery, query, DocModificationList());
        if (doc.isEmpty()) {
            qCWarning(lcShibokenDoc, "%s",
                      qPrintable(msgCannotFindDocumentation(doxyFilePath, metaClass, meta_enum, query)));
        }
        meta_enum.setDocumentation(Documentation(doc, {}));
    }

}

Documentation DoxygenParser::retrieveModuleDocumentation(const QString& name){

    QString sourceFile = documentationDataDirectory() + u"/indexpage.xml"_s;

    if (!QFile::exists(sourceFile)) {
        qCWarning(lcShibokenDoc).noquote().nospace()
            << "Can't find doxygen XML file for module " << name << ", tried: "
            << QDir::toNativeSeparators(sourceFile);
        return Documentation();
    }

    QString errorMessage;
    XQueryPtr xquery = XQuery::create(sourceFile, &errorMessage);
    if (!xquery) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return {};
    }

    // Module documentation
    QString query = u"/doxygen/compounddef/detaileddescription"_s;
    const QString doc = getDocumentation(xquery, query, DocModificationList());
    return Documentation(doc, {});
}

