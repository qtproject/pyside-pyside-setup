// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <abstractmetabuilder_p.h>
#include <parser/codemodel.h>
#include <clangparser/compilersupport.h>

#include <QtCore/QCoreApplication>
#include <QtCore/QCommandLineOption>
#include <QtCore/QCommandLineParser>
#include <QtCore/QDateTime>
#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QLibraryInfo>
#include <QtCore/QVersionNumber>
#include <QtCore/QXmlStreamWriter>

#include <iostream>
#include <algorithm>
#include <iterator>

using namespace Qt::StringLiterals;

static bool optJoinNamespaces = false;

static inline QString languageLevelDescription()
{
    return u"C++ Language level (c++11..c++20, default="_s
        + QLatin1StringView(clang::languageLevelOption(clang::emulatedCompilerLanguageLevel()))
        + u')';
}

static void formatDebugOutput(const FileModelItem &dom, bool verbose)
{
    QString output;
    {
        QDebug debug(&output);
        if (verbose)
            debug.setVerbosity(3);
        debug << dom.get();
    }
    std::cout << qPrintable(output) << '\n';
}

static const char *primitiveTypes[] = {
    "int", "unsigned", "short", "unsigned short", "long", "unsigned long",
    "float", "double"
};

static inline QString nameAttribute() { return QStringLiteral("name"); }

static void formatXmlClass(QXmlStreamWriter &writer, const ClassModelItem &klass);

static void formatXmlEnum(QXmlStreamWriter &writer, const EnumModelItem &en)
{
    writer.writeStartElement(u"enum-type"_s);
    writer.writeAttribute(nameAttribute(), en->name());
    writer.writeEndElement();
}

static bool useClass(const ClassModelItem &c)
{
    return c->classType() != CodeModel::Union && c->templateParameters().isEmpty()
        && !c->name().isEmpty(); // No anonymous structs
}

static void formatXmlScopeMembers(QXmlStreamWriter &writer, const ScopeModelItem &nsp)
{
    for (const auto &klass : nsp->classes()) {
        if (useClass(klass))
            formatXmlClass(writer, klass);
    }
    for (const auto &en : nsp->enums())
        formatXmlEnum(writer, en);
}

static bool isPublicCopyConstructor(const FunctionModelItem &f)
{
    return f->functionType() == CodeModel::CopyConstructor
        && f->accessPolicy() == Access::Public && !f->isDeleted();
}

static void formatXmlLocationComment(QXmlStreamWriter &writer, const CodeModelItem &i)
{
    QString comment;
    QTextStream(&comment) << ' ' << i->fileName() << ':' << i->startLine() << ' ';
    writer.writeComment(comment);
}

static void formatXmlClass(QXmlStreamWriter &writer, const ClassModelItem &klass)
{
    // Heuristics for value types: check on public copy constructors.
    const auto functions = klass->functions();
    const bool isValueType = std::any_of(functions.cbegin(), functions.cend(),
                                         isPublicCopyConstructor);
    formatXmlLocationComment(writer, klass);
    writer.writeStartElement(isValueType ? u"value-type"_s
                                         : u"object-type"_s);
    writer.writeAttribute(nameAttribute(), klass->name());
    formatXmlScopeMembers(writer, klass);
    writer.writeEndElement();
}

// Check whether a namespace is relevant for type system
// output, that is, has non template classes, functions or enumerations.
static bool hasMembers(const NamespaceModelItem &nsp)
{
    if (!nsp->namespaces().isEmpty() || !nsp->enums().isEmpty()
        || !nsp->functions().isEmpty()) {
        return true;
    }
    const auto classes = nsp->classes();
    return std::any_of(classes.cbegin(), classes.cend(), useClass);
}

static void startXmlNamespace(QXmlStreamWriter &writer, const NamespaceModelItem &nsp)
{
    formatXmlLocationComment(writer, nsp);
    writer.writeStartElement(u"namespace-type"_s);
    writer.writeAttribute(nameAttribute(), nsp->name());
}

static void formatXmlNamespaceMembers(QXmlStreamWriter &writer, const NamespaceModelItem &nsp)
{
    auto nestedNamespaces = nsp->namespaces();
    for (auto i = nestedNamespaces.size() - 1; i >= 0; --i) {
        if (!hasMembers(nestedNamespaces.at(i)))
            nestedNamespaces.removeAt(i);
    }
    while (!nestedNamespaces.isEmpty()) {
        auto current = nestedNamespaces.takeFirst();
        startXmlNamespace(writer, current);
        formatXmlNamespaceMembers(writer, current);
        if (optJoinNamespaces) {
            // Write out members of identical namespaces and remove
            const QString name = current->name();
            for (qsizetype i = 0; i < nestedNamespaces.size(); ) {
                if (nestedNamespaces.at(i)->name() == name) {
                    formatXmlNamespaceMembers(writer, nestedNamespaces.at(i));
                    nestedNamespaces.removeAt(i);
                } else {
                    ++i;
                }
            }
        }
        writer.writeEndElement();
    }

    for (const auto &func : nsp->functions()) {
        const QString signature = func->typeSystemSignature();
        if (!signature.contains(u"operator")) { // Skip free operators
            writer.writeStartElement(u"function"_s);
            writer.writeAttribute(u"signature"_s, signature);
            writer.writeEndElement();
        }
    }
    formatXmlScopeMembers(writer, nsp);
}

static void formatXmlOutput(const FileModelItem &dom)
{
    QString output;
    QXmlStreamWriter writer(&output);
    writer.setAutoFormatting(true);
    writer.writeStartDocument();
    writer.writeStartElement(u"typesystem"_s);
    writer.writeAttribute(u"package"_s, u"insert_name"_s);
    writer.writeComment(u"Auto-generated "_s +
                        QDateTime::currentDateTime().toString(Qt::ISODate));
    for (auto p : primitiveTypes) {
        writer.writeStartElement(u"primitive-type"_s);
        writer.writeAttribute(nameAttribute(), QLatin1StringView(p));
        writer.writeEndElement();
    }
    formatXmlNamespaceMembers(writer, dom);
    writer.writeEndElement();
    writer.writeEndDocument();
    std::cout << qPrintable(output) << '\n';
}

static const char descriptionFormat[] = R"(
Type system dumper

Parses a C++ header and dumps out the classes found in typesystem XML syntax.
Arguments are arguments to the compiler the last of which should be the header
or source file.
It is recommended to create a .hh include file including the desired headers
and pass that along with the required include paths.

Based on Qt %1 and LibClang v%2.)";

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);

    QCommandLineParser parser;
    parser.setSingleDashWordOptionMode(QCommandLineParser::ParseAsLongOptions);
    parser.setOptionsAfterPositionalArgumentsMode(QCommandLineParser::ParseAsPositionalArguments);
    const QString description =
        QString::fromLatin1(descriptionFormat).arg(QLatin1StringView(qVersion()),
                                                   clang::libClangVersion().toString());
    parser.setApplicationDescription(description);
    parser.addHelpOption();
    parser.addVersionOption();
    QCommandLineOption verboseOption(u"verbose"_s,
                                     u"Display verbose output about types"_s);
    parser.addOption(verboseOption);
    QCommandLineOption debugOption(u"debug"_s,
                                     u"Display debug output"_s);
    parser.addOption(debugOption);

    QCommandLineOption joinNamespacesOption({u"j"_s, u"join-namespaces"_s},
                                            u"Join namespaces"_s);
    parser.addOption(joinNamespacesOption);

    QCommandLineOption languageLevelOption(u"std"_s,
                                           languageLevelDescription(),
                                           u"level"_s);
    parser.addOption(languageLevelOption);
    parser.addPositionalArgument(u"argument"_s,
                                 u"C++ compiler argument"_s,
                                 u"argument(s)"_s);

    parser.process(app);
    const QStringList &positionalArguments = parser.positionalArguments();
    if (positionalArguments.isEmpty())
        parser.showHelp(1);

    QByteArrayList arguments;
    std::transform(positionalArguments.cbegin(), positionalArguments.cend(),
                   std::back_inserter(arguments), QFile::encodeName);

    LanguageLevel level = LanguageLevel::Default;
    if (parser.isSet(languageLevelOption)) {
        const QByteArray value = parser.value(languageLevelOption).toLatin1();
        level = clang::languageLevelFromOption(value.constData());
        if (level == LanguageLevel::Default) {
            std::cerr << "Invalid value \"" << value.constData()
                << "\" for language level option.\n";
            return -2;
        }
    }

    optJoinNamespaces = parser.isSet(joinNamespacesOption);

    const FileModelItem dom = AbstractMetaBuilderPrivate::buildDom(arguments, true, level, 0);
    if (!dom) {
        QString message = u"Unable to parse "_s + positionalArguments.join(u' ');
        std::cerr << qPrintable(message) << '\n';
        return -2;
    }

    if (parser.isSet(debugOption))
        formatDebugOutput(dom, parser.isSet(verboseOption));
    else
        formatXmlOutput(dom);

    return 0;
}
