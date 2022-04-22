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
#include "messages.h"
#include "typesystem.h"
#include "typesystemparser_p.h"
#include "conditionalstreamreader.h"
#include "predefined_templates.h"
#include "clangparser/compilersupport.h"

#include "qtcompat.h"

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

using namespace Qt::StringLiterals;

using TypeDatabaseParserContextPtr = QSharedPointer<TypeDatabaseParserContext>;

// package -> api-version

static QString wildcardToRegExp(QString w)
{
    w.replace(u'?', u'.');
    w.replace(u'*', QStringLiteral(".*"));
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
        {u"PyArrayObject"_s, u"PyArray_Check"_s, TypeSystem::CPythonType::Other},
        {u"PyBuffer"_s, u"Shiboken::Buffer::checkType"_s, TypeSystem::CPythonType::Other},
        {u"PyByteArray"_s, u"PyByteArray_Check"_s, TypeSystem::CPythonType::Other},
        {u"PyBytes"_s, u"PyBytes_Check"_s, TypeSystem::CPythonType::Other},
        {u"PyCallable"_s, u"PyCallable_Check"_s, TypeSystem::CPythonType::Other},
        {u"PyDate"_s, u"PyDate_Check"_s, TypeSystem::CPythonType::Other},
        {u"PyDateTime"_s, u"PyDateTime_Check_Check"_s, TypeSystem::CPythonType::Other},
        {u"PyDict"_s, u"PyDict_Check"_s, TypeSystem::CPythonType::Other},
        // Convenience macro in sbkconverter.h
        {u"PyObject"_s, u"true"_s, TypeSystem::CPythonType::Other},
        // shiboken-specific
        {u"PyPathLike"_s, u"Shiboken::String::checkPath"_s, TypeSystem::CPythonType::Other},
        {u"PySequence"_s, u"Shiboken::String::checkIterable"_s, TypeSystem::CPythonType::Other},
        {u"PyUnicode"_s, u"PyUnicode_Check"_s, TypeSystem::CPythonType::String},
        {u"PyTypeObject"_s, u"PyType_Check"_s, TypeSystem::CPythonType::Other},
        {u"str"_s, u"Shiboken::String::check"_s, TypeSystem::CPythonType::String},
        // Types used as target lang API types for primitive types
        {u"PyBool"_s, u"PyBool_Check"_s, TypeSystem::CPythonType::Bool},
        {u"PyComplex"_s, u"PyComplex_Check"_s, TypeSystem::CPythonType::Other},
        {u"PyLong"_s, u"PyLong_Check"_s, TypeSystem::CPythonType::Integer},
        {u"PyFloat"_s, u"PyFloat_Check"_s, TypeSystem::CPythonType::Float},
        // Single character strings to match C++ char types
        {u"SbkChar"_s, u"SbkChar_Check"_s, TypeSystem::CPythonType::String}
    };
    return result;
}

struct TypeDatabasePrivate
{
    const TypeSystemTypeEntry *defaultTypeSystemType() const;
    TypeEntry *findType(const QString &name) const;
    TypeEntries findCppTypes(const QString &name) const;
    bool addType(TypeEntry *e, QString *errorMessage = nullptr);
    bool parseFile(QIODevice *device, TypeDatabase *db, bool generate = true);
    static bool parseFile(const TypeDatabaseParserContextPtr &context,
                          QIODevice *device, bool generate = true);
    bool parseFile(const TypeDatabaseParserContextPtr &context,
                   const QString &filename, const QString &currentPath, bool generate);
    bool prepareParsing(QFile &file, const QString &origFileName,
                        const QString &currentPath = {});

    QString modifiedTypesystemFilepath(const QString& tsFile,
                                       const QString &currentPath) const;
    void addBuiltInType(TypeEntry *e);
    PrimitiveTypeEntry *addBuiltInPrimitiveType(const QString &name,
                                                const TypeSystemTypeEntry *root,
                                                const QString &rootPackage,
                                                CustomTypeEntry *targetLang);
    void addBuiltInCppStringPrimitiveType(const QString &name,
                                          const QString &viewName,
                                          const TypeSystemTypeEntry *root,
                                          const QString &rootPackage,
                                          CustomTypeEntry *targetLang);
    void addBuiltInPrimitiveTypes();
    void addBuiltInContainerTypes(const TypeDatabaseParserContextPtr &context);
    TypeEntryMultiMapConstIteratorRange findTypeRange(const QString &name) const;
    template <class Predicate>
    TypeEntries findTypesHelper(const QString &name, Predicate pred) const;
    template <class Type, class Predicate>
    QList<const Type *> findTypesByTypeHelper(Predicate pred) const;
    TypeEntry *resolveTypeDefEntry(TypedefEntry *typedefEntry, QString *errorMessage);
    template <class String>
    bool isSuppressedWarningHelper(const String &s) const;
    bool resolveSmartPointerInstantiations(const TypeDatabaseParserContextPtr &context);
    void formatDebug(QDebug &d) const;

    bool m_suppressWarnings = true;
    TypeEntryMultiMap m_entries; // Contains duplicate entries (cf addInlineNamespaceLookups).
    TypeEntryMap m_flagsEntries;
    TypedefEntryMap m_typedefEntries;
    TemplateEntryMap m_templates;
    QList<QRegularExpression> m_suppressedWarnings;
    QList<const TypeSystemTypeEntry *> m_typeSystemEntries; // maintain order, default is first.

    AddedFunctionList m_globalUserFunctions;
    FunctionModificationList m_functionMods;

    QStringList m_requiredTargetImports;

    QStringList m_typesystemPaths;
    QStringList m_typesystemKeywords;
    QHash<QString, bool> m_parsedTypesystemFiles;

    QList<TypeRejection> m_rejections;

    QStringList m_dropTypeEntries;
    QStringList m_systemIncludes;
};

TypeDatabase::TypeDatabase() : d(new TypeDatabasePrivate)
{
    d->addBuiltInType(new VoidTypeEntry());
    d->addBuiltInType(new VarargsTypeEntry());
    for (const auto &pt : builtinPythonTypes())
        d->addBuiltInType(new PythonTypeEntry(pt.name, pt.checkFunction, pt.type));

    for (const auto &p : predefinedTemplates())
        addTemplate(p.name, p.content);
}

TypeDatabase::~TypeDatabase()
{
    delete d;
}

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
            const QString intType = QLatin1StringView(t);
            if (!TypeDatabase::instance()->findType(u'u' + intType)) {
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
    QByteArray normalizedB = QMetaObject::normalizedSignature(signature.toUtf8().constData());
    QString normalized = QLatin1StringView(normalizedB);

    if (instance() && signature.contains(u"unsigned")) {
        const IntTypeNormalizationEntries &entries = intTypeNormalizationEntries();
        for (const auto &entry : entries)
            normalized.replace(entry.regex, entry.replacement);
    }

    return normalized;
}

QStringList TypeDatabase::requiredTargetImports() const
{
    return d->m_requiredTargetImports;
}

void TypeDatabase::addRequiredTargetImport(const QString& moduleName)
{
    if (!d->m_requiredTargetImports.contains(moduleName))
        d->m_requiredTargetImports << moduleName;
}

void TypeDatabase::addTypesystemPath(const QString& typesystem_paths)
{
    #if defined(Q_OS_WIN32)
    const char path_splitter = ';';
    #else
    const char path_splitter = ':';
    #endif
    d->m_typesystemPaths += typesystem_paths.split(QLatin1Char(path_splitter));
}

void TypeDatabase::setTypesystemKeywords(const QStringList &keywords)
{
    d->m_typesystemKeywords = keywords;
}

QStringList TypeDatabase::typesystemKeywords() const
{
    QStringList result = d->m_typesystemKeywords;
    for (const auto &d : d->m_dropTypeEntries)
        result.append(QStringLiteral("no_") + d);

    switch (clang::emulatedCompilerLanguageLevel()) {
    case LanguageLevel::Cpp11:
        result.append(u"c++11"_s);
        break;
    case LanguageLevel::Cpp14:
        result.append(u"c++14"_s);
        break;
    case LanguageLevel::Cpp17:
        result.append(u"c++17"_s);
        break;
    case LanguageLevel::Cpp20:
        result.append(u"c++20"_s);
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

const QStringList &TypeDatabase::systemIncludes() const
{
    return d->m_systemIncludes;
}

void TypeDatabase::addSystemInclude(const QString &name)
{
    d->m_systemIncludes.append(name);
}

// Add a lookup for the short name excluding inline namespaces
// so that "std::shared_ptr" finds "std::__1::shared_ptr" as well.
// Note: This inserts duplicate TypeEntry * into m_entries.
void TypeDatabase::addInlineNamespaceLookups(const NamespaceTypeEntry *n)
{
    TypeEntryList additionalEntries; // Store before modifying the hash
    for (TypeEntry *entry : qAsConst(d->m_entries)) {
        if (entry->isChildOf(n))
            additionalEntries.append(entry);
    }
    for (const auto &ae : qAsConst(additionalEntries))
        d->m_entries.insert(ae->shortName(), ae);
}

ContainerTypeEntry* TypeDatabase::findContainerType(const QString &name) const
{
    QString template_name = name;

    int pos = name.indexOf(u'<');
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
    const auto entries = d->findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (entry->type() == TypeEntry::FunctionType && useType(entry))
            return static_cast<FunctionTypeEntry*>(entry);
    }
    return nullptr;
}

void TypeDatabase::addTypeSystemType(const TypeSystemTypeEntry *e)
{
    d->m_typeSystemEntries.append(e);
}

const TypeSystemTypeEntry *TypeDatabase::findTypeSystemType(const QString &name) const
{
    for (auto entry : d->m_typeSystemEntries) {
        if (entry->name() == name)
            return entry;
    }
    return nullptr;
}

const TypeSystemTypeEntry *TypeDatabase::defaultTypeSystemType() const
{
    return d->defaultTypeSystemType();
}

const TypeSystemTypeEntry *TypeDatabasePrivate::defaultTypeSystemType() const
{
    return m_typeSystemEntries.value(0, nullptr);
}

QString TypeDatabase::defaultPackageName() const
{
    Q_ASSERT(!d->m_typeSystemEntries.isEmpty());
    return d->m_typeSystemEntries.constFirst()->name();
}

TypeEntry* TypeDatabase::findType(const QString& name) const
{
    return d->findType(name);
}

TypeEntry* TypeDatabasePrivate::findType(const QString& name) const
{
    const auto entries = findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (useType(entry))
            return entry;
    }
    return nullptr;
}

template <class Predicate>
TypeEntries TypeDatabasePrivate::findTypesHelper(const QString &name, Predicate pred) const
{
    TypeEntries result;
    const auto entries = findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (pred(entry))
            result.append(entry);
    }
    return result;
}

template<class Type, class Predicate>
QList<const Type *> TypeDatabasePrivate::findTypesByTypeHelper(Predicate pred) const
{
    QList<const Type *> result;
    for (auto *entry : m_entries) {
        if (pred(entry))
            result.append(static_cast<const Type *>(entry));
    }
    return result;
}

TypeEntries TypeDatabase::findTypes(const QString &name) const
{
    return d->findTypesHelper(name, useType);
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
    return d->findCppTypes(name);
}

TypeEntries TypeDatabasePrivate::findCppTypes(const QString &name) const
{
    return findTypesHelper(name, useCppType);
}

const TypeEntryMultiMap &TypeDatabase::entries() const
{
    return d->m_entries;
}

const TypedefEntryMap &TypeDatabase::typedefEntries() const
{
    return d->m_typedefEntries;
}

TypeEntryMultiMapConstIteratorRange TypeDatabasePrivate::findTypeRange(const QString &name) const
{
    const auto range = m_entries.equal_range(name);
    return {range.first, range.second};
}

PrimitiveTypeEntryList TypeDatabase::primitiveTypes() const
{
    auto pred = [](const TypeEntry *t) { return t->isPrimitive(); };
    return d->findTypesByTypeHelper<PrimitiveTypeEntry>(pred);
}

ContainerTypeEntryList TypeDatabase::containerTypes() const
{
    auto pred = [](const TypeEntry *t) { return t->isContainer(); };
    return d->findTypesByTypeHelper<ContainerTypeEntry>(pred);
}

SmartPointerTypeEntryList TypeDatabase::smartPointerTypes() const
{
    auto pred = [](const TypeEntry *t) { return t->isSmartPointer(); };
    return d->findTypesByTypeHelper<SmartPointerTypeEntry>(pred);
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
    d->m_rejections << r;
}

// Match class name only
bool TypeDatabase::isClassRejected(const QString& className, QString *reason) const
{
    for (const TypeRejection& r : d->m_rejections) {
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
    return findRejection(d->m_rejections, TypeRejection::Enum, className, enumName, reason);
}

TypeEntry *TypeDatabasePrivate::resolveTypeDefEntry(TypedefEntry *typedefEntry,
                                             QString *errorMessage)
{
    QString sourceName = typedefEntry->sourceType();
    const int lessThanPos = sourceName.indexOf(u'<');
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
            *errorMessage = u"Unable to resolve typedef \""_s
                            + typedefEntry->sourceType() + u'"';
        return nullptr;
    }

    m_typedefEntries.insert(typedefEntry->qualifiedCppName(), typedefEntry);
    return TypeDatabase::initializeTypeDefEntry(typedefEntry, source);
}

ComplexTypeEntry *
    TypeDatabase::initializeTypeDefEntry(TypedefEntry *typedefEntry,
                                         const ComplexTypeEntry *source)
{
    auto *result = static_cast<ComplexTypeEntry *>(source->clone());
    result->useAsTypedef(typedefEntry);
    typedefEntry->setSource(source);
    typedefEntry->setTarget(result);
    return result;
}

bool TypeDatabase::addType(TypeEntry *e, QString *errorMessage)
{
    return d->addType(e, errorMessage);
}

bool TypeDatabasePrivate::addType(TypeEntry *e, QString *errorMessage)
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
    return findRejection(d->m_rejections, TypeRejection::Function, className, functionName, reason);
}

bool TypeDatabase::isFieldRejected(const QString& className, const QString& fieldName,
                                   QString *reason) const
{
    return findRejection(d->m_rejections, TypeRejection::Field, className, fieldName, reason);
}

bool TypeDatabase::isArgumentTypeRejected(const QString& className, const QString& typeName,
                                          QString *reason) const
{
    return findRejection(d->m_rejections, TypeRejection::ArgumentType, className, typeName, reason);
}

bool TypeDatabase::isReturnTypeRejected(const QString& className, const QString& typeName,
                                        QString *reason) const
{
    return findRejection(d->m_rejections, TypeRejection::ReturnType, className, typeName, reason);
}

FlagsTypeEntry* TypeDatabase::findFlagsType(const QString &name) const
{
    TypeEntry *fte = findType(name);
    if (!fte) {
        fte = d->m_flagsEntries.value(name);
        if (!fte) {
            //last hope, search for flag without scope  inside of flags hash
            const auto end = d->m_flagsEntries.cend();
            for (auto it = d->m_flagsEntries.cbegin(); it != end; ++it) {
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
    d->m_flagsEntries[fte->originalName()] = fte;
}

TemplateEntry *TypeDatabase::findTemplate(const QString &name) const
{
    return d->m_templates[name];
}

void TypeDatabase::addTemplate(TemplateEntry *t)
{
    d->m_templates[t->name()] = t;
}

void TypeDatabase::addTemplate(const QString &name, const QString &code)
{
    auto *te = new TemplateEntry(name);
    te->addCode(code);
    addTemplate(te);
}

AddedFunctionList TypeDatabase::globalUserFunctions() const
{
    return d->m_globalUserFunctions;
}

void TypeDatabase::addGlobalUserFunctions(const AddedFunctionList &functions)
{
    d->m_globalUserFunctions << functions;
}

AddedFunctionList TypeDatabase::findGlobalUserFunctions(const QString& name) const
{
    AddedFunctionList addedFunctions;
    for (const AddedFunctionPtr &func : d->m_globalUserFunctions) {
        if (func->name() == name)
            addedFunctions.append(func);
    }
    return addedFunctions;
}

void TypeDatabase::addGlobalUserFunctionModifications(const FunctionModificationList &functionModifications)
{
    d->m_functionMods << functionModifications;
}

QString TypeDatabase::globalNamespaceClassName(const TypeEntry * /*entry*/)
{
    return u"Global"_s;
}

FunctionModificationList TypeDatabase::functionModifications(const QString& signature) const
{
    FunctionModificationList lst;
    for (const auto &mod : d->m_functionMods) {
        if (mod.matches(signature))
            lst << mod;
    }

    return lst;
}

void TypeDatabase::setSuppressWarnings(bool on)
{
    d->m_suppressWarnings = on;
}

bool TypeDatabase::addSuppressedWarning(const QString &warning, QString *errorMessage)
{
    QString pattern;
    if (warning.startsWith(u'^') && warning.endsWith(u'$')) {
        pattern = warning;
    } else {
        // Legacy syntax: Use wildcards '*' (unless escaped by '\')
        QList<int> asteriskPositions;
        const int warningSize = warning.size();
        for (int i = 0; i < warningSize; ++i) {
            if (warning.at(i) == u'\\')
                ++i;
            else if (warning.at(i) == u'*')
                asteriskPositions.append(i);
        }
        asteriskPositions.append(warningSize);

        pattern.append(u'^');
        int lastPos = 0;
        for (int a = 0, aSize = asteriskPositions.size(); a < aSize; ++a) {
            if (a)
                pattern.append(QStringLiteral(".*"));
            const int nextPos = asteriskPositions.at(a);
            if (nextPos > lastPos)
                pattern.append(QRegularExpression::escape(warning.mid(lastPos, nextPos - lastPos)));
            lastPos = nextPos + 1;
        }
        pattern.append(u'$');
    }

    QRegularExpression expression(pattern);
    if (!expression.isValid()) {
        *errorMessage = u"Invalid message pattern \""_s + warning
            + u"\": "_s + expression.errorString();
        return false;
    }
    expression.setPatternOptions(expression.patternOptions() | QRegularExpression::MultilineOption);

    d->m_suppressedWarnings.append(expression);
    return true;
}

bool TypeDatabase::isSuppressedWarning(QStringView s) const
{
    if (!d->m_suppressWarnings)
        return false;
    return std::any_of(d->m_suppressedWarnings.cbegin(), d->m_suppressedWarnings.cend(),
                       [&s] (const QRegularExpression &e) {
                           return e.match(s).hasMatch();
                       });
}

QString TypeDatabase::modifiedTypesystemFilepath(const QString& tsFile, const QString &currentPath) const
{
    return d->modifiedTypesystemFilepath(tsFile, currentPath);
}

QString TypeDatabasePrivate::modifiedTypesystemFilepath(const QString& tsFile,
                                                        const QString &currentPath) const
{
    const QFileInfo tsFi(tsFile);
    if (tsFi.isAbsolute()) // No point in further lookups
        return tsFi.absoluteFilePath();
    if (tsFi.isFile()) // Make path absolute
        return tsFi.absoluteFilePath();
    if (!currentPath.isEmpty()) {
        const QFileInfo fi(currentPath + u'/' + tsFile);
        if (fi.isFile())
            return fi.absoluteFilePath();
    }
    for (const QString &path : m_typesystemPaths) {
        const QFileInfo fi(path + u'/' + tsFile);
        if (fi.isFile())
            return fi.absoluteFilePath();
    }
    return tsFile;
}

void TypeDatabasePrivate::addBuiltInContainerTypes(const TypeDatabaseParserContextPtr &context)
{
    // Unless the user has added the standard containers (potentially with
    // some opaque types), add them by default.
    const bool hasStdPair = findType(u"std::pair"_s) != nullptr;
    const bool hasStdList = findType(u"std::list"_s) != nullptr;
    const bool hasStdVector = findType(u"std::vector"_s) != nullptr;
    const bool hasStdMap = findType(u"std::map"_s) != nullptr;
    const bool hasStdUnorderedMap = findType(u"std::unordered_map"_s) != nullptr;

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
    const bool ok = parseFile(context, &buffer, true);
    Q_ASSERT(ok);
}

bool TypeDatabase::parseFile(const QString &filename, bool generate)
{
    QString filepath = modifiedTypesystemFilepath(filename, {});
    QFile file(filepath);
    return d->prepareParsing(file, filename) && d->parseFile(&file, this, generate);
}

bool TypeDatabase::parseFile(const TypeDatabaseParserContextPtr &context,
                             const QString &filename, const QString &currentPath,
                             bool generate)
{
    return d->parseFile(context, filename, currentPath, generate);
}

bool TypeDatabasePrivate::prepareParsing(QFile &file, const QString &origFileName,
                                         const QString &currentPath)
{
    const QString &filepath = file.fileName();
    if (!file.exists()) {
        m_parsedTypesystemFiles[filepath] = false;
        QString message = u"Can't find "_s + origFileName;
        if (!currentPath.isEmpty())
            message += u", current path: "_s + currentPath;
        message += u", typesystem paths: "_s + m_typesystemPaths.join(u", "_s);
        qCWarning(lcShiboken, "%s", qPrintable(message));
        return false;
    }
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        m_parsedTypesystemFiles[filepath] = false;
        qCWarning(lcShiboken, "%s", qPrintable(msgCannotOpenForReading(file)));
        return false;
    }

    m_parsedTypesystemFiles[filepath] = true;
    return true;
}

bool TypeDatabasePrivate::parseFile(const TypeDatabaseParserContextPtr &context,
                                    const QString &filename, const QString &currentPath,
                                    bool generate)
{
    // Prevent recursion when including self.
    QString filepath = modifiedTypesystemFilepath(filename, currentPath);
    const auto it = m_parsedTypesystemFiles.constFind(filepath);
    if (it != m_parsedTypesystemFiles.cend())
        return it.value();

    QFile file(filepath);
    if (!prepareParsing(file, filename, currentPath))
        return false;

    const bool ok = parseFile(context, &file, generate);
    m_parsedTypesystemFiles[filepath] = ok;
    return ok;
}

bool TypeDatabase::parseFile(QIODevice* device, bool generate)
{
    return d->parseFile(device, this, generate);
}

bool TypeDatabasePrivate::parseFile(QIODevice* device, TypeDatabase *db, bool generate)
{
    const TypeDatabaseParserContextPtr context(new TypeDatabaseParserContext);
    context->db = db;

    if (!parseFile(context, device, generate))
        return false;

    addBuiltInPrimitiveTypes();
    addBuiltInContainerTypes(context);
    return resolveSmartPointerInstantiations(context);
}

bool TypeDatabase::parseFile(const TypeDatabaseParserContextPtr &context,
                             QIODevice *device, bool generate)
{
    return d->parseFile(context, device, generate);
}

bool TypeDatabasePrivate::parseFile(const TypeDatabaseParserContextPtr &context,
                                    QIODevice *device, bool generate)
{
    ConditionalStreamReader reader(device);
    reader.setConditions(context->db->typesystemKeywords());
    TypeSystemParser handler(context, generate);
    const bool result = handler.parse(reader);
    if (!result) {
        qCWarning(lcShiboken, "%s", qPrintable(handler.errorString()));
        return false;
    }
    return result;
}

// Split a type list potentially with template types
// "A<B,C>,D" -> ("A<B,C>", "D")
static QStringList splitTypeList(const QString &s)
{
    QStringList result;
    int templateDepth = 0;
    int lastPos = 0;
    const int size = s.size();
    for (int i = 0; i < size; ++i) {
        switch (s.at(i).toLatin1()) {
        case '<':
            ++templateDepth;
            break;
        case '>':
            --templateDepth;
            break;
        case ',':
            if (templateDepth == 0) {
                result.append(s.mid(lastPos, i - lastPos).trimmed());
                lastPos = i + 1;
            }
            break;
        }
    }
    if (lastPos < size)
        result.append(s.mid(lastPos, size - lastPos).trimmed());
    return result;
}

bool TypeDatabasePrivate::resolveSmartPointerInstantiations(const TypeDatabaseParserContextPtr &context)
{
    const auto &instantiations = context->smartPointerInstantiations;
    for (auto it = instantiations.cbegin(), end = instantiations.cend(); it != end; ++it) {
        auto smartPointerEntry = it.key();
        const auto instantiationNames = splitTypeList(it.value());
        SmartPointerTypeEntry::Instantiations instantiations;
        instantiations.reserve(instantiationNames.size());
        for (const auto &instantiationName : instantiationNames) {
            const auto types = findCppTypes(instantiationName);
            if (types.isEmpty()) {
                const QString m = msgCannotFindTypeEntryForSmartPointer(instantiationName,
                                                                        smartPointerEntry->name());
                qCWarning(lcShiboken, "%s", qPrintable(m));
                return false;
            }
            if (types.size() > 1) {
                const QString m = msgAmbiguousTypesFound(instantiationName, types);
                qCWarning(lcShiboken, "%s", qPrintable(m));
                return false;
            }
            instantiations.append(types.constFirst());
        }
        smartPointerEntry->setInstantiations(instantiations);
    }
    return true;
}

PrimitiveTypeEntry *TypeDatabase::findPrimitiveType(const QString& name) const
{
    const auto entries = d->findTypeRange(name);
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
    const auto entries = d->findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (entry->isComplex() && useType(entry))
            return static_cast<ComplexTypeEntry*>(entry);
    }
    return nullptr;
}

ObjectTypeEntry* TypeDatabase::findObjectType(const QString& name) const
{
    const auto entries = d->findTypeRange(name);
    for (TypeEntry *entry : entries) {
        if (entry && entry->isObject() && useType(entry))
            return static_cast<ObjectTypeEntry*>(entry);
    }
    return nullptr;
}

NamespaceTypeEntryList TypeDatabase::findNamespaceTypes(const QString& name) const
{
    NamespaceTypeEntryList result;
    const auto entries = d->findTypeRange(name);
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
    return d->m_dropTypeEntries.contains(fullTypeName);
}

void TypeDatabase::setDropTypeEntries(QStringList dropTypeEntries)
{
    d->m_dropTypeEntries = dropTypeEntries;
    d->m_dropTypeEntries.sort();
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

bool TypeDatabase::hasDroppedTypeEntries() const
{
    return !d->m_dropTypeEntries.isEmpty();
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

void TypeDatabase::formatDebug(QDebug &debug) const
{
    d->formatDebug(debug);
}

void TypeDatabasePrivate::formatDebug(QDebug &d) const
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

void TypeDatabasePrivate::addBuiltInType(TypeEntry *e)
{
    e->setBuiltIn(true);
    addType(e);
}

PrimitiveTypeEntry *
    TypeDatabasePrivate::addBuiltInPrimitiveType(const QString &name,
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

void TypeDatabasePrivate::addBuiltInCppStringPrimitiveType(const QString &name,
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

void TypeDatabasePrivate::addBuiltInPrimitiveTypes()
{
    auto *root = defaultTypeSystemType();
    const QString &rootPackage = root->name();

    // C++ primitive types
    auto *pyLongEntry = findType(u"PyLong"_s);
    Q_ASSERT(pyLongEntry && pyLongEntry->isCustom());
    auto *pyLongCustomEntry = static_cast<CustomTypeEntry *>(pyLongEntry);
    auto *pyBoolEntry = findType(u"PyBool"_s);
    Q_ASSERT(pyBoolEntry && pyBoolEntry->isCustom());
    auto *sbkCharEntry = findType(u"SbkChar"_s);
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

    auto *pyFloatEntry = findType(u"PyFloat"_s);
    Q_ASSERT(pyFloatEntry && pyFloatEntry->isCustom());
    auto *pyFloatCustomEntry = static_cast<CustomTypeEntry *>(pyFloatEntry);
    for (const auto &t : AbstractMetaType::cppFloatTypes()) {
        if (!m_entries.contains(t))
            addBuiltInPrimitiveType(t, root, rootPackage, pyFloatCustomEntry);
    }

    auto *pyUnicodeEntry = findType(u"PyUnicode"_s);
    Q_ASSERT(pyUnicodeEntry && pyUnicodeEntry->isCustom());
    auto *pyUnicodeCustomEntry = static_cast<CustomTypeEntry *>(pyUnicodeEntry);

    const QString stdString = u"std::string"_s;
    if (!m_entries.contains(stdString)) {
        addBuiltInCppStringPrimitiveType(stdString, u"std::string_view"_s,
                                         root, rootPackage,
                                         pyUnicodeCustomEntry);
    }
    const QString stdWString = u"std::wstring"_s;
    if (!m_entries.contains(stdWString)) {
        addBuiltInCppStringPrimitiveType(stdWString, u"std::wstring_view"_s,
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
