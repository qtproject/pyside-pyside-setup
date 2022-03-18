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

#include "qtdocgenerator.h"
#include "exception.h"
#include "apiextractorresult.h"
#include "qtxmltosphinx.h"
#include "rstformat.h"
#include "ctypenames.h"
#include "pytypenames.h"
#include <abstractmetaenum.h>
#include <abstractmetafield.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <fileout.h>
#include <messages.h>
#include <modifications.h>
#include <propertyspec.h>
#include <reporthandler.h>
#include <textstream.h>
#include <typedatabase.h>
#include <typesystem.h>
#include <qtdocparser.h>
#include <doxygenparser.h>

#include <QtCore/QTextStream>
#include <QtCore/QFile>
#include <QtCore/QDir>

#include <algorithm>
#include <limits>

static inline QString additionalDocumentationOption() { return QStringLiteral("additional-documentation"); }

static inline QString none() { return QStringLiteral("None"); }

static bool shouldSkip(const AbstractMetaFunctionCPtr &func)
{
    // Constructors go to separate section
    if (DocParser::skipForQuery(func) || func->isConstructor())
        return true;

    // Search a const clone (QImage::bits() vs QImage::bits() const)
    if (func->isConstant())
        return false;

    const AbstractMetaArgumentList funcArgs = func->arguments();
    const auto &ownerFunctions = func->ownerClass()->functions();
    for (const auto &f : ownerFunctions) {
        if (f != func
            && f->isConstant()
            && f->name() == func->name()
            && f->arguments().size() == funcArgs.size()) {
            // Compare each argument
            bool cloneFound = true;

            const AbstractMetaArgumentList fargs = f->arguments();
            for (qsizetype i = 0, max = funcArgs.size(); i < max; ++i) {
                if (funcArgs.at(i).type().typeEntry() != fargs.at(i).type().typeEntry()) {
                    cloneFound = false;
                    break;
                }
            }
            if (cloneFound)
                return true;
        }
    }
    return false;
}

static bool functionSort(const AbstractMetaFunctionCPtr &func1, const AbstractMetaFunctionCPtr &func2)
{
    return func1->name() < func2->name();
}

static inline QVersionNumber versionOf(const TypeEntry *te)
{
    if (te) {
        const auto version = te->version();
        if (!version.isNull() && version > QVersionNumber(0, 0))
            return version;
    }
    return QVersionNumber();
}

QtDocGenerator::QtDocGenerator()
{
    m_parameters.snippetComparison =
        ReportHandler::debugLevel() >= ReportHandler::FullDebug;
}

QtDocGenerator::~QtDocGenerator() = default;

QString QtDocGenerator::fileNameSuffix()
{
    return u".rst"_qs;
}

bool QtDocGenerator::shouldGenerate(const AbstractMetaClass *cls) const
{
    return Generator::shouldGenerate(cls)
        && cls->typeEntry()->type() != TypeEntry::SmartPointerType;
}

QString QtDocGenerator::fileNameForContext(const GeneratorContext &context) const
{
    return fileNameForContextHelper(context, fileNameSuffix(),
                                    false /* qualified */);
}

void QtDocGenerator::writeFormattedBriefText(TextStream &s, const Documentation &doc,
                                             const AbstractMetaClass *metaclass) const
{
    writeFormattedText(s, doc.brief(), doc.format(), metaclass);
}

void QtDocGenerator::writeFormattedDetailedText(TextStream &s, const Documentation &doc,
                                                const AbstractMetaClass *metaclass) const
{
    writeFormattedText(s, doc.detailed(), doc.format(), metaclass);
}

void QtDocGenerator::writeFormattedText(TextStream &s, const QString &doc,
                                        Documentation::Format format,
                                        const AbstractMetaClass *metaClass) const
{
    QString metaClassName;

    if (metaClass)
        metaClassName = metaClass->fullName();

    if (format == Documentation::Native) {
        QtXmlToSphinx x(this, m_parameters, doc, metaClassName);
        s << x;
    } else {
        const auto lines = QStringView{doc}.split(QLatin1Char('\n'));
        int typesystemIndentation = std::numeric_limits<int>::max();
        // check how many spaces must be removed from the beginning of each line
        for (const auto &line : lines) {
            const auto it = std::find_if(line.cbegin(), line.cend(),
                                         [] (QChar c) { return !c.isSpace(); });
            if (it != line.cend())
                typesystemIndentation = qMin(typesystemIndentation, int(it - line.cbegin()));
        }
        if (typesystemIndentation == std::numeric_limits<int>::max())
            typesystemIndentation = 0;
        for (const auto &line : lines) {
            s << (typesystemIndentation > 0 && typesystemIndentation < line.size()
                    ? line.right(line.size() - typesystemIndentation) : line)
                << '\n';
        }
    }

    s << '\n';
}

static void writeInheritedByList(TextStream& s, const AbstractMetaClass* metaClass,
                                 const AbstractMetaClassCList& allClasses)
{
    AbstractMetaClassCList res;
    for (auto c : allClasses) {
        if (c != metaClass && c->inheritsFrom(metaClass))
            res << c;
    }

    if (res.isEmpty())
        return;

    s << "**Inherited by:** ";
    QStringList classes;
    for (auto c : qAsConst(res))
        classes << QLatin1String(":ref:`") + c->name() + QLatin1Char('`');
    s << classes.join(QLatin1String(", ")) << "\n\n";
}

void QtDocGenerator::generateClass(TextStream &s, const GeneratorContext &classContext)
{
    const AbstractMetaClass *metaClass = classContext.metaClass();
    qCDebug(lcShibokenDoc).noquote().nospace() << "Generating Documentation for " << metaClass->fullName();

    m_packages[metaClass->package()] << fileNameForContext(classContext);

    m_docParser->setPackageName(metaClass->package());
    m_docParser->fillDocumentation(const_cast<AbstractMetaClass*>(metaClass));

    QString className = metaClass->name();
    s << ".. _" << className << ":" << "\n\n";
    s << ".. currentmodule:: " << metaClass->package() << "\n\n\n";

    s << className << '\n';
    s << Pad('*', className.size()) << "\n\n";

    auto documentation = metaClass->documentation();
    if (documentation.hasBrief())
        writeFormattedBriefText(s, documentation, metaClass);

    s << ".. inheritance-diagram:: " << metaClass->fullName()<< '\n'
      << "    :parts: 2\n\n";
    // TODO: This would be a parameter in the future...


    writeInheritedByList(s, metaClass, api().classes());

    const auto version = versionOf(metaClass->typeEntry());
    if (!version.isNull())
        s << rstVersionAdded(version);
    if (metaClass->attributes().testFlag(AbstractMetaClass::Deprecated))
        s << rstDeprecationNote("class");

    writeFunctionList(s, metaClass);

    //Function list
    auto functionList = metaClass->functions();
    std::sort(functionList.begin(), functionList.end(), functionSort);

    s << "\nDetailed Description\n"
           "--------------------\n\n"
        << ".. _More:\n";

    writeInjectDocumentation(s, TypeSystem::DocModificationPrepend, metaClass, nullptr);
    if (!writeInjectDocumentation(s, TypeSystem::DocModificationReplace, metaClass, nullptr))
        writeFormattedDetailedText(s, documentation, metaClass);

    if (!metaClass->isNamespace())
        writeConstructors(s, metaClass);
    writeEnums(s, metaClass);
    if (!metaClass->isNamespace())
        writeFields(s, metaClass);


    QStringList uniqueFunctions;
    for (const auto &func : qAsConst(functionList)) {
        if (shouldSkip(func))
            continue;

        if (func->isStatic())
            s <<  ".. staticmethod:: ";
        else
            s <<  ".. method:: ";

        writeFunction(s, metaClass, func, !uniqueFunctions.contains(func->name()));
        uniqueFunctions.append(func->name());
    }

    writeInjectDocumentation(s, TypeSystem::DocModificationAppend, metaClass, nullptr);
}

void QtDocGenerator::writeFunctionList(TextStream& s, const AbstractMetaClass* cppClass)
{
    QStringList functionList;
    QStringList virtualList;
    QStringList signalList;
    QStringList slotList;
    QStringList staticFunctionList;

    const auto &classFunctions = cppClass->functions();
    for (const auto &func : classFunctions) {
        if (shouldSkip(func))
            continue;

        QString className;
        if (!func->isConstructor())
            className = cppClass->fullName() + QLatin1Char('.');
        else if (func->implementingClass() && func->implementingClass()->enclosingClass())
            className = func->implementingClass()->enclosingClass()->fullName() + QLatin1Char('.');
        QString funcName = getFuncName(func);

        QString str = QLatin1String("def :meth:`");

        str += funcName;
        str += QLatin1Char('<');
        if (!funcName.startsWith(className))
            str += className;
        str += funcName;
        str += QLatin1String(">` (");
        str += parseArgDocStyle(cppClass, func);
        str += QLatin1Char(')');

        if (func->isStatic())
            staticFunctionList << str;
        else if (func->isVirtual())
            virtualList << str;
        else if (func->isSignal())
            signalList << str;
        else if (func->isSlot())
            slotList << str;
        else
            functionList << str;
    }

    if (!functionList.isEmpty() || !staticFunctionList.isEmpty()) {
        QtXmlToSphinx::Table functionTable;

        s << "\nSynopsis\n--------\n\n";

        writeFunctionBlock(s, QLatin1String("Functions"), functionList);
        writeFunctionBlock(s, QLatin1String("Virtual functions"), virtualList);
        writeFunctionBlock(s, QLatin1String("Slots"), slotList);
        writeFunctionBlock(s, QLatin1String("Signals"), signalList);
        writeFunctionBlock(s, QLatin1String("Static functions"), staticFunctionList);
    }
}

void QtDocGenerator::writeFunctionBlock(TextStream& s, const QString& title, QStringList& functions)
{
    if (!functions.isEmpty()) {
        s << title << '\n'
          << Pad('^', title.size()) << '\n';

        std::sort(functions.begin(), functions.end());

        s << ".. container:: function_list\n\n";
        Indentation indentation(s);
        for (const QString &func : qAsConst(functions))
            s << "* " << func << '\n';
        s << "\n\n";
    }
}

void QtDocGenerator::writeEnums(TextStream& s, const AbstractMetaClass* cppClass) const
{
    static const QString section_title = QLatin1String(".. attribute:: ");

    for (const AbstractMetaEnum &en : cppClass->enums()) {
        s << section_title << cppClass->fullName() << '.' << en.name() << "\n\n";
        writeFormattedDetailedText(s, en.documentation(), cppClass);
        const auto version = versionOf(en.typeEntry());
        if (!version.isNull())
            s << rstVersionAdded(version);
    }

}

void QtDocGenerator::writeFields(TextStream& s, const AbstractMetaClass* cppClass) const
{
    static const QString section_title = QLatin1String(".. attribute:: ");

    for (const AbstractMetaField &field : cppClass->fields()) {
        s << section_title << cppClass->fullName() << "." << field.name() << "\n\n";
        writeFormattedDetailedText(s, field.documentation(), cppClass);
    }
}

void QtDocGenerator::writeConstructors(TextStream& s, const AbstractMetaClass* cppClass) const
{
    static const QString sectionTitle = QLatin1String(".. class:: ");

    auto lst = cppClass->queryFunctions(FunctionQueryOption::Constructors | FunctionQueryOption::Visible);
    for (int i = lst.size() - 1; i >= 0; --i) {
        if (lst.at(i)->isModifiedRemoved() || lst.at(i)->functionType() == AbstractMetaFunction::MoveConstructorFunction)
            lst.removeAt(i);
    }

    bool first = true;
    QHash<QString, AbstractMetaArgument> arg_map;

    if (lst.isEmpty()) {
        s << sectionTitle << cppClass->fullName();
    } else {
        QByteArray pad;
        for (const auto &func : qAsConst(lst)) {
            s << pad;
            if (first) {
                first = false;
                s << sectionTitle;
                pad = QByteArray(sectionTitle.size(), ' ');
            }
            s << functionSignature(cppClass, func) << "\n\n";

            const auto version = versionOf(func->typeEntry());
            if (!version.isNull())
                s << pad << rstVersionAdded(version);
            if (func->attributes().testFlag(AbstractMetaFunction::Deprecated))
                s << pad << rstDeprecationNote("constructor");

            const AbstractMetaArgumentList &arguments = func->arguments();
            for (const AbstractMetaArgument &arg : arguments) {
                if (!arg_map.contains(arg.name())) {
                    arg_map.insert(arg.name(), arg);
                }
            }
        }
    }

    s << '\n';

    for (auto it = arg_map.cbegin(), end = arg_map.cend(); it != end; ++it) {
        s.indent(2);
        writeParameterType(s, cppClass, it.value());
        s.outdent(2);
    }

    s << '\n';

    for (const auto &func : qAsConst(lst))
        writeFormattedDetailedText(s, func->documentation(), cppClass);
}

QString QtDocGenerator::parseArgDocStyle(const AbstractMetaClass* /* cppClass */,
                                         const AbstractMetaFunctionCPtr &func)
{
    QString ret;
    int optArgs = 0;

    const AbstractMetaArgumentList &arguments = func->arguments();
    for (const AbstractMetaArgument &arg : arguments) {

        if (arg.isModifiedRemoved())
            continue;

        bool thisIsoptional = !arg.defaultValueExpression().isEmpty();
        if (optArgs || thisIsoptional) {
            ret += QLatin1Char('[');
            optArgs++;
        }

        if (arg.argumentIndex() > 0)
            ret += QLatin1String(", ");

        ret += arg.name();

        if (thisIsoptional) {
            QString defValue = arg.defaultValueExpression();
            if (defValue == QLatin1String("QString()")) {
                defValue = QLatin1String("\"\"");
            } else if (defValue == QLatin1String("QStringList()")
                       || defValue.startsWith(QLatin1String("QVector"))
                       || defValue.startsWith(QLatin1String("QList"))) {
                defValue = QLatin1String("list()");
            } else if (defValue == QLatin1String("QVariant()")) {
                defValue = none();
            } else {
                defValue.replace(QLatin1String("::"), QLatin1String("."));
                if (defValue == QLatin1String("nullptr"))
                    defValue = none();
                else if (defValue == QLatin1String("0") && arg.type().isObject())
                    defValue = none();
            }
            ret += QLatin1Char('=') + defValue;
        }
    }

    ret += QString(optArgs, QLatin1Char(']'));
    return ret;
}

void QtDocGenerator::writeDocSnips(TextStream &s,
                                 const CodeSnipList &codeSnips,
                                 TypeSystem::CodeSnipPosition position,
                                 TypeSystem::Language language)
{
    Indentation indentation(s);
    QStringList invalidStrings;
    const static QString startMarkup = QLatin1String("[sphinx-begin]");
    const static QString endMarkup = QLatin1String("[sphinx-end]");

    invalidStrings << QLatin1String("*") << QLatin1String("//") << QLatin1String("/*") << QLatin1String("*/");

    for (const CodeSnip &snip : codeSnips) {
        if ((snip.position != position) ||
            !(snip.language & language))
            continue;

        QString code = snip.code();
        while (code.contains(startMarkup) && code.contains(endMarkup)) {
            int startBlock = code.indexOf(startMarkup) + startMarkup.size();
            int endBlock = code.indexOf(endMarkup);

            if ((startBlock == -1) || (endBlock == -1))
                break;

            QString codeBlock = code.mid(startBlock, endBlock - startBlock);
            const QStringList rows = codeBlock.split(QLatin1Char('\n'));
            int currentRow = 0;
            int offset = 0;

            for (QString row : rows) {
                for (const QString &invalidString : qAsConst(invalidStrings))
                    row.remove(invalidString);

                if (row.trimmed().size() == 0) {
                    if (currentRow == 0)
                        continue;
                    s << '\n';
                }

                if (currentRow == 0) {
                    //find offset
                    for (auto c : row) {
                        if (c == QLatin1Char(' '))
                            offset++;
                        else if (c == QLatin1Char('\n'))
                            offset = 0;
                        else
                            break;
                    }
                }
                s << QStringView{row}.mid(offset) << '\n';
                currentRow++;
            }

            code = code.mid(endBlock+endMarkup.size());
        }
    }
}

bool QtDocGenerator::writeInjectDocumentation(TextStream& s,
                                            TypeSystem::DocModificationMode mode,
                                            const AbstractMetaClass* cppClass,
                                            const AbstractMetaFunctionCPtr &func)
{
    Indentation indentation(s);
    bool didSomething = false;

    const DocModificationList &mods = cppClass->typeEntry()->docModifications();
    for (const DocModification &mod : mods) {
        if (mod.mode() == mode) {
            bool modOk = func ? mod.signature() == func->minimalSignature() : mod.signature().isEmpty();

            if (modOk) {
                Documentation::Format fmt;

                if (mod.format() == TypeSystem::NativeCode)
                    fmt = Documentation::Native;
                else if (mod.format() == TypeSystem::TargetLangCode)
                    fmt = Documentation::Target;
                else
                    continue;

                writeFormattedText(s, mod.code(), fmt, cppClass);
                didSomething = true;
            }
        }
    }

    s << '\n';

    // TODO: Deprecate the use of doc string on glue code.
    //       This is pre "add-function" and "inject-documentation" tags.
    const TypeSystem::CodeSnipPosition pos = mode == TypeSystem::DocModificationPrepend
        ? TypeSystem::CodeSnipPositionBeginning : TypeSystem::CodeSnipPositionEnd;
    if (func)
        writeDocSnips(s, func->injectedCodeSnips(), pos, TypeSystem::TargetLangCode);
    else
        writeDocSnips(s, cppClass->typeEntry()->codeSnips(), pos, TypeSystem::TargetLangCode);
    return didSomething;
}

QString QtDocGenerator::functionSignature(const AbstractMetaClass* cppClass,
                                          const AbstractMetaFunctionCPtr &func)
{
    QString funcName;

    funcName = cppClass->fullName();
    if (!func->isConstructor())
        funcName += QLatin1Char('.') + getFuncName(func);

    return funcName + QLatin1Char('(') + parseArgDocStyle(cppClass, func)
        + QLatin1Char(')');
}

QString QtDocGenerator::translateToPythonType(const AbstractMetaType &type,
                                              const AbstractMetaClass* cppClass) const
{
    static const QStringList nativeTypes =
        {boolT(), floatT(), intT(), pyObjectT(), pyStrT()};

    const QString name = type.name();
    if (nativeTypes.contains(name))
        return name;

    static const QMap<QString, QString> typeMap = {
        { cPyObjectT(), pyObjectT() },
        { qStringT(), pyStrT() },
        { QLatin1String("uchar"), pyStrT() },
        { QLatin1String("QStringList"), QLatin1String("list of strings") },
        { qVariantT(), pyObjectT() },
        { QLatin1String("quint32"), intT() },
        { QLatin1String("uint32_t"), intT() },
        { QLatin1String("quint64"), intT() },
        { QLatin1String("qint64"), intT() },
        { QLatin1String("size_t"), intT() },
        { QLatin1String("int64_t"), intT() },
        { QLatin1String("qreal"), floatT() }
    };
    const auto found = typeMap.find(name);
    if (found != typeMap.end())
        return found.value();

    QString strType;
    if (type.isConstant() && name == QLatin1String("char") && type.indirections() == 1) {
        strType = QLatin1String("str");
    } else if (name.startsWith(unsignedShortT())) {
        strType = intT();
    } else if (name.startsWith(unsignedT())) { // uint and ulong
        strType = intT();
    } else if (type.isContainer()) {
        QString strType = translateType(type, cppClass, Options(ExcludeConst) | ExcludeReference);
        strType.remove(QLatin1Char('*'));
        strType.remove(QLatin1Char('>'));
        strType.remove(QLatin1Char('<'));
        strType.replace(QLatin1String("::"), QLatin1String("."));
        if (strType.contains(QLatin1String("QList")) || strType.contains(QLatin1String("QVector"))) {
            strType.replace(QLatin1String("QList"), QLatin1String("list of "));
            strType.replace(QLatin1String("QVector"), QLatin1String("list of "));
        } else if (strType.contains(QLatin1String("QHash")) || strType.contains(QLatin1String("QMap"))) {
            strType.remove(QLatin1String("QHash"));
            strType.remove(QLatin1String("QMap"));
            QStringList types = strType.split(QLatin1Char(','));
            strType = QString::fromLatin1("Dictionary with keys of type %1 and values of type %2.")
                                         .arg(types[0], types[1]);
        }
    } else {
        auto k = AbstractMetaClass::findClass(api().classes(), type.typeEntry());
        strType = k ? k->fullName() : type.name();
        strType = QStringLiteral(":any:`") + strType + QLatin1Char('`');
    }
    return strType;
}

QString QtDocGenerator::getFuncName(const AbstractMetaFunctionCPtr& cppFunc)
{
    QString result = cppFunc->name();
    if (cppFunc->isOperatorOverload()) {
        const QString pythonOperator = Generator::pythonOperatorFunctionName(result);
        if (!pythonOperator.isEmpty())
            return pythonOperator;
    }
    result.replace(u"::"_qs, u"."_qs);
    return result;
}

void QtDocGenerator::writeParameterType(TextStream& s, const AbstractMetaClass* cppClass,
                                        const AbstractMetaArgument &arg) const
{
    s << ":param " << arg.name() << ": "
      << translateToPythonType(arg.type(), cppClass) << '\n';
}

void QtDocGenerator::writeFunctionParametersType(TextStream &s, const AbstractMetaClass *cppClass,
                                                 const AbstractMetaFunctionCPtr &func) const
{
    s << '\n';
    const AbstractMetaArgumentList &funcArgs = func->arguments();
    for (const AbstractMetaArgument &arg : funcArgs) {
        if (!arg.isModifiedRemoved())
            writeParameterType(s, cppClass, arg);
    }

    if (!func->isConstructor() && !func->isVoid()) {

        QString retType;
        // check if the return type was modified
        for (const auto &mod : func->modifications()) {
            for (const ArgumentModification &argMod : mod.argument_mods()) {
                if (argMod.index() == 0) {
                    retType = argMod.modifiedType();
                    break;
                }
            }
        }

        if (retType.isEmpty())
            retType = translateToPythonType(func->type(), cppClass);
        s << ":rtype: " << retType << '\n';
    }
    s << '\n';
}

void QtDocGenerator::writeFunction(TextStream& s, const AbstractMetaClass* cppClass,
                                   const AbstractMetaFunctionCPtr &func, bool indexed)
{
    s << functionSignature(cppClass, func);

    {
        Indentation indentation(s);
        if (!indexed)
            s << "\n:noindex:";
        s << "\n\n";
        writeFunctionParametersType(s, cppClass, func);
        const auto version = versionOf(func->typeEntry());
        if (!version.isNull())
            s << rstVersionAdded(version);
        if (func->attributes().testFlag(AbstractMetaFunction::Deprecated))
            s << rstDeprecationNote("function");
    }
    writeInjectDocumentation(s, TypeSystem::DocModificationPrepend, cppClass, func);
    if (!writeInjectDocumentation(s, TypeSystem::DocModificationReplace, cppClass, func)) {
        writeFormattedBriefText(s, func->documentation(), cppClass);
        writeFormattedDetailedText(s, func->documentation(), cppClass);
    }
    writeInjectDocumentation(s, TypeSystem::DocModificationAppend, cppClass, func);
}

static void writeFancyToc(TextStream& s, const QStringList& items)
{
    using TocMap = QMap<QChar, QStringList>;
    TocMap tocMap;
    QChar Q = QLatin1Char('Q');
    QChar idx;
    for (QString item : items) {
        if (item.isEmpty())
            continue;
        item.chop(4); // Remove the .rst extension
        // skip namespace if necessary
        const QString className = item.split(QLatin1Char('.')).last();
        if (className.startsWith(Q) && className.length() > 1)
            idx = className[1];
        else
            idx = className[0];
        tocMap[idx] << item;
    }

    static const qsizetype numColumns = 4;

    QtXmlToSphinx::Table table;
    for (auto it = tocMap.cbegin(), end = tocMap.cend(); it != end; ++it) {
        QtXmlToSphinx::TableRow row;
        const QString charEntry = QLatin1String("**") + it.key() + QLatin1String("**");
        row << QtXmlToSphinx::TableCell(charEntry);
        for (const QString &item : qAsConst(it.value())) {
            if (row.size() >= numColumns) {
                table.appendRow(row);
                row.clear();
                row << QtXmlToSphinx::TableCell(QString{});
            }
            const QString entry = QLatin1String("* :doc:`") + item + QLatin1Char('`');
            row << QtXmlToSphinx::TableCell(entry);
        }
        if (!row.isEmpty())
            table.appendRow(row);
    }

    table.normalize();
    s << ".. container:: pysidetoc\n\n";
    table.format(s);
}

bool QtDocGenerator::finishGeneration()
{
    if (!api().classes().isEmpty())
        writeModuleDocumentation();
    if (!m_additionalDocumentationList.isEmpty())
        writeAdditionalDocumentation();
    return true;
}

void QtDocGenerator::writeModuleDocumentation()
{
    QMap<QString, QStringList>::iterator it = m_packages.begin();
    for (; it != m_packages.end(); ++it) {
        std::sort(it.value().begin(), it.value().end());

        QString key = it.key();
        key.replace(QLatin1Char('.'), QLatin1Char('/'));
        QString outputDir = outputDirectory() + QLatin1Char('/') + key;
        FileOut output(outputDir + QLatin1String("/index.rst"));
        TextStream& s = output.stream;

        const QString &title = it.key();
        s << ".. module:: " << title << "\n\n"
            << title << '\n'
            << Pad('*', title.length()) << "\n\n";

        // Store the it.key() in a QString so that it can be stripped off unwanted
        // information when neeeded. For example, the RST files in the extras directory
        // doesn't include the PySide# prefix in their names.
        QString moduleName = it.key();
        const int lastIndex = moduleName.lastIndexOf(QLatin1Char('.'));
        if (lastIndex >= 0)
            moduleName.remove(0, lastIndex + 1);

        // Search for extra-sections
        if (!m_extraSectionDir.isEmpty()) {
            QDir extraSectionDir(m_extraSectionDir);
            if (!extraSectionDir.exists()) {
                const QString m = QStringLiteral("Extra sections directory ") +
                                  m_extraSectionDir + QStringLiteral(" doesn't exist");
                throw Exception(m);
            }

            // Filter for "QtCore.Property.rst", skipping module doc "QtCore.rst"
            const QString filter = moduleName + QLatin1String(".?*.rst");
            const auto fileList =
                extraSectionDir.entryInfoList({filter}, QDir::Files, QDir::Name);
            for (const auto &fi : fileList) {
                // Strip to "Property.rst" in output directory
                const QString newFileName = fi.fileName().mid(moduleName.size() + 1);
                it.value().append(newFileName);
                const QString newFilePath = outputDir + QLatin1Char('/') + newFileName;
                if (QFile::exists(newFilePath))
                    QFile::remove(newFilePath);
                if (!QFile::copy(fi.absoluteFilePath(), newFilePath)) {
                    qCDebug(lcShibokenDoc).noquote().nospace() << "Error copying extra doc "
                        << QDir::toNativeSeparators(fi.absoluteFilePath())
                        << " to " << QDir::toNativeSeparators(newFilePath);
                }
            }
        }

        writeFancyToc(s, it.value());

        s << ".. container:: hide\n\n" << indent
            << ".. toctree::\n" << indent
            << ":maxdepth: 1\n\n";
        for (const QString &className : qAsConst(it.value()))
            s << className << '\n';
        s << "\n\n" << outdent << outdent
            << "Detailed Description\n--------------------\n\n";

        // module doc is always wrong and C++istic, so go straight to the extra directory!
        QFile moduleDoc(m_extraSectionDir + QLatin1Char('/') + moduleName
                        + QLatin1String(".rst"));
        if (moduleDoc.open(QIODevice::ReadOnly | QIODevice::Text)) {
            s << moduleDoc.readAll();
            moduleDoc.close();
        } else {
            // try the normal way
            Documentation moduleDoc = m_docParser->retrieveModuleDocumentation(it.key());
            if (moduleDoc.format() == Documentation::Native) {
                QString context = it.key();
                QtXmlToSphinx::stripPythonQualifiers(&context);
                QtXmlToSphinx x(this, m_parameters, moduleDoc.detailed(), context);
                s << x;
            } else {
                s << moduleDoc.detailed();
            }
        }
        output.done();
    }
}

static inline QString msgNonExistentAdditionalDocFile(const QString &dir,
                                                      const QString &fileName)
{
    QString result;
    QTextStream(&result) << "Additional documentation file \""
        << fileName << "\" does not exist in "
        << QDir::toNativeSeparators(dir) << '.';
    return result;
}

void QtDocGenerator::writeAdditionalDocumentation() const
{
    QFile additionalDocumentationFile(m_additionalDocumentationList);
    if (!additionalDocumentationFile.open(QIODevice::ReadOnly | QIODevice::Text))
        throw Exception(msgCannotOpenForReading(additionalDocumentationFile));

    QDir outDir(outputDirectory());
    const QString rstSuffix = fileNameSuffix();

    QString errorMessage;
    int successCount = 0;
    int count = 0;

    QString targetDir = outDir.absolutePath();

    while (!additionalDocumentationFile.atEnd()) {
        const QByteArray lineBA = additionalDocumentationFile.readLine().trimmed();
        if (lineBA.isEmpty() || lineBA.startsWith('#'))
            continue;
        const QString line = QFile::decodeName(lineBA);
        // Parse "[directory]" specification
        if (line.size() > 2 && line.startsWith(QLatin1Char('[')) && line.endsWith(QLatin1Char(']'))) {
            const QString dir = line.mid(1, line.size() - 2);
            if (dir.isEmpty() || dir == QLatin1String(".")) {
                targetDir = outDir.absolutePath();
            } else {
                if (!outDir.exists(dir) && !outDir.mkdir(dir)) {
                    const QString m = QStringLiteral("Cannot create directory ")
                                      + dir + QStringLiteral(" under ")
                                      + QDir::toNativeSeparators(outputDirectory());
                    throw Exception(m);
                }
                targetDir = outDir.absoluteFilePath(dir);
            }
        } else {
            // Normal file entry
            QFileInfo fi(m_parameters.docDataDir + QLatin1Char('/') + line);
            if (fi.isFile()) {
                const QString rstFileName = fi.baseName() + rstSuffix;
                const QString rstFile = targetDir + QLatin1Char('/') + rstFileName;
                const QString context = targetDir.mid(targetDir.lastIndexOf(QLatin1Char('/')) + 1);
                if (convertToRst(fi.absoluteFilePath(),
                                 rstFile, context, &errorMessage)) {
                    ++successCount;
                    qCDebug(lcShibokenDoc).nospace().noquote() << __FUNCTION__
                        << " converted " << fi.fileName()
                        << ' ' << rstFileName;
                } else {
                    qCWarning(lcShibokenDoc, "%s", qPrintable(errorMessage));
                }
            } else {
                // FIXME: This should be an exception, in principle, but it
                // requires building all modules.
                qCWarning(lcShibokenDoc, "%s",
                          qPrintable(msgNonExistentAdditionalDocFile(m_parameters.docDataDir, line)));
            }
            ++count;
        }
    }
    additionalDocumentationFile.close();

    qCInfo(lcShibokenDoc, "Created %d/%d additional documentation files.",
           successCount, count);
}

#ifdef __WIN32__
#   define PATH_SEP ';'
#else
#   define PATH_SEP ':'
#endif

bool QtDocGenerator::doSetup()
{
    if (m_parameters.codeSnippetDirs.isEmpty()) {
        m_parameters.codeSnippetDirs =
            m_parameters.libSourceDir.split(QLatin1Char(PATH_SEP));
    }

    if (m_docParser.isNull())
        m_docParser.reset(new QtDocParser);

    if (m_parameters.libSourceDir.isEmpty()
        || m_parameters.docDataDir.isEmpty()) {
        qCWarning(lcShibokenDoc) << "Documentation data dir and/or Qt source dir not informed, "
                                 "documentation will not be extracted from Qt sources.";
        return false;
    }

    m_docParser->setDocumentationDataDirectory(m_parameters.docDataDir);
    m_docParser->setLibrarySourceDirectory(m_parameters.libSourceDir);
    m_parameters.outputDirectory = outputDirectory();
    return true;
}


Generator::OptionDescriptions QtDocGenerator::options() const
{
    auto result = Generator::options();
    result.append({
        {QLatin1String("doc-parser=<parser>"),
         QLatin1String("The documentation parser used to interpret the documentation\n"
                        "input files (qdoc|doxygen)")},
        {QLatin1String("documentation-code-snippets-dir=<dir>"),
         QLatin1String("Directory used to search code snippets used by the documentation")},
        {u"snippets-path-rewrite=old:new"_qs,
         u"Replacements in code snippet path to find .cpp/.h snippets converted to Python"_qs},
        {QLatin1String("documentation-data-dir=<dir>"),
         QLatin1String("Directory with XML files generated by documentation tool")},
        {QLatin1String("documentation-extra-sections-dir=<dir>"),
         QLatin1String("Directory used to search for extra documentation sections")},
        {QLatin1String("library-source-dir=<dir>"),
         QLatin1String("Directory where library source code is located")},
        {additionalDocumentationOption() + QLatin1String("=<file>"),
         QLatin1String("List of additional XML files to be converted to .rst files\n"
                       "(for example, tutorials).")}
    });
    return result;
}

bool QtDocGenerator::handleOption(const QString &key, const QString &value)
{
    if (Generator::handleOption(key, value))
        return true;
    if (key == QLatin1String("library-source-dir")) {
        m_parameters.libSourceDir = value;
        return true;
    }
    if (key == QLatin1String("documentation-data-dir")) {
        m_parameters.docDataDir = value;
        return true;
    }
    if (key == QLatin1String("documentation-code-snippets-dir")) {
        m_parameters.codeSnippetDirs = value.split(QLatin1Char(PATH_SEP));
        return true;
    }

    if (key == u"snippets-path-rewrite") {
        const auto pos = value.indexOf(u':');
        if (pos == -1)
            return false;
        m_parameters.codeSnippetRewriteOld= value.left(pos);
        m_parameters.codeSnippetRewriteNew = value.mid(pos + 1);
        return true;
    }

    if (key == QLatin1String("documentation-extra-sections-dir")) {
        m_extraSectionDir = value;
        return true;
    }
    if (key == QLatin1String("doc-parser")) {
        qCDebug(lcShibokenDoc).noquote().nospace() << "doc-parser: " << value;
        if (value == QLatin1String("doxygen"))
            m_docParser.reset(new DoxygenParser);
        return true;
    }
    if (key == additionalDocumentationOption()) {
        m_additionalDocumentationList = value;
        return true;
    }
    return false;
}

bool QtDocGenerator::convertToRst(const QString &sourceFileName,
                                  const QString &targetFileName,
                                  const QString &context,
                                  QString *errorMessage) const
{
    QFile sourceFile(sourceFileName);
    if (!sourceFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
        if (errorMessage)
            *errorMessage = msgCannotOpenForReading(sourceFile);
        return false;
    }
    const QString doc = QString::fromUtf8(sourceFile.readAll());
    sourceFile.close();

    FileOut targetFile(targetFileName);
    QtXmlToSphinx x(this, m_parameters, doc, context);
    targetFile.stream << x;
    targetFile.done();
    return true;
}

// QtXmlToSphinxDocGeneratorInterface
QString QtDocGenerator::expandFunction(const QString &function) const
{
    const int firstDot = function.indexOf(QLatin1Char('.'));
    const AbstractMetaClass *metaClass = nullptr;
    if (firstDot != -1) {
        const auto className = QStringView{function}.left(firstDot);
        for (auto cls : api().classes()) {
            if (cls->name() == className) {
                metaClass = cls;
                break;
            }
        }
    }

    return metaClass
        ? metaClass->typeEntry()->qualifiedTargetLangName()
          + function.right(function.size() - firstDot)
        : function;
}

QString QtDocGenerator::expandClass(const QString &context,
                                    const QString &name) const
{
    if (auto typeEntry = TypeDatabase::instance()->findType(name))
        return typeEntry->qualifiedTargetLangName();
    // fall back to the old heuristic if the type wasn't found.
    QString result = name;
    const auto rawlinklist = QStringView{name}.split(QLatin1Char('.'));
    QStringList splittedContext = context.split(QLatin1Char('.'));
    if (rawlinklist.size() == 1 || rawlinklist.constFirst() == splittedContext.constLast()) {
        splittedContext.removeLast();
        result.prepend(QLatin1Char('~') + splittedContext.join(QLatin1Char('.'))
                       + QLatin1Char('.'));
    }
    return result;
}

QString QtDocGenerator::resolveContextForMethod(const QString &context,
                                                const QString &methodName) const
{
    const auto currentClass = QStringView{context}.split(QLatin1Char('.')).constLast();

    const AbstractMetaClass *metaClass = nullptr;
    for (auto cls : api().classes()) {
        if (cls->name() == currentClass) {
            metaClass = cls;
            break;
        }
    }

    if (metaClass) {
        AbstractMetaFunctionCList funcList;
        const auto &methods = metaClass->queryFunctionsByName(methodName);
        for (const auto &func : methods) {
            if (methodName == func->name())
                funcList.append(func);
        }

        const AbstractMetaClass *implementingClass = nullptr;
        for (const auto &func : qAsConst(funcList)) {
            implementingClass = func->implementingClass();
            if (implementingClass->name() == currentClass)
                break;
        }

        if (implementingClass)
            return implementingClass->typeEntry()->qualifiedTargetLangName();
    }

    return QLatin1Char('~') + context;
}

const QLoggingCategory &QtDocGenerator::loggingCategory() const
{
    return lcShibokenDoc();
}

static bool isRelativeHtmlFile(const QString &linkRef)
{
    return !linkRef.startsWith(u"http")
        && (linkRef.endsWith(u".html") || linkRef.contains(u".html#"));
}

// Resolve relative, local .html documents links to doc.qt.io as they
// otherwise will not work and neither be found in the HTML tree.
QtXmlToSphinxLink QtDocGenerator::resolveLink(const QtXmlToSphinxLink &link) const
{
    if (link.type != QtXmlToSphinxLink::Reference || !isRelativeHtmlFile(link.linkRef))
        return link;
    static const QString prefix = QStringLiteral("https://doc.qt.io/qt-")
        + QString::number(QT_VERSION_MAJOR) + QLatin1Char('/');
    QtXmlToSphinxLink resolved = link;
    resolved.type = QtXmlToSphinxLink::External;
    resolved.linkRef = prefix + link.linkRef;
    if (resolved.linkText.isEmpty()) {
        resolved.linkText = link.linkRef;
        const qsizetype anchor = resolved.linkText.lastIndexOf(u'#');
        if (anchor != -1)
            resolved.linkText.truncate(anchor);
    }
    qDebug() << __FUNCTION__ << link << "->" << resolved;
    return resolved;
}
