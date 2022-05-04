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

#include "typesystemparser_p.h"
#include "typedatabase.h"
#include "messages.h"
#include "reporthandler.h"
#include "sourcelocation.h"
#include "conditionalstreamreader.h"

#include "qtcompat.h"

#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QFileInfo>
#include <QtCore/QRegularExpression>
#include <QtCore/QSet>
#include <QtCore/QStringView>
#include <QtCore/QStringAlgorithms>
#include <QtCore/QVersionNumber>
#include <QtCore/QXmlStreamAttributes>
#include <QtCore/QXmlStreamReader>
#include <QtCore/QXmlStreamEntityResolver>

#include <algorithm>
#include <optional>
#include <memory>

using namespace Qt::StringLiterals;

static inline QString allowThreadAttribute() { return QStringLiteral("allow-thread"); }
static inline QString colonColon() { return QStringLiteral("::"); }
static inline QString checkFunctionAttribute() { return QStringLiteral("check-function"); }
static inline QString copyableAttribute() { return QStringLiteral("copyable"); }
static inline QString accessAttribute() { return QStringLiteral("access"); }
static inline QString actionAttribute() { return QStringLiteral("action"); }
static inline QString quoteAfterLineAttribute() { return QStringLiteral("quote-after-line"); }
static inline QString quoteBeforeLineAttribute() { return QStringLiteral("quote-before-line"); }
static inline QString textAttribute() { return QStringLiteral("text"); }
static inline QString nameAttribute() { return QStringLiteral("name"); }
static inline QString sinceAttribute() { return QStringLiteral("since"); }
static inline QString untilAttribute() { return QStringLiteral("until"); }
static inline QString defaultSuperclassAttribute() { return QStringLiteral("default-superclass"); }
static inline QString deleteInMainThreadAttribute() { return QStringLiteral("delete-in-main-thread"); }
static inline QString deprecatedAttribute() { return QStringLiteral("deprecated"); }
static inline QString disableWrapperAttribute() { return QStringLiteral("disable-wrapper"); }
static inline QString exceptionHandlingAttribute() { return QStringLiteral("exception-handling"); }
static inline QString extensibleAttribute() { return QStringLiteral("extensible"); }
static inline QString fileNameAttribute() { return QStringLiteral("file-name"); }
static inline QString flagsAttribute() { return QStringLiteral("flags"); }
static inline QString forceAbstractAttribute() { return QStringLiteral("force-abstract"); }
static inline QString forceIntegerAttribute() { return QStringLiteral("force-integer"); }
static inline QString formatAttribute() { return QStringLiteral("format"); }
static inline QString generateUsingAttribute() { return QStringLiteral("generate-using"); }
static inline QString classAttribute() { return QStringLiteral("class"); }
static inline QString generateAttribute() { return QStringLiteral("generate"); }
static inline QString generateGetSetDefAttribute() { return QStringLiteral("generate-getsetdef"); }
static inline QString genericClassAttribute() { return QStringLiteral("generic-class"); }
static inline QString indexAttribute() { return QStringLiteral("index"); }
static inline QString invalidateAfterUseAttribute() { return QStringLiteral("invalidate-after-use"); }
static inline QString isNullAttribute() { return QStringLiteral("isNull"); }
static inline QString locationAttribute() { return QStringLiteral("location"); }
static inline QString modifiedTypeAttribute() { return QStringLiteral("modified-type"); }
static inline QString operatorBoolAttribute() { return QStringLiteral("operator-bool"); }
static inline QString pyiTypeAttribute() { return QStringLiteral("pyi-type"); }
static inline QString overloadNumberAttribute() { return QStringLiteral("overload-number"); }
static inline QString ownershipAttribute() { return QStringLiteral("owner"); }
static inline QString packageAttribute() { return QStringLiteral("package"); }
static inline QString positionAttribute() { return QStringLiteral("position"); }
static inline QString preferredConversionAttribute() { return QStringLiteral("preferred-conversion"); }
static inline QString preferredTargetLangTypeAttribute() { return QStringLiteral("preferred-target-lang-type"); }
static inline QString qtMetaTypeAttribute() { return QStringLiteral("qt-register-metatype"); }
static inline QString removeAttribute() { return QStringLiteral("remove"); }
static inline QString renameAttribute() { return QStringLiteral("rename"); }
static inline QString readAttribute() { return QStringLiteral("read"); }
static inline QString targetLangNameAttribute() { return QStringLiteral("target-lang-name"); }
static inline QString writeAttribute() { return QStringLiteral("write"); }
static inline QString opaqueContainerFieldAttribute() { return QStringLiteral("opaque-container"); }
static inline QString replaceAttribute() { return QStringLiteral("replace"); }
static inline QString toAttribute() { return QStringLiteral("to"); }
static inline QString signatureAttribute() { return QStringLiteral("signature"); }
static inline QString snippetAttribute() { return QStringLiteral("snippet"); }
static inline QString snakeCaseAttribute() { return QStringLiteral("snake-case"); }
static inline QString staticAttribute() { return QStringLiteral("static"); }
static inline QString classmethodAttribute() { return QStringLiteral("classmethod"); }
static inline QString threadAttribute() { return QStringLiteral("thread"); }
static inline QString sourceAttribute() { return QStringLiteral("source"); }
static inline QString streamAttribute() { return QStringLiteral("stream"); }
static inline QString privateAttribute() { return QStringLiteral("private"); }
static inline QString xPathAttribute() { return QStringLiteral("xpath"); }
static inline QString virtualSlotAttribute() { return QStringLiteral("virtual-slot"); }
static inline QString visibleAttribute() { return QStringLiteral("visible"); }
static inline QString enumIdentifiedByValueAttribute() { return QStringLiteral("identified-by-value"); }

static inline QString noAttributeValue() { return QStringLiteral("no"); }
static inline QString yesAttributeValue() { return QStringLiteral("yes"); }
static inline QString trueAttributeValue() { return QStringLiteral("true"); }
static inline QString falseAttributeValue() { return QStringLiteral("false"); }

static bool isTypeEntry(StackElement el)
{
    return el >= StackElement::FirstTypeEntry && el <= StackElement::LastTypeEntry;
}

static bool isComplexTypeEntry(StackElement el)
{
    return el >= StackElement::FirstTypeEntry && el <= StackElement::LastComplexTypeEntry;
}

static bool isDocumentation(StackElement el)
{
    return el >= StackElement::FirstDocumentation && el <= StackElement::LastDocumentation;
}

static QList<CustomConversion *> customConversionsForReview;

// Set a regular expression for rejection from text. By legacy, those are fixed
// strings, except for '*' meaning 'match all'. Enclosing in "^..$"
// indicates regular expression.
static bool setRejectionRegularExpression(const QString &patternIn,
                                          QRegularExpression *re,
                                          QString *errorMessage)
{
    QString pattern;
    if (patternIn.startsWith(u'^') && patternIn.endsWith(u'$'))
        pattern = patternIn;
    else if (patternIn == u"*")
        pattern = QStringLiteral("^.*$");
    else
        pattern = u'^' + QRegularExpression::escape(patternIn) + u'$';
    re->setPattern(pattern);
    if (!re->isValid()) {
        *errorMessage = msgInvalidRegularExpression(patternIn, re->errorString());
        return false;
    }
    return true;
}

// Extract a snippet from a file within annotation "// @snippet label".
std::optional<QString>
    extractSnippet(const QString &code, const QString &snippetLabel)
{
    if (snippetLabel.isEmpty())
        return code;
    const QString pattern = QStringLiteral(R"(^\s*//\s*@snippet\s+)")
        + QRegularExpression::escape(snippetLabel)
        + QStringLiteral(R"(\s*$)");
    const QRegularExpression snippetRe(pattern);
    Q_ASSERT(snippetRe.isValid());

    bool useLine = false;
    bool foundLabel = false;
    QString result;
    const auto lines = QStringView{code}.split(u'\n');
    for (const auto &line : lines) {
        if (snippetRe.match(line).hasMatch()) {
            foundLabel = true;
            useLine = !useLine;
            if (!useLine)
                break; // End of snippet reached
        } else if (useLine)
            result += line.toString() + u'\n';
    }
    if (!foundLabel)
        return {};
    return CodeSnipAbstract::fixSpaces(result);
}

template <class EnumType, Qt::CaseSensitivity cs = Qt::CaseInsensitive>
struct EnumLookup
{
    QStringView name;
    EnumType value;
};

template <class EnumType, Qt::CaseSensitivity cs>
bool operator==(const EnumLookup<EnumType, cs> &e1, const EnumLookup<EnumType, cs> &e2)
{
    return e1.name.compare(e2.name, cs) == 0;
}

template <class EnumType, Qt::CaseSensitivity cs>
bool operator<(const EnumLookup<EnumType, cs> &e1, const EnumLookup<EnumType, cs> &e2)
{
    return e1.name.compare(e2.name, cs) < 0;
}

// Helper macros to define lookup functions that take a QStringView needle
// and an optional default return value.
#define ENUM_LOOKUP_BEGIN(EnumType, caseSensitivity, functionName) \
static std::optional<EnumType> functionName(QStringView needle) \
{ \
    using HaystackEntry = EnumLookup<EnumType, caseSensitivity>; \
    static const HaystackEntry haystack[] =

#define ENUM_LOOKUP_LINEAR_SEARCH() \
    const auto end = haystack + sizeof(haystack) / sizeof(haystack[0]); \
    const auto it = std::find(haystack, end, HaystackEntry{needle, {} }); \
    if (it != end) \
        return it->value; \
    return {}; \
}

#define ENUM_LOOKUP_BINARY_SEARCH() \
    const auto end = haystack + sizeof(haystack) / sizeof(haystack[0]); \
    const HaystackEntry needleEntry{needle, {} }; \
    const auto lb = std::lower_bound(haystack, end, needleEntry); \
    if (lb != end && *lb == needleEntry) \
        return lb->value; \
    return {}; \
}

ENUM_LOOKUP_BEGIN(TypeSystem::AllowThread, Qt::CaseInsensitive,
                  allowThreadFromAttribute)
    {
        {u"yes", TypeSystem::AllowThread::Allow},
        {u"true", TypeSystem::AllowThread::Allow},
        {u"auto", TypeSystem::AllowThread::Auto},
        {u"no", TypeSystem::AllowThread::Disallow},
        {u"false", TypeSystem::AllowThread::Disallow},
    };
ENUM_LOOKUP_LINEAR_SEARCH()


ENUM_LOOKUP_BEGIN(TypeSystem::BoolCast, Qt::CaseInsensitive,
                  boolCastFromAttribute)
    {
        {u"yes", TypeSystem::BoolCast::Enabled},
        {u"true", TypeSystem::BoolCast::Enabled},
        {u"no", TypeSystem::BoolCast::Disabled},
        {u"false", TypeSystem::BoolCast::Disabled},
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(TypeSystem::QtMetaTypeRegistration, Qt::CaseSensitive,
                  qtMetaTypeFromAttribute)
    {
        {u"yes", TypeSystem::QtMetaTypeRegistration::Enabled},
        {u"true", TypeSystem::QtMetaTypeRegistration::Enabled},
        {u"base", TypeSystem::QtMetaTypeRegistration::BaseEnabled},
        {u"no", TypeSystem::QtMetaTypeRegistration::Disabled},
        {u"false", TypeSystem::QtMetaTypeRegistration::Disabled},
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(TypeSystem::Language, Qt::CaseInsensitive,
                  languageFromAttribute)
    {
        {u"all", TypeSystem::All}, // sorted!
        {u"native", TypeSystem::NativeCode}, // em algum lugar do cpp
        {u"shell", TypeSystem::ShellCode}, // coloca no header, mas antes da declaracao da classe
        {u"target", TypeSystem::TargetLangCode}  // em algum lugar do cpp
    };
ENUM_LOOKUP_BINARY_SEARCH()

ENUM_LOOKUP_BEGIN(TypeSystem::Ownership, Qt::CaseInsensitive,
                   ownershipFromFromAttribute)
    {
        {u"target", TypeSystem::TargetLangOwnership},
        {u"c++", TypeSystem::CppOwnership},
        {u"default", TypeSystem::DefaultOwnership}
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(AddedFunction::Access, Qt::CaseInsensitive,
                  addedFunctionAccessFromAttribute)
    {
        {u"public", AddedFunction::Public},
        {u"protected", AddedFunction::Protected},
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(FunctionModification::ModifierFlag, Qt::CaseSensitive,
                  modifierFromAttribute)
    {
        {u"private", FunctionModification::Private},
        {u"public", FunctionModification::Public},
        {u"protected", FunctionModification::Protected},
        {u"friendly", FunctionModification::Friendly},
        {u"rename", FunctionModification::Rename},
        {u"final", FunctionModification::Final},
        {u"non-final", FunctionModification::NonFinal}
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(ReferenceCount::Action, Qt::CaseInsensitive,
                  referenceCountFromAttribute)
    {
        {u"add", ReferenceCount::Add},
        {u"add-all", ReferenceCount::AddAll},
        {u"remove", ReferenceCount::Remove},
        {u"set", ReferenceCount::Set},
        {u"ignore", ReferenceCount::Ignore}
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(ArgumentOwner::Action, Qt::CaseInsensitive,
                  argumentOwnerActionFromAttribute)
    {
        {u"add", ArgumentOwner::Add},
        {u"remove", ArgumentOwner::Remove}
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(TypeSystem::CodeSnipPosition, Qt::CaseInsensitive,
                  codeSnipPositionFromAttribute)
    {
        {u"beginning", TypeSystem::CodeSnipPositionBeginning},
        {u"end", TypeSystem::CodeSnipPositionEnd},
        {u"declaration", TypeSystem::CodeSnipPositionDeclaration}
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(Include::IncludeType, Qt::CaseInsensitive,
                  locationFromAttribute)
    {
        {u"global", Include::IncludePath},
        {u"local", Include::LocalPath},
        {u"target", Include::TargetLangImport}
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(TypeSystem::DocModificationMode, Qt::CaseInsensitive,
                  docModificationFromAttribute)
    {
        {u"append", TypeSystem::DocModificationAppend},
        {u"prepend", TypeSystem::DocModificationPrepend},
        {u"replace", TypeSystem::DocModificationReplace}
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(ContainerTypeEntry::ContainerKind, Qt::CaseSensitive,
                  containerTypeFromAttribute)
    {
        {u"list", ContainerTypeEntry::ListContainer},
        {u"string-list", ContainerTypeEntry::ListContainer},
        {u"linked-list", ContainerTypeEntry::ListContainer},
        {u"vector", ContainerTypeEntry::ListContainer},
        {u"stack", ContainerTypeEntry::ListContainer},
        {u"queue", ContainerTypeEntry::ListContainer},
        {u"set", ContainerTypeEntry::SetContainer},
        {u"map", ContainerTypeEntry::MapContainer},
        {u"multi-map", ContainerTypeEntry::MultiMapContainer},
        {u"hash", ContainerTypeEntry::MapContainer},
        {u"multi-hash", ContainerTypeEntry::MultiMapContainer},
        {u"pair", ContainerTypeEntry::PairContainer}
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(TypeRejection::MatchType, Qt::CaseSensitive,
                  typeRejectionFromAttribute)
    {
        {u"class", TypeRejection::ExcludeClass},
        {u"function-name", TypeRejection::Function},
        {u"field-name", TypeRejection::Field},
        {u"enum-name", TypeRejection::Enum },
        {u"argument-type", TypeRejection::ArgumentType},
        {u"return-type", TypeRejection::ReturnType}
    };
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(TypeSystem::ExceptionHandling, Qt::CaseSensitive,
                  exceptionHandlingFromAttribute)
{
    {u"no", TypeSystem::ExceptionHandling::Off},
    {u"false", TypeSystem::ExceptionHandling::Off},
    {u"auto-off", TypeSystem::ExceptionHandling::AutoDefaultToOff},
    {u"auto-on", TypeSystem::ExceptionHandling::AutoDefaultToOn},
    {u"yes", TypeSystem::ExceptionHandling::On},
    {u"true", TypeSystem::ExceptionHandling::On},
};
ENUM_LOOKUP_LINEAR_SEARCH()

template <class EnumType>
static std::optional<EnumType>
    lookupHashElement(const QHash<QStringView, EnumType> &hash,
                      QStringView needle, Qt::CaseSensitivity cs = Qt::CaseSensitive)
{
    auto end = hash.cend();
    auto it = hash.constFind(needle);
    if (it != end)
        return it.value();
    if (cs == Qt::CaseInsensitive) { // brute force search for the unlikely case mismatch
        for (it = hash.cbegin(); it != end; ++it) {
            if (it.key().compare(needle, cs) == 0)
                return it.value();
        }
    }
    return std::nullopt;
}

using StackElementHash = QHash<QStringView, StackElement>;

static const StackElementHash &stackElementHash()
{
    static const StackElementHash result{
        {u"add-conversion", StackElement::AddConversion},
        {u"add-function", StackElement::AddFunction},
        {u"array", StackElement::Array},
        {u"container-type", StackElement::ContainerTypeEntry},
        {u"conversion-rule", StackElement::ConversionRule},
        {u"custom-constructor", StackElement::Unimplemented},
        {u"custom-destructor", StackElement::Unimplemented},
        {u"custom-type", StackElement::CustomTypeEntry},
        {u"declare-function", StackElement::DeclareFunction},
        {u"define-ownership", StackElement::DefineOwnership},
        {u"enum-type", StackElement::EnumTypeEntry},
        {u"extra-includes", StackElement::ExtraIncludes},
        {u"function", StackElement::FunctionTypeEntry},
        {u"import-file", StackElement::ImportFile},
        {u"include", StackElement::Include},
        {u"inject-code", StackElement::InjectCode},
        {u"inject-documentation", StackElement::InjectDocumentation},
        {u"insert-template", StackElement::InsertTemplate},
        {u"interface-type", StackElement::InterfaceTypeEntry},
        {u"load-typesystem", StackElement::LoadTypesystem},
        {u"modify-argument", StackElement::ModifyArgument},
        {u"modify-documentation", StackElement::ModifyDocumentation},
        {u"modify-field", StackElement::ModifyField},
        {u"modify-function", StackElement::ModifyFunction},
        {u"namespace-type", StackElement::NamespaceTypeEntry},
        {u"native-to-target", StackElement::NativeToTarget},
        {u"no-null-pointer", StackElement::NoNullPointers},
        {u"object-type", StackElement::ObjectTypeEntry},
        {u"parent", StackElement::ParentOwner},
        {u"primitive-type", StackElement::PrimitiveTypeEntry},
        {u"property", StackElement::Property},
        {u"reference-count", StackElement::ReferenceCount},
        {u"reject-enum-value", StackElement::RejectEnumValue},
        {u"rejection", StackElement::Rejection},
        {u"remove-argument", StackElement::RemoveArgument},
        {u"remove-default-expression", StackElement::RemoveDefaultExpression},
        {u"rename", StackElement::Rename}, // ### fixme PySide7: remove
        {u"replace", StackElement::Replace},
        {u"replace-default-expression", StackElement::ReplaceDefaultExpression},
        {u"replace-type", StackElement::ReplaceType},
        {u"smart-pointer-type", StackElement::SmartPointerTypeEntry},
        {u"suppress-warning", StackElement::SuppressedWarning},
        {u"system-include", StackElement::SystemInclude},
        {u"target-to-native", StackElement::TargetToNative},
        {u"template", StackElement::Template},
        {u"typedef-type", StackElement::TypedefTypeEntry},
        {u"typesystem", StackElement::Root},
        {u"value-type", StackElement::ValueTypeEntry},
    };
    return result;
}

static std::optional<StackElement> elementFromTag(QStringView needle)
{
     return lookupHashElement(stackElementHash(), needle,
                              Qt::CaseInsensitive); // FIXME PYSIDE-7: case sensitive
}

static QStringView tagFromElement(StackElement st)
{
    return stackElementHash().key(st);
}

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, StackElement st)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << tagFromElement(st);
    return d;
}
#endif // QT_NO_DEBUG_STREAM

ENUM_LOOKUP_BEGIN(TypeSystem::SnakeCase, Qt::CaseSensitive,
                  snakeCaseFromAttribute)
{
    {u"no", TypeSystem::SnakeCase::Disabled},
    {u"false", TypeSystem::SnakeCase::Disabled},
    {u"yes", TypeSystem::SnakeCase::Enabled},
    {u"true", TypeSystem::SnakeCase::Enabled},
    {u"both", TypeSystem::SnakeCase::Both},
};
ENUM_LOOKUP_LINEAR_SEARCH()

ENUM_LOOKUP_BEGIN(TypeSystem::Visibility, Qt::CaseSensitive,
                  visibilityFromAttribute)
{
    {u"no", TypeSystem::Visibility::Invisible},
    {u"false", TypeSystem::Visibility::Invisible},
    {u"auto", TypeSystem::Visibility::Auto},
    {u"yes", TypeSystem::Visibility::Visible},
    {u"true", TypeSystem::Visibility::Visible},
};
ENUM_LOOKUP_LINEAR_SEARCH()

static int indexOfAttribute(const QXmlStreamAttributes &atts,
                            QStringView name)
{
    for (int i = 0, size = atts.size(); i < size; ++i) {
        if (atts.at(i).qualifiedName() == name)
            return i;
    }
    return -1;
}

static QString msgMissingAttribute(const QString &a)
{
    return u"Required attribute '"_s + a
        + u"' missing."_s;
}

QTextStream &operator<<(QTextStream &str, const QXmlStreamAttribute &attribute)
{
    str << attribute.qualifiedName() << "=\"" << attribute.value() << '"';
    return str;
}

static QString msgInvalidAttributeValue(const QXmlStreamAttribute &attribute)
{
    QString result;
    QTextStream(&result) << "Invalid attribute value:" << attribute;
    return result;
}

static QString msgUnusedAttributes(QStringView tag, const QXmlStreamAttributes &attributes)
{
    QString result;
    QTextStream str(&result);
    str << attributes.size() << " attributes(s) unused on <" << tag << ">: ";
    for (int i = 0, size = attributes.size(); i < size; ++i) {
        if (i)
            str << ", ";
        str << attributes.at(i);
    }
    return result;
}

// QXmlStreamEntityResolver::resolveEntity(publicId, systemId) is not
// implemented; resolve via undeclared entities instead.
class TypeSystemEntityResolver : public QXmlStreamEntityResolver
{
public:
    explicit TypeSystemEntityResolver(const QString &currentPath) :
        m_currentPath(currentPath) {}

    QString resolveUndeclaredEntity(const QString &name) override;

private:
    QString readFile(const QString &entityName, QString *errorMessage) const;

    const QString m_currentPath;
};

QString TypeSystemEntityResolver::readFile(const QString &entityName, QString *errorMessage) const
{
    QString fileName = entityName;
    if (!fileName.contains(u'.'))
        fileName += u".xml"_s;
    QString path = TypeDatabase::instance()->modifiedTypesystemFilepath(fileName, m_currentPath);
    if (!QFileInfo::exists(path)) // PySide6-specific hack
        fileName.prepend(u"typesystem_"_s);
    path = TypeDatabase::instance()->modifiedTypesystemFilepath(fileName, m_currentPath);
    if (!QFileInfo::exists(path)) {
        *errorMessage = u"Unable to resolve: "_s + entityName;
        return QString();
    }
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        *errorMessage = msgCannotOpenForReading(file);
        return QString();
    }
    QString result = QString::fromUtf8(file.readAll()).trimmed();
    // Remove license header comments on which QXmlStreamReader chokes
    if (result.startsWith(u"<!--")) {
        const int commentEnd = result.indexOf(u"-->");
        if (commentEnd != -1) {
            result.remove(0, commentEnd + 3);
            result = result.trimmed();
        }
    }
    return result;
}

QString TypeSystemEntityResolver::resolveUndeclaredEntity(const QString &name)
{
    QString errorMessage;
    const QString result = readFile(name, &errorMessage);
    if (result.isEmpty()) { // The parser will fail and display the line number.
        qCWarning(lcShiboken, "%s",
                  qPrintable(msgCannotResolveEntity(name, errorMessage)));
    }
    return result;
}

// State depending on element stack
enum class ParserState
{
    None,
    PrimitiveTypeNativeToTargetConversion,
    PrimitiveTypeTargetToNativeConversion,
    ArgumentConversion, // Argument conversion rule with class attribute
    ArgumentNativeToTargetConversion,
    ArgumentTargetToNativeConversion,
    FunctionCodeInjection,
    TypeEntryCodeInjection,
    TypeSystemCodeInjection,
    Template
};

TypeSystemParser::TypeSystemParser(const QSharedPointer<TypeDatabaseParserContext> &context,
                                   bool generate) :
    m_context(context),
    m_generate(generate ? TypeEntry::GenerateCode : TypeEntry::GenerateForSubclass)
{
}

TypeSystemParser::~TypeSystemParser() = default;

static QString readerFileName(const ConditionalStreamReader &reader)
{
    const auto *file = qobject_cast<const QFile *>(reader.device());
    return file != nullptr ? file->fileName() : QString();
}

static QString msgReaderMessage(const ConditionalStreamReader &reader,
                                const char *type,
                                const QString &what)
{
    QString message;
    QTextStream str(&message);
    const QString fileName = readerFileName(reader);
    if (fileName.isEmpty())
        str << "<stdin>:";
    else
        str << QDir::toNativeSeparators(fileName) << ':';
    // Use a tab separator like SourceLocation for suppression detection
    str << reader.lineNumber() << ':' << reader.columnNumber()
        << ":\t" << type << ": " << what;
    return message;
}

static QString msgReaderWarning(const ConditionalStreamReader &reader, const QString &what)
{
    return  msgReaderMessage(reader, "Warning", what);
}

static QString msgReaderError(const ConditionalStreamReader &reader, const QString &what)
{
    return  msgReaderMessage(reader, "Error", what);
}

static QString msgUnimplementedElementWarning(const ConditionalStreamReader &reader,
                                              QStringView name)
{
    QString message;
    QTextStream(&message) << "The element \"" << name
        << "\" is not implemented.";
    return msgReaderMessage(reader, "Warning", message);
}

static QString msgUnimplementedAttributeWarning(const ConditionalStreamReader &reader,
                                                QStringView name)
{
    QString message;
    QTextStream(&message) <<  "The attribute \"" << name
        << "\" is not implemented.";
    return msgReaderMessage(reader, "Warning", message);
}

static inline QString msgUnimplementedAttributeWarning(const ConditionalStreamReader &reader,
                                                       const QXmlStreamAttribute &attribute)
{
    return msgUnimplementedAttributeWarning(reader, attribute.qualifiedName());
}

static QString
    msgUnimplementedAttributeValueWarning(const ConditionalStreamReader &reader,
                                          QStringView name, QStringView value)
{
    QString message;
    QTextStream(&message) << "The value \"" << value
        << "\" of the attribute \"" << name << "\" is not implemented.";
    return msgReaderMessage(reader, "Warning", message);
}

static inline
    QString msgUnimplementedAttributeValueWarning(const ConditionalStreamReader &reader,
                                                  const QXmlStreamAttribute &attribute)
{
    return msgUnimplementedAttributeValueWarning(reader,
                                                 attribute.qualifiedName(),
                                                 attribute.value());
}

static bool addRejection(TypeDatabase *database, QXmlStreamAttributes *attributes,
                         QString *errorMessage)
{
    const int classIndex = indexOfAttribute(*attributes, classAttribute());
    if (classIndex == -1) {
        *errorMessage = msgMissingAttribute(classAttribute());
        return false;
    }

    TypeRejection rejection;
    const QString className = attributes->takeAt(classIndex).value().toString();
    if (!setRejectionRegularExpression(className, &rejection.className, errorMessage))
        return false;

    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto &attribute = attributes->at(i);
        const auto name = attribute.qualifiedName();
        const auto typeOpt = typeRejectionFromAttribute(name);
        if (!typeOpt.has_value()) {
            *errorMessage = msgInvalidAttributeValue(attribute);
            return false;
        }
        switch (typeOpt.value()) {
        case TypeRejection::Function:
        case TypeRejection::Field:
        case TypeRejection::Enum:
        case TypeRejection::ArgumentType:
        case TypeRejection::ReturnType: {
            const QString pattern = attributes->takeAt(i).value().toString();
            if (!setRejectionRegularExpression(pattern, &rejection.pattern, errorMessage))
                return false;
            rejection.matchType = typeOpt.value();
            database->addRejection(rejection);
            return true;
        }
        case TypeRejection::ExcludeClass:
            break;
        }
    }

    // Special case: When all fields except class are empty, completely exclude class
    if (className == u"*") {
        *errorMessage = u"bad reject entry, neither 'class', 'function-name'"
                         " nor 'field' specified"_s;
        return false;
    }
    rejection.matchType = TypeRejection::ExcludeClass;
    database->addRejection(rejection);
    return true;
}

bool TypeSystemParser::parse(ConditionalStreamReader &reader)
{
    m_error.clear();
    m_currentPath.clear();
    m_currentFile.clear();
    return parseXml(reader);
}

bool TypeSystemParser::parseXml(ConditionalStreamReader &reader)
{
    const QString fileName = readerFileName(reader);
    if (!fileName.isEmpty()) {
        QFileInfo fi(fileName);
        m_currentPath = fi.absolutePath();
        m_currentFile = fi.absoluteFilePath();
    }
    m_entityResolver.reset(new TypeSystemEntityResolver(m_currentPath));
    reader.setEntityResolver(m_entityResolver.data());

    while (!reader.atEnd()) {
        switch (reader.readNext()) {
        case QXmlStreamReader::NoToken:
        case QXmlStreamReader::Invalid:
            m_error = msgReaderError(reader, reader.errorString());
            return false;
        case QXmlStreamReader::StartElement: {
            const auto elementTypeOpt = elementFromTag(reader.name());
            if (!elementTypeOpt.has_value()) {
                m_error = u"Unknown tag name: '"_s + reader.name().toString() + u'\'';
                return false;
            }
            m_stack.push(elementTypeOpt.value());
            if (!startElement(reader, m_stack.top())) {
                m_error = msgReaderError(reader, m_error);
                return false;
            }
        }
            break;
        case QXmlStreamReader::EndElement:
            if (!endElement(m_stack.top())) {
                m_error = msgReaderError(reader, m_error);
                return false;
            }
            m_stack.pop();
            break;
        case QXmlStreamReader::Characters:
            if (!characters(reader.text())) {
                m_error = msgReaderError(reader, m_error);
                return false;
            }
            break;
        case QXmlStreamReader::StartDocument:
        case QXmlStreamReader::EndDocument:
        case QXmlStreamReader::Comment:
        case QXmlStreamReader::DTD:
        case QXmlStreamReader::EntityReference:
        case QXmlStreamReader::ProcessingInstruction:
            break;
        }
    }
    return true;
}

bool TypeSystemParser::endElement(StackElement element)
{
    if (m_ignoreDepth) {
        --m_ignoreDepth;
        return true;
    }

    if (m_currentDroppedEntryDepth != 0) {
        --m_currentDroppedEntryDepth;
        return true;
    }

    if (element == StackElement::ImportFile)
        return true;

    if (m_contextStack.isEmpty())
        return true;

    const auto &top = m_contextStack.top();

    switch (element) {
    case StackElement::Unimplemented:
        return true;
    case StackElement::Root:
        if (m_generate == TypeEntry::GenerateCode) {
            TypeDatabase::instance()->addGlobalUserFunctions(top->addedFunctions);
            TypeDatabase::instance()->addGlobalUserFunctionModifications(top->functionMods);
            for (CustomConversion *customConversion : qAsConst(customConversionsForReview)) {
                const CustomConversion::TargetToNativeConversions &toNatives = customConversion->targetToNativeConversions();
                for (CustomConversion::TargetToNativeConversion *toNative : toNatives)
                    toNative->setSourceType(m_context->db->findType(toNative->sourceTypeName()));
            }
        }
        purgeEmptyCodeSnips(&top->entry->codeSnips());
        break;
    case StackElement::FunctionTypeEntry:
        TypeDatabase::instance()->addGlobalUserFunctionModifications(top->functionMods);
        break;
    case StackElement::ObjectTypeEntry:
    case StackElement::ValueTypeEntry:
    case StackElement::InterfaceTypeEntry:
    case StackElement::ContainerTypeEntry:
    case StackElement::NamespaceTypeEntry: {
        Q_ASSERT(top->entry);
        Q_ASSERT(top->entry->isComplex());
        auto *centry = static_cast<ComplexTypeEntry *>(top->entry);
        purgeEmptyCodeSnips(&centry->codeSnips());
        centry->setAddedFunctions(top->addedFunctions);
        centry->setFunctionModifications(top->functionMods);
        centry->setFieldModifications(top->fieldMods);
        centry->setDocModification(top->docModifications);
    }
    break;

    case StackElement::TypedefTypeEntry: {
        auto *centry = static_cast<TypedefEntry *>(top->entry)->target();
        centry->setAddedFunctions(centry->addedFunctions() + top->addedFunctions);
        centry->setFunctionModifications(centry->functionModifications() + top->functionMods);
        centry->setFieldModifications(centry->fieldModifications() + top->fieldMods);
        centry->setCodeSnips(centry->codeSnips() + top->entry->codeSnips());
        centry->setDocModification(centry->docModifications() + top->docModifications);
    }
    break;

    case StackElement::AddFunction:
    case StackElement::DeclareFunction: {
        // Leaving add-function: Assign all modifications to the added function
        const int modIndex = top->addedFunctionModificationIndex;
        top->addedFunctionModificationIndex = -1;
        Q_ASSERT(modIndex >= 0);
        Q_ASSERT(!top->addedFunctions.isEmpty());
        while (modIndex < top->functionMods.size())
            top->addedFunctions.last()->modifications.append(top->functionMods.takeAt(modIndex));
    }
    break;
    case StackElement::NativeToTarget:
    case StackElement::AddConversion:
        switch (parserState()) {
        case ParserState::PrimitiveTypeNativeToTargetConversion:
        case ParserState::PrimitiveTypeTargetToNativeConversion:
            if (auto *customConversion = top->entry->customConversion()) {
                QString code = top->conversionCodeSnips.constLast().code();
                if (element == StackElement::AddConversion) {
                    if (customConversion->targetToNativeConversions().isEmpty()) {
                        m_error = u"CustomConversion's target to native conversions missing."_s;
                        return false;
                    }
                    customConversion->targetToNativeConversions().last()->setConversion(code);
                } else {
                    customConversion->setNativeToTargetConversion(code);
                }
            } else {
                m_error = u"CustomConversion object is missing."_s;
                return false;
            }
            break;

        case ParserState::ArgumentNativeToTargetConversion: {
            top->conversionCodeSnips.last().language = TypeSystem::TargetLangCode;
            auto &lastArgMod = m_contextStack.top()->functionMods.last().argument_mods().last();
            lastArgMod.conversionRules().append(top->conversionCodeSnips.constLast());
        }
            break;
        case ParserState::ArgumentTargetToNativeConversion: {
            top->conversionCodeSnips.last().language = TypeSystem::NativeCode;
            auto &lastArgMod = m_contextStack.top()->functionMods.last().argument_mods().last();
            lastArgMod.conversionRules().append(top->conversionCodeSnips.constLast());
        }
            break;
        default:
            break;
        }
        top->conversionCodeSnips.clear();
        break;

    case StackElement::EnumTypeEntry:
        top->entry->setDocModification(top->docModifications);
        top->docModifications = DocModificationList();
        m_currentEnum = nullptr;
        break;
    case StackElement::Template:
        m_context->db->addTemplate(m_templateEntry);
        m_templateEntry = nullptr;
        break;
    case StackElement::InsertTemplate:
        if (auto *snip = injectCodeTarget(1))
            snip->addTemplateInstance(m_templateInstance);
        m_templateInstance.reset();
        break;

    case StackElement::ModifyArgument:
        purgeEmptyCodeSnips(&top->functionMods.last().argument_mods().last().conversionRules());
        break;

    default:
        break;
    }

    if (isTypeEntry(element) || element == StackElement::Root)
        m_contextStack.pop();

    return true;
}

ParserState TypeSystemParser::parserState(qsizetype offset) const
{
    const auto stackSize = m_stack.size() - offset;
    if (stackSize <= 0 || m_contextStack.isEmpty())
        return ParserState::None;

    const auto last = stackSize - 1;

    switch (m_stack.at(last)) {
        // Primitive entry with conversion rule
    case StackElement::NativeToTarget: // <conversion-rule><native-to-target>
        if (stackSize > 2 && m_stack.at(last - 2) == StackElement::ModifyArgument)
            return ParserState::ArgumentNativeToTargetConversion;
        return ParserState::PrimitiveTypeNativeToTargetConversion;

    case StackElement::AddConversion: // <conversion-rule><target-to-native><add-conversion>
        if (stackSize > 3 && m_stack.at(last - 3) == StackElement::ModifyArgument)
            return ParserState::ArgumentTargetToNativeConversion;
        return ParserState::PrimitiveTypeTargetToNativeConversion;

    case StackElement::ConversionRule:
        if (stackSize > 1 && m_stack.at(last - 1) == StackElement::ModifyArgument)
            return ParserState::ArgumentConversion;
        break;

    case StackElement::InjectCode:
        switch (m_stack.value(last - 1, StackElement::None)) {
        case StackElement::Root:
            return ParserState::TypeSystemCodeInjection;
        case StackElement::ModifyFunction:
        case StackElement::AddFunction:
            return ParserState::FunctionCodeInjection;
        case StackElement::NamespaceTypeEntry:
        case StackElement::ObjectTypeEntry:
        case StackElement::ValueTypeEntry:
        case StackElement::InterfaceTypeEntry:
            return ParserState::TypeEntryCodeInjection;
        default:
            break;
        }
        break;

    case StackElement::Template:
        return ParserState::Template;

    default:
        break;
    }

    return ParserState::None;
}

// Return where to add injected code depending on elements.
CodeSnipAbstract *TypeSystemParser::injectCodeTarget(qsizetype offset) const
{
    const auto state = parserState(offset);
    if (state == ParserState::None)
        return nullptr;

    const auto &top = m_contextStack.top();
    switch (state) {
    case ParserState::PrimitiveTypeNativeToTargetConversion:
    case ParserState::PrimitiveTypeTargetToNativeConversion:
    case ParserState::ArgumentNativeToTargetConversion:
    case ParserState::ArgumentTargetToNativeConversion:
        return &top->conversionCodeSnips.last();
    case ParserState::ArgumentConversion:
        return &top->functionMods.last().argument_mods().last().conversionRules().last();
    case ParserState::FunctionCodeInjection: {
        auto &funcMod = top->functionMods.last();
        funcMod.setModifierFlag(FunctionModification::CodeInjection);
        return &funcMod.snips().last();
    }
    case ParserState::TypeEntryCodeInjection:
    case ParserState::TypeSystemCodeInjection:
        return &top->entry->codeSnips().last();
    case ParserState::Template:
        return m_templateEntry;
    default:
        break;
    }

    return nullptr;
}

template <class String> // QString/QStringRef
bool TypeSystemParser::characters(const String &ch)
{
    const auto stackSize = m_stack.size();
    if (m_currentDroppedEntryDepth != 0 || m_ignoreDepth != 0
        || stackSize == 0 || m_stack.top() == StackElement::Unimplemented) {
        return true;
    }

    const StackElement type =  m_stack.top();

    if (type == StackElement::Template) {
        m_templateEntry->addCode(ch);
        return true;
    }

    if (m_contextStack.isEmpty()) {
        m_error = msgNoRootTypeSystemEntry();
        return false;
    }

    if (auto *snip = injectCodeTarget()) {
        snip->addCode(ch);
        return true;
    }

    if (isDocumentation(type))
        m_contextStack.top()->docModifications.last().setCode(ch);

    return true;
}

bool TypeSystemParser::importFileElement(const QXmlStreamAttributes &atts)
{
    const QString fileName = atts.value(nameAttribute()).toString();
    if (fileName.isEmpty()) {
        m_error = u"Required attribute 'name' missing for include-file tag."_s;
        return false;
    }

    QFile file(fileName);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        file.setFileName(u":/trolltech/generator/"_s + fileName);
        if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
            m_error = msgCannotOpenForReading(file);
            return false;
        }
    }

    const auto quoteFrom = atts.value(quoteAfterLineAttribute());
    bool foundFromOk = quoteFrom.isEmpty();
    bool from = quoteFrom.isEmpty();

    const auto quoteTo = atts.value(quoteBeforeLineAttribute());
    bool foundToOk = quoteTo.isEmpty();
    bool to = true;

    QTextStream in(&file);
    while (!in.atEnd()) {
        QString line = in.readLine();
        if (from && to && line.contains(quoteTo)) {
            to = false;
            foundToOk = true;
            break;
        }
        if (from && to)
            characters(line + u'\n');
        if (!from && line.contains(quoteFrom)) {
            from = true;
            foundFromOk = true;
        }
    }
    if (!foundFromOk || !foundToOk) {
        QString fromError = QStringLiteral("Could not find quote-after-line='%1' in file '%2'.")
                                           .arg(quoteFrom.toString(), fileName);
        QString toError = QStringLiteral("Could not find quote-before-line='%1' in file '%2'.")
                                         .arg(quoteTo.toString(), fileName);

        if (!foundToOk)
            m_error = toError;
        if (!foundFromOk)
            m_error = fromError;
        if (!foundFromOk && !foundToOk)
            m_error = fromError + u' ' + toError;
        return false;
    }

    return true;
}

static bool convertBoolean(QStringView value, const QString &attributeName, bool defaultValue)
{
    if (value.compare(trueAttributeValue(), Qt::CaseInsensitive) == 0
        || value.compare(yesAttributeValue(), Qt::CaseInsensitive) == 0) {
        return true;
    }
    if (value.compare(falseAttributeValue(), Qt::CaseInsensitive) == 0
        || value.compare(noAttributeValue(), Qt::CaseInsensitive) == 0) {
        return false;
    }
    const QString warn = QStringLiteral("Boolean value '%1' not supported in attribute '%2'. Use 'yes' or 'no'. Defaulting to '%3'.")
                                      .arg(value)
                                      .arg(attributeName,
                                           defaultValue ? yesAttributeValue() : noAttributeValue());

    qCWarning(lcShiboken).noquote().nospace() << warn;
    return defaultValue;
}

static bool convertRemovalAttribute(QStringView value)
{
    return value == u"all" // Legacy
        || convertBoolean(value, removeAttribute(), false);
}

// Check whether an entry should be dropped, allowing for dropping the module
// name (match 'Class' and 'Module.Class').
static bool shouldDropTypeEntry(const TypeDatabase *db,
                                const TypeSystemParser::ContextStack &stack                                ,
                                QString name)
{
    for (auto i = stack.size() - 1; i >= 0; --i) {
        if (auto *entry = stack.at(i)->entry) {
            if (entry->type() == TypeEntry::TypeSystemType) {
                if (db->shouldDropTypeEntry(name)) // Unqualified
                    return true;
            }
            name.prepend(u'.');
            name.prepend(entry->name());
        }
    }
    return db->shouldDropTypeEntry(name);
}

// Returns empty string if there's no error.
static QString checkSignatureError(const QString& signature, const QString& tag)
{
    QString funcName = signature.left(signature.indexOf(u'(')).trimmed();
    static const QRegularExpression whiteSpace(QStringLiteral("\\s"));
    Q_ASSERT(whiteSpace.isValid());
    if (!funcName.startsWith(u"operator ") && funcName.contains(whiteSpace)) {
        return QString::fromLatin1("Error in <%1> tag signature attribute '%2'.\n"
                                   "White spaces aren't allowed in function names, "
                                   "and return types should not be part of the signature.")
                                   .arg(tag, signature);
    }
    return QString();
}

inline const TypeEntry *TypeSystemParser::currentParentTypeEntry() const
{
    const auto size = m_contextStack.size();
    return size > 1 ? m_contextStack.at(size - 2)->entry : nullptr;
}

bool TypeSystemParser::checkRootElement()
{
    for (auto i = m_contextStack.size() - 1; i >= 0; --i) {
        auto *e = m_contextStack.at(i)->entry;
        if (e && e->isTypeSystem())
            return true;
    }
    m_error = msgNoRootTypeSystemEntry();
    return false;
}

static TypeEntry *findViewedType(const QString &name)
{
    const auto range = TypeDatabase::instance()->entries().equal_range(name);
    for (auto i = range.first; i != range.second; ++i) {
        switch (i.value()->type()) {
        case TypeEntry::BasicValueType:
        case TypeEntry::PrimitiveType:
        case TypeEntry::ContainerType:
        case TypeEntry::ObjectType:
            return i.value();
        default:
            break;
        }
    }
    return nullptr;
}

bool TypeSystemParser::applyCommonAttributes(const ConditionalStreamReader &reader, TypeEntry *type,
                                             QXmlStreamAttributes *attributes)
{
    type->setSourceLocation(SourceLocation(m_currentFile,
                                           reader.lineNumber()));
    type->setCodeGeneration(m_generate);
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name ==  u"revision") {
            type->setRevision(attributes->takeAt(i).value().toInt());
        } else if (name == u"view-on") {
            const QString name = attributes->takeAt(i).value().toString();
            TypeEntry *views = findViewedType(name);
            if (views == nullptr) {
                m_error = msgCannotFindView(name, type->name());
                return false;
            }
            type->setViewOn(views);
        }
    }
    return true;
}

CustomTypeEntry *TypeSystemParser::parseCustomTypeEntry(const ConditionalStreamReader &,
                                                        const QString &name,
                                                        const QVersionNumber &since,
                                                        QXmlStreamAttributes *attributes)
{
    if (!checkRootElement())
        return nullptr;
    auto *result = new CustomTypeEntry(name, since, m_contextStack.top()->entry);
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == checkFunctionAttribute())
            result->setCheckFunction(attributes->takeAt(i).value().toString());
    }
    return result;
}

FlagsTypeEntry *
    TypeSystemParser::parseFlagsEntry(const ConditionalStreamReader &reader,
                             EnumTypeEntry *enumEntry, QString flagName,
                             const QVersionNumber &since,
                             QXmlStreamAttributes *attributes)

{
    if (!checkRootElement())
        return nullptr;
    auto ftype = new FlagsTypeEntry(u"QFlags<"_s + enumEntry->name() + u'>',
                                    since,
                                    currentParentTypeEntry()->typeSystemTypeEntry());
    ftype->setOriginator(enumEntry);
    ftype->setTargetLangPackage(enumEntry->targetLangPackage());
    // Try toenumEntry get the guess the qualified flag name
    if (!flagName.contains(colonColon())) {
        auto eq = enumEntry->qualifier();
        if (!eq.isEmpty())
            flagName.prepend(eq + colonColon());
    }

    ftype->setOriginalName(flagName);
    if (!applyCommonAttributes(reader, ftype, attributes))
        return nullptr;

    QStringList lst = flagName.split(colonColon());
    const QString name = lst.takeLast();
    const QString targetLangFlagName = lst.join(u'.');
    const QString &targetLangQualifier = enumEntry->targetLangQualifier();
    if (targetLangFlagName != targetLangQualifier) {
        qCWarning(lcShiboken).noquote().nospace()
            << QStringLiteral("enum %1 and flags %2 (%3) differ in qualifiers")
                              .arg(targetLangQualifier, lst.value(0), targetLangFlagName);
    }

    ftype->setFlagsName(name);
    enumEntry->setFlags(ftype);

    m_context->db->addFlagsType(ftype);
    m_context->db->addType(ftype);

    const int revisionIndex =
        indexOfAttribute(*attributes, u"flags-revision");
    ftype->setRevision(revisionIndex != -1
                       ? attributes->takeAt(revisionIndex).value().toInt()
                       : enumEntry->revision());
    return ftype;
}

SmartPointerTypeEntry *
    TypeSystemParser::parseSmartPointerEntry(const ConditionalStreamReader &reader,
                                    const QString &name, const QVersionNumber &since,
                                    QXmlStreamAttributes *attributes)
{
    if (!checkRootElement())
        return nullptr;
    QString smartPointerType;
    QString getter;
    QString refCountMethodName;
    QString valueCheckMethod;
    QString nullCheckMethod;
    QString resetMethod;
    QString instantiations;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == u"type") {
             smartPointerType = attributes->takeAt(i).value().toString();
        } else if (name == u"getter") {
            getter = attributes->takeAt(i).value().toString();
        } else if (name == u"ref-count-method") {
            refCountMethodName = attributes->takeAt(i).value().toString();
        } else if (name == u"instantiations") {
            instantiations = attributes->takeAt(i).value().toString();
        } else if (name == u"value-check-method") {
            valueCheckMethod = attributes->takeAt(i).value().toString();
        } else if (name == u"null-check-method") {
            nullCheckMethod = attributes->takeAt(i).value().toString();
        } else if (name == u"reset-method") {
            resetMethod =  attributes->takeAt(i).value().toString();
        }
    }

    if (smartPointerType.isEmpty()) {
        m_error = u"No type specified for the smart pointer. Currently supported types: 'shared',"_s;
        return nullptr;
    }
    if (smartPointerType != u"shared") {
        m_error = u"Currently only the 'shared' type is supported."_s;
        return nullptr;
    }

    if (getter.isEmpty()) {
        m_error = u"No function getter name specified for getting the raw pointer held by the smart pointer."_s;
        return nullptr;
    }

    QString signature = getter + u"()"_s;
    signature = TypeDatabase::normalizedSignature(signature);
    if (signature.isEmpty()) {
        m_error = u"No signature for the smart pointer getter found."_s;
        return nullptr;
    }

    QString errorString = checkSignatureError(signature,
                                              u"smart-pointer-type"_s);
    if (!errorString.isEmpty()) {
        m_error = errorString;
        return nullptr;
    }

    auto *type = new SmartPointerTypeEntry(name, getter, smartPointerType,
                                           refCountMethodName, since, currentParentTypeEntry());
    if (!applyCommonAttributes(reader, type, attributes))
        return nullptr;
    applyComplexTypeAttributes(reader, type, attributes);
    type->setNullCheckMethod(nullCheckMethod);
    type->setValueCheckMethod(valueCheckMethod);
    type->setResetMethod(resetMethod);
    m_context->smartPointerInstantiations.insert(type, instantiations);
    return type;
}

PrimitiveTypeEntry *
    TypeSystemParser::parsePrimitiveTypeEntry(const ConditionalStreamReader &reader,
                                     const QString &name, const QVersionNumber &since,
                                     QXmlStreamAttributes *attributes)
{
    if (!checkRootElement())
        return nullptr;
    auto *type = new PrimitiveTypeEntry(name, since, currentParentTypeEntry());
    QString targetLangApiName;
    if (!applyCommonAttributes(reader, type, attributes))
        return nullptr;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == targetLangNameAttribute()) {
            type->setTargetLangName(attributes->takeAt(i).value().toString());
        } else if (name == u"target-lang-api-name") {
            targetLangApiName = attributes->takeAt(i).value().toString();
        } else if (name == preferredConversionAttribute()) {
            qCWarning(lcShiboken, "%s",
                      qPrintable(msgUnimplementedAttributeWarning(reader, name)));
        } else if (name == preferredTargetLangTypeAttribute()) {
            const bool v = convertBoolean(attributes->takeAt(i).value(),
                                          preferredTargetLangTypeAttribute(), true);
            type->setPreferredTargetLangType(v);
        } else if (name == u"default-constructor") {
             type->setDefaultConstructor(attributes->takeAt(i).value().toString());
        }
    }

    if (!targetLangApiName.isEmpty()) {
        auto *e = m_context->db->findType(targetLangApiName);
        if (e == nullptr || !e->isCustom()) {
               m_error = msgInvalidTargetLanguageApiName(targetLangApiName);
               return nullptr;
        }
        type->setTargetLangApiType(static_cast<CustomTypeEntry *>(e));
    }
    type->setTargetLangPackage(m_defaultPackage);
    return type;
}

// "int:QList_int;QString:QList_QString"
static bool parseOpaqueContainers(QStringView s, ContainerTypeEntry *cte)
{
    const auto entries = s.split(u';');
    for (const auto &entry : entries) {
        const auto values = entry.split(u':');
        if (values.size() != 2)
            return false;
        QString instantiation = values.at(0).trimmed().toString();
        QString name = values.at(1).trimmed().toString();
        cte->addOpaqueContainer({instantiation, name});
    }
    return true;
}

ContainerTypeEntry *
    TypeSystemParser::parseContainerTypeEntry(const ConditionalStreamReader &reader,
                                     const QString &name, const QVersionNumber &since,
                                     QXmlStreamAttributes *attributes)
{
    if (!checkRootElement())
        return nullptr;
    const int typeIndex = indexOfAttribute(*attributes, u"type");
    if (typeIndex == -1) {
        m_error = u"no 'type' attribute specified"_s;
        return nullptr;
    }
    const auto typeName = attributes->at(typeIndex).value();
    const auto containerTypeOpt = containerTypeFromAttribute(typeName);
    if (!containerTypeOpt.has_value()) {
        m_error = u"there is no container of type "_s + typeName.toString();
        return nullptr;
    }
    attributes->removeAt(typeIndex);
    auto *type = new ContainerTypeEntry(name, containerTypeOpt.value(),
                                        since, currentParentTypeEntry());
    if (!applyCommonAttributes(reader, type, attributes))
        return nullptr;
    applyComplexTypeAttributes(reader, type, attributes);

    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == u"opaque-containers") {
            const auto attribute = attributes->takeAt(i);
            if (!parseOpaqueContainers(attribute.value(), type)) {
                m_error = u"Error parsing the opaque container attribute: \""_s
                          + attribute.value().toString() + u"\"."_s;
                return nullptr;
            }
        }
    }

    return type;
}

EnumTypeEntry *
    TypeSystemParser::parseEnumTypeEntry(const ConditionalStreamReader &reader,
                                const QString &name, const QVersionNumber &since,
                                QXmlStreamAttributes *attributes)
{
    if (!checkRootElement())
        return nullptr;
    auto *entry = new EnumTypeEntry(name, since, currentParentTypeEntry());
    applyCommonAttributes(reader, entry, attributes);
    entry->setTargetLangPackage(m_defaultPackage);

    QString flagNames;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == u"upper-bound") {
            qCWarning(lcShiboken, "%s",
                      qPrintable(msgUnimplementedAttributeWarning(reader, name)));
        } else if (name == u"lower-bound") {
            qCWarning(lcShiboken, "%s",
                      qPrintable(msgUnimplementedAttributeWarning(reader, name)));
        } else if (name == forceIntegerAttribute()) {
            qCWarning(lcShiboken, "%s",
                      qPrintable(msgUnimplementedAttributeWarning(reader, name)));
        } else if (name == extensibleAttribute()) {
            qCWarning(lcShiboken, "%s",
                      qPrintable(msgUnimplementedAttributeWarning(reader, name)));
        } else if (name == flagsAttribute()) {
            flagNames = attributes->takeAt(i).value().toString();
        }
    }

    // put in the flags parallel...
    if (!flagNames.isEmpty()) {
        const QStringList &flagNameList = flagNames.split(u',');
        for (const QString &flagName : flagNameList)
            parseFlagsEntry(reader, entry, flagName.trimmed(), since, attributes);
    }
    return entry;
}


NamespaceTypeEntry *
    TypeSystemParser::parseNamespaceTypeEntry(const ConditionalStreamReader &reader,
                                     const QString &name, const QVersionNumber &since,
                                     QXmlStreamAttributes *attributes)
{
    if (!checkRootElement())
        return nullptr;
    std::unique_ptr<NamespaceTypeEntry> result(new NamespaceTypeEntry(name, since, currentParentTypeEntry()));
    auto visibility = TypeSystem::Visibility::Unspecified;
    applyCommonAttributes(reader, result.get(), attributes);
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto attributeName = attributes->at(i).qualifiedName();
        if (attributeName == u"files") {
            const QString pattern = attributes->takeAt(i).value().toString();
            QRegularExpression re(pattern);
            if (!re.isValid()) {
                m_error = msgInvalidRegularExpression(pattern, re.errorString());
                return nullptr;
            }
            result->setFilePattern(re);
        } else if (attributeName == u"extends") {
            const auto extendsPackageName = attributes->at(i).value();
            auto allEntries = TypeDatabase::instance()->findNamespaceTypes(name);
            auto extendsIt = std::find_if(allEntries.cbegin(), allEntries.cend(),
                                          [extendsPackageName] (const NamespaceTypeEntry *e) {
                                              return e->targetLangPackage() == extendsPackageName;
                                          });
            if (extendsIt == allEntries.cend()) {
                m_error = msgCannotFindNamespaceToExtend(name, extendsPackageName.toString());
                return nullptr;
            }
            result->setExtends(*extendsIt);
            attributes->removeAt(i);
        } else if (attributeName == visibleAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto visibilityOpt = visibilityFromAttribute(attribute.value());
            if (!visibilityOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return nullptr;
            }
            visibility = visibilityOpt.value();
        } else if (attributeName == generateAttribute()) {
            if (!convertBoolean(attributes->takeAt(i).value(), generateAttribute(), true))
                visibility = TypeSystem::Visibility::Invisible;
        } else if (attributeName == generateUsingAttribute()) {
            result->setGenerateUsing(convertBoolean(attributes->takeAt(i).value(), generateUsingAttribute(), true));
        }
    }

    if (visibility != TypeSystem::Visibility::Unspecified)
        result->setVisibility(visibility);
    // Handle legacy "generate" before the common handling
    applyComplexTypeAttributes(reader, result.get(), attributes);

    if (result->extends() && !result->hasPattern()) {
        m_error = msgExtendingNamespaceRequiresPattern(name);
        return nullptr;
    }

    return result.release();
}

ValueTypeEntry *
    TypeSystemParser::parseValueTypeEntry(const ConditionalStreamReader &reader,
                                 const QString &name, const QVersionNumber &since,
                                 QXmlStreamAttributes *attributes)
{
    if (!checkRootElement())
        return nullptr;
    auto *typeEntry = new ValueTypeEntry(name, since, currentParentTypeEntry());
    if (!applyCommonAttributes(reader, typeEntry, attributes))
        return nullptr;
    applyComplexTypeAttributes(reader, typeEntry, attributes);
    const int defaultCtIndex =
        indexOfAttribute(*attributes, u"default-constructor");
    if (defaultCtIndex != -1)
         typeEntry->setDefaultConstructor(attributes->takeAt(defaultCtIndex).value().toString());
    return typeEntry;
}

FunctionTypeEntry *
    TypeSystemParser::parseFunctionTypeEntry(const ConditionalStreamReader &reader,
                                    const QString &name, const QVersionNumber &since,
                                    QXmlStreamAttributes *attributes)
{
    if (!checkRootElement())
        return nullptr;

    QString signature;
    TypeSystem::SnakeCase snakeCase = TypeSystem::SnakeCase::Disabled;

    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == signatureAttribute()) {
            signature = TypeDatabase::normalizedSignature(attributes->takeAt(i).value().toString());
        } else if (name == snakeCaseAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto snakeCaseOpt = snakeCaseFromAttribute(attribute.value());
            if (!snakeCaseOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return nullptr;
            }
            snakeCase = snakeCaseOpt.value();
        }
    }

    if (signature.isEmpty()) {
        m_error =  msgMissingAttribute(signatureAttribute());
        return nullptr;
    }

    TypeEntry *existingType = m_context->db->findType(name);

    if (!existingType) {
        auto *result = new FunctionTypeEntry(name, signature, since, currentParentTypeEntry());
        result->setSnakeCase(snakeCase);
        applyCommonAttributes(reader, result, attributes);
        return result;
    }

    if (existingType->type() != TypeEntry::FunctionType) {
        m_error = QStringLiteral("%1 expected to be a function, but isn't! Maybe it was already declared as a class or something else.")
                 .arg(name);
        return nullptr;
    }

    auto *result = reinterpret_cast<FunctionTypeEntry *>(existingType);
    result->addSignature(signature);
    return result;
}

TypedefEntry *
 TypeSystemParser::parseTypedefEntry(const ConditionalStreamReader &reader,
                                     const QString &name, StackElement topElement,
                                     const QVersionNumber &since,
                                     QXmlStreamAttributes *attributes)
{
    if (!checkRootElement())
        return nullptr;
    if (topElement != StackElement::Root
        && topElement != StackElement::NamespaceTypeEntry) {
        m_error = u"typedef entries must be nested in namespaces or type system."_s;
        return nullptr;
    }
    const int sourceIndex = indexOfAttribute(*attributes, sourceAttribute());
    if (sourceIndex == -1) {
        m_error =  msgMissingAttribute(sourceAttribute());
        return nullptr;
    }
    const QString sourceType = attributes->takeAt(sourceIndex).value().toString();
    auto result = new TypedefEntry(name, sourceType, since, currentParentTypeEntry());
    if (!applyCommonAttributes(reader, result, attributes))
        return nullptr;
    applyComplexTypeAttributes(reader, result, attributes);
    return result;
}

void TypeSystemParser::applyComplexTypeAttributes(const ConditionalStreamReader &reader,
                                         ComplexTypeEntry *ctype,
                                         QXmlStreamAttributes *attributes) const
{
    bool generate = true;
    ctype->setCopyable(ComplexTypeEntry::Unknown);
    auto exceptionHandling = m_exceptionHandling;
    auto allowThread = m_allowThread;

    QString package = m_defaultPackage;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == streamAttribute()) {
            ctype->setStream(convertBoolean(attributes->takeAt(i).value(), streamAttribute(), false));
        } else if (name == privateAttribute()) {
            ctype->setPrivate(convertBoolean(attributes->takeAt(i).value(),
                                             privateAttribute(), false));
        } else if (name == generateAttribute()) {
            generate = convertBoolean(attributes->takeAt(i).value(), generateAttribute(), true);
        } else if (name ==packageAttribute()) {
            package = attributes->takeAt(i).value().toString();
        } else if (name == defaultSuperclassAttribute()) {
            ctype->setDefaultSuperclass(attributes->takeAt(i).value().toString());
        } else if (name == genericClassAttribute()) {
            qCWarning(lcShiboken, "%s",
                      qPrintable(msgUnimplementedAttributeWarning(reader, name)));
            const bool v = convertBoolean(attributes->takeAt(i).value(), genericClassAttribute(), false);
            ctype->setGenericClass(v);
        } else if (name == targetLangNameAttribute()) {
            ctype->setTargetLangName(attributes->takeAt(i).value().toString());
        } else if (name == u"polymorphic-base") {
            ctype->setPolymorphicIdValue(attributes->takeAt(i).value().toString());
        } else if (name == u"polymorphic-id-expression") {
            ctype->setPolymorphicIdValue(attributes->takeAt(i).value().toString());
        } else if (name == copyableAttribute()) {
            const bool v = convertBoolean(attributes->takeAt(i).value(), copyableAttribute(), false);
            ctype->setCopyable(v ? ComplexTypeEntry::CopyableSet : ComplexTypeEntry::NonCopyableSet);
        } else if (name == exceptionHandlingAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto exceptionOpt = exceptionHandlingFromAttribute(attribute.value());
            if (exceptionOpt.has_value()) {
                exceptionHandling = exceptionOpt.value();
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        } else if (name == allowThreadAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto allowThreadOpt = allowThreadFromAttribute(attribute.value());
            if (allowThreadOpt.has_value()) {
                allowThread = allowThreadOpt.value();
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        } else if (name == u"held-type") {
            qCWarning(lcShiboken, "%s",
                      qPrintable(msgUnimplementedAttributeWarning(reader, name)));
        } else if (name == u"hash-function") {
            ctype->setHashFunction(attributes->takeAt(i).value().toString());
        } else if (name == forceAbstractAttribute()) {
            if (convertBoolean(attributes->takeAt(i).value(), forceAbstractAttribute(), false))
                ctype->setTypeFlags(ctype->typeFlags() | ComplexTypeEntry::ForceAbstract);
        } else if (name == deprecatedAttribute()) {
            if (convertBoolean(attributes->takeAt(i).value(), deprecatedAttribute(), false))
                ctype->setTypeFlags(ctype->typeFlags() | ComplexTypeEntry::Deprecated);
        } else if (name == disableWrapperAttribute()) {
            if (convertBoolean(attributes->takeAt(i).value(), disableWrapperAttribute(), false))
                ctype->setTypeFlags(ctype->typeFlags() | ComplexTypeEntry::DisableWrapper);
        } else if (name == deleteInMainThreadAttribute()) {
            if (convertBoolean(attributes->takeAt(i).value(), deleteInMainThreadAttribute(), false))
                ctype->setDeleteInMainThread(true);
        } else if (name == u"target-type") {
            ctype->setTargetType(attributes->takeAt(i).value().toString());
        }  else if (name == snakeCaseAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto snakeCaseOpt = snakeCaseFromAttribute(attribute.value());
            if (snakeCaseOpt.has_value()) {
                ctype->setSnakeCase(snakeCaseOpt.value());
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        }  else if (name == isNullAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto boolCastOpt = boolCastFromAttribute(attribute.value());
            if (boolCastOpt.has_value()) {
                ctype->setIsNullMode(boolCastOpt.value());
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        }  else if (name == operatorBoolAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto boolCastOpt = boolCastFromAttribute(attribute.value());
            if (boolCastOpt.has_value()) {
                ctype->setOperatorBoolMode(boolCastOpt.value());
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        } else if (name == qtMetaTypeAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto qtMetaTypeOpt = qtMetaTypeFromAttribute(attribute.value());
            if (qtMetaTypeOpt.has_value()) {
                ctype->setQtMetaTypeRegistration(qtMetaTypeOpt.value());
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        }
    }

    if (exceptionHandling != TypeSystem::ExceptionHandling::Unspecified)
         ctype->setExceptionHandling(exceptionHandling);
    if (allowThread != TypeSystem::AllowThread::Unspecified)
        ctype->setAllowThread(allowThread);

    // The generator code relies on container's package being empty.
    if (ctype->type() != TypeEntry::ContainerType)
        ctype->setTargetLangPackage(package);

    if (generate)
        ctype->setCodeGeneration(m_generate);
    else
        ctype->setCodeGeneration(TypeEntry::GenerationDisabled);
}

bool TypeSystemParser::parseRenameFunction(const ConditionalStreamReader &,
                                  QString *name, QXmlStreamAttributes *attributes)
{
    QString signature;
    QString rename;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == signatureAttribute()) {
            // Do not remove as it is needed for the type entry later on
            signature = attributes->at(i).value().toString();
        } else if (name == renameAttribute()) {
            rename = attributes->takeAt(i).value().toString();
        }
    }

    if (signature.isEmpty()) {
        m_error = msgMissingAttribute(signatureAttribute());
        return false;
    }

    *name = signature.left(signature.indexOf(u'(')).trimmed();

    QString errorString = checkSignatureError(signature, u"function"_s);
    if (!errorString.isEmpty()) {
        m_error = errorString;
        return false;
    }

    if (!rename.isEmpty()) {
        static const QRegularExpression functionNameRegExp(u"^[a-zA-Z_][a-zA-Z0-9_]*$"_s);
        Q_ASSERT(functionNameRegExp.isValid());
        if (!functionNameRegExp.match(rename).hasMatch()) {
            m_error = u"can not rename '"_s + signature + u"', '"_s
                      + rename + u"' is not a valid function name"_s;
            return false;
        }
        FunctionModification mod;
        if (!mod.setSignature(signature, &m_error))
            return false;
        mod.setRenamedToName(rename);
        mod.setModifierFlag(FunctionModification::Rename);
        m_contextStack.top()->functionMods << mod;
    }
    return true;
}

bool TypeSystemParser::parseInjectDocumentation(const ConditionalStreamReader &, StackElement topElement,
                                       QXmlStreamAttributes *attributes)
{
    const bool validParent = isTypeEntry(topElement)
        || topElement == StackElement::ModifyFunction
        || topElement == StackElement::ModifyField
        || topElement == StackElement::AddFunction;
    if (!validParent) {
        m_error = u"inject-documentation must be inside modify-function, add-function"
                   "modify-field or other tags that creates a type"_s;
        return false;
    }

    TypeSystem::DocModificationMode mode = TypeSystem::DocModificationReplace;
    TypeSystem::Language lang = TypeSystem::NativeCode;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == u"mode") {
            const auto attribute = attributes->takeAt(i);
            const auto modeOpt = docModificationFromAttribute(attribute.value());
            if (!modeOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return false;
            }
            mode = modeOpt.value();
        } else if (name == formatAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto langOpt = languageFromAttribute(attribute.value());
            if (!langOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return false;
            }
            lang = langOpt.value();
        }
    }

    QString signature = isTypeEntry(topElement) ? QString() : m_currentSignature;
    DocModification mod(mode, signature);
    mod.setFormat(lang);
    m_contextStack.top()->docModifications << mod;
    return true;
}

bool TypeSystemParser::parseModifyDocumentation(const ConditionalStreamReader &,
                                       StackElement topElement,
                                       QXmlStreamAttributes *attributes)
{
    const bool validParent = isTypeEntry(topElement)
        || topElement == StackElement::ModifyFunction
        || topElement == StackElement::ModifyField;
    if (!validParent) {
        m_error = u"modify-documentation must be inside modify-function, "
                   "modify-field or other tags that creates a type"_qs;
        return false;
    }

    const int xpathIndex = indexOfAttribute(*attributes, xPathAttribute());
    if (xpathIndex == -1) {
        m_error = msgMissingAttribute(xPathAttribute());
        return false;
    }

    const QString xpath = attributes->takeAt(xpathIndex).value().toString();
    QString signature = isTypeEntry(topElement) ? QString() : m_currentSignature;
    m_contextStack.top()->docModifications
        << DocModification(xpath, signature);
    return true;
}

// m_exceptionHandling
TypeSystemTypeEntry *TypeSystemParser::parseRootElement(const ConditionalStreamReader &,
                                               const QVersionNumber &since,
                                               QXmlStreamAttributes *attributes)
{
    TypeSystem::SnakeCase snakeCase = TypeSystem::SnakeCase::Unspecified;

    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == packageAttribute()) {
            m_defaultPackage = attributes->takeAt(i).value().toString();
        } else if (name == defaultSuperclassAttribute()) {
            m_defaultSuperclass = attributes->takeAt(i).value().toString();
        } else if (name == exceptionHandlingAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto exceptionOpt = exceptionHandlingFromAttribute(attribute.value());
            if (exceptionOpt.has_value()) {
                m_exceptionHandling = exceptionOpt.value();
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        } else if (name == allowThreadAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto allowThreadOpt = allowThreadFromAttribute(attribute.value());
            if (allowThreadOpt.has_value()) {
                m_allowThread = allowThreadOpt.value();
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        } else if (name == snakeCaseAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto snakeCaseOpt = snakeCaseFromAttribute(attribute.value());
            if (snakeCaseOpt.has_value()) {
                snakeCase = snakeCaseOpt.value();
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        }
    }

    if (m_defaultPackage.isEmpty()) { // Extending default, see addBuiltInContainerTypes()
        auto *moduleEntry = const_cast<TypeSystemTypeEntry *>(m_context->db->defaultTypeSystemType());
        Q_ASSERT(moduleEntry);
        m_defaultPackage = moduleEntry->name();
        return moduleEntry;
    }

    auto *moduleEntry =
        const_cast<TypeSystemTypeEntry *>(m_context->db->findTypeSystemType(m_defaultPackage));
    const bool add = moduleEntry == nullptr;
    if (add) {
        moduleEntry = new TypeSystemTypeEntry(m_defaultPackage, since,
                                              currentParentTypeEntry());
    }
    moduleEntry->setCodeGeneration(m_generate);
    moduleEntry->setSnakeCase(snakeCase);

    if ((m_generate == TypeEntry::GenerateForSubclass ||
         m_generate == TypeEntry::GenerateNothing) && !m_defaultPackage.isEmpty())
        TypeDatabase::instance()->addRequiredTargetImport(m_defaultPackage);

    if (add)
        m_context->db->addTypeSystemType(moduleEntry);
    return moduleEntry;
}

bool TypeSystemParser::loadTypesystem(const ConditionalStreamReader &,
                             QXmlStreamAttributes *attributes)
{
    QString typeSystemName;
    bool generateChild = true;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == nameAttribute())
            typeSystemName = attributes->takeAt(i).value().toString();
        else if (name == generateAttribute())
           generateChild = convertBoolean(attributes->takeAt(i).value(), generateAttribute(), true);
    }
    if (typeSystemName.isEmpty()) {
            m_error = u"No typesystem name specified"_s;
            return false;
    }
    const bool result =
        m_context->db->parseFile(m_context, typeSystemName, m_currentPath,
                                 generateChild && m_generate == TypeEntry::GenerateCode);
    if (!result)
        m_error = u"Failed to parse: '"_s + typeSystemName + u'\'';
    return result;
}

bool TypeSystemParser::parseRejectEnumValue(const ConditionalStreamReader &,
                                   QXmlStreamAttributes *attributes)
{
    if (!m_currentEnum) {
        m_error = u"<reject-enum-value> node must be used inside a <enum-type> node"_s;
        return false;
    }
    const int nameIndex = indexOfAttribute(*attributes, nameAttribute());
    if (nameIndex == -1) {
        m_error = msgMissingAttribute(nameAttribute());
        return false;
    }
    m_currentEnum->addEnumValueRejection(attributes->takeAt(nameIndex).value().toString());
    return true;
}

bool TypeSystemParser::parseReplaceArgumentType(const ConditionalStreamReader &,
                                       StackElement topElement,
                                       QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::ModifyArgument) {
        m_error = u"Type replacement can only be specified for argument modifications"_s;
        return false;
    }
    const int modifiedTypeIndex = indexOfAttribute(*attributes, modifiedTypeAttribute());
    if (modifiedTypeIndex == -1) {
        m_error = u"Type replacement requires 'modified-type' attribute"_s;
        return false;
    }
    m_contextStack.top()->functionMods.last().argument_mods().last().setModifiedType(
        attributes->takeAt(modifiedTypeIndex).value().toString());
    return true;
}

bool TypeSystemParser::parseCustomConversion(const ConditionalStreamReader &,
                                    StackElement topElement,
                                    QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::ModifyArgument
        && topElement != StackElement::ValueTypeEntry
        && topElement != StackElement::PrimitiveTypeEntry
        && topElement != StackElement::ContainerTypeEntry) {
        m_error = u"Conversion rules can only be specified for argument modification, "
                   "value-type, primitive-type or container-type conversion."_s;
        return false;
    }

    QString sourceFile;
    QString snippetLabel;
    TypeSystem::Language lang = TypeSystem::NativeCode;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == classAttribute()) {
            const auto languageAttribute = attributes->takeAt(i);
            const auto langOpt = languageFromAttribute(languageAttribute.value());
            if (!langOpt.has_value()) {
                m_error = msgInvalidAttributeValue(languageAttribute);
                return false;
            }
            lang = langOpt.value();
        } else if (name == u"file") {
            sourceFile = attributes->takeAt(i).value().toString();
        } else if (name == snippetAttribute()) {
            snippetLabel = attributes->takeAt(i).value().toString();
        }
    }

    const auto &top = m_contextStack.top();
    if (topElement == StackElement::ModifyArgument) {
        CodeSnip snip;
        snip.language = lang;
        top->functionMods.last().argument_mods().last().conversionRules().append(snip);
        return true;
    }

    if (top->entry->hasTargetConversionRule() || top->entry->hasCustomConversion()) {
        m_error = u"Types can have only one conversion rule"_s;
        return false;
    }

    // The old conversion rule tag that uses a file containing the conversion
    // will be kept temporarily for compatibility reasons. FIXME PYSIDE7: Remove
    if (!sourceFile.isEmpty()) {
        if (m_generate != TypeEntry::GenerateForSubclass
                && m_generate != TypeEntry::GenerateNothing) {
            qWarning(lcShiboken, "Specifying conversion rules by \"file\" is deprecated.");
            if (lang != TypeSystem::TargetLangCode)
                return true;

            QFile conversionSource(sourceFile);
            if (!conversionSource.open(QIODevice::ReadOnly | QIODevice::Text)) {
                m_error = msgCannotOpenForReading(conversionSource);
                return false;
            }
            const auto conversionRuleOptional =
                extractSnippet(QString::fromUtf8(conversionSource.readAll()), snippetLabel);
            if (!conversionRuleOptional.has_value()) {
                m_error = msgCannotFindSnippet(sourceFile, snippetLabel);
                return false;
            }
            top->entry->setTargetConversionRule(conversionRuleOptional.value());
        }
        return true;
    }

    auto *customConversion = new CustomConversion(top->entry);
    customConversionsForReview.append(customConversion);
    return true;
}

bool TypeSystemParser::parseNativeToTarget(const ConditionalStreamReader &,
                                  StackElement topElement,
                                  QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::ConversionRule) {
        m_error = u"Native to Target conversion code can only be specified for custom conversion rules."_s;
        return false;
    }
    CodeSnip snip;
    if (!readFileSnippet(attributes, &snip))
        return false;
    m_contextStack.top()->conversionCodeSnips.append(snip);
    return true;
}

bool TypeSystemParser::parseAddConversion(const ConditionalStreamReader &,
                                 StackElement topElement,
                                 QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::TargetToNative) {
        m_error = u"Target to Native conversions can only be added inside 'target-to-native' tags."_s;
        return false;
    }
    QString sourceTypeName;
    QString typeCheck;
    CodeSnip snip;
    if (!readFileSnippet(attributes, &snip))
        return false;

    const auto &top = m_contextStack.top();
    top->conversionCodeSnips.append(snip);

    if (parserState() == ParserState::ArgumentTargetToNativeConversion)
        return true;

    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == u"type")
             sourceTypeName = attributes->takeAt(i).value().toString();
        else if (name == u"check")
           typeCheck = attributes->takeAt(i).value().toString();
    }

    if (sourceTypeName.isEmpty()) {
        m_error = u"Target to Native conversions must specify the input type with the 'type' attribute."_s;
        return false;
    }
    top->entry->customConversion()->addTargetToNativeConversion(sourceTypeName, typeCheck);
    return true;
}

static bool parseIndex(const QString &index, int *result, QString *errorMessage)
{
    bool ok = false;
    *result = index.toInt(&ok);
    if (!ok)
        *errorMessage = QStringLiteral("Cannot convert '%1' to integer").arg(index);
    return ok;
}

static bool parseArgumentIndex(const QString &index, int *result, QString *errorMessage)
{
    if (index == u"return") {
        *result = 0;
        return true;
    }
    if (index == u"this") {
        *result = -1;
        return true;
    }
    return parseIndex(index, result, errorMessage);
}

bool TypeSystemParser::parseModifyArgument(const ConditionalStreamReader &,
                                  StackElement topElement, QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::ModifyFunction
        && topElement != StackElement::AddFunction
        && topElement != StackElement::DeclareFunction) {
        m_error = u"Argument modification requires <modify-function>,"
                  " <add-function> or <declare-function> as parent, was "_s
                  + tagFromElement(topElement).toString();
        return false;
    }

    QString index;
    QString renameTo;
    QString pyiType;
    bool resetAfterUse = false;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == indexAttribute()) {
             index = attributes->takeAt(i).value().toString();
        } else if (name == invalidateAfterUseAttribute()) {
            resetAfterUse = convertBoolean(attributes->takeAt(i).value(),
                                           invalidateAfterUseAttribute(), false);
        } else if (name == renameAttribute()) {
            renameTo = attributes->takeAt(i).value().toString();
        } else if (name == pyiTypeAttribute()) {
            pyiType = attributes->takeAt(i).value().toString();
        }
    }

    if (index.isEmpty()) {
        m_error = msgMissingAttribute(indexAttribute());
        return false;
    }

    int idx;
    if (!parseArgumentIndex(index, &idx, &m_error))
        return false;

    ArgumentModification argumentModification = ArgumentModification(idx);
    argumentModification.setResetAfterUse(resetAfterUse);
    argumentModification.setRenamedToName(renameTo);
    argumentModification.setPyiType(pyiType);
    m_contextStack.top()->functionMods.last().argument_mods().append(argumentModification);
    return true;
}

bool TypeSystemParser::parseNoNullPointer(const ConditionalStreamReader &reader,
                                 StackElement topElement, QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::ModifyArgument) {
        m_error = u"no-null-pointer requires argument modification as parent"_s;
        return false;
    }

    ArgumentModification &lastArgMod = m_contextStack.top()->functionMods.last().argument_mods().last();
    lastArgMod.setNoNullPointers(true);

    const int defaultValueIndex =
        indexOfAttribute(*attributes, u"default-value");
    if (defaultValueIndex != -1) {
        const QXmlStreamAttribute attribute = attributes->takeAt(defaultValueIndex);
        qCWarning(lcShiboken, "%s",
                  qPrintable(msgUnimplementedAttributeWarning(reader, attribute)));
    }
    return true;
}

bool TypeSystemParser::parseDefineOwnership(const ConditionalStreamReader &,
                                   StackElement topElement,
                                   QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::ModifyArgument) {
        m_error = u"define-ownership requires argument modification as parent"_s;
        return false;
    }

    TypeSystem::Language lang = TypeSystem::TargetLangCode;
    std::optional<TypeSystem::Ownership> ownershipOpt;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == classAttribute()) {
            const auto classAttribute = attributes->takeAt(i);
            const auto langOpt = languageFromAttribute(classAttribute.value());
            if (!langOpt.has_value() || langOpt.value() == TypeSystem::ShellCode) {
                m_error = msgInvalidAttributeValue(classAttribute);
                return false;
            }
            lang = langOpt.value();
        } else if (name == ownershipAttribute()) {
            const auto attribute = attributes->takeAt(i);
            ownershipOpt = ownershipFromFromAttribute(attribute.value());
            if (!ownershipOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return false;
            }
        }
    }

    if (!ownershipOpt.has_value()) {
        m_error = QStringLiteral("unspecified ownership");
        return false;
    }
    auto &lastArgMod = m_contextStack.top()->functionMods.last().argument_mods().last();
    switch (lang) {
    case TypeSystem::TargetLangCode:
        lastArgMod.setTargetOwnerShip(ownershipOpt.value());
        break;
    case TypeSystem::NativeCode:
        lastArgMod.setNativeOwnership(ownershipOpt.value());
        break;
    default:
        break;
    }
    return true;
}

// ### fixme PySide7: remove (replaced by attribute).
bool TypeSystemParser::parseRename(const ConditionalStreamReader &,
                          StackElement topElement,
                          QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::ModifyArgument) {
        m_error = u"Argument modification parent required"_s;
        return false;
    }

    const int toIndex = indexOfAttribute(*attributes, toAttribute());
    if (toIndex == -1) {
        m_error = msgMissingAttribute(toAttribute());
        return false;
    }
    const QString renamed_to = attributes->takeAt(toIndex).value().toString();
    m_contextStack.top()->functionMods.last().argument_mods().last().setRenamedToName(renamed_to);
    return true;
}

bool TypeSystemParser::parseModifyField(const ConditionalStreamReader &,
                                        QXmlStreamAttributes *attributes)
{
    FieldModification fm;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == nameAttribute()) {
            fm.setName(attributes->takeAt(i).value().toString());
        } else if (name == removeAttribute()) {
            fm.setRemoved(convertRemovalAttribute(attributes->takeAt(i).value()));
        } else if (name == opaqueContainerFieldAttribute()) {
            fm.setOpaqueContainer(convertBoolean(attributes->takeAt(i).value(),
                                                 opaqueContainerFieldAttribute(), false));
        }  else if (name == readAttribute()) {
            fm.setReadable(convertBoolean(attributes->takeAt(i).value(), readAttribute(), true));
        } else if (name == writeAttribute()) {
            fm.setWritable(convertBoolean(attributes->takeAt(i).value(), writeAttribute(), true));
        } else if (name == renameAttribute()) {
            fm.setRenamedToName(attributes->takeAt(i).value().toString());
        } else if (name == snakeCaseAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto snakeCaseOpt = snakeCaseFromAttribute(attribute.value());
            if (snakeCaseOpt.has_value()) {
                fm.setSnakeCase(snakeCaseOpt.value());
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        }
    }
    if (fm.name().isEmpty()) {
        m_error = msgMissingAttribute(nameAttribute());
        return false;
    }
    m_contextStack.top()->fieldMods << fm;
    return true;
}

static bool parseOverloadNumber(const QXmlStreamAttribute &attribute, int *overloadNumber,
                                QString *errorMessage)
{
    bool ok;
    *overloadNumber = attribute.value().toInt(&ok);
    if (!ok || *overloadNumber < 0) {
        *errorMessage = msgInvalidAttributeValue(attribute);
        return false;
    }
    return true;
}

bool TypeSystemParser::parseAddFunction(const ConditionalStreamReader &,
                                        StackElement topElement,
                                        StackElement t,
                                        QXmlStreamAttributes *attributes)
{
    const bool validParent = isComplexTypeEntry(topElement)
        || topElement == StackElement::Root
        || topElement ==  StackElement::ContainerTypeEntry;
    if (!validParent) {
        m_error = QString::fromLatin1("Add/Declare function requires a complex/container type or a root tag as parent"
                                      ", was=%1").arg(tagFromElement(topElement));
        return false;
    }
    QString originalSignature;
    QString returnType;
    bool staticFunction = false;
    bool classMethod = false;
    QString access;
    int overloadNumber = TypeSystem::OverloadNumberUnset;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == u"signature") {
            originalSignature = attributes->takeAt(i).value().toString();
        } else if (name == u"return-type") {
            returnType = attributes->takeAt(i).value().toString();
        } else if (name == staticAttribute()) {
            staticFunction = convertBoolean(attributes->takeAt(i).value(),
                                            staticAttribute(), false);
        } else if (name == classmethodAttribute()) {
            classMethod = convertBoolean(attributes->takeAt(i).value(),
                                            classmethodAttribute(), false);
        } else if (name == accessAttribute()) {
            access = attributes->takeAt(i).value().toString();
        } else if (name == overloadNumberAttribute()) {
            if (!parseOverloadNumber(attributes->takeAt(i), &overloadNumber, &m_error))
                return false;
        }
    }

    QString signature = TypeDatabase::normalizedAddedFunctionSignature(originalSignature);
    if (signature.isEmpty()) {
        m_error = u"No signature for the added function"_s;
        return false;
    }

    QString errorString = checkSignatureError(signature, u"add-function"_s);
    if (!errorString.isEmpty()) {
        m_error = errorString;
        return false;
    }

    AddedFunctionPtr func = AddedFunction::createAddedFunction(signature, returnType, &errorString);
    if (func.isNull()) {
        m_error = errorString;
        return false;
    }

    func->setStatic(staticFunction);
    func->setClassMethod(classMethod);

    // Create signature for matching modifications
    signature = TypeDatabase::normalizedSignature(originalSignature);
    if (!signature.contains(u'('))
        signature += u"()"_s;
    m_currentSignature = signature;

    if (!access.isEmpty()) {
        const auto acessOpt = addedFunctionAccessFromAttribute(access);
        if (!acessOpt.has_value()) {
            m_error = u"Bad access type '"_s + access + u'\'';
            return false;
        }
        func->setAccess(acessOpt.value());
    }
    func->setDeclaration(t == StackElement::DeclareFunction);

    m_contextStack.top()->addedFunctions << func;
    m_contextStack.top()->addedFunctionModificationIndex =
        m_contextStack.top()->functionMods.size();

    FunctionModification mod;
    mod.setOverloadNumber(overloadNumber);
    if (!mod.setSignature(m_currentSignature, &m_error))
        return false;
    mod.setOriginalSignature(originalSignature);
    m_contextStack.top()->functionMods << mod;
    return true;
}

bool TypeSystemParser::parseProperty(const ConditionalStreamReader &, StackElement topElement,
                                     QXmlStreamAttributes *attributes)
{
    if (!isComplexTypeEntry(topElement)) {
        m_error = QString::fromLatin1("Add property requires a complex type as parent"
                                      ", was=%1").arg(tagFromElement(topElement));
        return false;
    }

    TypeSystemProperty property;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == nameAttribute()) {
            property.name = attributes->takeAt(i).value().toString();
        } else if (name == u"get") {
            property.read = attributes->takeAt(i).value().toString();
        } else if (name == u"type") {
            property.type = attributes->takeAt(i).value().toString();
        } else if (name == u"set") {
            property.write = attributes->takeAt(i).value().toString();
        } else if (name == generateGetSetDefAttribute()) {
            property.generateGetSetDef =
                convertBoolean(attributes->takeAt(i).value(),
                               generateGetSetDefAttribute(), false);
        }
    }
    if (!property.isValid()) {
        m_error = u"<property> element is missing required attibutes (name/type/get)."_s;
        return false;
    }
    static_cast<ComplexTypeEntry *>(m_contextStack.top()->entry)->addProperty(property);
    return true;
}

bool TypeSystemParser::parseModifyFunction(const ConditionalStreamReader &reader,
                                  StackElement topElement,
                                  QXmlStreamAttributes *attributes)
{
    const bool validParent = isComplexTypeEntry(topElement)
        || topElement == StackElement::TypedefTypeEntry
        || topElement == StackElement::FunctionTypeEntry;
    if (!validParent) {
        m_error = QString::fromLatin1("Modify function requires complex type as parent"
                                      ", was=%1").arg(tagFromElement(topElement));
        return false;
    }

    QString originalSignature;
    QString access;
    bool removed = false;
    QString rename;
    bool deprecated = false;
    bool isThread = false;
    int overloadNumber = TypeSystem::OverloadNumberUnset;
    TypeSystem::ExceptionHandling exceptionHandling = TypeSystem::ExceptionHandling::Unspecified;
    TypeSystem::AllowThread allowThread = TypeSystem::AllowThread::Unspecified;
    TypeSystem::SnakeCase snakeCase = TypeSystem::SnakeCase::Unspecified;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == u"signature") {
            originalSignature = attributes->takeAt(i).value().toString();
        } else if (name == accessAttribute()) {
            access = attributes->takeAt(i).value().toString();
        } else if (name == renameAttribute()) {
            rename = attributes->takeAt(i).value().toString();
        } else if (name == removeAttribute()) {
            removed = convertRemovalAttribute(attributes->takeAt(i).value());
        } else if (name == deprecatedAttribute()) {
            deprecated = convertBoolean(attributes->takeAt(i).value(),
                                        deprecatedAttribute(), false);
        } else if (name == threadAttribute()) {
            isThread = convertBoolean(attributes->takeAt(i).value(),
                                      threadAttribute(), false);
        } else if (name == allowThreadAttribute()) {
            const QXmlStreamAttribute attribute = attributes->takeAt(i);
            const auto allowThreadOpt = allowThreadFromAttribute(attribute.value());
            if (!allowThreadOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return false;
            }
            allowThread = allowThreadOpt.value();
        } else if (name == exceptionHandlingAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto exceptionOpt = exceptionHandlingFromAttribute(attribute.value());
            if (exceptionOpt.has_value()) {
                exceptionHandling = exceptionOpt.value();
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        } else if (name == overloadNumberAttribute()) {
            if (!parseOverloadNumber(attributes->takeAt(i), &overloadNumber, &m_error))
                return false;
        } else if (name == snakeCaseAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto snakeCaseOpt = snakeCaseFromAttribute(attribute.value());
            if (snakeCaseOpt.has_value()) {
                snakeCase = snakeCaseOpt.value();
            } else {
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgInvalidAttributeValue(attribute)));
            }
        } else if (name == virtualSlotAttribute()) {
            qCWarning(lcShiboken, "%s",
                      qPrintable(msgUnimplementedAttributeWarning(reader, name)));
        }
    }

    // Child of global <function>
    const auto &top = m_contextStack.top();
    if (originalSignature.isEmpty() && top->entry->isFunction()) {
        auto f = static_cast<const FunctionTypeEntry *>(top->entry);
        originalSignature = f->signatures().value(0);
    }

    const QString signature = TypeDatabase::normalizedSignature(originalSignature);
    if (signature.isEmpty()) {
        m_error = u"No signature for modified function"_s;
        return false;
    }

    QString errorString = checkSignatureError(signature, u"modify-function"_s);
    if (!errorString.isEmpty()) {
        m_error = errorString;
        return false;
    }

    FunctionModification mod;
    if (!mod.setSignature(signature, &m_error))
        return false;
    mod.setOriginalSignature(originalSignature);
    mod.setExceptionHandling(exceptionHandling);
    mod.setOverloadNumber(overloadNumber);
    mod.setSnakeCase(snakeCase);
    m_currentSignature = signature;

    if (!access.isEmpty()) {
        const auto modifierFlagOpt = modifierFromAttribute(access);
        if (!modifierFlagOpt.has_value()) {
            m_error = u"Bad access type '"_s + access + u'\'';
            return false;
        }
        const FunctionModification::ModifierFlag m = modifierFlagOpt.value();
        if (m == FunctionModification::Final || m == FunctionModification::NonFinal) {
            qCWarning(lcShiboken, "%s",
                      qPrintable(msgUnimplementedAttributeValueWarning(reader,
                      accessAttribute(), access)));
        }
        mod.setModifierFlag(m);
    }

    if (deprecated)
        mod.setModifierFlag(FunctionModification::Deprecated);

    mod.setRemoved(removed);

    if (!rename.isEmpty()) {
        mod.setRenamedToName(rename);
        mod.setModifierFlag(FunctionModification::Rename);
    }

    mod.setIsThread(isThread);
    if (allowThread != TypeSystem::AllowThread::Unspecified)
        mod.setAllowThread(allowThread);

    top->functionMods << mod;
    return true;
}

bool TypeSystemParser::parseReplaceDefaultExpression(const ConditionalStreamReader &,
                                            StackElement topElement,
                                            QXmlStreamAttributes *attributes)
{
    if (!(topElement & StackElement::ModifyArgument)) {
        m_error = u"Replace default expression only allowed as child of argument modification"_s;
        return false;
    }
    const int withIndex = indexOfAttribute(*attributes, u"with");
    if (withIndex == -1 || attributes->at(withIndex).value().isEmpty()) {
        m_error = u"Default expression replaced with empty string. Use remove-default-expression instead."_s;
        return false;
    }

    m_contextStack.top()->functionMods.last().argument_mods().last().setReplacedDefaultExpression(
        attributes->takeAt(withIndex).value().toString());
    return true;
}

bool TypeSystemParser::parseReferenceCount(const ConditionalStreamReader &reader,
                                  StackElement topElement,
                                  QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::ModifyArgument) {
        m_error = u"reference-count must be child of modify-argument"_s;
        return false;
    }

    ReferenceCount rc;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == actionAttribute()) {
            const QXmlStreamAttribute attribute = attributes->takeAt(i);
            const auto actionOpt = referenceCountFromAttribute(attribute.value());
            if (!actionOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return false;
            }
            rc.action = actionOpt.value();
            switch (rc.action) {
            case ReferenceCount::AddAll:
            case ReferenceCount::Ignore:
                qCWarning(lcShiboken, "%s",
                          qPrintable(msgUnimplementedAttributeValueWarning(reader, attribute)));
                break;
            default:
                break;
            }
        } else if (name == u"variable-name") {
            rc.varName = attributes->takeAt(i).value().toString();
        }
    }

    m_contextStack.top()->functionMods.last().argument_mods().last().addReferenceCount(rc);
    return true;
}

bool TypeSystemParser::parseParentOwner(const ConditionalStreamReader &,
                               StackElement topElement,
                               QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::ModifyArgument) {
        m_error = u"parent-policy must be child of modify-argument"_s;
        return false;
    }
    ArgumentOwner ao;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == indexAttribute()) {
            const QString index = attributes->takeAt(i).value().toString();
            if (!parseArgumentIndex(index, &ao.index, &m_error))
                return false;
        } else if (name == actionAttribute()) {
            const auto action = attributes->takeAt(i);
            const auto actionOpt = argumentOwnerActionFromAttribute(action.value());
            if (!actionOpt.has_value()) {
                m_error = msgInvalidAttributeValue(action);
                return false;
            }
            ao.action = actionOpt.value();
        }
    }
    m_contextStack.top()->functionMods.last().argument_mods().last().setOwner(ao);
    return true;
}

bool TypeSystemParser::readFileSnippet(QXmlStreamAttributes *attributes, CodeSnip *snip)
{
    QString fileName;
    QString snippetLabel;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == u"file") {
            fileName = attributes->takeAt(i).value().toString();
        } else if (name == snippetAttribute()) {
            snippetLabel = attributes->takeAt(i).value().toString();
        }
    }
    if (fileName.isEmpty())
        return true;
    const QString resolved = m_context->db->modifiedTypesystemFilepath(fileName, m_currentPath);
    if (!QFile::exists(resolved)) {
        m_error = u"File for inject code not exist: "_s
            + QDir::toNativeSeparators(fileName);
        return false;
    }
    QFile codeFile(resolved);
    if (!codeFile.open(QIODevice::Text | QIODevice::ReadOnly)) {
        m_error = msgCannotOpenForReading(codeFile);
        return false;
    }
    const auto codeOptional = extractSnippet(QString::fromUtf8(codeFile.readAll()), snippetLabel);
    codeFile.close();
    if (!codeOptional.has_value()) {
        m_error = msgCannotFindSnippet(resolved, snippetLabel);
        return false;
    }

    QString source = fileName;
    if (!snippetLabel.isEmpty())
        source += u" ("_s + snippetLabel + u')';
    QString content;
    QTextStream str(&content);
    str << "// ========================================================================\n"
           "// START of custom code block [file: "
        << source << "]\n" << codeOptional.value()
        << "// END of custom code block [file: " << source
        << "]\n// ========================================================================\n";
    snip->addCode(content);
    return true;
}

bool TypeSystemParser::parseInjectCode(const ConditionalStreamReader &,
                              StackElement topElement,
                              QXmlStreamAttributes *attributes)
{
    if (!isComplexTypeEntry(topElement)
        && (topElement != StackElement::AddFunction)
        && (topElement != StackElement::ModifyFunction)
        && (topElement != StackElement::Root)) {
        m_error = u"wrong parent type for code injection"_s;
        return false;
    }

    TypeSystem::CodeSnipPosition position = TypeSystem::CodeSnipPositionBeginning;
    TypeSystem::Language lang = TypeSystem::TargetLangCode;
    CodeSnip snip;
    if (!readFileSnippet(attributes, &snip))
        return false;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == classAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto langOpt = languageFromAttribute(attribute.value());
            if (!langOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return false;
            }
            lang = langOpt.value();
        } else if (name == positionAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto positionOpt = codeSnipPositionFromAttribute(attribute.value());
            if (!positionOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return false;
            }
            position = positionOpt.value();
        }
    }

    snip.position = position;
    snip.language = lang;

    if (topElement == StackElement::ModifyFunction
        || topElement == StackElement::AddFunction) {
        FunctionModification &mod = m_contextStack.top()->functionMods.last();
        mod.appendSnip(snip);
        if (!snip.code().isEmpty())
            mod.setModifierFlag(FunctionModification::CodeInjection);
    } else {
        m_contextStack.top()->entry->addCodeSnip(snip);
    }
    return true;
}

bool TypeSystemParser::parseInclude(const ConditionalStreamReader &,
                           StackElement topElement,
                           TypeEntry *entry, QXmlStreamAttributes *attributes)
{
    QString fileName;
    Include::IncludeType location = Include::IncludePath;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == fileNameAttribute()) {
            fileName = attributes->takeAt(i).value().toString();
        } else if (name == locationAttribute()) {
            const auto attribute = attributes->takeAt(i);
            const auto locationOpt = locationFromAttribute(attribute.value());
            if (!locationOpt.has_value()) {
                m_error = msgInvalidAttributeValue(attribute);
                return false;
            }
            location = locationOpt.value();
        }
    }

    Include inc(location, fileName);
    if (isComplexTypeEntry(topElement)
        || topElement == StackElement::PrimitiveTypeEntry
        || topElement == StackElement::ContainerTypeEntry
        || topElement == StackElement::SmartPointerTypeEntry
        || topElement == StackElement::TypedefTypeEntry) {
        entry->setInclude(inc);
    } else if (topElement == StackElement::ExtraIncludes) {
        entry->addExtraInclude(inc);
    } else {
        m_error = u"Only supported parent tags are primitive-type, complex types or extra-includes"_s;
        return false;
    }
    return true;
}

bool TypeSystemParser::parseSystemInclude(const ConditionalStreamReader &,
                                          QXmlStreamAttributes *attributes)
{
    const int index = indexOfAttribute(*attributes, fileNameAttribute());
    if (index == -1) {
        m_error = msgMissingAttribute(fileNameAttribute());
        return false;
    }
    TypeDatabase::instance()->addSystemInclude(attributes->takeAt(index).value().toString());
    return true;
}

TemplateInstance *
    TypeSystemParser::parseInsertTemplate(const ConditionalStreamReader &,
                                          StackElement topElement,
                                          QXmlStreamAttributes *attributes)
{
    if ((topElement != StackElement::InjectCode) &&
        (topElement != StackElement::Template) &&
        (topElement != StackElement::NativeToTarget) &&
        (topElement != StackElement::AddConversion) &&
        (topElement != StackElement::ConversionRule)) {
        m_error = u"Can only insert templates into code snippets, templates, "\
                   "conversion-rule, native-to-target or add-conversion tags."_s;
        return nullptr;
    }
    const int nameIndex = indexOfAttribute(*attributes, nameAttribute());
    if (nameIndex == -1) {
        m_error = msgMissingAttribute(nameAttribute());
        return nullptr;
    }
    return new TemplateInstance(attributes->takeAt(nameIndex).value().toString());
}

bool TypeSystemParser::parseReplace(const ConditionalStreamReader &,
                           StackElement topElement, QXmlStreamAttributes *attributes)
{
    if (topElement != StackElement::InsertTemplate) {
        m_error = u"Can only insert replace rules into insert-template."_s;
        return false;
    }
    QString from;
    QString to;
    for (int i = attributes->size() - 1; i >= 0; --i) {
        const auto name = attributes->at(i).qualifiedName();
        if (name == u"from")
            from = attributes->takeAt(i).value().toString();
        else if (name == toAttribute())
            to = attributes->takeAt(i).value().toString();
    }
    m_templateInstance->addReplaceRule(from, to);
    return true;
}

// Check for a duplicated type entry and return whether to add the new one.
// We need to be able to have duplicate primitive type entries,
// or it's not possible to cover all primitive target language
// types (which we need to do in order to support fake meta objects)
bool TypeSystemParser::checkDuplicatedTypeEntry(const ConditionalStreamReader &reader,
                                                StackElement t,
                                                const QString &name) const
{
    if (t == StackElement::PrimitiveTypeEntry || t == StackElement::FunctionTypeEntry)
        return true;
    const auto *duplicated = m_context->db->findType(name);
    if (!duplicated || duplicated->isNamespace())
        return true;
    if (duplicated->isBuiltIn()) {
        qCWarning(lcShiboken, "%s",
                  qPrintable(msgReaderMessage(reader, "Warning",
                                              msgDuplicateBuiltInTypeEntry(name))));
        return false;
    }
    qCWarning(lcShiboken, "%s",
              qPrintable(msgReaderMessage(reader, "Warning",
                                          msgDuplicateTypeEntry(name))));
    return true;
}

static bool parseVersion(const QString &versionSpec, const QString &package,
                         QVersionNumber *result, QString *errorMessage)
{
    *result = QVersionNumber::fromString(versionSpec);
    if (result->isNull()) {
        *errorMessage = msgInvalidVersion(versionSpec, package);
        return false;
    }
    return true;
}

bool TypeSystemParser::startElement(const ConditionalStreamReader &reader, StackElement element)
{
    if (m_ignoreDepth) {
        ++m_ignoreDepth;
        return true;
    }

    const auto tagName = reader.name();
    QXmlStreamAttributes attributes = reader.attributes();

    VersionRange versionRange;
    for (int i = attributes.size() - 1; i >= 0; --i) {
        const auto name = attributes.at(i).qualifiedName();
        if (name == sinceAttribute()) {
            if (!parseVersion(attributes.takeAt(i).value().toString(),
                              m_defaultPackage, &versionRange.since, &m_error)) {
                return false;
            }
        } else if (name == untilAttribute()) {
            if (!parseVersion(attributes.takeAt(i).value().toString(),
                              m_defaultPackage, &versionRange.until, &m_error)) {
                return false;
            }
        }
    }

    if (!m_defaultPackage.isEmpty() && !versionRange.isNull()) {
        TypeDatabase* td = TypeDatabase::instance();
        if (!td->checkApiVersion(m_defaultPackage, versionRange)) {
            ++m_ignoreDepth;
            return true;
        }
    }

    if (element == StackElement::ImportFile)
        return importFileElement(attributes);

    if (m_currentDroppedEntryDepth) {
        ++m_currentDroppedEntryDepth;
        return true;
    }

    if (element == StackElement::Root && m_generate == TypeEntry::GenerateCode)
        customConversionsForReview.clear();

    if (element == StackElement::Unimplemented) {
        qCWarning(lcShiboken, "%s",
                  qPrintable(msgUnimplementedElementWarning(reader, tagName)));
        return true;
    }

    if (isTypeEntry(element) || element == StackElement::Root)
        m_contextStack.push(StackElementContextPtr(new StackElementContext()));

    if (m_contextStack.isEmpty()) {
        m_error = msgNoRootTypeSystemEntry();
        return false;
    }

    const auto &top = m_contextStack.top();
    const StackElement topElement = m_stack.value(m_stack.size() - 2, StackElement::None);

    if (isTypeEntry(element)) {
        QString name;
        if (element != StackElement::FunctionTypeEntry) {
            const int nameIndex = indexOfAttribute(attributes, nameAttribute());
            if (nameIndex != -1) {
                name = attributes.takeAt(nameIndex).value().toString();
            } else if (element != StackElement::EnumTypeEntry) { // anonymous enum?
                m_error = msgMissingAttribute(nameAttribute());
                return false;
            }
        }
        // Allow for primitive and/or std:: types only, else require proper nesting.
        if (element != StackElement::PrimitiveTypeEntry && name.contains(u':')
            && !name.contains(u"std::")) {
            m_error = msgIncorrectlyNestedName(name);
            return false;
        }

        if (m_context->db->hasDroppedTypeEntries()) {
            const QString identifier = element == StackElement::FunctionTypeEntry
                ? attributes.value(signatureAttribute()).toString() : name;
            if (shouldDropTypeEntry(m_context->db, m_contextStack, identifier)) {
                m_currentDroppedEntryDepth = 1;
                if (ReportHandler::isDebug(ReportHandler::SparseDebug)) {
                    qCInfo(lcShiboken, "Type system entry '%s' was intentionally dropped from generation.",
                           qPrintable(identifier));
                }
                 m_contextStack.pop();
                return true;
            }
        }

        // The top level tag 'function' has only the 'signature' tag
        // and we should extract the 'name' value from it.
        if (element == StackElement::FunctionTypeEntry
            && !parseRenameFunction(reader, &name, &attributes)) {
                return false;
        }

        // We need to be able to have duplicate primitive type entries,
        // or it's not possible to cover all primitive target language
        // types (which we need to do in order to support fake meta objects)
        if (element != StackElement::PrimitiveTypeEntry
            && element != StackElement::FunctionTypeEntry) {
            TypeEntry *tmp = m_context->db->findType(name);
            if (tmp && !tmp->isNamespace())
                qCWarning(lcShiboken).noquote().nospace()
                    << "Duplicate type entry: '" << name << '\'';
        }

        if (element == StackElement::EnumTypeEntry) {
            const int enumIdentifiedByIndex = indexOfAttribute(attributes, enumIdentifiedByValueAttribute());
            const QString identifiedByValue = enumIdentifiedByIndex != -1
                ? attributes.takeAt(enumIdentifiedByIndex).value().toString() : QString();
            if (name.isEmpty()) {
                name = identifiedByValue;
            } else if (!identifiedByValue.isEmpty()) {
                m_error = u"can't specify both 'name' and 'identified-by-value' attributes"_s;
                return false;
            }
        }

        if (name.isEmpty()) {
            m_error = u"no 'name' attribute specified"_s;
            return false;
        }

        switch (element) {
        case StackElement::CustomTypeEntry:
            top->entry = parseCustomTypeEntry(reader, name, versionRange.since, &attributes);
            if (Q_UNLIKELY(!top->entry))
                return false;
            break;
        case StackElement::PrimitiveTypeEntry:
            top->entry = parsePrimitiveTypeEntry(reader, name, versionRange.since, &attributes);
            if (Q_UNLIKELY(!top->entry))
                return false;
            break;
        case StackElement::ContainerTypeEntry:
            top->entry = parseContainerTypeEntry(reader, name, versionRange.since, &attributes);
            if (top->entry == nullptr)
                return false;
            break;

        case StackElement::SmartPointerTypeEntry:
            top->entry = parseSmartPointerEntry(reader, name, versionRange.since, &attributes);
            if (top->entry == nullptr)
                return false;
            break;
        case StackElement::EnumTypeEntry:
            m_currentEnum = parseEnumTypeEntry(reader, name, versionRange.since, &attributes);
            if (Q_UNLIKELY(!m_currentEnum))
                return false;
            top->entry = m_currentEnum;
            break;

        case StackElement::ValueTypeEntry:
           top->entry = parseValueTypeEntry(reader, name, versionRange.since, &attributes);
           if (top->entry == nullptr)
               return false;
           break;
        case StackElement::NamespaceTypeEntry:
            top->entry = parseNamespaceTypeEntry(reader, name, versionRange.since, &attributes);
            if (top->entry == nullptr)
                return false;
            break;
        case StackElement::ObjectTypeEntry:
        case StackElement::InterfaceTypeEntry: {
            if (!checkRootElement())
                return false;
            auto *ce  = new ObjectTypeEntry(name, versionRange.since, currentParentTypeEntry());
            top->entry = ce;
            applyCommonAttributes(reader, top->entry, &attributes);
            applyComplexTypeAttributes(reader, ce, &attributes);
        }
            break;
        case StackElement::FunctionTypeEntry:
            top->entry = parseFunctionTypeEntry(reader, name, versionRange.since, &attributes);
            if (Q_UNLIKELY(!top->entry))
                return false;
            break;
        case StackElement::TypedefTypeEntry:
            top->entry = parseTypedefEntry(reader, name, topElement,
                                           versionRange.since, &attributes);
            if (top->entry == nullptr)
                return false;
            break;
        default:
            Q_ASSERT(false);
        }

        if (top->entry) {
            if (checkDuplicatedTypeEntry(reader, element, top->entry->name())
                && !m_context->db->addType(top->entry, &m_error)) {
                return false;
            }
        } else {
            qCWarning(lcShiboken).noquote().nospace()
                << u"Type: "_s + name + u" was rejected by typesystem"_s;
        }

    } else if (element == StackElement::InjectDocumentation) {
        if (!parseInjectDocumentation(reader, topElement, &attributes))
            return false;
    } else if (element == StackElement::ModifyDocumentation) {
        if (!parseModifyDocumentation(reader, topElement, &attributes))
            return false;
    } else if (element != StackElement::None) {
        bool topLevel = element == StackElement::Root
                        || element == StackElement::SuppressedWarning
                        || element == StackElement::Rejection
                        || element == StackElement::LoadTypesystem
                        || element == StackElement::InjectCode
                        || element == StackElement::ExtraIncludes
                        || element == StackElement::SystemInclude
                        || element == StackElement::ConversionRule
                        || element == StackElement::AddFunction
                        || element == StackElement::DeclareFunction
                        || element == StackElement::Template;

        if (!topLevel && m_stack.at(m_stack.size() - 2) == StackElement::Root) {
            m_error = u"Tag requires parent: '"_s + tagName.toString() + u'\'';
            return false;
        }

        switch (element) {
        case StackElement::Root:
            top->entry = parseRootElement(reader, versionRange.since, &attributes);
            break;
        case StackElement::LoadTypesystem:
            if (!loadTypesystem(reader, &attributes))
                return false;
            break;
        case StackElement::RejectEnumValue:
            if (!parseRejectEnumValue(reader, &attributes))
                return false;
            break;
        case StackElement::ReplaceType:
            if (!parseReplaceArgumentType(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::ConversionRule:
            if (!TypeSystemParser::parseCustomConversion(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::NativeToTarget:
            if (!parseNativeToTarget(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::TargetToNative: {
            if (topElement != StackElement::ConversionRule) {
                m_error = u"Target to Native conversions can only be specified for custom conversion rules."_s;
                return false;
            }

            const auto topParent = m_stack.value(m_stack.size() - 3, StackElement::None);
            if (isTypeEntry(topParent)) {
                const int replaceIndex = indexOfAttribute(attributes, replaceAttribute());
                const bool replace = replaceIndex == -1
                    || convertBoolean(attributes.takeAt(replaceIndex).value(),
                                      replaceAttribute(), true);
                top->entry->customConversion()->setReplaceOriginalTargetToNativeConversions(replace);
            }
        }
        break;
        case StackElement::AddConversion:
            if (!parseAddConversion(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::ModifyArgument:
            if (!parseModifyArgument(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::NoNullPointers:
            if (!parseNoNullPointer(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::DefineOwnership:
            if (!parseDefineOwnership(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::SuppressedWarning: {
            const int textIndex = indexOfAttribute(attributes, textAttribute());
            if (textIndex == -1) {
                qCWarning(lcShiboken) << "Suppressed warning with no text specified";
            } else {
                const QString suppressedWarning =
                    attributes.takeAt(textIndex).value().toString();
                if (!m_context->db->addSuppressedWarning(suppressedWarning, &m_error))
                    return false;
            }
        }
            break;
        case StackElement::Rename:
             if (!parseRename(reader, topElement, &attributes))
                 return false;
             break;
        case StackElement::RemoveArgument:
            if (topElement != StackElement::ModifyArgument) {
                m_error = u"Removing argument requires argument modification as parent"_s;
                return false;
            }

            top->functionMods.last().argument_mods().last().setRemoved(true);
            break;

        case StackElement::ModifyField:
            if (!parseModifyField(reader, &attributes))
                return false;
            break;
        case StackElement::DeclareFunction:
        case StackElement::AddFunction:
            if (!parseAddFunction(reader, topElement, element, &attributes))
                return false;
            break;
        case StackElement::Property:
            if (!parseProperty(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::ModifyFunction:
            if (!parseModifyFunction(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::ReplaceDefaultExpression:
            if (!parseReplaceDefaultExpression(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::RemoveDefaultExpression:
            top->functionMods.last().argument_mods().last().setRemovedDefaultExpression(true);
            break;
        case StackElement::ReferenceCount:
            if (!parseReferenceCount(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::ParentOwner:
            if (!parseParentOwner(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::Array:
            if (topElement != StackElement::ModifyArgument) {
                m_error = u"array must be child of modify-argument"_s;
                return false;
            }
            top->functionMods.last().argument_mods().last().setArray(true);
            break;
        case StackElement::InjectCode:
            if (!parseInjectCode(reader, topElement, &attributes))
                return false;
            break;
        case StackElement::Include:
            if (!parseInclude(reader, topElement, top->entry, &attributes))
                return false;
            break;
        case StackElement::Rejection:
            if (!addRejection(m_context->db, &attributes, &m_error))
                return false;
            break;
        case StackElement::SystemInclude:
            if (!parseSystemInclude(reader, &attributes))
                return false;
            break;
        case StackElement::Template: {
            const int nameIndex = indexOfAttribute(attributes, nameAttribute());
            if (nameIndex == -1) {
                m_error = msgMissingAttribute(nameAttribute());
                return false;
            }
            m_templateEntry =
                new TemplateEntry(attributes.takeAt(nameIndex).value().toString());
        }
            break;
        case StackElement::InsertTemplate:
            m_templateInstance.reset(parseInsertTemplate(reader, topElement, &attributes));
            if (m_templateInstance.isNull())
                return false;
            break;
        case StackElement::Replace:
            if (!parseReplace(reader, topElement, &attributes))
                return false;
            break;
        default:
            break; // nada
        }
    }

    if (!attributes.isEmpty()) {
        const QString message = msgUnusedAttributes(tagName, attributes);
        qCWarning(lcShiboken, "%s", qPrintable(msgReaderWarning(reader, message)));
    }

    return true;
}
