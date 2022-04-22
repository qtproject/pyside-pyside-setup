/****************************************************************************
**
** Copyright (C) 2020 The Qt Company Ltd.
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

#include "doxygenparser.h"
#include "abstractmetalang.h"
#include "abstractmetafield.h"
#include "abstractmetafunction.h"
#include "abstractmetaenum.h"
#include "documentation.h"
#include "messages.h"
#include "modifications.h"
#include "propertyspec.h"
#include "reporthandler.h"
#include "typesystem.h"
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

void DoxygenParser::fillDocumentation(AbstractMetaClass* metaClass)
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
    if (xquery.isNull()) {
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

            QString doc = getDocumentation(xquery, funcQuery, DocModificationList());
            if (doc.isEmpty()) {
                qCWarning(lcShibokenDoc, "%s",
                          qPrintable(msgCannotFindDocumentation(doxyFilePath, func.data(),
                                                                funcQuery)));
            } else {
                funcDoc.setValue(doc, tag.first);
            }
        }
        qSharedPointerConstCast<AbstractMetaFunction>(func)->setDocumentation(funcDoc);
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
    if (xquery.isNull()) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return {};
    }

    // Module documentation
    QString query = u"/doxygen/compounddef/detaileddescription"_s;
    const QString doc = getDocumentation(xquery, query, DocModificationList());
    return Documentation(doc, {});
}

