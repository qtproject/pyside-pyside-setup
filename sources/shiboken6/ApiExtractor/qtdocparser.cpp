// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "qtdocparser.h"
#include "classdocumentation.h"
#include "abstractmetaargument.h"
#include "abstractmetaenum.h"
#include "abstractmetafunction.h"
#include "abstractmetalang.h"
#include "abstractmetatype.h"
#include "documentation.h"
#include "exception.h"
#include "modifications.h"
#include "messages.h"
#include "propertyspec.h"
#include "reporthandler.h"
#include "flagstypeentry.h"
#include "complextypeentry.h"
#include "functiontypeentry.h"
#include "enumtypeentry.h"
#include "typesystemtypeentry.h"
#include "typedatabase.h"

#include "qtcompat.h"

#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QHash>
#include <QtCore/QUrl>

#include <algorithm>
#include <iterator>

using namespace Qt::StringLiterals;

enum { debugFunctionSearch = 0 };

constexpr auto briefStartElement = "<brief>"_L1;
constexpr auto briefEndElement = "</brief>"_L1;
constexpr auto webxmlSuffix = ".webxml"_L1;

// Return the package of a type "PySide6.QtGui.QPainter" -> "PySide6.QtGui"
static QStringView packageFromPythonType(QStringView pythonType)
{
    qsizetype pos = pythonType.startsWith(u"PySide6.") ? 8 : 0;
    auto dot = pythonType.indexOf(u'.', pos);
    return dot != -1 ? pythonType.sliced(0, dot) : pythonType;
}

// Return the qdoc dir "PySide6.QtGui.QPainter" -> "qtgui/webxml" (QTBUG-119500)
static QString qdocModuleDirFromPackage(QStringView package)
{
    if (package.startsWith(u"PySide6."))
        package = package.sliced(8);
    return package.toString().toLower() + "/webxml"_L1;
}

// Populate a cache of package to WebXML dir
static QHash<QString, QString> getPackageToModuleDir()
{
    QHash<QString, QString> result;
    const auto &typeSystemEntries = TypeDatabase::instance()->typeSystemEntries();
    for (const auto &te : typeSystemEntries) {
        const QString &package = te->name();
        const QString &docPackage = te->hasDocTargetLangPackage()
                                    ? te->docTargetLangPackage() : package;
        result.insert(package, qdocModuleDirFromPackage(docPackage));
    }
    return result;
}

QString QtDocParser::qdocModuleDir(const QString &pythonType)
{
    static const QHash<QString, QString> packageToModuleDir = getPackageToModuleDir();

    const QStringView package = packageFromPythonType(pythonType);
    const auto it = packageToModuleDir.constFind(package);
    if (it == packageToModuleDir.cend()) {
        const QString known = packageToModuleDir.keys().join(", "_L1);
        qCWarning(lcShibokenDoc, "Type from unknown package: \"%s\" (known: %s).",
                  qPrintable(pythonType), qPrintable(known));
        return qdocModuleDirFromPackage(package);
    }
    return it.value();
}

static QString xmlFileBaseName(const AbstractMetaClassPtr &metaClass)
{
    QString className = metaClass->qualifiedCppName().toLower();
    className.replace("::"_L1, "-"_L1);
    return className;
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
        const auto flagsEntry = std::static_pointer_cast<const FlagsTypeEntry>(metaType.typeEntry());
        QString name = flagsEntry->qualifiedCppName();
        if (name.endsWith(u'>') && name.startsWith(u"QFlags<")) {
            const auto lastColon = name.lastIndexOf(u':');
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
        const auto &instantiations = metaType.instantiations();
        for (qsizetype i = 0, size = instantiations.size(); i < size; ++i) {
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

QtDocParser::FunctionDocumentationOpt
    QtDocParser::functionDocumentation(const QString &sourceFileName,
                                       const ClassDocumentation &classDocumentation,
                                       const AbstractMetaClassCPtr &metaClass,
                                       const AbstractMetaFunctionCPtr &func, QString *errorMessage)
{
    errorMessage->clear();

    FunctionDocumentationOpt orig = queryFunctionDocumentation(sourceFileName, classDocumentation, metaClass,
                                                               func, errorMessage);
    if (!orig.has_value() || orig.value().description.isEmpty())
        return orig;

    const auto funcModifs = DocParser::getXpathDocModifications(func, metaClass);
    if (funcModifs.isEmpty())
        return orig;

    FunctionDocumentation modified = orig.value();
    modified.description = applyDocModifications(funcModifs, orig->description);
    return modified;
}

QtDocParser::FunctionDocumentationOpt
    QtDocParser::queryFunctionDocumentation(const QString &sourceFileName,
                                            const ClassDocumentation &classDocumentation,
                                            const AbstractMetaClassCPtr &metaClass,
                                            const AbstractMetaFunctionCPtr &func, QString *errorMessage)
{
    // Search candidates by name and const-ness
    FunctionDocumentationList candidates =
        classDocumentation.findFunctionCandidates(func->name(), func->isConstant());
    if (candidates.isEmpty()) {
        *errorMessage = msgCannotFindDocumentation(sourceFileName, func.get())
                        + u" (no matches)"_s;
        return std::nullopt;
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
            classType.prepend(u"const "_s);
            classType.append(u" &"_s);
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
        return candidates.at(index);

    // Fallback: Try matching by argument count
    const auto parameterCount = func->arguments().size();
    auto pend = std::remove_if(candidates.begin(), candidates.end(),
                               [parameterCount](const FunctionDocumentation &fd) {
                                   return fd.parameters.size() != parameterCount; });
    candidates.erase(pend, candidates.end());
    if (candidates.size() == 1) {
        const auto &match = candidates.constFirst();
        QTextStream(errorMessage) << msgFallbackForDocumentation(sourceFileName, func.get())
            << "\n  Falling back to \"" << match.signature
            << "\" obtained by matching the argument count only.";
        return candidates.constFirst();
    }

    QTextStream(errorMessage) << msgCannotFindDocumentation(sourceFileName, func.get())
        << " (" << candidates.size() << " candidates matching the argument count)";
    return std::nullopt;
}

// Extract the <brief> section from a WebXML (class) documentation and remove it
// from the source.
static QString extractBrief(QString *value)
{
    const auto briefStart = value->indexOf(briefStartElement);
    if (briefStart < 0)
        return {};
    const auto briefEnd = value->indexOf(briefEndElement,
                                         briefStart + briefStartElement.size());
    if (briefEnd < briefStart)
        return {};
    const auto briefLength = briefEnd + briefEndElement.size() - briefStart;
    QString briefValue = value->mid(briefStart, briefLength);
    briefValue.insert(briefValue.size() - briefEndElement.size(),
                      u"<rst> More_...</rst>"_s);
    value->remove(briefStart, briefLength);
    return briefValue;
}

// Apply the documentation parsed from WebXML to a AbstractMetaFunction and complete argument
// names missing from parsed headers using the WebXML names (exact match only).
static void applyDocumentation(const FunctionDocumentation &funcDoc,
                               const QString &sourceFileName,
                               const AbstractMetaFunctionPtr &func)
{
    const Documentation documentation(funcDoc.description, {}, sourceFileName);
    func->setDocumentation(documentation);

    if (const auto argCount = func->arguments().size(); argCount == funcDoc.parameterNames.size()) {
        for (qsizetype a = 0; a < argCount; ++a) {
            if (!func->arguments().at(a).hasName() && !funcDoc.parameterNames.at(a).isEmpty())
                func->setArgumentName(a, funcDoc.parameterNames.at(a));
        }
    }
}

// Find the webxml file for global functions/enums
// by the doc-file typesystem attribute or via include file.
static QString findGlobalWebXmLFile(const QString &documentationDataDirectory,
                                    const QString &package,
                                    const QString &docFile,
                                    const Include &include)
{
    QString result;
    const QString root = documentationDataDirectory + u'/'
                         + QtDocParser::qdocModuleDir(package) + u'/';
    if (!docFile.isEmpty()) {
        result = root + docFile;
        if (!result.endsWith(webxmlSuffix))
            result += webxmlSuffix;
        return QFileInfo::exists(result) ? result : QString{};
    }
    if (include.name().isEmpty())
        return {};
    // qdoc "\headerfile <QtLogging>" directive produces "qtlogging.webxml"
    result = root + QFileInfo(include.name()).baseName() + webxmlSuffix;
    if (QFileInfo::exists(result))
        return result;
    // qdoc "\headerfile <qdrawutil.h>" produces "qdrawutil-h.webxml"
    result.insert(result.size() - webxmlSuffix.size(), "-h"_L1);
    return QFileInfo::exists(result) ? result : QString{};
}

void  QtDocParser::fillGlobalFunctionDocumentation(const AbstractMetaFunctionPtr &f)
{
    auto te = f->typeEntry();
    if (te == nullptr)
        return;

    const QString sourceFileName =
        findGlobalWebXmLFile(documentationDataDirectory(), te->targetLangPackage(), te->docFile(), te->include());
    if (sourceFileName.isEmpty())
        return;

    QString errorMessage;
    auto classDocumentationO = parseWebXml({sourceFileName}, &errorMessage);
    if (!classDocumentationO.has_value()) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return;
    }

    const auto funcDocOpt = functionDocumentation(sourceFileName, classDocumentationO.value(),
                                                  {}, f, &errorMessage);
    if (funcDocOpt.has_value())
        applyDocumentation(funcDocOpt.value(), sourceFileName, f);
    else if (!errorMessage.isEmpty())
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
}

void QtDocParser::fillGlobalEnumDocumentation(AbstractMetaEnum &e)
{
    auto te = e.typeEntry();
    const QString sourceFileName =
        findGlobalWebXmLFile(documentationDataDirectory(), te->targetLangPackage(), te->docFile(), te->include());
    if (sourceFileName.isEmpty())
        return;

    QString errorMessage;
    auto classDocumentationO = parseWebXml({sourceFileName}, &errorMessage);
    if (!classDocumentationO.has_value()) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return;
    }
    if (!extractEnumDocumentation(classDocumentationO.value(), sourceFileName, e)) {
        qCWarning(lcShibokenDoc, "%s",
                  qPrintable(msgCannotFindDocumentation(sourceFileName, {}, e, {})));
    }
}

QString QtDocParser::fillDocumentation(const AbstractMetaClassPtr &metaClass)
{
    if (!metaClass)
        return {};

    auto context = metaClass->enclosingClass();
    while (context) {
        if (!context->enclosingClass())
            break;
        context = context->enclosingClass();
    }

    // Find qdoc files of a class.
    QStringList allCandidates;
    const auto typeEntry = metaClass->typeEntry();
    const QString docDir = documentationDataDirectory() + u'/'
                           + QtDocParser::qdocModuleDir(typeEntry->targetLangPackage()) + u'/';
    const QString baseName = xmlFileBaseName(metaClass);
    allCandidates.append(docDir + baseName + webxmlSuffix);
    const QString &docFile = typeEntry->docFile();
    if (!docFile.isEmpty())
        allCandidates.append(docDir + docFile + webxmlSuffix);
    allCandidates.append(docDir + baseName + ".xml"_L1);
    QStringList candidates;
    std::copy_if(allCandidates.cbegin(), allCandidates.cend(), std::back_inserter(candidates),
                 qOverload<const QString &>(QFileInfo::exists));

   if (candidates.isEmpty()) {
       qCWarning(lcShibokenDoc, "%s", qPrintable(msgCannotFindQDocFile(metaClass, allCandidates)));
       return {};
    }

    QString errorMessage;
    const auto classDocumentationO = parseWebXml(candidates, &errorMessage);
    if (!classDocumentationO.has_value()) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return {};
    }

    const auto &classDocumentation = classDocumentationO.value();
    const QString &sourceFileName = candidates.constFirst();
    for (const auto &p : classDocumentation.properties) {
        Documentation doc(p.description, p.brief, sourceFileName);
        metaClass->setPropertyDocumentation(p.name, doc);
    }

    QString docString = applyDocModifications(DocParser::getXpathDocModifications(metaClass),
                                              classDocumentation.description);

    if (docString.isEmpty()) {
        QString className = metaClass->name();
        qCWarning(lcShibokenDoc, "%s",
                  qPrintable(msgCannotFindDocumentation(sourceFileName, "class", className, {})));
    }
    const QString brief = extractBrief(&docString);

    Documentation doc;
    doc.setSourceFile(sourceFileName);
    if (!brief.isEmpty())
        doc.setValue(brief, DocumentationType::Brief);
    doc.setValue(docString);
    metaClass->setDocumentation(doc);

    //Functions Documentation
    const auto &funcs = DocParser::documentableFunctions(metaClass);
    for (const auto &func : funcs) {
        const auto funcDocOpt = functionDocumentation(sourceFileName, classDocumentation,
                                                      metaClass, func, &errorMessage);
        if (funcDocOpt.has_value()) {
            applyDocumentation(funcDocOpt.value(), sourceFileName,
                               std::const_pointer_cast<AbstractMetaFunction>(func));
        } else if (!errorMessage.isEmpty()) {
            qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        }
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
        if (!extractEnumDocumentation(classDocumentation, sourceFileName, meta_enum)) {
            qCWarning(lcShibokenDoc, "%s",
                      qPrintable(msgCannotFindDocumentation(sourceFileName, metaClass, meta_enum, {})));
        }
    }

    return sourceFileName;
}

bool QtDocParser::extractEnumDocumentation(const ClassDocumentation &classDocumentation,
                                           const QString &sourceFileName,
                                           AbstractMetaEnum &meta_enum)
{
    const auto index = classDocumentation.indexOfEnum(meta_enum.name());
    if (index == -1)
        return false;
    QString doc = classDocumentation.enums.at(index).description;
    const auto firstPara = doc.indexOf(u"<para>");
    if (firstPara != -1) {
        const QString baseClass = QtDocParser::enumBaseClass(meta_enum);
        if (baseClass != "Enum"_L1) {
            const QString note = "(inherits <teletype>enum."_L1 + baseClass
                                 + "</teletype>) "_L1;
            doc.insert(firstPara + 6, note);
        }
    }
    doc.replace("::None</term>"_L1, "::None\\_</term>"_L1);
    Documentation enumDoc(doc, {}, sourceFileName);
    meta_enum.setDocumentation(enumDoc);
    return true;
}

static QString qmlReferenceLink(const QFileInfo &qmlModuleFi)
{
    return "https://doc.qt.io/qt-"_L1 + QString::number(QT_VERSION_MAJOR)
        + u'/' + qmlModuleFi.baseName() + ".html"_L1;
}

ModuleDocumentation QtDocParser::retrieveModuleDocumentation(const QString &name)
{
    // TODO: This method of acquiring the module name supposes that the target language uses
    // dots as module separators in package names. Improve this.
    QString completeModuleName = name;
    if (completeModuleName.endsWith("QtQuickControls2"_L1))
        completeModuleName.chop(1);
    const QString moduleName = completeModuleName.sliced(name.lastIndexOf(u'.') + 1);
    const QString lowerModuleName = moduleName.toLower();

    const QString dirPath = documentationDataDirectory() + u'/' + qdocModuleDir(completeModuleName);
    const QString sourceFile = dirPath + u'/' + lowerModuleName + "-index.webxml"_L1;
    if (!QFile::exists(sourceFile)) {
        qCWarning(lcShibokenDoc).noquote().nospace()
            << "Can't find qdoc file for module " <<  name << ", tried: "
            << QDir::toNativeSeparators(sourceFile);
        return {};
    }

    QString errorMessage;
    QString docString = webXmlModuleDescription(sourceFile, &errorMessage);
    if (!errorMessage.isEmpty()) {
        qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
        return {};
    }
    if (docString.isEmpty()) {
        qCWarning(lcShibokenDoc, "%s",
                  qPrintable(msgCannotFindDocumentation(sourceFile, "module", name)));
        return {};
    }

    ModuleDocumentation result{Documentation{docString, {}, sourceFile}, {}};

    // If a QML module info file exists, insert a link to the Qt docs.
    // Use a filter as some file names are irregular.
    // Note: These files are empty; we need to point to the web docs.
    const QFileInfoList qmlModuleFiles =
        QDir(dirPath).entryInfoList({"*-qmlmodule.webxml"_L1}, QDir::Files);
    if (!qmlModuleFiles.isEmpty())
        result.qmlTypesUrl = qmlReferenceLink(qmlModuleFiles.constFirst());
    return result;
}
