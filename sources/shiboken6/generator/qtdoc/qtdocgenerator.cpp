// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "qtdocgenerator.h"
#include "generatorcontext.h"
#include "codesnip.h"
#include "exception.h"
#include "abstractmetaargument.h"
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
#include <functiontypeentry.h>
#include <enumtypeentry.h>
#include <complextypeentry.h>
#include <qtdocparser.h>
#include <doxygenparser.h>

#include "qtcompat.h"

#include <QtCore/QTextStream>
#include <QtCore/QFile>
#include <QtCore/QDir>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>

#include <algorithm>
#include <limits>

using namespace Qt::StringLiterals;

struct GeneratorDocumentation
{
    struct Property
    {
        QString name;
        Documentation documentation;
        AbstractMetaType type;
        AbstractMetaFunctionCPtr getter;
        AbstractMetaFunctionCPtr setter;
        AbstractMetaFunctionCPtr reset;
        AbstractMetaFunctionCPtr notify;
    };

    AbstractMetaFunctionCList constructors;
    AbstractMetaFunctionCList allFunctions; // Except constructors
    AbstractMetaFunctionCList tocNormalFunctions; // Index lists
    AbstractMetaFunctionCList tocVirtuals;
    AbstractMetaFunctionCList tocSignalFunctions;
    AbstractMetaFunctionCList tocSlotFunctions;
    AbstractMetaFunctionCList tocStaticFunctions;

    QList<Property> properties;
};

static bool operator<(const GeneratorDocumentation::Property &lhs,
                      const GeneratorDocumentation::Property &rhs)
{
    return lhs.name < rhs.name;
}

static QString propertyRefTarget(const AbstractMetaClassCPtr &cppClass, const QString &name)
{
    QString result = cppClass->fullName() +  u'.' + name;
    result.replace(u"::"_s, u"."_s);
    // For sphinx referencing, disambiguate the target from the getter name
    // by inserting an invisible "Hangul choseong filler" character.
    result.insert(1, QChar(0x115F));
    return result;
}

static inline QString additionalDocumentationOption() { return QStringLiteral("additional-documentation"); }

static inline QString none() { return QStringLiteral("None"); }

static bool shouldSkip(const AbstractMetaFunctionCPtr &func)
{
    if (DocParser::skipForQuery(func))
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

static inline QVersionNumber versionOf(const TypeEntryCPtr &te)
{
    if (te) {
        const auto version = te->version();
        if (!version.isNull() && version > QVersionNumber(0, 0))
            return version;
    }
    return QVersionNumber();
}

// Format a documentation reference (meth/attr): ":meth:`name<target>`"
// We do not use the short form ":meth:`~target`" since that adds parentheses ()
// for functions where we list the parameters instead.
struct docRef
{
    explicit docRef(const char *kind, const QString &name,
                    const AbstractMetaClassCPtr &cppClass) :
        m_kind(kind), m_name(name), m_cppClass(cppClass) {}

    const char *m_kind;
    const QString &m_name;
    const AbstractMetaClassCPtr m_cppClass;
};

static TextStream &operator<<(TextStream &s, const docRef &dr)
{
    QString className = dr.m_cppClass->fullName();
    className.replace(u"::"_s, u"."_s);
    s << ':' << dr.m_kind << ":`" << dr.m_name << '<';
    if (!dr.m_name.startsWith(className))
        s << className << '.';
    s << dr.m_name << ">`";
    return s;
}

// Format a short documentation reference (automatically dropping the prefix
// by using '~'), usable for property/attributes ("attr").
struct shortDocRef
{
    explicit shortDocRef(const char *kind, const QString &target) :
        m_kind(kind), m_target(target) {}

    const char *m_kind;
    const QString &m_target;
};

static TextStream &operator<<(TextStream &s, const shortDocRef &sdr)
{
    s << ':' << sdr.m_kind << ":`~" << sdr.m_target << '`';
    return s;
}

struct functionRef : public docRef
{
    explicit functionRef(const QString &name, const AbstractMetaClassCPtr &cppClass) :
        docRef("meth", name, cppClass) {}
};

struct functionTocEntry // Format a TOC entry for a function
{
    explicit functionTocEntry(const AbstractMetaFunctionCPtr& func,
                              const AbstractMetaClassCPtr &cppClass) :
        m_func(func), m_cppClass(cppClass) {}

    AbstractMetaFunctionCPtr m_func;
    const AbstractMetaClassCPtr m_cppClass;
};

static TextStream &operator<<(TextStream &s, const functionTocEntry &ft)
{
    s << functionRef(QtDocGenerator::getFuncName(ft.m_func), ft.m_cppClass)
        << ' ' << QtDocGenerator::formatArgs(ft.m_func);
    return s;
}

struct propRef : public shortDocRef // Attribute/property (short) reference
{
    explicit propRef(const QString &target) :
        shortDocRef("attr", target) {}
};

QtDocGenerator::QtDocGenerator()
{
    m_parameters.snippetComparison =
        ReportHandler::debugLevel() >= ReportHandler::FullDebug;
}

QtDocGenerator::~QtDocGenerator() = default;

QString QtDocGenerator::fileNameSuffix()
{
    return u".rst"_s;
}

bool QtDocGenerator::shouldGenerate(const TypeEntryCPtr &te) const
{
    return Generator::shouldGenerate(te)
        && te->type() != TypeEntry::SmartPointerType;
}

QString QtDocGenerator::fileNameForContext(const GeneratorContext &context) const
{
    return fileNameForContextHelper(context, fileNameSuffix(),
                                    FileNameFlag::UnqualifiedName
                                    | FileNameFlag::KeepCase);
}

void QtDocGenerator::writeFormattedBriefText(TextStream &s, const Documentation &doc,
                                             const AbstractMetaClassCPtr &metaclass) const
{
    writeFormattedText(s, doc.brief(), doc.format(), metaclass);
}

void QtDocGenerator::writeFormattedDetailedText(TextStream &s, const Documentation &doc,
                                                const AbstractMetaClassCPtr &metaclass) const
{
    writeFormattedText(s, doc.detailed(), doc.format(), metaclass);
}

void QtDocGenerator::writeFormattedText(TextStream &s, const QString &doc,
                                        Documentation::Format format,
                                        const AbstractMetaClassCPtr &metaClass) const
{
    QString metaClassName;

    if (metaClass)
        metaClassName = metaClass->fullName();

    if (format == Documentation::Native) {
        QtXmlToSphinx x(this, m_parameters, doc, metaClassName);
        s << x;
    } else {
        const auto lines = QStringView{doc}.split(u'\n');
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

static void writeInheritedByList(TextStream &s, const AbstractMetaClassCPtr &metaClass,
                                 const AbstractMetaClassCList& allClasses)
{
    AbstractMetaClassCList res;
    for (const auto &c : allClasses) {
        if (c != metaClass && inheritsFrom(c, metaClass))
            res << c;
    }

    if (res.isEmpty())
        return;

    s << "**Inherited by:** ";
    QStringList classes;
    for (const auto &c : std::as_const(res))
        classes << u":ref:`"_s + c->name() + u'`';
    s << classes.join(u", "_s) << "\n\n";
}

void QtDocGenerator::generateClass(TextStream &s, const GeneratorContext &classContext)
{
    AbstractMetaClassCPtr metaClass = classContext.metaClass();
    qCDebug(lcShibokenDoc).noquote().nospace() << "Generating Documentation for " << metaClass->fullName();

    m_packages[metaClass->package()] << fileNameForContext(classContext);

    m_docParser->setPackageName(metaClass->package());
    m_docParser->fillDocumentation(std::const_pointer_cast<AbstractMetaClass>(metaClass));

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

    const GeneratorDocumentation doc = generatorDocumentation(metaClass);

    if (!doc.allFunctions.isEmpty() || !doc.properties.isEmpty()) {
        s << "\nSynopsis\n--------\n\n";
        writePropertyToc(s, doc, metaClass);
        writeFunctionToc(s, u"Functions"_s, metaClass, doc.tocNormalFunctions);
        writeFunctionToc(s, u"Virtual functions"_s, metaClass, doc.tocVirtuals);
        writeFunctionToc(s, u"Slots"_s, metaClass, doc.tocSlotFunctions);
        writeFunctionToc(s, u"Signals"_s, metaClass, doc.tocSignalFunctions);
        writeFunctionToc(s, u"Static functions"_s, metaClass, doc.tocStaticFunctions);
    }

    s << "\n.. note::\n"
         "    This documentation may contain snippets that were automatically\n"
         "    translated from C++ to Python. We always welcome contributions\n"
         "    to the snippet translation. If you see an issue with the\n"
         "    translation, you can also let us know by creating a ticket on\n"
         "    https:/bugreports.qt.io/projects/PYSIDE\n\n";

    s << "\nDetailed Description\n"
           "--------------------\n\n"
        << ".. _More:\n";

    writeInjectDocumentation(s, TypeSystem::DocModificationPrepend, metaClass, nullptr);
    if (!writeInjectDocumentation(s, TypeSystem::DocModificationReplace, metaClass, nullptr))
        writeFormattedDetailedText(s, documentation, metaClass);

    if (!metaClass->isNamespace())
        writeConstructors(s, metaClass, doc.constructors);

    if (!doc.properties.isEmpty())
        writeProperties(s, doc, metaClass);

    writeEnums(s, metaClass);
    if (!metaClass->isNamespace())
        writeFields(s, metaClass);

    QString lastName;
    for (const auto &func : std::as_const(doc.allFunctions)) {
        const bool indexed = func->name() != lastName;
        lastName = func->name();
        s << (func->isStatic() ? ".. py:staticmethod:: " : ".. py:method:: ");
        writeFunction(s, metaClass, func, indexed);
    }

    writeInjectDocumentation(s, TypeSystem::DocModificationAppend, metaClass, nullptr);
}

void QtDocGenerator::writeFunctionToc(TextStream &s, const QString &title,
                                      const AbstractMetaClassCPtr &cppClass,
                                      const AbstractMetaFunctionCList &functions)
{
    if (!functions.isEmpty()) {
        s << title << '\n'
          << Pad('^', title.size()) << '\n';

        s << ".. container:: function_list\n\n" << indent;
        for (const auto &func : functions)
            s << "* def " << functionTocEntry(func, cppClass) << '\n';
        s << outdent << "\n\n";
    }
}

void QtDocGenerator::writePropertyToc(TextStream &s,
                                      const GeneratorDocumentation &doc,
                                      const AbstractMetaClassCPtr &cppClass)
{
    if (doc.properties.isEmpty())
        return;

    const QString title = u"Properties"_s;
    s << title << '\n'
      << Pad('^', title.size()) << '\n';

    s << ".. container:: function_list\n\n" << indent;
    for (const auto &prop : doc.properties) {
        s << "* " << propRef(propertyRefTarget(cppClass, prop.name));
        if (prop.documentation.hasBrief())
            s << " - " << prop.documentation.brief();
        s << '\n';
    }
    s << outdent << "\n\n";
}

void QtDocGenerator::writeProperties(TextStream &s,
                                     const GeneratorDocumentation &doc,
                                     const AbstractMetaClassCPtr &cppClass) const
{
    s << "\n.. note:: Properties can be used directly when "
        << "``from __feature__ import true_property`` is used or via accessor "
        << "functions otherwise.\n\n";

    for (const auto &prop : doc.properties) {
        const QString type = translateToPythonType(prop.type, cppClass, /* createRef */ false);
        s <<  ".. py:property:: " << propertyRefTarget(cppClass, prop.name)
            << "\n   :type: " << type << "\n\n\n";
        if (!prop.documentation.isEmpty())
            writeFormattedText(s, prop.documentation.detailed(), Documentation::Native, cppClass);
        s << "**Access functions:**\n";
        if (prop.getter)
            s << " * " << functionTocEntry(prop.getter, cppClass) << '\n';
        if (prop.setter)
            s << " * " << functionTocEntry(prop.setter, cppClass) << '\n';
        if (prop.reset)
            s << " * " << functionTocEntry(prop.reset, cppClass) << '\n';
        if (prop.notify)
            s << " * Signal " << functionTocEntry(prop.notify, cppClass) << '\n';
        s << '\n';
    }
}

void QtDocGenerator::writeEnums(TextStream &s, const AbstractMetaClassCPtr &cppClass) const
{
    static const QString section_title = u".. attribute:: "_s;

    for (const AbstractMetaEnum &en : cppClass->enums()) {
        s << section_title << cppClass->fullName() << '.' << en.name() << "\n\n";
        writeFormattedDetailedText(s, en.documentation(), cppClass);
        const auto version = versionOf(en.typeEntry());
        if (!version.isNull())
            s << rstVersionAdded(version);
    }

}

void QtDocGenerator::writeFields(TextStream &s, const AbstractMetaClassCPtr &cppClass) const
{
    static const QString section_title = u".. attribute:: "_s;

    for (const AbstractMetaField &field : cppClass->fields()) {
        s << section_title << cppClass->fullName() << "." << field.name() << "\n\n";
        writeFormattedDetailedText(s, field.documentation(), cppClass);
    }
}

void QtDocGenerator::writeConstructors(TextStream &s, const AbstractMetaClassCPtr &cppClass,
                                       const AbstractMetaFunctionCList &constructors) const
{
    static const QString sectionTitle = u".. class:: "_s;

    bool first = true;
    QHash<QString, AbstractMetaArgument> arg_map;

    if (constructors.isEmpty()) {
        s << sectionTitle << cppClass->fullName();
    } else {
        QByteArray pad;
        for (const auto &func : constructors) {
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
            if (func->isDeprecated())
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

    for (const auto &func : constructors)
        writeFormattedDetailedText(s, func->documentation(), cppClass);
}

QString QtDocGenerator::formatArgs(const AbstractMetaFunctionCPtr &func)
{
    QString ret = u"("_s;
    int optArgs = 0;

    const AbstractMetaArgumentList &arguments = func->arguments();
    for (const AbstractMetaArgument &arg : arguments) {

        if (arg.isModifiedRemoved())
            continue;

        bool thisIsoptional = !arg.defaultValueExpression().isEmpty();
        if (optArgs || thisIsoptional) {
            ret += u'[';
            optArgs++;
        }

        if (arg.argumentIndex() > 0)
            ret += u", "_s;

        ret += arg.name();

        if (thisIsoptional) {
            QString defValue = arg.defaultValueExpression();
            if (defValue == u"QString()") {
                defValue = u"\"\""_s;
            } else if (defValue == u"QStringList()"
                       || defValue.startsWith(u"QVector")
                       || defValue.startsWith(u"QList")) {
                defValue = u"list()"_s;
            } else if (defValue == u"QVariant()") {
                defValue = none();
            } else {
                defValue.replace(u"::"_s, u"."_s);
                if (defValue == u"nullptr")
                    defValue = none();
                else if (defValue == u"0" && arg.type().isObject())
                    defValue = none();
            }
            ret += u'=' + defValue;
        }
    }

    ret += QString(optArgs, u']') + u')';
    return ret;
}

void QtDocGenerator::writeDocSnips(TextStream &s,
                                 const CodeSnipList &codeSnips,
                                 TypeSystem::CodeSnipPosition position,
                                 TypeSystem::Language language)
{
    Indentation indentation(s);
    static const QStringList invalidStrings{u"*"_s, u"//"_s, u"/*"_s, u"*/"_s};
    const static QString startMarkup = u"[sphinx-begin]"_s;
    const static QString endMarkup = u"[sphinx-end]"_s;

    for (const CodeSnip &snip : codeSnips) {
        if ((snip.position != position) ||
            !(snip.language & language))
            continue;

        QString code = snip.code();
        while (code.contains(startMarkup) && code.contains(endMarkup)) {
            const auto startBlock = code.indexOf(startMarkup) + startMarkup.size();
            const auto endBlock = code.indexOf(endMarkup);

            if ((startBlock == -1) || (endBlock == -1))
                break;

            QString codeBlock = code.mid(startBlock, endBlock - startBlock);
            const QStringList rows = codeBlock.split(u'\n');
            int currentRow = 0;
            qsizetype offset = 0;

            for (QString row : rows) {
                for (const QString &invalidString : std::as_const(invalidStrings))
                    row.remove(invalidString);

                if (row.trimmed().size() == 0) {
                    if (currentRow == 0)
                        continue;
                    s << '\n';
                }

                if (currentRow == 0) {
                    //find offset
                    for (auto c : row) {
                        if (c == u' ')
                            offset++;
                        else if (c == u'\n')
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

bool QtDocGenerator::writeInjectDocumentation(TextStream &s,
                                            TypeSystem::DocModificationMode mode,
                                            const AbstractMetaClassCPtr &cppClass,
                                            const AbstractMetaFunctionCPtr &func)
{
    Indentation indentation(s);
    bool didSomething = false;

    const DocModificationList mods = DocParser::getDocModifications(cppClass, func);

    for (const DocModification &mod : mods) {
        if (mod.mode() == mode) {
            switch (mod.format()) {
            case TypeSystem::NativeCode:
                writeFormattedText(s, mod.code(), Documentation::Native, cppClass);
                didSomething = true;
                break;
            case TypeSystem::TargetLangCode:
                writeFormattedText(s, mod.code(), Documentation::Target, cppClass);
                didSomething = true;
                break;
            default:
                break;
            }
        }
    }

    s << '\n';

    // FIXME PYSIDE-7: Deprecate the use of doc string on glue code.
    //       This is pre "add-function" and "inject-documentation" tags.
    const TypeSystem::CodeSnipPosition pos = mode == TypeSystem::DocModificationPrepend
        ? TypeSystem::CodeSnipPositionBeginning : TypeSystem::CodeSnipPositionEnd;
    if (func)
        writeDocSnips(s, func->injectedCodeSnips(), pos, TypeSystem::TargetLangCode);
    else
        writeDocSnips(s, cppClass->typeEntry()->codeSnips(), pos, TypeSystem::TargetLangCode);
    return didSomething;
}

QString QtDocGenerator::functionSignature(const AbstractMetaClassCPtr &cppClass,
                                          const AbstractMetaFunctionCPtr &func)
{
    QString funcName = cppClass->fullName();
    if (!func->isConstructor())
        funcName += u'.' + getFuncName(func);

    return funcName + formatArgs(func);
}

QString QtDocGenerator::translateToPythonType(const AbstractMetaType &type,
                                              const AbstractMetaClassCPtr &cppClass,
                                              bool createRef) const
{
    static const QStringList nativeTypes =
        {boolT(), floatT(), intT(), pyObjectT(), pyStrT()};

    const QString name = type.name();
    if (nativeTypes.contains(name))
        return name;

    static const QMap<QString, QString> typeMap = {
        { cPyObjectT(), pyObjectT() },
        { qStringT(), pyStrT() },
        { u"uchar"_s, pyStrT() },
        { u"QStringList"_s, u"list of strings"_s },
        { qVariantT(), pyObjectT() },
        { u"quint32"_s, intT() },
        { u"uint32_t"_s, intT() },
        { u"quint64"_s, intT() },
        { u"qint64"_s, intT() },
        { u"size_t"_s, intT() },
        { u"int64_t"_s, intT() },
        { u"qreal"_s, floatT() }
    };
    const auto found = typeMap.find(name);
    if (found != typeMap.end())
        return found.value();

    QString strType;
    if (type.isConstant() && name == u"char" && type.indirections() == 1) {
        strType = u"str"_s;
    } else if (name.startsWith(unsignedShortT())) {
        strType = intT();
    } else if (name.startsWith(unsignedT())) { // uint and ulong
        strType = intT();
    } else if (type.isContainer()) {
        QString strType = translateType(type, cppClass, Options(ExcludeConst) | ExcludeReference);
        strType.remove(u'*');
        strType.remove(u'>');
        strType.remove(u'<');
        strType.replace(u"::"_s, u"."_s);
        if (strType.contains(u"QList") || strType.contains(u"QVector")) {
            strType.replace(u"QList"_s, u"list of "_s);
            strType.replace(u"QVector"_s, u"list of "_s);
        } else if (strType.contains(u"QHash") || strType.contains(u"QMap")) {
            strType.remove(u"QHash"_s);
            strType.remove(u"QMap"_s);
            QStringList types = strType.split(u',');
            strType = QString::fromLatin1("Dictionary with keys of type %1 and values of type %2.")
                                         .arg(types[0], types[1]);
        }
    } else {
        auto k = AbstractMetaClass::findClass(api().classes(), type.typeEntry());
        strType = k ? k->fullName() : type.name();
        if (createRef) {
            strType.prepend(u":any:`"_s);
            strType.append(u'`');
        }
    }
    return strType;
}

QString QtDocGenerator::getFuncName(const AbstractMetaFunctionCPtr &cppFunc)
{
    QString result = cppFunc->name();
    if (cppFunc->isOperatorOverload()) {
        const QString pythonOperator = Generator::pythonOperatorFunctionName(result);
        if (!pythonOperator.isEmpty())
            return pythonOperator;
    }
    result.replace(u"::"_s, u"."_s);
    return result;
}

void QtDocGenerator::writeParameterType(TextStream &s,
                                        const AbstractMetaClassCPtr &cppClass,
                                        const AbstractMetaArgument &arg) const
{
    s << ":param " << arg.name() << ": "
      << translateToPythonType(arg.type(), cppClass) << '\n';
}

void QtDocGenerator::writeFunctionParametersType(TextStream &s,
                                                 const AbstractMetaClassCPtr &cppClass,
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

void QtDocGenerator::writeFunction(TextStream &s, const AbstractMetaClassCPtr &cppClass,
                                   const AbstractMetaFunctionCPtr &func, bool indexed)
{
    s << functionSignature(cppClass, func);

    {
        Indentation indentation(s);
        if (!indexed)
            s << "\n:noindex:";
        if (func->attributes().testFlag(AbstractMetaFunction::Attribute::FinalCppMethod))
            s << "\n:final:";
        else if (func->isAbstract())
            s << "\n:abstractmethod:";
        s << "\n\n";
        writeFunctionParametersType(s, cppClass, func);
        const auto version = versionOf(func->typeEntry());
        if (!version.isNull())
            s << rstVersionAdded(version);
        if (func->isDeprecated())
            s << rstDeprecationNote("function");
    }
    writeInjectDocumentation(s, TypeSystem::DocModificationPrepend, cppClass, func);
    if (!writeInjectDocumentation(s, TypeSystem::DocModificationReplace, cppClass, func)) {
        writeFormattedBriefText(s, func->documentation(), cppClass);
        writeFormattedDetailedText(s, func->documentation(), cppClass);
    }
    writeInjectDocumentation(s, TypeSystem::DocModificationAppend, cppClass, func);

    if (auto propIndex = func->propertySpecIndex(); propIndex >= 0) {
        const QString name = cppClass->propertySpecs().at(propIndex).name();
        const QString target = propertyRefTarget(cppClass, name);
        if (func->isPropertyReader())
            s << "\nGetter of property " << propRef(target) << " .\n\n";
        else if (func->isPropertyWriter())
            s << "\nSetter of property " << propRef(target) << " .\n\n";
        else if (func->isPropertyResetter())
            s << "\nReset function of property " << propRef(target) << " .\n\n";
        else if (func->attributes().testFlag(AbstractMetaFunction::Attribute::PropertyNotify))
            s << "\nNotification signal of property " << propRef(target) << " .\n\n";
    }
}

static void writeFancyToc(TextStream& s, const QStringList& items)
{
    using TocMap = QMap<QChar, QStringList>;
    TocMap tocMap;
    QChar idx;
    for (QString item : items) {
        if (item.isEmpty())
            continue;
        item.chop(4); // Remove the .rst extension
        // skip namespace if necessary
        const QString className = item.split(u'.').last();
        if (className.startsWith(u'Q') && className.length() > 1)
            idx = className[1];
        else
            idx = className[0];
        tocMap[idx] << item;
    }

    static const qsizetype numColumns = 4;

    QtXmlToSphinx::Table table;
    for (auto it = tocMap.cbegin(), end = tocMap.cend(); it != end; ++it) {
        QtXmlToSphinx::TableRow row;
        const QString charEntry = u"**"_s + it.key() + u"**"_s;
        row << QtXmlToSphinx::TableCell(charEntry);
        for (const QString &item : std::as_const(it.value())) {
            if (row.size() >= numColumns) {
                table.appendRow(row);
                row.clear();
                row << QtXmlToSphinx::TableCell(QString{});
            }
            const QString entry = u"* :doc:`"_s + item + u'`';
            row << QtXmlToSphinx::TableCell(entry);
        }
        if (row.size() > 1)
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
    if (!m_inheritanceFile.isEmpty() && !writeInheritanceFile())
        return false;
    return true;
}

bool QtDocGenerator::writeInheritanceFile()
{
    QFile inheritanceFile(m_inheritanceFile);
    if (!inheritanceFile.open(QIODevice::WriteOnly | QIODevice::Text))
        throw Exception(msgCannotOpenForWriting(m_inheritanceFile));

    QJsonObject dict;
    for (const auto &c : api().classes()) {
        const auto &bases = c->baseClasses();
        if (!bases.isEmpty()) {
            QJsonArray list;
            for (const auto &base : bases)
                list.append(QJsonValue(base->fullName()));
            dict[c->fullName()] = list;
        }
    }
    QJsonDocument document;
    document.setObject(dict);
    inheritanceFile.write(document.toJson(QJsonDocument::Compact));
    return true;
}

void QtDocGenerator::writeModuleDocumentation()
{
    QMap<QString, QStringList>::iterator it = m_packages.begin();
    for (; it != m_packages.end(); ++it) {
        std::sort(it.value().begin(), it.value().end());

        QString key = it.key();
        key.replace(u'.', u'/');
        QString outputDir = outputDirectory() + u'/' + key;
        FileOut output(outputDir + u"/index.rst"_s);
        TextStream& s = output.stream;

        const QString &title = it.key();
        s << ".. module:: " << title << "\n\n"
            << title << '\n'
            << Pad('*', title.length()) << "\n\n";

        // Store the it.key() in a QString so that it can be stripped off unwanted
        // information when neeeded. For example, the RST files in the extras directory
        // doesn't include the PySide# prefix in their names.
        QString moduleName = it.key();
        const int lastIndex = moduleName.lastIndexOf(u'.');
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
            const QString filter = moduleName + u".?*.rst"_s;
            const auto fileList =
                extraSectionDir.entryInfoList({filter}, QDir::Files, QDir::Name);
            for (const auto &fi : fileList) {
                // Strip to "Property.rst" in output directory
                const QString newFileName = fi.fileName().mid(moduleName.size() + 1);
                it.value().append(newFileName);
                const QString newFilePath = outputDir + u'/' + newFileName;
                if (QFile::exists(newFilePath))
                    QFile::remove(newFilePath);
                if (!QFile::copy(fi.absoluteFilePath(), newFilePath)) {
                    qCDebug(lcShibokenDoc).noquote().nospace() << "Error copying extra doc "
                        << QDir::toNativeSeparators(fi.absoluteFilePath())
                        << " to " << QDir::toNativeSeparators(newFilePath);
                }
            }
        }

        s << ".. container:: hide\n\n" << indent
            << ".. toctree::\n" << indent
            << ":maxdepth: 1\n\n";
        for (const QString &className : std::as_const(it.value()))
            s << className << '\n';
        s << "\n\n" << outdent << outdent
            << "Detailed Description\n--------------------\n\n";

        // module doc is always wrong and C++istic, so go straight to the extra directory!
        QFile moduleDoc(m_extraSectionDir + u'/' + moduleName
                        + u".rst"_s);
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

        s << "\nList of Classes\n"
            << "---------------\n\n";
        writeFancyToc(s, it.value());

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
        if (line.size() > 2 && line.startsWith(u'[') && line.endsWith(u']')) {
            const QString dir = line.mid(1, line.size() - 2);
            if (dir.isEmpty() || dir == u".") {
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
            QFileInfo fi(m_parameters.docDataDir + u'/' + line);
            if (fi.isFile()) {
                const QString rstFileName = fi.baseName() + rstSuffix;
                const QString rstFile = targetDir + u'/' + rstFileName;
                const QString context = targetDir.mid(targetDir.lastIndexOf(u'/') + 1);
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
        {u"doc-parser=<parser>"_s,
         u"The documentation parser used to interpret the documentation\n"
          "input files (qdoc|doxygen)"_s},
        {u"documentation-code-snippets-dir=<dir>"_s,
         u"Directory used to search code snippets used by the documentation"_s},
        {u"snippets-path-rewrite=old:new"_s,
         u"Replacements in code snippet path to find .cpp/.h snippets converted to Python"_s},
        {u"documentation-data-dir=<dir>"_s,
         u"Directory with XML files generated by documentation tool"_s},
        {u"documentation-extra-sections-dir=<dir>"_s,
         u"Directory used to search for extra documentation sections"_s},
        {u"library-source-dir=<dir>"_s,
         u"Directory where library source code is located"_s},
        {additionalDocumentationOption() + u"=<file>"_s,
         u"List of additional XML files to be converted to .rst files\n"
          "(for example, tutorials)."_s},
        {u"inheritance-file=<file>"_s,
         u"Generate a JSON file containing the class inheritance."_s}

    });
    return result;
}

bool QtDocGenerator::handleOption(const QString &key, const QString &value)
{
    if (Generator::handleOption(key, value))
        return true;
    if (key == u"library-source-dir") {
        m_parameters.libSourceDir = value;
        return true;
    }
    if (key == u"documentation-data-dir") {
        m_parameters.docDataDir = value;
        return true;
    }
    if (key == u"documentation-code-snippets-dir") {
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

    if (key == u"documentation-extra-sections-dir") {
        m_extraSectionDir = value;
        return true;
    }
    if (key == u"doc-parser") {
        qCDebug(lcShibokenDoc).noquote().nospace() << "doc-parser: " << value;
        if (value == u"doxygen")
            m_docParser.reset(new DoxygenParser);
        return true;
    }
    if (key == additionalDocumentationOption()) {
        m_additionalDocumentationList = value;
        return true;
    }

    if (key == u"inheritance-file") {
        m_inheritanceFile = value;
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

GeneratorDocumentation
    QtDocGenerator::generatorDocumentation(const AbstractMetaClassCPtr &cppClass) const
{
    GeneratorDocumentation result;
    const auto allFunctions = cppClass->functions();
    result.allFunctions.reserve(allFunctions.size());
    for (const auto &func : allFunctions) {
        if (!shouldSkip(func)) {
            if (func->isConstructor())
                result.constructors.append(func);
            else
                result.allFunctions.append(func);
        }
    }

    std::sort(result.allFunctions.begin(), result.allFunctions.end(), functionSort);

    for (const auto &func : std::as_const(result.allFunctions)) {
        if (func->isStatic())
            result.tocStaticFunctions.append(func);
        else if (func->isVirtual())
            result.tocVirtuals.append(func);
        else if (func->isSignal())
            result.tocSignalFunctions.append(func);
        else if (func->isSlot())
            result.tocSlotFunctions.append(func);
        else
            result.tocNormalFunctions.append(func);
    }

    // Find the property getters/setters
    for (const auto &spec: cppClass->propertySpecs()) {
        GeneratorDocumentation::Property property;
        property.name = spec.name();
        property.type = spec.type();
        property.documentation = spec.documentation();
        if (!spec.read().isEmpty())
            property.getter = AbstractMetaFunction::find(result.allFunctions, spec.read());
        if (!spec.write().isEmpty())
            property.setter = AbstractMetaFunction::find(result.allFunctions, spec.write());
        if (!spec.reset().isEmpty())
            property.reset = AbstractMetaFunction::find(result.allFunctions, spec.reset());
        if (!spec.notify().isEmpty())
            property.notify = AbstractMetaFunction::find(result.tocSignalFunctions, spec.notify());
        result.properties.append(property);
    }
    std::sort(result.properties.begin(), result.properties.end());

    return result;
}

// QtXmlToSphinxDocGeneratorInterface
QString QtDocGenerator::expandFunction(const QString &function) const
{
    const int firstDot = function.indexOf(u'.');
    AbstractMetaClassCPtr metaClass;
    if (firstDot != -1) {
        const auto className = QStringView{function}.left(firstDot);
        for (const auto &cls : api().classes()) {
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
    const auto rawlinklist = QStringView{name}.split(u'.');
    QStringList splittedContext = context.split(u'.');
    if (rawlinklist.size() == 1 || rawlinklist.constFirst() == splittedContext.constLast()) {
        splittedContext.removeLast();
        result.prepend(u'~' + splittedContext.join(u'.') + u'.');
    }
    return result;
}

QString QtDocGenerator::resolveContextForMethod(const QString &context,
                                                const QString &methodName) const
{
    const auto currentClass = QStringView{context}.split(u'.').constLast();

    AbstractMetaClassCPtr metaClass;
    for (const auto &cls : api().classes()) {
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

        AbstractMetaClassCPtr implementingClass;
        for (const auto &func : std::as_const(funcList)) {
            implementingClass = func->implementingClass();
            if (implementingClass->name() == currentClass)
                break;
        }

        if (implementingClass)
            return implementingClass->typeEntry()->qualifiedTargetLangName();
    }

    return u'~' + context;
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
        + QString::number(QT_VERSION_MAJOR) + u'/';
    QtXmlToSphinxLink resolved = link;
    resolved.type = QtXmlToSphinxLink::External;
    resolved.linkRef = prefix + link.linkRef;
    if (resolved.linkText.isEmpty()) {
        resolved.linkText = link.linkRef;
        const qsizetype anchor = resolved.linkText.lastIndexOf(u'#');
        if (anchor != -1)
            resolved.linkText.truncate(anchor);
    }
    return resolved;
}
