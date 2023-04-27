// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "generator.h"
#include "defaultvalue.h"
#include "generatorcontext.h"
#include "apiextractorresult.h"
#include "abstractmetaargument.h"
#include "abstractmetaenum.h"
#include "abstractmetafunction.h"
#include "abstractmetalang.h"
#include "messages.h"
#include "reporthandler.h"
#include "fileout.h"
#include "arraytypeentry.h"
#include "enumtypeentry.h"
#include "enumvaluetypeentry.h"
#include "namespacetypeentry.h"
#include "primitivetypeentry.h"
#include "typesystemtypeentry.h"
#include <typedatabase.h>

#include "qtcompat.h"

#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QFileInfo>
#include <QtCore/QRegularExpression>

using namespace Qt::StringLiterals;

static const char ENABLE_PYSIDE_EXTENSIONS[] = "enable-pyside-extensions";
static const char AVOID_PROTECTED_HACK[] = "avoid-protected-hack";

struct Generator::GeneratorPrivate
{
    ApiExtractorResult api;
    QString outDir;
    // License comment
    QString licenseComment;
    AbstractMetaClassCList m_invisibleTopNamespaces;
    bool m_hasPrivateClasses = false;
    bool m_usePySideExtensions = false;
    bool m_avoidProtectedHack = false;
};

Generator::Generator() : m_d(new GeneratorPrivate)
{
}

Generator::~Generator()
{
    delete m_d;
}

bool Generator::setup(const ApiExtractorResult &api)
{
    m_d->api = api;
    const auto moduleEntry = TypeDatabase::instance()->defaultTypeSystemType();
    if (!moduleEntry) {
        qCWarning(lcShiboken,"Couldn't find the package name!!");
        return false;
    }
    if (!moduleEntry->generateCode()) {
        qCWarning(lcShiboken, "Code generation of root typesystem is disabled!!");
        return false;
    }

    for (const auto &c : api.classes()) {
        if (c->enclosingClass() == nullptr && c->isInvisibleNamespace()) {
            m_d->m_invisibleTopNamespaces.append(c);
            c->invisibleNamespaceRecursion([&](const AbstractMetaClassCPtr &ic) {
                m_d->m_invisibleTopNamespaces.append(ic);
            });
        }
    }

    return doSetup();
}

Generator::OptionDescriptions Generator::options() const
{
    return {
        {QLatin1StringView(AVOID_PROTECTED_HACK),
         u"Avoid the use of the '#define protected public' hack."_s},
        {QLatin1StringView(ENABLE_PYSIDE_EXTENSIONS),
         u"Enable PySide extensions, such as support for signal/slots,\n"
          "use this if you are creating a binding for a Qt-based library."_s}
    };
}

bool Generator::handleOption(const QString & key, const QString & /* value */)
{
    if (key == QLatin1StringView(ENABLE_PYSIDE_EXTENSIONS))
        return ( m_d->m_usePySideExtensions = true);
    if (key == QLatin1StringView(AVOID_PROTECTED_HACK))
        return (m_d->m_avoidProtectedHack = true);
    return false;
}

QString Generator::fileNameForContextHelper(const GeneratorContext &context,
                                            const QString &suffix,
                                            FileNameFlags flags)

{
    if (!context.forSmartPointer()) {
        const auto metaClass = context.metaClass();
        QString fileNameBase = flags.testFlag(FileNameFlag::UnqualifiedName)
            ? metaClass->name() : metaClass->qualifiedCppName();
        if (!flags.testFlag(FileNameFlag::KeepCase))
            fileNameBase = fileNameBase.toLower();
        fileNameBase.replace(u"::"_s, u"_"_s);
        return fileNameBase + suffix;
    }

    // FIXME: PYSIDE7: Use the above code path for all types. Note the file
    // names will then change to reflect the namespaces of the pointee
    // (smart/integer2).
    const AbstractMetaType &smartPointerType = context.preciseType();
    QString fileNameBase = getFileNameBaseForSmartPointer(smartPointerType);
    return fileNameBase + suffix;
}

const AbstractMetaClassCList &Generator::invisibleTopNamespaces() const
{
    return m_d->m_invisibleTopNamespaces;
}

PrimitiveTypeEntryCList Generator::primitiveTypes()
{
    return TypeDatabase::instance()->primitiveTypes();
}

ContainerTypeEntryCList Generator::containerTypes()
{
    return TypeDatabase::instance()->containerTypes();
}

QString Generator::licenseComment() const
{
    return m_d->licenseComment;
}

void Generator::setLicenseComment(const QString &licenseComment)
{
    m_d->licenseComment = licenseComment;
}

QString Generator::packageName()
{
    return TypeDatabase::instance()->defaultPackageName();
}

static QString getModuleName()
{
    QString result = TypeDatabase::instance()->defaultPackageName();
    result.remove(0, result.lastIndexOf(u'.') + 1);
    return result;
}

QString Generator::moduleName()
{
    static const QString result = getModuleName();
    return result;
}

QString Generator::outputDirectory() const
{
    return m_d->outDir;
}

void Generator::setOutputDirectory(const QString &outDir)
{
    m_d->outDir = outDir;
}

bool Generator::generateFileForContext(const GeneratorContext &context)
{
    const auto cls = context.metaClass();
    auto typeEntry = cls->typeEntry();

    if (!shouldGenerate(typeEntry))
        return true;

    const QString fileName = fileNameForContext(context);
    if (fileName.isEmpty())
        return true;

    QString filePath = outputDirectory() + u'/'
        + subDirectoryForPackage(typeEntry->targetLangPackage())
        + u'/' + fileName;
    FileOut fileOut(filePath);

    generateClass(fileOut.stream, context);

    fileOut.done();
    return true;
}

QString Generator::getFileNameBaseForSmartPointer(const AbstractMetaType &smartPointerType)
{
    const AbstractMetaType innerType = smartPointerType.getSmartPointerInnerType();
    smartPointerType.typeEntry()->qualifiedCppName();
    QString fileName = smartPointerType.typeEntry()->qualifiedCppName().toLower();
    fileName.replace(u"::"_s, u"_"_s);
    fileName.append(u"_"_s);
    fileName.append(innerType.name().toLower());

    return fileName;
}

GeneratorContext Generator::contextForClass(const AbstractMetaClassCPtr &c) const
{
    GeneratorContext result;
    result.m_metaClass = c;
    return result;
}

GeneratorContext
    Generator::contextForSmartPointer(const AbstractMetaClassCPtr &c,
                                      const AbstractMetaType &t,
                                      const AbstractMetaClassCPtr &pointeeClass)
{
    GeneratorContext result;
    result.m_metaClass = c;
    result.m_preciseClassType = t;
    result.m_type = GeneratorContext::SmartPointer;
    result.m_pointeeClass = pointeeClass;
    return result;
}

bool Generator::generate()
{
    for (const auto &cls : m_d->api.classes()) {
        if (!generateFileForContext(contextForClass(cls)))
            return false;
        auto te = cls->typeEntry();
        if (shouldGenerate(te) && te->isPrivate())
            m_d->m_hasPrivateClasses = true;
    }

    for (const auto &smp: m_d->api.instantiatedSmartPointers()) {
        AbstractMetaClassCPtr pointeeClass;
        const auto instantiatedType = smp.type.instantiations().constFirst().typeEntry();
        if (instantiatedType->isComplex()) // not a C++ primitive
            pointeeClass = AbstractMetaClass::findClass(m_d->api.classes(), instantiatedType);
        if (!generateFileForContext(contextForSmartPointer(smp.specialized, smp.type,
                                                           pointeeClass))) {
            return false;
        }
    }
    return finishGeneration();
}

bool Generator::shouldGenerate(const TypeEntryCPtr &typeEntry) const
{
    return typeEntry->shouldGenerate();
}

const ApiExtractorResult &Generator::api() const
{
    return m_d->api;
}

bool Generator::hasPrivateClasses() const
{
    return m_d->m_hasPrivateClasses;
}

bool Generator::usePySideExtensions() const
{
    return m_d->m_usePySideExtensions;
}

bool Generator::avoidProtectedHack() const
{
    return m_d->m_avoidProtectedHack;
}

QString Generator::getFullTypeName(TypeEntryCPtr type)
{
    QString result = type->qualifiedCppName();
    if (type->isArray())
        type = std::static_pointer_cast<const ArrayTypeEntry>(type)->nestedTypeEntry();
    if (!isCppPrimitive(type))
        result.prepend(u"::"_s);
    return result;
}

QString Generator::getFullTypeName(const AbstractMetaType &type)
{
    if (type.isCString())
        return u"const char*"_s;
    if (type.isVoidPointer())
        return u"void*"_s;
    if (type.typeEntry()->isContainer())
        return u"::"_s + type.cppSignature();
    QString typeName;
    if (type.typeEntry()->isComplex() && type.hasInstantiations())
        typeName = getFullTypeNameWithoutModifiers(type);
    else
        typeName = getFullTypeName(type.typeEntry());
    return typeName + QString::fromLatin1("*").repeated(type.indirections());
}

QString Generator::getFullTypeName(const AbstractMetaClassCPtr &metaClass)
{
    return u"::"_s + metaClass->qualifiedCppName();
}

QString Generator::getFullTypeNameWithoutModifiers(const AbstractMetaType &type)
{
    if (type.isCString())
        return u"const char*"_s;
    if (type.isVoidPointer())
        return u"void*"_s;
    if (!type.hasInstantiations())
        return getFullTypeName(type.typeEntry());
    QString typeName = type.cppSignature();
    if (type.isConstant())
        typeName.remove(0, sizeof("const ") / sizeof(char) - 1);
    switch (type.referenceType()) {
    case NoReference:
        break;
    case LValueReference:
        typeName.chop(1);
        break;
    case RValueReference:
        typeName.chop(2);
        break;
    }
    while (typeName.endsWith(u'*') || typeName.endsWith(u' '))
        typeName.chop(1);
    return u"::"_s + typeName;
}

std::optional<DefaultValue>
    Generator::minimalConstructor(const ApiExtractorResult &api,
                                  const AbstractMetaType &type,
                                  QString *errorString)
{
    if (type.referenceType() == LValueReference && type.isObjectType())
        return {};

    if (type.isContainer()) {
        QString ctor = type.cppSignature();
        if (ctor.endsWith(u'*')) {
            ctor.chop(1);
            return DefaultValue(DefaultValue::Pointer, ctor.trimmed());
        }
        if (ctor.startsWith(u"const "))
            ctor.remove(0, sizeof("const ") / sizeof(char) - 1);
        if (ctor.endsWith(u'&')) {
            ctor.chop(1);
            ctor = ctor.trimmed();
        }
        return DefaultValue(DefaultValue::DefaultConstructor, u"::"_s + ctor);
    }

    if (type.isNativePointer())
        return DefaultValue(DefaultValue::Pointer, type.typeEntry()->qualifiedCppName());
    if (type.isPointer())
        return DefaultValue(DefaultValue::Pointer, u"::"_s + type.typeEntry()->qualifiedCppName());

    if (type.typeEntry()->isSmartPointer())
        return minimalConstructor(api, type.typeEntry());

    if (type.typeEntry()->isComplex()) {
        auto cType = std::static_pointer_cast<const ComplexTypeEntry>(type.typeEntry());
        if (cType->hasDefaultConstructor())
            return DefaultValue(DefaultValue::Custom, cType->defaultConstructor());
        auto klass = AbstractMetaClass::findClass(api.classes(), cType);
        if (!klass) {
            if (errorString != nullptr)
                *errorString = msgClassNotFound(cType);
            return {};
        }
        auto ctorO = minimalConstructor(api, klass);
        if (ctorO.has_value() && type.hasInstantiations()) {
            auto ctor = ctorO.value();
            QString v = ctor.value();
            v.replace(getFullTypeName(cType), getFullTypeNameWithoutModifiers(type));
            ctor.setValue(v);
            return ctor;
        }
        return ctorO;
    }

    return minimalConstructor(api, type.typeEntry(), errorString);
}

std::optional<DefaultValue>
   Generator::minimalConstructor(const ApiExtractorResult &api,
                                 const TypeEntryCPtr &type,
                                 QString *errorString)
{
    if (!type)
        return {};

    if (isCppPrimitive(type)) {
        const QString &name = type->qualifiedCppName();
        return name == u"bool"
            ? DefaultValue(DefaultValue::Boolean)
            : DefaultValue(DefaultValue::CppScalar, name);
    }

    if (type->isEnum()) {
        const auto enumEntry = std::static_pointer_cast<const EnumTypeEntry>(type);
        if (const auto nullValue = enumEntry->nullValue())
            return DefaultValue(DefaultValue::Enum, nullValue->name());
        return DefaultValue(DefaultValue::Custom,
                            u"static_cast< ::"_s + type->qualifiedCppName()
                            + u">(0)"_s);
    }

    if (type->isFlags()) {
        return DefaultValue(DefaultValue::Custom,
                            type->qualifiedCppName() + u"(0)"_s);
    }

    if (type->isPrimitive()) {
        QString ctor = std::static_pointer_cast<const PrimitiveTypeEntry>(type)->defaultConstructor();
        // If a non-C++ (i.e. defined by the user) primitive type does not have
        // a default constructor defined by the user, the empty constructor is
        // heuristically returned. If this is wrong the build of the generated
        // bindings will tell.
        return ctor.isEmpty()
            ? DefaultValue(DefaultValue::DefaultConstructorWithDefaultValues, u"::"_s
                           + type->qualifiedCppName())
            : DefaultValue(DefaultValue::Custom, ctor);
    }

    if (type->isSmartPointer())
        return DefaultValue(DefaultValue::DefaultConstructor, type->qualifiedCppName());

    if (type->isComplex()) {
        auto klass = AbstractMetaClass::findClass(api.classes(), type);
        if (!klass) {
            if (errorString != nullptr)
                *errorString = msgClassNotFound(type);
            return {};
        }
        return minimalConstructor(api, klass, errorString);
    }

    if (errorString != nullptr)
        *errorString = u"No default value could be determined."_s;
    return {};
}

static QString constructorCall(const QString &qualifiedCppName, const QStringList &args)
{
    return u"::"_s + qualifiedCppName + u'('
        + args.join(u", "_s) + u')';
}

std::optional<DefaultValue>
    Generator::minimalConstructor(const ApiExtractorResult &api,
                                  const AbstractMetaClassCPtr &metaClass,
                                  QString *errorString)
{
    if (!metaClass)
        return {};

    auto cType = std::static_pointer_cast<const ComplexTypeEntry>(metaClass->typeEntry());
    if (cType->hasDefaultConstructor())
        return DefaultValue(DefaultValue::Custom, cType->defaultConstructor());

    const QString qualifiedCppName = cType->qualifiedCppName();
    // Obtain a list of constructors sorted by complexity and number of arguments
    QMultiMap<int, const AbstractMetaFunctionCPtr> candidates;
    const auto &constructors = metaClass->queryFunctions(FunctionQueryOption::Constructors);
    for (const auto &ctor : constructors) {
        if (!ctor->isUserAdded() && !ctor->isPrivate()
            && (ctor->isPublic() || !api.flags().testFlag(ApiExtractorFlag::AvoidProtectedHack))) {
            // No arguments: Default constructible
            const auto &arguments = ctor->arguments();
            if (arguments.isEmpty()) {
                return DefaultValue(DefaultValue::DefaultConstructor,
                                    u"::"_s + qualifiedCppName);
            }
            // First argument has unmodified default: Default constructible with values
            if (arguments.constFirst().hasUnmodifiedDefaultValueExpression()) {
                return DefaultValue(DefaultValue::DefaultConstructorWithDefaultValues,
                                    u"::"_s + qualifiedCppName);
            }
            // Examine arguments, exclude functions taking a self parameter
            bool simple = true;
            bool suitable = true;
            for (qsizetype i = 0, size = arguments.size();
                 suitable && i < size && !arguments.at(i).hasOriginalDefaultValueExpression(); ++i) {
                const AbstractMetaArgument &arg = arguments.at(i);
                TypeEntryCPtr aType = arg.type().typeEntry();
                suitable &= aType != cType;
                simple &= isCppPrimitive(aType) || aType->isEnum() || arg.type().isPointer();
            }
            if (suitable)
                candidates.insert(arguments.size() + (simple ? 0 : 100), ctor);
        }
    }

    for (auto it = candidates.cbegin(), end = candidates.cend(); it != end; ++it) {
        const AbstractMetaArgumentList &arguments = it.value()->arguments();
        QStringList args;
        for (qsizetype i = 0, size = arguments.size(); i < size; ++i) {
            const AbstractMetaArgument &arg = arguments.at(i);
            if (arg.hasModifiedDefaultValueExpression()) {
                args << arg.defaultValueExpression(); // Spell out modified values
                break;
            }
            if (arg.hasOriginalDefaultValueExpression())
                break;
            auto argValue = minimalConstructor(api, arg.type(), errorString);
            if (!argValue.has_value())
                return {};
            args << argValue->constructorParameter();
        }
        return DefaultValue(DefaultValue::Custom, constructorCall(qualifiedCppName, args));
    }

    return {};
}

QString Generator::translateType(AbstractMetaType cType,
                                 const AbstractMetaClassCPtr &context,
                                 Options options) const
{
    QString s;

    if (context &&
        context->typeEntry()->isGenericClass() &&
        cType.originalTemplateType()) {
        cType = *cType.originalTemplateType();
    }

    if (cType.isVoid()) {
        s = u"void"_s;
    } else if (cType.isArray()) {
        s = translateType(*cType.arrayElementType(), context, options) + u"[]"_s;
    } else {
        AbstractMetaType copyType = cType;
        if (options & Generator::ExcludeConst || options & Generator::ExcludeReference) {
            if (options & Generator::ExcludeConst)
                copyType.setConstant(false);
            if (options & Generator::ExcludeReference)
                copyType.setReferenceType(NoReference);
        }

        s = copyType.cppSignature();
        const auto te = copyType.typeEntry();
        if (!te->isVoid() && !isCppPrimitive(te)) { // Add scope resolution
            const auto pos = s.indexOf(te->qualifiedCppName()); // Skip const/volatile
            Q_ASSERT(pos >= 0);
            s.insert(pos, u"::"_s);
        }
    }

    return s;
}

static const QHash<QString, QString> &pythonOperators()
{
    static const QHash<QString, QString> result = {
        // call operator
        {u"operator()"_s, u"__call__"_s},
        // Arithmetic operators
        {u"operator+"_s, u"__add__"_s},
        {u"operator-"_s, u"__sub__"_s},
        {u"operator*"_s, u"__mul__"_s},
        {u"operator/"_s, u"__div__"_s},
        {u"operator%"_s, u"__mod__"_s},
        // Inplace arithmetic operators
        {u"operator+="_s, u"__iadd__"_s},
        {u"operator-="_s, u"__isub__"_s},
        {u"operator++"_s, u"__iadd__"_s},
        {u"operator--"_s, u"__isub__"_s},
        {u"operator*="_s, u"__imul__"_s},
        {u"operator/="_s, u"__idiv__"_s},
        {u"operator%="_s, u"__imod__"_s},
        // Bitwise operators
        {u"operator&"_s, u"__and__"_s},
        {u"operator^"_s, u"__xor__"_s},
        {u"operator|"_s, u"__or__"_s},
        {u"operator<<"_s, u"__lshift__"_s},
        {u"operator>>"_s, u"__rshift__"_s},
        {u"operator~"_s, u"__invert__"_s},
        // Inplace bitwise operators
        {u"operator&="_s, u"__iand__"_s},
        {u"operator^="_s, u"__ixor__"_s},
        {u"operator|="_s, u"__ior__"_s},
        {u"operator<<="_s, u"__ilshift__"_s},
        {u"operator>>="_s, u"__irshift__"_s},
        // Comparison operators
        {u"operator=="_s, u"__eq__"_s},
        {u"operator!="_s, u"__ne__"_s},
        {u"operator<"_s, u"__lt__"_s},
        {u"operator>"_s, u"__gt__"_s},
        {u"operator<="_s, u"__le__"_s},
        {u"operator>="_s, u"__ge__"_s}
    };
    return result;
}

QString Generator::pythonOperatorFunctionName(const QString &cppOpFuncName)
{
    return pythonOperators().value(cppOpFuncName);
}

QString Generator::subDirectoryForPackage(QString packageNameIn) const
{
    if (packageNameIn.isEmpty())
        packageNameIn = packageName();
    packageNameIn.replace(u'.', QDir::separator());
    return packageNameIn;
}

template<typename T>
static QString getClassTargetFullName_(T t, bool includePackageName)
{
    QString name = t->name();
    AbstractMetaClassCPtr context = t->enclosingClass();
    while (context) {
        // If the type was marked as 'visible=false' we should not use it in
        // the type name
        if (NamespaceTypeEntry::isVisibleScope(context->typeEntry())) {
            name.prepend(u'.');
            name.prepend(context->name());
        }
        context = context->enclosingClass();
    }
    if (includePackageName) {
        name.prepend(u'.');
        name.prepend(t->package());
    }
    return name;
}

QString getClassTargetFullName(const AbstractMetaClassCPtr &metaClass,
                               bool includePackageName)
{
    return getClassTargetFullName_(metaClass, includePackageName);
}

QString getClassTargetFullName(const AbstractMetaEnum &metaEnum,
                               bool includePackageName)
{
    return getClassTargetFullName_(&metaEnum, includePackageName);
}

QString getFilteredCppSignatureString(QString signature)
{
    signature.replace(u"::"_s, u"_"_s);
    signature.replace(u'<', u'_');
    signature.replace(u'>', u'_');
    signature.replace(u' ', u'_');
    return signature;
}
