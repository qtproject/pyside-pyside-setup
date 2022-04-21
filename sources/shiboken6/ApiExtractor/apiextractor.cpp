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

#include "apiextractor.h"
#include "apiextractorresult.h"
#include "apiextractorresultdata_p.h"
#include "abstractmetaargument.h"
#include "abstractmetabuilder.h"
#include "abstractmetaenum.h"
#include "abstractmetafield.h"
#include "abstractmetafunction.h"
#include "abstractmetalang.h"
#include "exception.h"
#include "fileout.h"
#include "modifications.h"
#include "reporthandler.h"
#include "typedatabase.h"
#include "typesystem.h"

#include "qtcompat.h"

#include <QtCore/QDir>
#include <QtCore/QDebug>
#include <QtCore/QTemporaryFile>

#include <algorithm>
#include <iostream>
#include <iterator>

using namespace Qt::StringLiterals;

struct InstantiationCollectContext
{
    AbstractMetaTypeList instantiatedContainers;
    InstantiatedSmartPointers instantiatedSmartPointers;
    QStringList instantiatedContainersNames;
};

struct ApiExtractorPrivate
{
    bool runHelper(ApiExtractorFlags flags);

    static QString getSimplifiedContainerTypeName(const AbstractMetaType &type);
    void addInstantiatedContainersAndSmartPointers(InstantiationCollectContext &context,
                                                   const AbstractMetaType &type,
                                                   const QString &contextName);
    void collectInstantiatedContainersAndSmartPointers(InstantiationCollectContext &context,
                                                       const AbstractMetaFunctionCPtr &func);
    void collectInstantiatedContainersAndSmartPointers(InstantiationCollectContext &context,
                                                       const AbstractMetaClass *metaClass);
    void collectInstantiatedContainersAndSmartPointers(InstantiationCollectContext &context);
    void collectInstantiatedOpqaqueContainers(InstantiationCollectContext &context);
    void collectContainerTypesFromSnippets(InstantiationCollectContext &context);
    void collectContainerTypesFromConverterMacros(InstantiationCollectContext &context,
                                                  const QString &code,
                                                  bool toPythonMacro);
    void addInstantiatedSmartPointer(InstantiationCollectContext &context,
                                     const AbstractMetaType &type);

    QString m_typeSystemFileName;
    QFileInfoList m_cppFileNames;
    HeaderPaths m_includePaths;
    QStringList m_clangOptions;
    AbstractMetaBuilder* m_builder = nullptr;
    QString m_logDirectory;
    LanguageLevel m_languageLevel = LanguageLevel::Default;
    bool m_skipDeprecated = false;
};

ApiExtractor::ApiExtractor() :
      d(new ApiExtractorPrivate)
{
    // Environment TYPESYSTEMPATH
    QString envTypesystemPaths = QFile::decodeName(qgetenv("TYPESYSTEMPATH"));
    if (!envTypesystemPaths.isEmpty())
        TypeDatabase::instance()->addTypesystemPath(envTypesystemPaths);
}

ApiExtractor::~ApiExtractor()
{
    delete d->m_builder;
    delete d;
}

void ApiExtractor::addTypesystemSearchPath (const QString& path)
{
    TypeDatabase::instance()->addTypesystemPath(path);
}

void ApiExtractor::addTypesystemSearchPath(const QStringList& paths)
{
    for (const QString &path : paths)
        addTypesystemSearchPath(path);
}

void ApiExtractor::setTypesystemKeywords(const QStringList &keywords)
{
    TypeDatabase::instance()->setTypesystemKeywords(keywords);
}

void ApiExtractor::addIncludePath(const HeaderPath& path)
{
    d->m_includePaths << path;
}

void ApiExtractor::addIncludePath(const HeaderPaths& paths)
{
    d->m_includePaths << paths;
}

HeaderPaths ApiExtractor::includePaths() const
{
    return d->m_includePaths;
}

void ApiExtractor::setLogDirectory(const QString& logDir)
{
    d->m_logDirectory = logDir;
}

void ApiExtractor::setCppFileNames(const QFileInfoList &cppFileName)
{
    d->m_cppFileNames = cppFileName;
}

QFileInfoList ApiExtractor::cppFileNames() const
{
    return d->m_cppFileNames;
}

void ApiExtractor::setTypeSystem(const QString& typeSystemFileName)
{
    d->m_typeSystemFileName = typeSystemFileName;
}

QString ApiExtractor::typeSystem() const
{
    return d->m_typeSystemFileName;
}

void ApiExtractor::setSkipDeprecated(bool value)
{
    d->m_skipDeprecated = value;
    if (d->m_builder)
        d->m_builder->setSkipDeprecated(d->m_skipDeprecated);
}

void ApiExtractor::setSuppressWarnings ( bool value )
{
    TypeDatabase::instance()->setSuppressWarnings(value);
}

void ApiExtractor::setSilent ( bool value )
{
    ReportHandler::setSilent(value);
}

bool ApiExtractor::setApiVersion(const QString& package, const QString &version)
{
    return TypeDatabase::setApiVersion(package, version);
}

void ApiExtractor::setDropTypeEntries(const QStringList &dropEntries)
{
    TypeDatabase::instance()->setDropTypeEntries(dropEntries);
}

const AbstractMetaEnumList &ApiExtractor::globalEnums() const
{
    Q_ASSERT(d->m_builder);
    return d->m_builder->globalEnums();
}

const AbstractMetaFunctionCList &ApiExtractor::globalFunctions() const
{
    Q_ASSERT(d->m_builder);
    return d->m_builder->globalFunctions();
}

const AbstractMetaClassList &ApiExtractor::classes() const
{
    Q_ASSERT(d->m_builder);
    return d->m_builder->classes();
}

const AbstractMetaClassList &ApiExtractor::smartPointers() const
{
    Q_ASSERT(d->m_builder);
    return d->m_builder->smartPointers();
}

// Add defines required for parsing Qt code headers
static void addPySideExtensions(QByteArrayList *a)
{
    // Make "signals:", "slots:" visible as access specifiers
    a->append(QByteArrayLiteral("-DQT_ANNOTATE_ACCESS_SPECIFIER(a)=__attribute__((annotate(#a)))"));

    // Q_PROPERTY is defined as class annotation which does not work since a
    // sequence of properties will to expand to a sequence of annotations
    // annotating nothing, causing clang to complain. Instead, define it away in a
    // static assert with the stringified argument in a ','-operator (cf qdoc).
    a->append(QByteArrayLiteral("-DQT_ANNOTATE_CLASS(type,...)=static_assert(sizeof(#__VA_ARGS__),#type);"));

    // With Qt6, qsimd.h became public header and was included in <QtCore>. That
    // introduced a conflict with libclang headers on macOS. To be able to include
    // <QtCore>, we prevent its inclusion by adding its include guard.
    a->append(QByteArrayLiteral("-DQSIMD_H"));
}

bool ApiExtractorPrivate::runHelper(ApiExtractorFlags flags)
{
    if (m_builder)
        return false;

    if (!TypeDatabase::instance()->parseFile(m_typeSystemFileName)) {
        std::cerr << "Cannot parse file: " << qPrintable(m_typeSystemFileName);
        return false;
    }

    const QString pattern = QDir::tempPath() + u'/'
        + m_cppFileNames.constFirst().baseName()
        + QStringLiteral("_XXXXXX.hpp");
    QTemporaryFile ppFile(pattern);
    bool autoRemove = !qEnvironmentVariableIsSet("KEEP_TEMP_FILES");
    // make sure that a tempfile can be written
    if (!ppFile.open()) {
        std::cerr << "could not create tempfile " << qPrintable(pattern)
            << ": " << qPrintable(ppFile.errorString()) << '\n';
        return false;
    }
    for (const auto &cppFileName : qAsConst(m_cppFileNames)) {
        ppFile.write("#include \"");
        ppFile.write(cppFileName.absoluteFilePath().toLocal8Bit());
        ppFile.write("\"\n");
    }
    const QString preprocessedCppFileName = ppFile.fileName();
    ppFile.close();
    m_builder = new AbstractMetaBuilder;
    m_builder->setLogDirectory(m_logDirectory);
    m_builder->setGlobalHeaders(m_cppFileNames);
    m_builder->setSkipDeprecated(m_skipDeprecated);
    m_builder->setHeaderPaths(m_includePaths);

    QByteArrayList arguments;
    const auto clangOptionsSize = m_clangOptions.size();
    arguments.reserve(m_includePaths.size() + clangOptionsSize + 1);

    bool addCompilerSupportArguments = true;
    if (clangOptionsSize > 0) {
        qsizetype i = 0;
        if (m_clangOptions.at(i) == u"-") {
            ++i;
            addCompilerSupportArguments = false; // No built-in options
        }
        for (; i < clangOptionsSize; ++i)
            arguments.append(m_clangOptions.at(i).toUtf8());
    }

    for (const HeaderPath &headerPath : qAsConst(m_includePaths))
        arguments.append(HeaderPath::includeOption(headerPath));
    arguments.append(QFile::encodeName(preprocessedCppFileName));
    if (ReportHandler::isDebug(ReportHandler::SparseDebug)) {
        qCInfo(lcShiboken).noquote().nospace()
            << "clang language level: " << int(m_languageLevel)
            << "\nclang arguments: " << arguments;
    }

    if (flags.testFlag(ApiExtractorFlag::UsePySideExtensions))
        addPySideExtensions(&arguments);

    const bool result = m_builder->build(arguments, flags, addCompilerSupportArguments,
                                         m_languageLevel);
    if (!result)
        autoRemove = false;
    if (!autoRemove) {
        ppFile.setAutoRemove(false);
        std::cerr << "Keeping temporary file: " << qPrintable(QDir::toNativeSeparators(preprocessedCppFileName)) << '\n';
    }
    return result;
}

static inline void classListToCList(const AbstractMetaClassList &list, AbstractMetaClassCList *target)
{
    target->reserve(list.size());
    std::copy(list.cbegin(), list.cend(), std::back_inserter(*target));
}

std::optional<ApiExtractorResult> ApiExtractor::run(ApiExtractorFlags flags)
{
    if (!d->runHelper(flags))
        return {};
    InstantiationCollectContext collectContext;
    d->collectInstantiatedContainersAndSmartPointers(collectContext);

    auto *data = new ApiExtractorResultData;

    classListToCList(d->m_builder->takeClasses(), &data->m_metaClasses);
    classListToCList(d->m_builder->takeTemplates(), &data->m_templates);
    classListToCList(d->m_builder->takeSmartPointers(), &data->m_smartPointers);
    data->m_globalFunctions = d->m_builder->globalFunctions();
    data->m_globalEnums = d->m_builder->globalEnums();
    data->m_enums = d->m_builder->typeEntryToEnumsHash();
    data->m_flags = flags;
    qSwap(data->m_instantiatedContainers, collectContext.instantiatedContainers);
    qSwap(data->m_instantiatedSmartPointers, collectContext.instantiatedSmartPointers);
    return ApiExtractorResult(data);
}

LanguageLevel ApiExtractor::languageLevel() const
{
    return d->m_languageLevel;
}

void ApiExtractor::setLanguageLevel(LanguageLevel languageLevel)
{
    d->m_languageLevel = languageLevel;
}

QStringList ApiExtractor::clangOptions() const
{
    return d->m_clangOptions;
}

void ApiExtractor::setClangOptions(const QStringList &co)
{
    d->m_clangOptions = co;
}

void ApiExtractor::setUseGlobalHeader(bool h)
{
    AbstractMetaBuilder::setUseGlobalHeader(h);
}

AbstractMetaFunctionPtr
    ApiExtractor::inheritTemplateFunction(const AbstractMetaFunctionCPtr &function,
                                          const AbstractMetaTypeList &templateTypes)
{
    return AbstractMetaBuilder::inheritTemplateFunction(function, templateTypes);
}

AbstractMetaFunctionPtr
    ApiExtractor::inheritTemplateMember(const AbstractMetaFunctionCPtr &function,
                                        const AbstractMetaTypeList &templateTypes,
                                        const AbstractMetaClass *templateClass,
                                        AbstractMetaClass *subclass)
{
    return AbstractMetaBuilder::inheritTemplateMember(function, templateTypes,
                                                      templateClass, subclass);
}

QString ApiExtractorPrivate::getSimplifiedContainerTypeName(const AbstractMetaType &type)
{
    const QString signature = type.cppSignature();
    if (!type.typeEntry()->isContainer() && !type.typeEntry()->isSmartPointer())
        return signature;
    QString typeName = signature;
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
    return typeName;
}

// Strip a "const QSharedPtr<const Foo> &" or similar to "QSharedPtr<Foo>" (PYSIDE-1016/454)
AbstractMetaType canonicalSmartPtrInstantiation(const AbstractMetaType &type)
{
    const AbstractMetaTypeList &instantiations = type.instantiations();
    Q_ASSERT(instantiations.size() == 1);
    const bool needsFix = type.isConstant() || type.referenceType() != NoReference;
    const bool pointeeNeedsFix = instantiations.constFirst().isConstant();
    if (!needsFix && !pointeeNeedsFix)
        return type;
    auto fixedType = type;
    fixedType.setReferenceType(NoReference);
    fixedType.setConstant(false);
    if (pointeeNeedsFix) {
        auto fixedPointeeType = instantiations.constFirst();
        fixedPointeeType.setConstant(false);
        fixedType.setInstantiations(AbstractMetaTypeList(1, fixedPointeeType));
    }
    return fixedType;
}

static inline const TypeEntry *pointeeTypeEntry(const AbstractMetaType &smartPtrType)
{
    return smartPtrType.instantiations().constFirst().typeEntry();
}

void
ApiExtractorPrivate::addInstantiatedContainersAndSmartPointers(InstantiationCollectContext &context,
                                                               const AbstractMetaType &type,
                                                               const QString &contextName)
{
    for (const auto &t : type.instantiations())
        addInstantiatedContainersAndSmartPointers(context, t, contextName);
    const auto typeEntry = type.typeEntry();
    const bool isContainer = typeEntry->isContainer();
    if (!isContainer
        && !(typeEntry->isSmartPointer() && typeEntry->generateCode())) {
        return;
    }
    if (type.hasTemplateChildren()) {
        QString piece = isContainer ? QStringLiteral("container") : QStringLiteral("smart pointer");
        QString warning =
            QString::fromLatin1("Skipping instantiation of %1 '%2' because it has template"
                                " arguments.").arg(piece, type.originalTypeDescription());
        if (!contextName.isEmpty())
            warning.append(QStringLiteral(" Calling context: ") + contextName);

        qCWarning(lcShiboken).noquote().nospace() << warning;
        return;

    }
    if (isContainer) {
        const QString typeName = getSimplifiedContainerTypeName(type);
        if (!context.instantiatedContainersNames.contains(typeName)) {
            context.instantiatedContainersNames.append(typeName);
            auto simplifiedType = type;
            simplifiedType.setIndirections(0);
            simplifiedType.setConstant(false);
            simplifiedType.setReferenceType(NoReference);
            simplifiedType.decideUsagePattern();
            context.instantiatedContainers.append(simplifiedType);
        }
        return;
    }

    // Is smart pointer. Check if the (const?) pointee is already known for the given
    // smart pointer type entry.
    auto pt = pointeeTypeEntry(type);
    const bool present =
        std::any_of(context.instantiatedSmartPointers.cbegin(),
                    context.instantiatedSmartPointers.cend(),
                    [typeEntry, pt] (const InstantiatedSmartPointer &smp) {
                        return smp.type.typeEntry() == typeEntry
                            && pointeeTypeEntry(smp.type) == pt;
                    });
    if (!present)
        addInstantiatedSmartPointer(context, type);
}

void ApiExtractorPrivate::addInstantiatedSmartPointer(InstantiationCollectContext &context,
                                                      const AbstractMetaType &type)
{
    InstantiatedSmartPointer smp;
    smp.type = type;
    smp.smartPointer = AbstractMetaClass::findClass(m_builder->smartPointers(),
                                                    type.typeEntry());
    Q_ASSERT(smp.smartPointer);
    context.instantiatedSmartPointers.append(smp);
}

void
ApiExtractorPrivate::collectInstantiatedContainersAndSmartPointers(InstantiationCollectContext &context,
                                                                   const AbstractMetaFunctionCPtr &func)
{
    addInstantiatedContainersAndSmartPointers(context, func->type(), func->signature());
    for (const AbstractMetaArgument &arg : func->arguments())
        addInstantiatedContainersAndSmartPointers(context, arg.type(), func->signature());
}

void
ApiExtractorPrivate::collectInstantiatedContainersAndSmartPointers(InstantiationCollectContext &context,
                                                                   const AbstractMetaClass *metaClass)
{
    if (!metaClass->typeEntry()->generateCode())
        return;
    for (const auto &func : metaClass->functions())
        collectInstantiatedContainersAndSmartPointers(context, func);
    for (const AbstractMetaField &field : metaClass->fields())
        addInstantiatedContainersAndSmartPointers(context, field.type(), field.name());
    for (auto *innerClass : metaClass->innerClasses())
        collectInstantiatedContainersAndSmartPointers(context, innerClass);
}

void
ApiExtractorPrivate::collectInstantiatedContainersAndSmartPointers(InstantiationCollectContext &context)
{
    collectInstantiatedOpqaqueContainers(context);
    for (const auto &func : m_builder->globalFunctions())
        collectInstantiatedContainersAndSmartPointers(context, func);
    for (auto metaClass : m_builder->classes())
        collectInstantiatedContainersAndSmartPointers(context, metaClass);
    collectContainerTypesFromSnippets(context);
}

// Whether to generate an opaque container: If the instantiation type is in
// the current package or, for primitive types, if the container is in the
// current package.
static bool generateOpaqueContainer(const AbstractMetaType &type,
                                    const TypeSystemTypeEntry *moduleEntry)
{
    auto *te = type.instantiations().constFirst().typeEntry();
    auto *typeModuleEntry = te->typeSystemTypeEntry();
    return typeModuleEntry == moduleEntry
           || (te->isPrimitive() && type.typeEntry()->typeSystemTypeEntry() == moduleEntry);
}

void ApiExtractorPrivate::collectInstantiatedOpqaqueContainers(InstantiationCollectContext &context)
{
    // Add all instantiations of opaque containers for types from the current
    // module.
    auto *td = TypeDatabase::instance();
    const auto *moduleEntry = TypeDatabase::instance()->defaultTypeSystemType();
    const auto &containers = td->containerTypes();
    for (const auto *container : containers) {
        for (const auto &oc : container->opaqueContainers()) {
            QString errorMessage;
            const QString typeName = container->qualifiedCppName() + u'<'
                                     + oc.instantiation + u'>';
            auto typeOpt = AbstractMetaType::fromString(typeName, &errorMessage);
            if (typeOpt.has_value()
                && generateOpaqueContainer(typeOpt.value(), moduleEntry)) {
                addInstantiatedContainersAndSmartPointers(context, typeOpt.value(),
                                                          u"opaque containers"_s);
            }
        }
    }
}

static void getCode(QStringList &code, const CodeSnipList &codeSnips)
{
    for (const CodeSnip &snip : qAsConst(codeSnips))
        code.append(snip.code());
}

static void getCode(QStringList &code, const TypeEntry *type)
{
    getCode(code, type->codeSnips());

    CustomConversion *customConversion = type->customConversion();
    if (!customConversion)
        return;

    if (!customConversion->nativeToTargetConversion().isEmpty())
        code.append(customConversion->nativeToTargetConversion());

    const auto &toCppConversions = customConversion->targetToNativeConversions();
    if (toCppConversions.isEmpty())
        return;

    for (CustomConversion::TargetToNativeConversion *toNative : qAsConst(toCppConversions))
        code.append(toNative->conversion());
}

void ApiExtractorPrivate::collectContainerTypesFromSnippets(InstantiationCollectContext &context)
{
    QStringList snips;
    auto *td = TypeDatabase::instance();
    const PrimitiveTypeEntryList &primitiveTypeList = td->primitiveTypes();
    for (const PrimitiveTypeEntry *type : primitiveTypeList)
        getCode(snips, type);
    const ContainerTypeEntryList &containerTypeList = td->containerTypes();
    for (const ContainerTypeEntry *type : containerTypeList)
        getCode(snips, type);
    for (auto metaClass : m_builder->classes())
        getCode(snips, metaClass->typeEntry());

    const TypeSystemTypeEntry *moduleEntry = td->defaultTypeSystemType();
    Q_ASSERT(moduleEntry);
    getCode(snips, moduleEntry);

    for (const auto &func : m_builder->globalFunctions())
        getCode(snips, func->injectedCodeSnips());

    for (const QString &code : qAsConst(snips)) {
        collectContainerTypesFromConverterMacros(context, code, true);
        collectContainerTypesFromConverterMacros(context, code, false);
    }
}

void
ApiExtractorPrivate::collectContainerTypesFromConverterMacros(InstantiationCollectContext &context,
                                                              const QString &code,
                                                              bool toPythonMacro)
{
    QString convMacro = toPythonMacro ? u"%CONVERTTOPYTHON["_s : u"%CONVERTTOCPP["_s;
    int offset = toPythonMacro ? sizeof("%CONVERTTOPYTHON") : sizeof("%CONVERTTOCPP");
    int start = 0;
    QString errorMessage;
    while ((start = code.indexOf(convMacro, start)) != -1) {
        int end = code.indexOf(u']', start);
        start += offset;
        if (code.at(start) != u'%') {
            QString typeString = code.mid(start, end - start);
            auto type = AbstractMetaType::fromString(typeString, &errorMessage);
            if (type.has_value()) {
                const QString &d = type->originalTypeDescription();
                addInstantiatedContainersAndSmartPointers(context, type.value(), d);
            } else {
                QString m;
                QTextStream(&m) << __FUNCTION__ << ": Cannot translate type \""
                                << typeString << "\": " << errorMessage;
                throw Exception(m);
            }
        }
        start = end;
    }
}

#ifndef QT_NO_DEBUG_STREAM
template <class Container>
static void debugFormatSequence(QDebug &d, const char *key, const Container& c)
{
    if (c.isEmpty())
        return;
    const auto begin = c.begin();
    d << "\n  " << key << '[' << c.size() << "]=(";
    for (auto it = begin, end = c.end(); it != end; ++it) {
        if (it != begin)
            d << ", ";
        d << *it;
    }
    d << ')';
}

QDebug operator<<(QDebug d, const ApiExtractor &ae)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    if (ReportHandler::debugLevel() >= ReportHandler::FullDebug)
        d.setVerbosity(3); // Trigger verbose output of AbstractMetaClass
    d << "ApiExtractor(typeSystem=\"" << ae.typeSystem() << "\", cppFileNames=\""
      << ae.cppFileNames() << ", ";
    ae.d->m_builder->formatDebug(d);
    d << ')';
    return d;
}
#endif // QT_NO_DEBUG_STREAM
