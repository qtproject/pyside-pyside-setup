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
#include "classdocumentation.h"
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

#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QUrl>

enum { debugFunctionSearch = 0 };

static inline QString briefStartElement() { return QStringLiteral("<brief>"); }
static inline QString briefEndElement() { return QStringLiteral("</brief>"); }

Documentation QtDocParser::retrieveModuleDocumentation()
{
    return retrieveModuleDocumentation(packageName());
}

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

static QString formatFunctionArgTypeQuery(const AbstractMetaType &metaType)
{
    QString result;
    QTextStream str(&result);formatPreQualifications(str, metaType);
    formatFunctionUnqualifiedArgTypeQuery(str, metaType);
    formatPostQualifications(str, metaType);
    return result;
}

QString QtDocParser::queryFunctionDocumentation(const QString &sourceFileName,
                                                const ClassDocumentation &classDocumentation,
                                                const AbstractMetaClass* metaClass,
                                                const AbstractMetaFunctionCPtr &func,
                                                const DocModificationList &signedModifs,
                                                QString *errorMessage)
{
    errorMessage->clear();

    DocModificationList funcModifs;
    for (const DocModification &funcModif : signedModifs) {
        if (funcModif.signature() == func->minimalSignature())
            funcModifs.append(funcModif);
    }

    const QString docString =
        queryFunctionDocumentation(sourceFileName, classDocumentation, metaClass,
                                   func, errorMessage);

    return docString.isEmpty() || funcModifs.isEmpty()
        ? docString : applyDocModifications(funcModifs, docString);
}

QString QtDocParser::queryFunctionDocumentation(const QString &sourceFileName,
                                                const ClassDocumentation &classDocumentation,
                                                const AbstractMetaClass* metaClass,
                                                const AbstractMetaFunctionCPtr &func,
                                                QString *errorMessage)
{
    // Properties
    if (func->isPropertyReader() || func->isPropertyWriter() || func->isPropertyResetter()) {
        const QPropertySpec &prop = metaClass->propertySpecs().at(func->propertySpecIndex());
        const auto index = classDocumentation.indexOfProperty(prop.name());
        if (index == -1) {
            *errorMessage = msgCannotFindDocumentation(sourceFileName, func.data());
            return {};
        }
        return classDocumentation.properties.at(index).description;
    }

    // Search candidates by name and const-ness
    FunctionDocumentationList candidates =
        classDocumentation.findFunctionCandidates(func->name(), func->isConstant());
    if (candidates.isEmpty()) {
        *errorMessage = msgCannotFindDocumentation(sourceFileName, func.data())
                        + u" (no matches)"_qs;
        return {};
    }

    // Try an exact query
    FunctionDocumentationQuery fq;
    fq.name = func->name();
    fq.constant = func->isConstant();
    for (const auto &arg : func->arguments())
        fq.parameters.append(formatFunctionArgTypeQuery(arg.type()));

    const auto funcFlags = func->flags();
    // Re-add arguments removed by the metabuilder to binary operator functions
    if (funcFlags.testFlag(AbstractMetaFunction::Flag::OperatorLeadingClassArgumentRemoved)
        || funcFlags.testFlag(AbstractMetaFunction::Flag::OperatorTrailingClassArgumentRemoved)) {
        QString classType = metaClass->qualifiedCppName();
        if (!funcFlags.testFlag(AbstractMetaFunction::Flag::OperatorClassArgumentByValue)) {
            classType.prepend(u"const "_qs);
            classType.append(u" &"_qs);
        }
        if (funcFlags.testFlag(AbstractMetaFunction::Flag::OperatorLeadingClassArgumentRemoved))
            fq.parameters.prepend(classType);
        else
            fq.parameters.append(classType);
    }

    const qsizetype index = ClassDocumentation::indexOfFunction(candidates, fq);

    if (debugFunctionSearch) {
        qDebug() << __FUNCTION__ << metaClass->name() << fq << funcFlags << "returns"
            << index << "\n  " << candidates.value(index) << "\n  " << candidates;
    }

    if (index != -1)
        return candidates.at(index).description;

    // Fallback: Try matching by argument count
    const auto parameterCount = func->arguments().size();
    auto pend = std::remove_if(candidates.begin(), candidates.end(),
                               [parameterCount](const FunctionDocumentation &fd) {
                                   return fd.parameters.size() != parameterCount; });
    candidates.erase(pend, candidates.end());
    if (candidates.size() == 1) {
        const auto &match = candidates.constFirst();
        QTextStream(errorMessage) << msgFallbackForDocumentation(sourceFileName, func.data())
            << "\n  Falling back to \"" << match.signature
            << "\" obtained by matching the argument count only.";
        return candidates.constFirst().description;
    }

    QTextStream(errorMessage) << msgCannotFindDocumentation(sourceFileName, func.data())
        << " (" << candidates.size() << " candidates matching the argument count)";
    return {};
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

    ClassDocumentation classDocumentation = parseWebXml(sourceFileName, &errorMessage);
    if (!classDocumentation) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return;
    }

    DocModificationList signedModifs, classModifs;
    const DocModificationList &mods = metaClass->typeEntry()->docModifications();
    for (const DocModification &docModif : mods) {
        if (docModif.signature().isEmpty())
            classModifs.append(docModif);
        else
            signedModifs.append(docModif);
    }

    QString docString = applyDocModifications(mods, classDocumentation.description);

    if (docString.isEmpty()) {
        QString className = metaClass->name();
        qCWarning(lcShibokenDoc, "%s",
                  qPrintable(msgCannotFindDocumentation(sourceFileName, "class", className, {})));
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
            queryFunctionDocumentation(sourceFileName, classDocumentation,
                                       metaClass, func, signedModifs, &errorMessage);
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
        Documentation enumDoc;
        const auto index = classDocumentation.indexOfEnum(meta_enum.name());
        if (index != -1) {
            enumDoc.setValue(classDocumentation.enums.at(index).description);
            meta_enum.setDocumentation(enumDoc);
        } else {
            qCWarning(lcShibokenDoc, "%s",
                      qPrintable(msgCannotFindDocumentation(sourceFileName, metaClass, meta_enum, {})));
        }
    }
}

static QString qmlReferenceLink(const QFileInfo &qmlModuleFi)
{
    QString result;
    QTextStream(&result) << "<para>The module also provides <link"
        << R"( type="page" page="http://doc.qt.io/qt-)" << QT_VERSION_MAJOR
        << '/' << qmlModuleFi.baseName() << R"(.html")"
        << ">QML types</link>.</para>";
    return result;
}

Documentation QtDocParser::retrieveModuleDocumentation(const QString& name)
{
    // TODO: This method of acquiring the module name supposes that the target language uses
    // dots as module separators in package names. Improve this.
    QString moduleName = name;
    moduleName.remove(0, name.lastIndexOf(QLatin1Char('.')) + 1);
    if (moduleName == u"QtQuickControls2")
        moduleName.chop(1);
    const QString prefix = documentationDataDirectory() + QLatin1Char('/')
        + moduleName.toLower();

    const QString sourceFile = prefix + u"-index.webxml"_qs;
    if (!QFile::exists(sourceFile)) {
        qCWarning(lcShibokenDoc).noquote().nospace()
            << "Can't find qdoc file for module " <<  name << ", tried: "
            << QDir::toNativeSeparators(sourceFile);
        return Documentation();
    }

    QString errorMessage;
    QString docString = webXmlModuleDescription(sourceFile, &errorMessage);
    if (!errorMessage.isEmpty()) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return {};
    }

    Documentation doc(docString, {});
    if (doc.isEmpty()) {
        qCWarning(lcShibokenDoc, "%s",
                  qPrintable(msgCannotFindDocumentation(sourceFile, "module", name)));
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
