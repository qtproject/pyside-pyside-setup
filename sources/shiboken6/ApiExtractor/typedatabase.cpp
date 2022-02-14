/****************************************************************************
**
** Copyright (C) 2019 The Qt Company Ltd.
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

#include "typedatabase.h"
#include "abstractmetatype.h"
#include "exception.h"
#include "typesystem.h"
#include "typesystemparser.h"
#include "conditionalstreamreader.h"
#include "predefined_templates.h"
#include "clangparser/compilersupport.h"

#include <QtCore/QBuffer>
#include <QtCore/QFile>
#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QPair>
#include <QtCore/QList>
#include <QtCore/QRegularExpression>
#include <QtCore/QVersionNumber>
#include <QtCore/QXmlStreamReader>
#include "reporthandler.h"
// #include <tr1/tuple>
#include <algorithm>

// package -> api-version

static QString wildcardToRegExp(QString w)
{
    w.replace(QLatin1Char('?'), QLatin1Char('.'));
    w.replace(QLatin1Char('*'), QStringLiteral(".*"));
    return w;
}

using ApiVersion =QPair<QRegularExpression, QVersionNumber>;
using ApiVersions = QList<ApiVersion>;

Q_GLOBAL_STATIC(ApiVersions, apiVersions)

struct PythonType
{
    QString name;
    QString checkFunction;
    TypeSystem::CPythonType type;
};

using PythonTypes = QList<PythonType>;

static const PythonTypes &builtinPythonTypes()
{
    static const PythonTypes result{
        // "Traditional" custom types
        // numpy
        {u"PyArrayObject"_qs, u"PyArray_Check"_qs, TypeSystem::CPythonType::Other},
        {u"PyBuffer"_qs, u"Shiboken::Buffer::checkType"_qs, TypeSystem::CPythonType::Other},
        {u"PyByteArray"_qs, u"PyByteArray_Check"_qs, TypeSystem::CPythonType::Other},
        {u"PyBytes"_qs, u"PyBytes_Check"_qs, TypeSystem::CPythonType::Other},
        {u"PyCallable"_qs, u"PyCallable_Check"_qs, TypeSystem::CPythonType::Other},
        {u"PyDate"_qs, u"PyDate_Check"_qs, TypeSystem::CPythonType::Other},
        {u"PyDateTime"_qs, u"PyDateTime_Check_Check"_qs, TypeSystem::CPythonType::Other},
        {u"PyDict"_qs, u"PyDict_Check"_qs, TypeSystem::CPythonType::Other},
        // Convenience macro in sbkconverter.h
        {u"PyObject"_qs, u"true"_qs, TypeSystem::CPythonType::Other},
        // shiboken-specific
        {u"PyPathLike"_qs, u"Shiboken::String::checkPath"_qs, TypeSystem::CPythonType::Other},
        {u"PySequence"_qs, u"Shiboken::String::checkIterable"_qs, TypeSystem::CPythonType::Other},
        {u"PyUnicode"_qs, u"PyUnicode_Check"_qs, TypeSystem::CPythonType::String},
        {u"PyTypeObject"_qs, u"PyType_Check"_qs, TypeSystem::CPythonType::Other},
        {u"str"_qs, u"Shiboken::String::check"_qs, TypeSystem::CPythonType::String},
        // Types used as target lang API types for primitive types
        {u"PyBool"_qs, u"PyBool_Check"_qs, TypeSystem::CPythonType::Bool},
        {u"PyComplex"_qs, u"PyComplex_Check"_qs, TypeSystem::CPythonType::Other},
        {u"PyLong"_qs, u"PyLong_Check"_qs, TypeSystem::CPythonType::Integer},
        {u"PyFloat"_qs, u"PyFloat_Check"_qs, TypeSystem::CPythonType::Float},
        // Single character strings to match C++ char types
        {u"SbkChar"_qs, u"SbkChar_Check"_qs, TypeSystem::CPythonType::String}
    };
    return result;
}

TypeDatabase::TypeDatabase()
{
    addBuiltInType(new VoidTypeEntry());
    addBuiltInType(new VarargsTypeEntry());
    for (const auto &pt : builtinPythonTypes())
        addBuiltInType(new PythonTypeEntry(pt.name, pt.checkFunction, pt.type));

    for (const auto &p : predefinedTemplates())
        addTemplate(p.name, p.content);
}

TypeDatabase::~TypeDatabase() = default;

TypeDatabase* TypeDatabase::instance(bool newInstance)
{
    static TypeDatabase *db = nullptr;
    if (!db || newInstance) {
        delete db;
        db = new TypeDatabase;
    }
    return db;
}

// A list of regex/replacements to fix int types like "ushort" to "unsigned short"
// unless present in TypeDatabase
struct IntTypeNormalizationEntry
{
    QRegularExpression regex;
    QString replacement;
};

using IntTypeNormalizationEntries = QList<IntTypeNormalizationEntry>;

static const IntTypeNormalizationEntries &intTypeNormalizationEntries()
{
    static IntTypeNormalizationEntries result;
    static bool firstTime = true;
    if (firstTime) {
        firstTime = false;
        for (auto t : {"char", "short", "int", "long"}) {
            const QString intType = QLatin1String(t);
            if (!TypeDatabase::instance()->findType(QLatin1Char('u') + intType)) {
                IntTypeNormalizationEntry entry;
                entry.replacement = QStringLiteral("unsigned ") + intType;
                entry.regex.setPattern(QStringLiteral("\\bu") + intType + QStringLiteral("\\b"));
                Q_ASSERT(entry.regex.isValid());
                result.append(entry);
            }
        }
    }
    return result;
}

// Normalization helpers
enum CharCategory { Space, Identifier, Other };

static CharCategory charCategory(QChar c)
{
    if (c.isSpace())
        return Space;
    if (c.isLetterOrNumber() || c == u'_')
        return Identifier;
    return Other;
}

// Normalize a C++ function signature:
// Drop space except between identifiers ("unsigned int", "const int")
static QString normalizeCppFunctionSignature(const QString &signatureIn)
{
    const QString signature = signatureIn.simplified();
    QString result;
    result.reserve(signature.size());

    CharCategory lastNonSpaceCategory = Other;
    bool pendingSpace = false;
    for (QChar c : signature) {
        if (c.isSpace()) {
            pendingSpace = true;
        } else {
            const auto category = charCategory(c);
            if (pendingSpace) {
                if (lastNonSpaceCategory == Identifier && category == Identifier)
                    result.append(u' ');
                pendingSpace = false;
            }
            lastNonSpaceCategory = category;
            result.append(c);
        }
    }
    return result;
}

// Normalize a signature for <add-function> by removing spaces
QString TypeDatabase::normalizedAddedFunctionSignature(const QString &signature)
{
    return normalizeCppFunctionSignature(signature);
}

// Normalize a signature for matching by <modify-function>/<function>
// by removing spaces and changing const-ref to value.
// FIXME: PYSIDE7: Check whether the above simple normalization can be used
// here as well. Note though that const-ref would then have to be spelled out
// in typeystem XML.
QString TypeDatabase::normalizedSignature(const QString &signature)
{
    // QMetaObject::normalizedSignature() changes const-ref to value and
    // changes "unsigned int" to "uint" which is undone by the below code
    QString normalized = QLatin1String(QMetaObject::normalizedSignature(signature.toUtf8().constData()));

    if (instance() && signature.contains(QLatin1String("unsigned"))) {
        const IntTypeNormalizationEntries &entries = intTypeNormalizationEntries();
        for (const auto &entry : entries)
            normalized.replace(entry.regex, entry.replacement);
    }

    return normalized;
}

QStringList TypeDatabase::requiredTargetImports() const
{
    return m_requiredTargetImports;
}

void TypeDatabase::addRequiredTargetImport(const QString& moduleName)
{
    if (!m_requiredTargetImports.contains(moduleName))
        m_requiredTargetImports << moduleName;
}

void TypeDatabase::addTypesystemPath(const QString& typesystem_paths)
{
    #if defined(Q_OS_WIN32)
    const char path_splitter = ';';
    #else
    const char path_splitter = ':';
    #endif
    m_typesystemPaths += typesystem_paths.split(QLatin1Char(path_splitter));
}

QStringList TypeDatabase::typesystemKeywords() const
{
    QStringList result = m_typesystemKeywords;
    for (const auto &d : m_dropTypeEntries)
        result.append(QStringLiteral("no_") + d);

    switch (clang::emulatedCompilerLanguageLevel()) {
    case LanguageLevel::Cpp11:
        result.append(u"c++11"_qs);
        break;
    case LanguageLevel::Cpp14:
        result.append(u"c++14"_qs);
        break;
    case LanguageLevel::Cpp17:
        result.append(u"c++17"_qs);
        break;
    case LanguageLevel::Cpp20:
        result.append(u"c++20"_qs);
        break;
    default:
        break;
    }
    return result;
}

IncludeList TypeDatabase::extraIncludes(const QString& className) const
{
    ComplexTypeEntry* typeEntry = findComplexType(className);
    return typeEntry ? typeEntry->extraIncludes() : IncludeList();
}

void TypeDatabase::addSystemInclude(const QString &name)
{
    m_systemIncludes.append(name);
}

// Add a lookup for the short name excluding inline namespaces
// so that "std::shared_ptr" finds "std::__1::shared_ptr" as well.
// Note: This inserts duplicate TypeEntry * into m_entries.
void TypeDatabase::addInlineNamespaceLookups(const NamespaceTypeEntry *n)
{
    TypeEntryList additionalEntries; // Store before modifying the hash
    for (TypeEntry *entry : qAsConst(m_entries)) {
        if (entry->isChildOf(n))
            additionalEntries.append(entry);
    }
    for (const auto &ae : qAsConst(additionalEntries))
        m_entries.insert(ae->shortName(), ae);
}

ContainerTypeEntry* TypeDatabase::findContainerType(const QString &name) const
{
    QString template_name = name;

    int pos = name.indexOf(QLatin1Char('<'));
    if (pos > 0)
        template_name = name.left(pos);

    TypeEntry* type_entry = findType(template_name);
    if (type_entry && type_entry->isContainer())
        return static_cast<ContainerTypeEntry*>(type_entry);
    return nullptr;
}

static bool inline useType(const TypeEntry *t)
{
    return !t->isPrimitive()
        || static_cast<const PrimitiveTypeEntry *>(t)->preferredTargetLangType();
}

FunctionTypeEntry* TypeDatabase::findFunctionType(const QString& name) const
{
    const auto entries = findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (entry->type() == TypeEntry::FunctionType && useType(entry))
            return static_cast<FunctionTypeEntry*>(entry);
    }
    return nullptr;
}

void TypeDatabase::addTypeSystemType(const TypeSystemTypeEntry *e)
{
    m_typeSystemEntries.append(e);
}

const TypeSystemTypeEntry *TypeDatabase::findTypeSystemType(const QString &name) const
{
    for (auto entry : m_typeSystemEntries) {
        if (entry->name() == name)
            return entry;
    }
    return nullptr;
}

const TypeSystemTypeEntry *TypeDatabase::defaultTypeSystemType() const
{
    return m_typeSystemEntries.value(0, nullptr);
}

QString TypeDatabase::defaultPackageName() const
{
    Q_ASSERT(!m_typeSystemEntries.isEmpty());
    return m_typeSystemEntries.constFirst()->name();
}

TypeEntry* TypeDatabase::findType(const QString& name) const
{
    const auto entries = findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (useType(entry))
            return entry;
    }
    return nullptr;
}

template <class Predicate>
TypeEntries TypeDatabase::findTypesHelper(const QString &name, Predicate pred) const
{
    TypeEntries result;
    const auto entries = findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (pred(entry))
            result.append(entry);
    }
    return result;
}

TypeEntries TypeDatabase::findTypes(const QString &name) const
{
    return findTypesHelper(name, useType);
}

static bool useCppType(const TypeEntry *t)
{
    bool result = false;
    switch (t->type()) {
    case TypeEntry::PrimitiveType:
    case TypeEntry::VoidType:
    case TypeEntry::FlagsType:
    case TypeEntry::EnumType:
    case TypeEntry::TemplateArgumentType:
    case TypeEntry::BasicValueType:
    case TypeEntry::ContainerType:
    case TypeEntry::ObjectType:
    case TypeEntry::ArrayType:
    case TypeEntry::CustomType:
    case TypeEntry::SmartPointerType:
    case TypeEntry::TypedefType:
        result = useType(t);
        break;
    default:
        break;
    }
    return result;
}

TypeEntries TypeDatabase::findCppTypes(const QString &name) const
{
    return findTypesHelper(name, useCppType);
}

TypeEntryMultiMapConstIteratorRange TypeDatabase::findTypeRange(const QString &name) const
{
    const auto range = m_entries.equal_range(name);
    return {range.first, range.second};
}

PrimitiveTypeEntryList TypeDatabase::primitiveTypes() const
{
    PrimitiveTypeEntryList returned;
    for (auto it = m_entries.cbegin(), end = m_entries.cend(); it != end; ++it) {
        TypeEntry *typeEntry = it.value();
        if (typeEntry->isPrimitive())
            returned.append(static_cast<PrimitiveTypeEntry *>(typeEntry));
    }
    return returned;
}

ContainerTypeEntryList TypeDatabase::containerTypes() const
{
    ContainerTypeEntryList returned;
    for (auto it = m_entries.cbegin(), end = m_entries.cend(); it != end; ++it) {
        TypeEntry *typeEntry = it.value();
        if (typeEntry->isContainer())
            returned.append(static_cast<ContainerTypeEntry *>(typeEntry));
    }
    return returned;
}

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const TypeRejection &r)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "TypeRejection(type=" << r.matchType << ", class="
        << r.className.pattern() << ", pattern=" << r.pattern.pattern() << ')';
    return d;
}
#endif // !QT_NO_DEBUG_STREAM

void TypeDatabase::addRejection(const TypeRejection &r)
{
    m_rejections << r;
}

static inline QString msgRejectReason(const TypeRejection &r, const QString &needle = QString())
{
    QString result;
    QTextStream str(&result);
    switch (r.matchType) {
    case TypeRejection::ExcludeClass:
        str << " matches class exclusion \"" << r.className.pattern() << '"';
        break;
    case TypeRejection::Function:
    case TypeRejection::Field:
    case TypeRejection::Enum:
        str << " matches class \"" << r.className.pattern() << "\" and \"" << r.pattern.pattern() << '"';
        break;
    case TypeRejection::ArgumentType:
    case TypeRejection::ReturnType:
        str << " matches class \"" << r.className.pattern() << "\" and \"" << needle
            << "\" matches \"" << r.pattern.pattern() << '"';
        break;
    }
    return result;
}

// Match class name only
bool TypeDatabase::isClassRejected(const QString& className, QString *reason) const
{
    for (const TypeRejection& r : m_rejections) {
        if (r.matchType == TypeRejection::ExcludeClass && r.className.match(className).hasMatch()) {
            if (reason)
                *reason = msgRejectReason(r);
            return true;
        }
    }
    return false;
}

// Match class name and function/enum/field
static bool findRejection(const QList<TypeRejection> &rejections,
                          TypeRejection::MatchType matchType,
                          const QString& className, const QString& name,
                          QString *reason = nullptr)
{
    Q_ASSERT(matchType != TypeRejection::ExcludeClass);
    for (const TypeRejection& r : rejections) {
        if (r.matchType == matchType && r.pattern.match(name).hasMatch()
            && r.className.match(className).hasMatch()) {
            if (reason)
                *reason = msgRejectReason(r, name);
            return true;
        }
    }
    return false;
}

bool TypeDatabase::isEnumRejected(const QString& className, const QString& enumName, QString *reason) const
{
    return findRejection(m_rejections, TypeRejection::Enum, className, enumName, reason);
}

TypeEntry *TypeDatabase::resolveTypeDefEntry(TypedefEntry *typedefEntry,
                                             QString *errorMessage)
{
    QString sourceName = typedefEntry->sourceType();
    const int lessThanPos = sourceName.indexOf(QLatin1Char('<'));
    if (lessThanPos != -1)
        sourceName.truncate(lessThanPos);
    ComplexTypeEntry *source = nullptr;
    for (TypeEntry *e : findTypeRange(sourceName)) {
        switch (e->type()) {
        case TypeEntry::BasicValueType:
        case TypeEntry::ContainerType:
        case TypeEntry::ObjectType:
        case TypeEntry::SmartPointerType:
            source = dynamic_cast<ComplexTypeEntry *>(e);
            Q_ASSERT(source);
            break;
        default:
            break;
        }
    }
    if (!source) {
        if (errorMessage)
            *errorMessage = QLatin1String("Unable to resolve typedef \"")
                            + typedefEntry->sourceType() + QLatin1Char('"');
        return nullptr;
    }

    auto *result = static_cast<ComplexTypeEntry *>(source->clone());
    result->useAsTypedef(typedefEntry);
    typedefEntry->setSource(source);
    typedefEntry->setTarget(result);
    m_typedefEntries.insert(typedefEntry->qualifiedCppName(), typedefEntry);
    return result;
}

bool TypeDatabase::addType(TypeEntry *e, QString *errorMessage)
{
    if (e->type() == TypeEntry::TypedefType) {
        e = resolveTypeDefEntry(static_cast<TypedefEntry *>(e), errorMessage);
        if (Q_UNLIKELY(!e))
            return false;
    }
    m_entries.insert(e->qualifiedCppName(), e);
    return true;
}

// Add a dummy value entry for non-type template parameters
ConstantValueTypeEntry *
    TypeDatabase::addConstantValueTypeEntry(const QString &value,
                                            const TypeEntry *parent)
{
    auto result = new ConstantValueTypeEntry(value, parent);
    result->setCodeGeneration(TypeEntry::GenerateNothing);
    addType(result);
    return result;
}

bool TypeDatabase::isFunctionRejected(const QString& className, const QString& functionName,
                                      QString *reason) const
{
    return findRejection(m_rejections, TypeRejection::Function, className, functionName, reason);
}

bool TypeDatabase::isFieldRejected(const QString& className, const QString& fieldName,
                                   QString *reason) const
{
    return findRejection(m_rejections, TypeRejection::Field, className, fieldName, reason);
}

bool TypeDatabase::isArgumentTypeRejected(const QString& className, const QString& typeName,
                                          QString *reason) const
{
    return findRejection(m_rejections, TypeRejection::ArgumentType, className, typeName, reason);
}

bool TypeDatabase::isReturnTypeRejected(const QString& className, const QString& typeName,
                                        QString *reason) const
{
    return findRejection(m_rejections, TypeRejection::ReturnType, className, typeName, reason);
}

FlagsTypeEntry* TypeDatabase::findFlagsType(const QString &name) const
{
    TypeEntry *fte = findType(name);
    if (!fte) {
        fte = m_flagsEntries.value(name);
        if (!fte) {
            //last hope, search for flag without scope  inside of flags hash
            for (auto it = m_flagsEntries.cbegin(), end = m_flagsEntries.cend(); it != end; ++it) {
                if (it.key().endsWith(name)) {
                    fte = it.value();
                    break;
                }
            }
        }
    }
    return static_cast<FlagsTypeEntry *>(fte);
}

void TypeDatabase::addFlagsType(FlagsTypeEntry *fte)
{
    m_flagsEntries[fte->originalName()] = fte;
}

void TypeDatabase::addTemplate(TemplateEntry *t)
{
    m_templates[t->name()] = t;
}

void TypeDatabase::addTemplate(const QString &name, const QString &code)
{
    auto *te = new TemplateEntry(name);
    te->addCode(code);
    addTemplate(te);
}

void TypeDatabase::addGlobalUserFunctions(const AddedFunctionList &functions)
{
    m_globalUserFunctions << functions;
}

AddedFunctionList TypeDatabase::findGlobalUserFunctions(const QString& name) const
{
    AddedFunctionList addedFunctions;
    for (const AddedFunctionPtr &func : m_globalUserFunctions) {
        if (func->name() == name)
            addedFunctions.append(func);
    }
    return addedFunctions;
}

void TypeDatabase::addGlobalUserFunctionModifications(const FunctionModificationList &functionModifications)
{
    m_functionMods << functionModifications;
}

QString TypeDatabase::globalNamespaceClassName(const TypeEntry * /*entry*/)
{
    return QLatin1String("Global");
}

FunctionModificationList TypeDatabase::functionModifications(const QString& signature) const
{
    FunctionModificationList lst;
    for (int i = 0; i < m_functionMods.count(); ++i) {
        const FunctionModification& mod = m_functionMods.at(i);
        if (mod.matches(signature))
            lst << mod;
    }

    return lst;
}

bool TypeDatabase::addSuppressedWarning(const QString &warning, QString *errorMessage)
{
    QString pattern;
    if (warning.startsWith(QLatin1Char('^')) && warning.endsWith(QLatin1Char('$'))) {
        pattern = warning;
    } else {
        // Legacy syntax: Use wildcards '*' (unless escaped by '\')
        QList<int> asteriskPositions;
        const int warningSize = warning.size();
        for (int i = 0; i < warningSize; ++i) {
            if (warning.at(i) == QLatin1Char('\\'))
                ++i;
            else if (warning.at(i) == QLatin1Char('*'))
                asteriskPositions.append(i);
        }
        asteriskPositions.append(warningSize);

        pattern.append(QLatin1Char('^'));
        int lastPos = 0;
        for (int a = 0, aSize = asteriskPositions.size(); a < aSize; ++a) {
            if (a)
                pattern.append(QStringLiteral(".*"));
            const int nextPos = asteriskPositions.at(a);
            if (nextPos > lastPos)
                pattern.append(QRegularExpression::escape(warning.mid(lastPos, nextPos - lastPos)));
            lastPos = nextPos + 1;
        }
        pattern.append(QLatin1Char('$'));
    }

    QRegularExpression expression(pattern);
    if (!expression.isValid()) {
        *errorMessage = QLatin1String("Invalid message pattern \"") + warning
            + QLatin1String("\": ") + expression.errorString();
        return false;
    }
    expression.setPatternOptions(expression.patternOptions() | QRegularExpression::MultilineOption);

    m_suppressedWarnings.append(expression);
    return true;
}

bool TypeDatabase::isSuppressedWarning(QStringView s) const
{
    if (!m_suppressWarnings)
        return false;
    return std::any_of(m_suppressedWarnings.cbegin(), m_suppressedWarnings.end(),
                       [&s] (const QRegularExpression &e) {
                           return e.match(s).hasMatch();
                       });
}

QString TypeDatabase::modifiedTypesystemFilepath(const QString& tsFile, const QString &currentPath) const
{
    const QFileInfo tsFi(tsFile);
    if (tsFi.isAbsolute()) // No point in further lookups
        return tsFi.absoluteFilePath();
    if (tsFi.isFile()) // Make path absolute
        return tsFi.absoluteFilePath();
    if (!currentPath.isEmpty()) {
        const QFileInfo fi(currentPath + QLatin1Char('/') + tsFile);
        if (fi.isFile())
            return fi.absoluteFilePath();
    }
    for (const QString &path : m_typesystemPaths) {
        const QFileInfo fi(path + QLatin1Char('/') + tsFile);
        if (fi.isFile())
            return fi.absoluteFilePath();
    }
    return tsFile;
}

void TypeDatabase::addBuiltInContainerTypes()
{
    // Unless the user has added the standard containers (potentially with
    // some opaque types), add them by default.
    const bool hasStdPair = findType(u"std::pair"_qs) != nullptr;
    const bool hasStdList = findType(u"std::list"_qs) != nullptr;
    const bool hasStdVector = findType(u"std::vector"_qs) != nullptr;
    const bool hasStdMap = findType(u"std::map"_qs) != nullptr;
    const bool hasStdUnorderedMap = findType(u"std::unordered_map"_qs) != nullptr;

    if (hasStdPair && hasStdList && hasStdVector && hasStdMap && hasStdUnorderedMap)
        return;

    QByteArray ts = R"(<?xml version="1.0" encoding="UTF-8"?><typesystem>)";
    if (!hasStdPair) {
        ts += containerTypeSystemSnippet(
                  "std::pair", "pair", "utility",
                  "shiboken_conversion_cpppair_to_pytuple",
                  "PySequence", "shiboken_conversion_pysequence_to_cpppair");
    }
    if (!hasStdList) {
        ts += containerTypeSystemSnippet(
                  "std::list", "list", "list",
                  "shiboken_conversion_cppsequence_to_pylist",
                  "PySequence",
                  "shiboken_conversion_pyiterable_to_cppsequentialcontainer");
    }
    if (!hasStdVector) {
        ts += containerTypeSystemSnippet(
                  "std::vector", "list", "vector",
                  "shiboken_conversion_cppsequence_to_pylist",
                  "PySequence",
                  "shiboken_conversion_pyiterable_to_cppsequentialcontainer_reserve");
    }
    if (!hasStdMap) {
        ts += containerTypeSystemSnippet(
                  "std::map", "map", "map",
                  "shiboken_conversion_stdmap_to_pydict",
                  "PyDict", "shiboken_conversion_pydict_to_stdmap");
    }
    if (!hasStdUnorderedMap) {
        ts += containerTypeSystemSnippet(
                  "std::unordered_map", "map", "unordered_map",
                  "shiboken_conversion_stdmap_to_pydict",
                  "PyDict", "shiboken_conversion_pydict_to_stdmap");
    }
    ts += "</typesystem>";
    QBuffer buffer(&ts);
    buffer.open(QIODevice::ReadOnly);
    const bool ok = parseFile(&buffer, true);
    Q_ASSERT(ok);
}

bool TypeDatabase::parseFile(const QString &filename, bool generate)
{
    return parseFile(filename, QString(), generate);
}

bool TypeDatabase::parseFile(const QString &filename, const QString &currentPath, bool generate)
{

    QString filepath = modifiedTypesystemFilepath(filename, currentPath);
    if (m_parsedTypesystemFiles.contains(filepath))
        return m_parsedTypesystemFiles[filepath];

    m_parsedTypesystemFiles[filepath] = true; // Prevent recursion when including self.

    QFile file(filepath);
    if (!file.exists()) {
        m_parsedTypesystemFiles[filepath] = false;
        QString message = QLatin1String("Can't find ") + filename;
        if (!currentPath.isEmpty())
            message += QLatin1String(", current path: ") + currentPath;
        message += QLatin1String(", typesystem paths: ") + m_typesystemPaths.join(QLatin1String(", "));
        qCWarning(lcShiboken).noquote().nospace() << message;
        return false;
    }
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        m_parsedTypesystemFiles[filepath] = false;
        qCWarning(lcShiboken).noquote().nospace()
            << "Can't open " << QDir::toNativeSeparators(filename) << ": " << file.errorString();
        return false;
    }

    bool ok = parseFile(&file, generate);
    m_parsedTypesystemFiles[filepath] = ok;
    return ok;
}

bool TypeDatabase::parseFile(QIODevice* device, bool generate)
{
    static int depth = 0;

    ++depth;
    ConditionalStreamReader reader(device);
    reader.setConditions(TypeDatabase::instance()->typesystemKeywords());
    TypeSystemParser handler(this, generate);
    const bool result = handler.parse(reader);
    --depth;

    if (!result) {
        qCWarning(lcShiboken, "%s", qPrintable(handler.errorString()));
        return false;
    }

    if (depth == 0) {
        addBuiltInPrimitiveTypes();
        addBuiltInContainerTypes();
    }

    return result;
}

PrimitiveTypeEntry *TypeDatabase::findPrimitiveType(const QString& name) const
{
    const auto entries = findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (entry->isPrimitive()) {
            auto *pe = static_cast<PrimitiveTypeEntry *>(entry);
            if (pe->preferredTargetLangType())
                return pe;
        }
    }

    return nullptr;
}

ComplexTypeEntry* TypeDatabase::findComplexType(const QString& name) const
{
    const auto entries = findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (entry->isComplex() && useType(entry))
            return static_cast<ComplexTypeEntry*>(entry);
    }
    return nullptr;
}

ObjectTypeEntry* TypeDatabase::findObjectType(const QString& name) const
{
    const auto entries = findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (entry && entry->isObject() && useType(entry))
            return static_cast<ObjectTypeEntry*>(entry);
    }
    return nullptr;
}

NamespaceTypeEntryList TypeDatabase::findNamespaceTypes(const QString& name) const
{
    NamespaceTypeEntryList result;
    const auto entries = findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (entry->isNamespace())
            result.append(static_cast<NamespaceTypeEntry*>(entry));
    }
    return result;
}

NamespaceTypeEntry *TypeDatabase::findNamespaceType(const QString& name,
                                                    const QString &fileName) const
{
    const auto entries = findNamespaceTypes(name);
    // Preferably check on matching file name first, if a pattern was given.
    if (!fileName.isEmpty()) {
        for (NamespaceTypeEntry *entry : entries) {
            if (entry->hasPattern() && entry->matchesFile(fileName))
                return entry;
        }
    }
    for (NamespaceTypeEntry *entry : entries) {
        if (!entry->hasPattern())
            return entry;
    }
    return nullptr;
}

bool TypeDatabase::shouldDropTypeEntry(const QString& fullTypeName) const
{
    return m_dropTypeEntries.contains(fullTypeName);
}

void TypeDatabase::setDropTypeEntries(QStringList dropTypeEntries)
{
    m_dropTypeEntries = dropTypeEntries;
    m_dropTypeEntries.sort();
}

static bool computeTypeIndexes = true;
static int maxTypeIndex;

static bool typeEntryLessThan(const TypeEntry* t1, const TypeEntry* t2)
{
    if (t1->revision() < t2->revision())
        return true;
    return t1->revision() == t2->revision()
        && t1->qualifiedCppName() < t2->qualifiedCppName();
}

static void _computeTypeIndexes()
{
    TypeDatabase* tdb = TypeDatabase::instance();

    TypeEntryList list;

    // Group type entries by revision numbers
    const auto &allEntries = tdb->entries();
    list.reserve(allEntries.size());
    for (auto  tit = allEntries.cbegin(), end = allEntries.cend(); tit != end; ++tit) {
        TypeEntry *entry = tit.value();
        if (entry->isPrimitive()
            || entry->isContainer()
            || entry->isFunction()
            || !entry->generateCode()
            || entry->isEnumValue()
            || entry->isVarargs()
            || entry->isTypeSystem()
            || entry->isVoid()
            || entry->isCustom())
            continue;
        if (!list.contains(entry)) // Remove duplicates
            list.append(entry);
    }

    // Sort the type entries by revision, name
    std::sort(list.begin(), list.end(), typeEntryLessThan);

    maxTypeIndex = 0;
    for (TypeEntry *e : qAsConst(list))
        e->setSbkIndex(maxTypeIndex++);
    computeTypeIndexes = false;
}

void TypeEntry::setRevision(int r)
{
    if (setRevisionHelper(r))
        computeTypeIndexes = true;
}

int TypeEntry::sbkIndex() const
{
    if (computeTypeIndexes)
        _computeTypeIndexes();
    return sbkIndexHelper();
}

int getMaxTypeIndex()
{
    if (computeTypeIndexes)
        _computeTypeIndexes();
    return maxTypeIndex;
}

void TypeDatabase::clearApiVersions()
{
    apiVersions()->clear();
}

bool TypeDatabase::setApiVersion(const QString& packageWildcardPattern, const QString &version)
{
    const QString packagePattern = wildcardToRegExp(packageWildcardPattern.trimmed());
    const QVersionNumber versionNumber = QVersionNumber::fromString(version);
    if (versionNumber.isNull())
        return false;
    ApiVersions &versions = *apiVersions();
    for (int i = 0, size = versions.size(); i < size; ++i) {
        if (versions.at(i).first.pattern() == packagePattern) {
            versions[i].second = versionNumber;
            return true;
        }
    }
    const QRegularExpression packageRegex(packagePattern);
    if (!packageRegex.isValid())
        return false;
    versions.append(qMakePair(packageRegex, versionNumber));
    return true;
}

bool TypeDatabase::checkApiVersion(const QString &package,
                                   const VersionRange &vr)
{
    const ApiVersions &versions = *apiVersions();
    if (versions.isEmpty()) // Nothing specified: use latest.
        return true;
    for (int i = 0, size = versions.size(); i < size; ++i) {
        if (versions.at(i).first.match(package).hasMatch())
            return versions.at(i).second >= vr.since
                && versions.at(i).second <= vr.until;
    }
    return false;
}

#ifndef QT_NO_DEBUG_STREAM

template <class Container, class Separator>
static void formatList(QDebug &d, const char *name, const Container &c, Separator sep)
{
    if (const int size = c.size()) {
        d << ", " << name << '[' << size << "]=(";
        for (int i = 0; i < size; ++i) {
            if (i)
                d << sep;
             d << c.at(i);
        }
        d << ')';
    }
}

void TypeDatabase::formatDebug(QDebug &d) const
{
    d << "TypeDatabase("
      << "entries[" << m_entries.size() << "]=";
    for (auto it = m_entries.cbegin(), end = m_entries.cend(); it != end; ++it)
        d << "  " << it.value() << '\n';
    if (!m_typedefEntries.isEmpty()) {
        d << "typedefs[" << m_typedefEntries.size() << "]=(";
        const auto begin = m_typedefEntries.cbegin();
        for (auto it = begin, end = m_typedefEntries.cend(); it != end; ++it) {
            if (it != begin)
                d << ", ";
            d << "  " << it.value() << '\n';
        }
        d << ")\n";
    }
    if (!m_templates.isEmpty()) {
        d << "templates[" << m_templates.size() << "]=(";
        const auto begin = m_templates.cbegin();
        for (auto  it = begin, end = m_templates.cend(); it != end; ++it) {
            if (it != begin)
                d << ", ";
            d << it.value();
        }
        d << ")\n";
    }
    if (!m_flagsEntries.isEmpty()) {
        d << "flags[" << m_flagsEntries.size() << "]=(";
        const auto begin = m_flagsEntries.cbegin();
        for (auto it = begin, end = m_flagsEntries.cend(); it != end; ++it) {
            if (it != begin)
                d << ", ";
            d << it.value();
        }
        d << ")\n";
    }
    d <<"\nglobalUserFunctions=" << m_globalUserFunctions << '\n';
    formatList(d, "globalFunctionMods", m_functionMods, '\n');
    d << ')';
}

void TypeDatabase::addBuiltInType(TypeEntry *e)
{
    e->setBuiltIn(true);
    addType(e);
}

PrimitiveTypeEntry *
    TypeDatabase::addBuiltInPrimitiveType(const QString &name,
                                          const TypeSystemTypeEntry *root,
                                          const QString &rootPackage,
                                          CustomTypeEntry *targetLang)
{
    auto *result = new PrimitiveTypeEntry(name, {}, root);
    result->setTargetLangApiType(targetLang);
    result->setTargetLangPackage(rootPackage);
    addBuiltInType(result);
    return result;
}

void TypeDatabase::addBuiltInCppStringPrimitiveType(const QString &name,
                                                    const QString &viewName,
                                                    const TypeSystemTypeEntry *root,
                                                    const QString &rootPackage,
                                                    CustomTypeEntry *targetLang)

{
    auto *stringType = addBuiltInPrimitiveType(name, root, rootPackage,
                                               targetLang);
    auto *viewType = addBuiltInPrimitiveType(viewName, root, rootPackage,
                                             nullptr);
    viewType->setViewOn(stringType);
}

void TypeDatabase::addBuiltInPrimitiveTypes()
{
    auto *root = defaultTypeSystemType();
    const QString &rootPackage = root->name();

    // C++ primitive types
    auto *pyLongEntry = findType(u"PyLong"_qs);
    Q_ASSERT(pyLongEntry && pyLongEntry->isCustom());
    auto *pyLongCustomEntry = static_cast<CustomTypeEntry *>(pyLongEntry);
    auto *pyBoolEntry = findType(u"PyBool"_qs);
    Q_ASSERT(pyBoolEntry && pyBoolEntry->isCustom());
    auto *sbkCharEntry = findType(u"SbkChar"_qs);
    Q_ASSERT(sbkCharEntry && sbkCharEntry->isCustom());
    auto *sbkCharCustomEntry = static_cast<CustomTypeEntry *>(sbkCharEntry);

    auto *pyBoolCustomEntry = static_cast<CustomTypeEntry *>(pyBoolEntry);
    for (const auto &t : AbstractMetaType::cppIntegralTypes()) {
        if (!m_entries.contains(t)) {
            CustomTypeEntry *targetLangApi = pyLongCustomEntry;
            if (t == u"bool")
                targetLangApi = pyBoolCustomEntry;
            else if (AbstractMetaType::cppCharTypes().contains(t))
                targetLangApi = sbkCharCustomEntry;
            addBuiltInPrimitiveType(t, root, rootPackage, targetLangApi);
        }
    }

    auto *pyFloatEntry = findType(u"PyFloat"_qs);
    Q_ASSERT(pyFloatEntry && pyFloatEntry->isCustom());
    auto *pyFloatCustomEntry = static_cast<CustomTypeEntry *>(pyFloatEntry);
    for (const auto &t : AbstractMetaType::cppFloatTypes()) {
        if (!m_entries.contains(t))
            addBuiltInPrimitiveType(t, root, rootPackage, pyFloatCustomEntry);
    }

    auto *pyUnicodeEntry = findType(u"PyUnicode"_qs);
    Q_ASSERT(pyUnicodeEntry && pyUnicodeEntry->isCustom());
    auto *pyUnicodeCustomEntry = static_cast<CustomTypeEntry *>(pyUnicodeEntry);

    const QString stdString = u"std::string"_qs;
    if (!m_entries.contains(stdString)) {
        addBuiltInCppStringPrimitiveType(stdString, u"std::string_view"_qs,
                                         root, rootPackage,
                                         pyUnicodeCustomEntry);
    }
    const QString stdWString = u"std::wstring"_qs;
    if (!m_entries.contains(stdWString)) {
        addBuiltInCppStringPrimitiveType(stdWString, u"std::wstring_view"_qs,
                                         root, rootPackage,
                                         pyUnicodeCustomEntry);
    }
}

QDebug operator<<(QDebug d, const TypeDatabase &db)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    db.formatDebug(d);
    return d;
}
#endif // !QT_NO_DEBUG_STREAM
