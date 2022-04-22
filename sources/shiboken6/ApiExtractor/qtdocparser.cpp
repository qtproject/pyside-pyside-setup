/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
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

#include "qtdocparser.h"
#include "abstractmetaenum.h"
#include "abstractmetafield.h"
#include "abstractmetafunction.h"
#include "abstractmetalang.h"
#include "documentation.h"
#include "modifications.h"
#include "messages.h"
#include "propertyspec.h"
#include "reporthandler.h"
#include "typesystem.h"
#include "xmlutils.h"

#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QTextStream>
#include <QtCore/QXmlStreamAttributes>
#include <QtCore/QXmlStreamReader>
#include <QtCore/QUrl>

static inline QString briefStartElement() { return QStringLiteral("<brief>"); }
static inline QString briefEndElement() { return QStringLiteral("</brief>"); }

Documentation QtDocParser::retrieveModuleDocumentation()
{
    return retrieveModuleDocumentation(packageName());
}

enum FunctionMatchFlags
{
    MatchArgumentCount = 0x1,
    MatchArgumentType = 0x2,
    MatchArgumentFuzzyType = 0x4, // Match a "const &" using contains()
    DescriptionOnly = 0x8
};

static void formatPreQualifications(QTextStream &str, const AbstractMetaType &type)
{
    if (type.isConstant())
        str << "const " ;
}

static void formatPostQualifications(QTextStream &str, const AbstractMetaType &type)
{
    if (type.referenceType() == LValueReference)
        str << " &";
    else if (type.referenceType() == RValueReference)
        str << " &&";
    else if (type.indirections())
        str << ' ' << QByteArray(type.indirections(), '*');
}

static void formatFunctionUnqualifiedArgTypeQuery(QTextStream &str,
                                                  const AbstractMetaType &metaType)
{
    switch (metaType.typeUsagePattern()) {
    case AbstractMetaType::FlagsPattern: {
        // Modify qualified name "QFlags<Qt::AlignmentFlag>" with name "Alignment"
        // to "Qt::Alignment" as seen by qdoc.
        const auto *flagsEntry = static_cast<const FlagsTypeEntry *>(metaType.typeEntry());
        QString name = flagsEntry->qualifiedCppName();
        if (name.endsWith(QLatin1Char('>')) && name.startsWith(QLatin1String("QFlags<"))) {
            const int lastColon = name.lastIndexOf(QLatin1Char(':'));
            if (lastColon != -1) {
                name.replace(lastColon + 1, name.size() - lastColon - 1, metaType.name());
                name.remove(0, 7);
            } else {
                name = metaType.name(); // QFlags<> of enum in global namespace
            }
        }
        str << name;
    }
        break;
    case AbstractMetaType::ContainerPattern: { // QVector<int>
        str << metaType.typeEntry()->qualifiedCppName() << '<';
        const auto instantiations = metaType.instantiations();
        for (int i = 0, size = instantiations.size(); i < size; ++i) {
            if (i)
                str << ", ";
            const auto &instantiation = instantiations.at(i);
            formatPreQualifications(str, instantiation);
            str << instantiation.typeEntry()->qualifiedCppName();
            formatPostQualifications(str, instantiation);
        }
        str << '>';
    }
        break;
    default: // Fully qualify enums (Qt::AlignmentFlag), nested classes, etc.
        str << metaType.typeEntry()->qualifiedCppName();
        break;
    }
}

static inline void formatFunctionArgTypeQuery(QTextStream &str, const AbstractMetaType &metaType)
{
    formatPreQualifications(str, metaType);
    formatFunctionUnqualifiedArgTypeQuery(str, metaType);
    formatPostQualifications(str, metaType);
}

static void formatFunctionArgTypeQuery(QTextStream &str, qsizetype n,
                                       const AbstractMetaType &metaType)
{
    // Fixme: Use arguments.at(i)->type()->originalTypeDescription()
    //        instead to get unresolved typedefs?
    str << "/parameter[" << (n + 1) << "][@type=\"";
    formatFunctionArgTypeQuery(str, metaType);
    str << "\"]/..";
}

// If there is any qualifier like '*', '&', we search by the type as a
// contained word to avoid space mismatches and apparently an issue in
// libxml/xslt that does not match '&amp;' in attributes.
// This should be "matches(type, "^(.*\W)?<type>(\W.*)?$")"), but
// libxslt only supports XPath 1.0. Also note,  "\b" is not supported
static void formatFunctionFuzzyArgTypeQuery(QTextStream &str, qsizetype n,
                                            const AbstractMetaType &metaType)
{
    str << "/parameter[" << (n + 1) << "][contains(@type, \"";
    formatFunctionUnqualifiedArgTypeQuery(str, metaType);
    str << " \")]/.."; // ending with space
}

static bool tryFuzzyMatching(const AbstractMetaType &metaType)
{
    return metaType.referenceType() != NoReference || metaType.indirections() != 0;
}

static bool tryFuzzyArgumentMatching(const AbstractMetaArgument &arg)
{
    return tryFuzzyMatching(arg.type());
}

static QString functionXQuery(const QString &classQuery,
                              const AbstractMetaFunctionCPtr &func,
                              unsigned matchFlags = MatchArgumentCount | MatchArgumentType
                                                    | DescriptionOnly)
{
    QString result;
    QTextStream str(&result);
    const AbstractMetaArgumentList &arguments = func->arguments();
    str << classQuery << "/function[@name=\"" << func->originalName()
        << "\" and @const=\"" << (func->isConstant() ? "true" : "false") << '"';
    if (matchFlags & MatchArgumentCount)
        str << " and count(parameter)=" << arguments.size();
    str << ']';
    if (!arguments.isEmpty()
        && (matchFlags & (MatchArgumentType | MatchArgumentFuzzyType)) != 0) {
        for (qsizetype i = 0, size = arguments.size(); i < size; ++i) {
            const auto &type = arguments.at(i).type();
            if ((matchFlags & MatchArgumentFuzzyType) != 0 && tryFuzzyMatching(type))
                formatFunctionFuzzyArgTypeQuery(str, i, type);
            else
                formatFunctionArgTypeQuery(str, i, type);
        }
    }
    if (matchFlags & DescriptionOnly)
        str << "/description";
    return result;
}

static QStringList signaturesFromWebXml(QString w)
{
    QStringList result;
    if (w.isEmpty())
        return result;
    w.prepend(QLatin1String("<root>")); // Fake root element
    w.append(QLatin1String("</root>"));
    QXmlStreamReader reader(w);
    while (!reader.atEnd()) {
        if (reader.readNext() == QXmlStreamReader::StartElement
            && reader.name() == QLatin1String("function")) {
            result.append(reader.attributes().value(QStringLiteral("signature")).toString());
        }
    }
    return result;
}

static QString msgArgumentMatch(const QString &query, const QStringList &matches)
{
    QString result;
    QTextStream str(&result);
    str << "\n  Note: Querying for " << query << " yields ";
    if (matches.isEmpty())
        str << "no";
    else
        str << matches.size();
    str << " matches";
    if (!matches.isEmpty())
        str << ": \"" << matches.join(QLatin1String("\", \"")) << '"';
    return result;
}

static inline QString msgArgumentFuzzyTypeMatch(const QStringList &matches)
{
    return msgArgumentMatch(u"arguments using fuzzy types"_qs, matches);
}

static inline QString msgArgumentCountMatch(const AbstractMetaArgumentList &args,
                                            const QStringList &matches)
{
    return msgArgumentMatch(u"the argument count=="_qs + QString::number(args.size()), matches);
}

QString QtDocParser::queryFunctionDocumentation(const QString &sourceFileName,
                                                const AbstractMetaClass* metaClass,
                                                const QString &classQuery,
                                                const AbstractMetaFunctionCPtr &func,
                                                const DocModificationList &signedModifs,
                                                const XQueryPtr &xquery,
                                                QString *errorMessage)
{
    errorMessage->clear();

    DocModificationList funcModifs;
    for (const DocModification &funcModif : signedModifs) {
        if (funcModif.signature() == func->minimalSignature())
            funcModifs.append(funcModif);
    }

    // Properties
    if (func->isPropertyReader() || func->isPropertyWriter() || func->isPropertyResetter()) {
        const auto prop = metaClass->propertySpecs().at(func->propertySpecIndex());
        const QString propertyQuery = classQuery + QLatin1String("/property[@name=\"")
            + prop.name() + QLatin1String("\"]/description");
        const QString properyDocumentation = getDocumentation(xquery, propertyQuery, funcModifs);
        if (properyDocumentation.isEmpty()) {
            *errorMessage =
                msgCannotFindDocumentation(sourceFileName, func.data(), propertyQuery);
        }
        return properyDocumentation;
    }

    // Query with full match of argument types
    const QString fullQuery = functionXQuery(classQuery, func);
    const QString result = getDocumentation(xquery, fullQuery, funcModifs);
    if (!result.isEmpty())
        return result;
    const auto &arguments = func->arguments();
    if (arguments.isEmpty()) { // No arguments, can't be helped
        *errorMessage = msgCannotFindDocumentation(sourceFileName, func.data(), fullQuery);
        return result;
    }

    // If there are any "const &" or similar parameters, try fuzzy matching.
    // Include the outer <function> element for checking.
    if (std::any_of(arguments.cbegin(), arguments.cend(), tryFuzzyArgumentMatching)) {
        const unsigned flags = MatchArgumentCount | MatchArgumentFuzzyType;
        QString fuzzyArgumentQuery = functionXQuery(classQuery, func, flags);
        QStringList signatures =
            signaturesFromWebXml(getDocumentation(xquery, fuzzyArgumentQuery, funcModifs));
        if (signatures.size() == 1) {
            // One match was found. Repeat the query restricted to the <description>
            // element and use the result with a warning.
            errorMessage->prepend(msgFallbackForDocumentation(sourceFileName, func.data(),
                                                              fullQuery));
            errorMessage->append(u"\n  Falling back to \""_qs + signatures.constFirst()
                                 + u"\" obtained by matching fuzzy argument types."_qs);
            fuzzyArgumentQuery = functionXQuery(classQuery, func, flags | DescriptionOnly);
            return getDocumentation(xquery, fuzzyArgumentQuery, funcModifs);
        }

        *errorMessage += msgArgumentFuzzyTypeMatch(signatures);

        if (signatures.size() > 1) { // Ambiguous, no point in trying argument count
            errorMessage->prepend(msgCannotFindDocumentation(sourceFileName, func.data(),
                                                             fullQuery));
            return result;
        }
    }

    // Finally, test whether some mismatch in argument types occurred by checking for
    // the argument count only.
    QString countOnlyQuery = functionXQuery(classQuery, func, MatchArgumentCount);
    QStringList signatures =
            signaturesFromWebXml(getDocumentation(xquery, countOnlyQuery, funcModifs));
    if (signatures.size() == 1) {
        // One match was found. Repeat the query restricted to the <description>
        // element and use the result with a warning.
        countOnlyQuery = functionXQuery(classQuery, func, MatchArgumentCount | DescriptionOnly);
        errorMessage->prepend(msgFallbackForDocumentation(sourceFileName, func.data(), fullQuery));
        errorMessage->append(QLatin1String("\n  Falling back to \"") + signatures.constFirst()
                             + QLatin1String("\" obtained by matching the argument count only."));
        return getDocumentation(xquery, countOnlyQuery, funcModifs);
    }

    errorMessage->prepend(msgCannotFindDocumentation(sourceFileName, func.data(), fullQuery));
    *errorMessage += msgArgumentCountMatch(arguments, signatures);
    return result;
}

// Extract the <brief> section from a WebXML (class) documentation and remove it
// from the source.
static QString extractBrief(QString *value)
{
    const auto briefStart = value->indexOf(briefStartElement());
    if (briefStart < 0)
        return {};
    const auto briefEnd = value->indexOf(briefEndElement(),
                                         briefStart + briefStartElement().size());
    if (briefEnd < briefStart)
        return {};
    const auto briefLength = briefEnd + briefEndElement().size() - briefStart;
    QString briefValue = value->mid(briefStart, briefLength);
    briefValue.insert(briefValue.size() - briefEndElement().size(),
                      QLatin1String("<rst> More_...</rst>"));
    value->remove(briefStart, briefLength);
    return briefValue;
}

void QtDocParser::fillDocumentation(AbstractMetaClass* metaClass)
{
    if (!metaClass)
        return;

    const AbstractMetaClass* context = metaClass->enclosingClass();
    while(context) {
        if (context->enclosingClass() == nullptr)
            break;
        context = context->enclosingClass();
    }

    QString sourceFileRoot = documentationDataDirectory() + QLatin1Char('/')
        + metaClass->qualifiedCppName().toLower();
    sourceFileRoot.replace(QLatin1String("::"), QLatin1String("-"));

    QFileInfo sourceFile(sourceFileRoot + QStringLiteral(".webxml"));
    if (!sourceFile.exists())
        sourceFile.setFile(sourceFileRoot + QStringLiteral(".xml"));
   if (!sourceFile.exists()) {
        qCWarning(lcShibokenDoc).noquote().nospace()
            << "Can't find qdoc file for class " << metaClass->name() << ", tried: "
            << QDir::toNativeSeparators(sourceFile.absoluteFilePath());
        return;
    }

    const QString sourceFileName = sourceFile.absoluteFilePath();
    QString errorMessage;
    XQueryPtr xquery = XQuery::create(sourceFileName, &errorMessage);
    if (xquery.isNull()) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return;
    }

    QString className = metaClass->name();

    // Class/Namespace documentation
    const QString classQuery = QLatin1String("/WebXML/document/")
         + (metaClass->isNamespace() ? QLatin1String("namespace") : QLatin1String("class"))
         + QLatin1String("[@name=\"") + className + QLatin1String("\"]");
    QString query = classQuery + QLatin1String("/description");

    DocModificationList signedModifs, classModifs;
    const DocModificationList &mods = metaClass->typeEntry()->docModifications();
    for (const DocModification &docModif : mods) {
        if (docModif.signature().isEmpty())
            classModifs.append(docModif);
        else
            signedModifs.append(docModif);
    }

    QString docString = getDocumentation(xquery, query, classModifs);
    if (docString.isEmpty()) {
        qCWarning(lcShibokenDoc, "%s",
                  qPrintable(msgCannotFindDocumentation(sourceFileName, "class", className, query)));
    }
    const QString brief = extractBrief(&docString);

    Documentation doc;
    if (!brief.isEmpty())
        doc.setValue(brief, Documentation::Brief);
    doc.setValue(docString);
    metaClass->setDocumentation(doc);

    //Functions Documentation
    const auto &funcs = DocParser::documentableFunctions(metaClass);
    for (const auto &func : funcs) {
        const QString detailed =
            queryFunctionDocumentation(sourceFileName, metaClass, classQuery,
                                       func, signedModifs, xquery, &errorMessage);
        if (!errorMessage.isEmpty())
            qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        const Documentation documentation(detailed, {});
        qSharedPointerConstCast<AbstractMetaFunction>(func)->setDocumentation(documentation);
    }
#if 0
    // Fields
    const AbstractMetaFieldList &fields = metaClass->fields();
    for (AbstractMetaField *field : fields) {
        if (field->isPrivate())
            return;

        QString query = "/doxygen/compounddef/sectiondef/memberdef/name[text()=\"" + field->name() + "\"]/..";
        Documentation doc = getDocumentation(DocModificationList(), xquery, query);
        field->setDocumentation(doc);
    }
#endif
    // Enums
    for (AbstractMetaEnum &meta_enum : metaClass->enums()) {
        query.clear();
        QTextStream(&query) << classQuery << "/enum[@name=\""
            << meta_enum.name() << "\"]/description";
        doc.setValue(getDocumentation(xquery, query, DocModificationList()));
        if (doc.isEmpty()) {
            qCWarning(lcShibokenDoc, "%s",
                      qPrintable(msgCannotFindDocumentation(sourceFileName, metaClass, meta_enum, query)));
        }
        meta_enum.setDocumentation(doc);
    }
}

static QString qmlReferenceLink(const QFileInfo &qmlModuleFi)
{
    QString result;
    QTextStream(&result) << "<para>The module also provides <link"
        << " type=\"page\""
        << " page=\"http://doc.qt.io/qt-5/" << qmlModuleFi.baseName() << ".html\""
        << ">QML types</link>.</para>";
    return result;
}

Documentation QtDocParser::retrieveModuleDocumentation(const QString& name)
{
    // TODO: This method of acquiring the module name supposes that the target language uses
    // dots as module separators in package names. Improve this.
    QString moduleName = name;
    moduleName.remove(0, name.lastIndexOf(QLatin1Char('.')) + 1);
    const QString prefix = documentationDataDirectory() + QLatin1Char('/')
        + moduleName.toLower();
    QString sourceFile = prefix + QLatin1String(".xml");

    if (!QFile::exists(sourceFile))
        sourceFile = prefix + QLatin1String("-module.webxml");
    if (!QFile::exists(sourceFile)) {
        qCWarning(lcShibokenDoc).noquote().nospace()
            << "Can't find qdoc file for module " <<  name << ", tried: "
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
    QString query = QLatin1String("/WebXML/document/module[@name=\"")
        + moduleName + QLatin1String("\"]/description");
    const QString detailed = getDocumentation(xquery, query, DocModificationList());
    Documentation doc(detailed, {});
    if (doc.isEmpty()) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(msgCannotFindDocumentation(sourceFile, "module", name, query)));
        return doc;
    }

    // If a QML module info file exists, insert a link to the Qt docs.
    const QFileInfo qmlModuleFi(prefix + QLatin1String("-qmlmodule.webxml"));
    if (qmlModuleFi.isFile()) {
        QString docString = doc.detailed();
        const int pos = docString.lastIndexOf(QLatin1String("</description>"));
        if (pos != -1) {
            docString.insert(pos, qmlReferenceLink(qmlModuleFi));
            doc.setDetailed(docString);
        }
    }

    return doc;
}
