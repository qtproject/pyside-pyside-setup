// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "headergenerator.h"
#include "configurablescope.h"
#include "generatorcontext.h"
#include <apiextractorresult.h>
#include <abstractmetaargument.h>
#include <abstractmetaenum.h>
#include <abstractmetafield.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetalang_helpers.h>
#include <codesnip.h>
#include <clangparser/compilersupport.h>
#include <typedatabase.h>
#include <reporthandler.h>
#include <textstream.h>
#include <fileout.h>
#include "containertypeentry.h"
#include "enumtypeentry.h"
#include "flagstypeentry.h"
#include "namespacetypeentry.h"
#include "primitivetypeentry.h"
#include "typedefentry.h"
#include "typesystemtypeentry.h"

#include "qtcompat.h"

#include <algorithm>
#include <set>

#include <QtCore/QDir>
#include <QtCore/QTextStream>
#include <QtCore/QVariant>
#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

//  PYSIDE-504: Handling the "protected hack"
//  The problem: Creating wrappers when the class has private destructors.
//  You can see an example on Windows in qclipboard_wrapper.h and others.
//  Simply search for the text "// C++11: need to declare (unimplemented) destructor".
//  The protected hack is the definition "#define protected public".
//  For most compilers, this "hack" is enabled, because the problem of private
//  destructors simply vanishes.
//
//  If one does not want to use this hack, then a new problem arises:
//  C++11 requires that a destructor is declared in a wrapper class when it is
//  private in the base class. There is no implementation allowed!
//
//  Unfortunately, MSVC in recent versions supports C++11, and due to restrictive
//  rules, it is impossible to use the hack with this compiler.
//  More unfortunate: Clang, when C++11 is enabled, also enforces a declaration
//  of a private destructor, but it falsely then creates a linker error!
//
//  Originally, we wanted to remove the protected hack. But due to the Clang
//  problem, we gave up on removal of the protected hack and use it always
//  when we can. This might change again when the Clang problem is solved.

static bool alwaysGenerateDestructorDeclaration()
{
    return  clang::compiler() == Compiler::Msvc;
}

const char *HeaderGenerator::protectedHackDefine = R"(// Workaround to access protected functions
#ifndef protected
#  define protected public
#endif

)";

QString HeaderGenerator::fileNameForContext(const GeneratorContext &context) const
{
    return headerFileNameForContext(context);
}

void HeaderGenerator::writeCopyCtor(TextStream &s,
                                    const AbstractMetaClassCPtr &metaClass) const
{
    s << wrapperName(metaClass) << "(const " << metaClass->qualifiedCppName()
      << "& self) : " << metaClass->qualifiedCppName() << "(self)\n{\n}\n\n";
}

static void writeProtectedEnums(TextStream &s, const AbstractMetaClassCPtr &metaClass)
{
    const QString name = metaClass->qualifiedCppName();
    for (const auto &e : metaClass->enums()) {
        if (e.isProtected())
            s << "using " << name << "::" << e.name() << ";\n";
    }
}

void HeaderGenerator::generateClass(TextStream &s, const GeneratorContext &classContext)
{
    const AbstractMetaClassCPtr metaClass = classContext.metaClass();

    // write license comment
    s << licenseComment();

    QString wrapperName = classContext.effectiveClassName();
    QString outerHeaderGuard = getFilteredCppSignatureString(wrapperName).toUpper();

    // Header
    s << "#ifndef SBK_" << outerHeaderGuard << "_H\n";
    s << "#define SBK_" << outerHeaderGuard << "_H\n\n";

    if (!avoidProtectedHack())
        s << protectedHackDefine;

    //Includes
    s << metaClass->typeEntry()->include() << '\n';
    for (auto &inst : metaClass->templateBaseClassInstantiations())
        s << inst.typeEntry()->include();

    if (classContext.useWrapper())
        writeWrapperClass(s, wrapperName, classContext);

    s << "#endif // SBK_" << outerHeaderGuard << "_H\n\n";
}

void HeaderGenerator::writeWrapperClass(TextStream &s,
                                        const QString &wrapperName,
                                        const GeneratorContext &classContext) const
{
    const auto metaClass = classContext.metaClass();

    if (avoidProtectedHack()) {
        const auto includeGroups = classIncludes(metaClass);
        for( const auto &includeGroup : includeGroups)
            s << includeGroup;
    }

    if (usePySideExtensions() && isQObject(metaClass))
        s << "namespace PySide { class DynamicQMetaObject; }\n\n";

    writeWrapperClassDeclaration(s, wrapperName, classContext);

    // PYSIDE-500: Use also includes for inherited wrapper classes other
    // modules, because without the protected hack, we sometimes need to
    // cast inherited wrappers. CppGenerator generates include statements for
    // the classes of the current module. For other modules, we insert the
    // declarations as recursive headers, since wrapper headers are not
    // installed. This keeps the file structure as simple as before the
    // enhanced inheritance.
    if (avoidProtectedHack()) {
        const auto &baseClasses = allBaseClasses(classContext.metaClass());
        for (const auto &baseClass : baseClasses) {
            const auto gen = baseClass->typeEntry()->codeGeneration();
            if (gen == TypeEntry::GenerateForSubclass) { // other module
                const auto baseContext = contextForClass(baseClass);
                if (baseContext.useWrapper())
                    writeInheritedWrapperClassDeclaration(s, baseContext);
            }
        }
    }
}

void HeaderGenerator::writeInheritedWrapperClassDeclaration(TextStream &s,
                                                            const GeneratorContext &classContext) const
{
    const QString wrapperName = classContext.effectiveClassName();
    const QString innerHeaderGuard =
        getFilteredCppSignatureString(wrapperName).toUpper();

    s << "#  ifndef SBK_" << innerHeaderGuard << "_H\n"
      << "#  define SBK_" << innerHeaderGuard << "_H\n\n"
      << "// Inherited base class:\n";

    writeWrapperClassDeclaration(s, wrapperName, classContext);

    s << "#  endif // SBK_" << innerHeaderGuard << "_H\n\n";
}

void HeaderGenerator::writeWrapperClassDeclaration(TextStream &s,
                                                   const QString &wrapperName,
                                                   const GeneratorContext &classContext) const
{
    const AbstractMetaClassCPtr metaClass = classContext.metaClass();
    const auto typeEntry = metaClass->typeEntry();
    InheritedOverloadSet inheritedOverloads;

    // write license comment
    s << licenseComment();

    // Class
    s << "class " << wrapperName
      << " : public " << metaClass->qualifiedCppName()
      << "\n{\npublic:\n" << indent;

    // Make protected enums accessible
    if (avoidProtectedHack()) {
        recurseClassHierarchy(metaClass, [&s] (const AbstractMetaClassCPtr &metaClass) {
            writeProtectedEnums(s, metaClass);
            return false;
        });
    }

    if (avoidProtectedHack() && metaClass->hasProtectedFields()) {
        s << "\n// Make protected fields accessible\n";
        const QString name = metaClass->qualifiedCppName();
        for (const auto &f : metaClass->fields()) {
            if (f.isProtected())
                s << "using " << name << "::"  << f.originalName() << ";\n";
        }
        s << '\n';
    }

    int maxOverrides = 0;
    for (const auto &func : metaClass->functions()) {
        const auto generation = functionGeneration(func);
        writeFunction(s, func, &inheritedOverloads, generation);
        // PYSIDE-803: Build a boolean cache for unused overrides.
        if (generation.testFlag(FunctionGenerationFlag::VirtualMethod))
            maxOverrides++;
    }
    if (!maxOverrides)
        maxOverrides = 1;

    //destructor
    // PYSIDE-504: When C++ 11 is used, then the destructor must always be declared.
    if (!avoidProtectedHack() || !metaClass->hasPrivateDestructor()
        || alwaysGenerateDestructorDeclaration()) {
        if (avoidProtectedHack() && metaClass->hasPrivateDestructor())
            s << "// C++11: need to declare (unimplemented) destructor because "
                 "the base class destructor is private.\n";
        s << '~' << wrapperName << "();\n";
    }

    writeClassCodeSnips(s, typeEntry->codeSnips(),
                        TypeSystem::CodeSnipPositionDeclaration, TypeSystem::NativeCode,
                        classContext);

    if ((!avoidProtectedHack() || !metaClass->hasPrivateDestructor())
        && usePySideExtensions() && isQObject(metaClass)) {
        s << outdent << "public:\n" << indent <<
            R"(int qt_metacall(QMetaObject::Call call, int id, void **args) override;
void *qt_metacast(const char *_clname) override;
)";
    }

    if (!inheritedOverloads.isEmpty()) {
        s << "// Inherited overloads, because the using keyword sux\n";
        for (const auto &func : std::as_const(inheritedOverloads))
            writeMemberFunctionWrapper(s, func);
    }

    if (usePySideExtensions())
        s << "static void pysideInitQtMetaTypes();\n";

    s << "void resetPyMethodCache();\n"
      << outdent << "private:\n" << indent
      << "mutable bool m_PyMethodCache[" << maxOverrides << "];\n"
      << outdent << "};\n\n";
}

// Write an inline wrapper around a function
void HeaderGenerator::writeMemberFunctionWrapper(TextStream &s,
                                                 const AbstractMetaFunctionCPtr &func,
                                                 const QString &postfix) const
{
    Q_ASSERT(!func->isConstructor() && !func->isOperatorOverload());
    s << "inline ";
    if (func->isStatic())
        s << "static ";
    s << functionSignature(func, {}, postfix, Generator::OriginalTypeDescription)
      << " { ";
    if (!func->isVoid())
        s << "return ";
    if (!func->isAbstract()) {
        // Use implementingClass() in case of multiple inheritance (for example
        // function setProperty() being inherited from QObject and
        // QDesignerPropertySheetExtension).
        auto klass = func->implementingClass();
        if (klass == nullptr)
            klass = func->ownerClass();
        s << klass->qualifiedCppName() << "::";
    }
    s << func->originalName() << '(';
    const AbstractMetaArgumentList &arguments = func->arguments();
    for (qsizetype i = 0, size = arguments.size(); i < size; ++i) {
        if (i > 0)
            s << ", ";
        const AbstractMetaArgument &arg = arguments.at(i);
        const auto &type = arg.type();
        TypeEntryCPtr enumTypeEntry;
        if (type.isFlags())
            enumTypeEntry = std::static_pointer_cast<const FlagsTypeEntry>(type.typeEntry())->originator();
        else if (type.isEnum())
            enumTypeEntry = type.typeEntry();
        if (enumTypeEntry) {
            s << type.cppSignature() << '(' << arg.name() << ')';
        } else if (type.passByValue() && type.isUniquePointer()) {
            s << stdMove(arg.name());
        } else {
            s << arg.name();
        }
    }
    s << "); }\n";
}

void HeaderGenerator::writeFunction(TextStream &s, const AbstractMetaFunctionCPtr &func,
                                    InheritedOverloadSet *inheritedOverloads,
                                    FunctionGeneration generation) const
{

    // do not write copy ctors here.
    if (generation.testFlag(FunctionGenerationFlag::WrapperSpecialCopyConstructor)) {
        writeCopyCtor(s, func->ownerClass());
        return;
    }

    if (generation.testFlag(FunctionGenerationFlag::ProtectedWrapper))
        writeMemberFunctionWrapper(s, func, u"_protected"_s);

    if (generation.testFlag(FunctionGenerationFlag::WrapperConstructor)) {
        Options option =  func->hasSignatureModifications()
            ? Generator::OriginalTypeDescription : Generator::NoOption;
        s << functionSignature(func, {}, {}, option) << ";\n";
        return;
    }

    const bool isVirtual = generation.testFlag(FunctionGenerationFlag::VirtualMethod);
    if (isVirtual || generation.testFlag(FunctionGenerationFlag::QMetaObjectMethod)) {
        s << functionSignature(func, {}, {}, Generator::OriginalTypeDescription)
            << " override;\n";
    }

    // Check if this method hide other methods in base classes
    if (isVirtual) {
        for (const auto &f : func->ownerClass()->functions()) {
            if (f != func
                && !f->isConstructor()
                && !f->isPrivate()
                && !f->isVirtual()
                && !f->isAbstract()
                && !f->isStatic()
                && f->name() == func->name()) {
                inheritedOverloads->insert(f);
            }
        }

        // TODO: when modified an abstract method ceases to be virtual but stays abstract
        //if (func->isModifiedRemoved() && func->isAbstract()) {
        //}
    }
}

static void _writeTypeIndexValue(TextStream &s, const QString &variableName,
                                 int typeIndex)
{
    s << "    " << AlignedField(variableName, 56) << " = " << typeIndex;
}

static inline void _writeTypeIndexValueLine(TextStream &s,
                                            const QString &variableName,
                                            int typeIndex)
{
    _writeTypeIndexValue(s, variableName, typeIndex);
    s << ",\n";
}

// Find equivalent typedefs "using Foo=QList<int>", "using Bar=QList<int>"
static AbstractMetaClassCPtr
    findEquivalentTemplateTypedef(const AbstractMetaClassCList &haystack,
                                  const AbstractMetaClassCPtr &needle)
{
    auto templateBaseClass = needle->templateBaseClass();
    const auto &instantiations = needle->templateBaseClassInstantiations();
    for (const auto &candidate : haystack) {
        if (candidate->isTypeDef()
            && candidate->templateBaseClass() == templateBaseClass
            && candidate->templateBaseClassInstantiations() == instantiations) {
            return candidate;
        }
    }
    return nullptr;
}

void HeaderGenerator::writeTypeIndexValueLine(TextStream &s, const ApiExtractorResult &api,
                                              const TypeEntryCPtr &typeEntry)
{
    if (!typeEntry || !typeEntry->generateCode())
        return;
    s.setFieldAlignment(QTextStream::AlignLeft);
    const int typeIndex = typeEntry->sbkIndex();
    _writeTypeIndexValueLine(s, getTypeIndexVariableName(typeEntry), typeIndex);
    if (typeEntry->isComplex()) {
        // For a typedef "using Foo=QList<int>", write a type index
        // SBK_QLIST_INT besides SBK_FOO which is then matched by function
        // argument. Check against duplicate typedefs for the same types.
        const auto cType = std::static_pointer_cast<const ComplexTypeEntry>(typeEntry);
        if (cType->baseContainerType()) {
            auto metaClass = AbstractMetaClass::findClass(api.classes(), cType);
            Q_ASSERT(metaClass != nullptr);
            if (metaClass->isTypeDef()
                && metaClass->templateBaseClass() != nullptr
                && findEquivalentTemplateTypedef(m_alternateTemplateIndexes,
                                                 metaClass) == nullptr) {
                const QString indexVariable =
                    getTypeAlternateTemplateIndexVariableName(metaClass);
                _writeTypeIndexValueLine(s, indexVariable, typeIndex);
                m_alternateTemplateIndexes.append(m_alternateTemplateIndexes);
            }
        }
    }
    if (typeEntry->isEnum()) {
        auto ete = std::static_pointer_cast<const EnumTypeEntry>(typeEntry);
        if (ete->flags())
            writeTypeIndexValueLine(s, api, ete->flags());
    }
}

void HeaderGenerator::writeTypeIndexValueLines(TextStream &s, const ApiExtractorResult &api,
                                               const AbstractMetaClassCPtr &metaClass)
{
    auto typeEntry = metaClass->typeEntry();
    if (!typeEntry->generateCode())
        return;
    // enum indices are required for invisible namespaces as well.
    for (const AbstractMetaEnum &metaEnum : metaClass->enums()) {
        if (!metaEnum.isPrivate())
            writeTypeIndexValueLine(s, api, metaEnum.typeEntry());
    }
    if (NamespaceTypeEntry::isVisibleScope(typeEntry))
        writeTypeIndexValueLine(s, api, typeEntry);
}

// Format the typedefs for the typedef entries to be generated
static void formatTypeDefEntries(TextStream &s)
{
    QList<TypedefEntryCPtr> entries;
    const auto typeDbEntries = TypeDatabase::instance()->typedefEntries();
    for (auto it = typeDbEntries.cbegin(), end = typeDbEntries.cend(); it != end; ++it) {
        if (it.value()->generateCode() != 0)
            entries.append(it.value());
    }
    if (entries.isEmpty())
        return;
    s << "\n// typedef entries\n";
    for (const auto &e : entries) {
        const QString name = e->qualifiedCppName();
        // Fixme: simplify by using nested namespaces in C++ 17.
        const auto components = QStringView{name}.split(u"::");
        const auto nameSpaceCount = components.size() -  1;
        for (qsizetype n = 0; n < nameSpaceCount; ++n)
            s << "namespace " << components.at(n) << " {\n";
        s << "using " << components.constLast() << " = " << e->sourceType() << ";\n";
        for (qsizetype n = 0; n < nameSpaceCount; ++n)
            s << "}\n";
    }
    s << '\n';
}

// Helpers for forward-declaring classes in the module header for the
// specialization of the SbkType template functions. This is possible if the
// class does not have inner types or enums which need to be known.
static bool canForwardDeclare(const AbstractMetaClassCPtr &c)
{
    if (c->isNamespace() || !c->enums().isEmpty()
        || !c->innerClasses().isEmpty() || c->isTypeDef()) {
        return false;
    }
    if (auto encl = c->enclosingClass())
        return encl->isNamespace();
    return true;
}

static void writeForwardDeclaration(TextStream &s, const AbstractMetaClassCPtr &c)
{
    Q_ASSERT(!c->isNamespace());
    const bool isStruct = c->attributes().testFlag(AbstractMetaClass::Struct);
    s << (isStruct ? "struct " : "class ");
    // Do not use name as this can be modified/renamed for target lang.
    const QString qualifiedCppName = c->qualifiedCppName();
    const auto lastQualifier = qualifiedCppName.lastIndexOf(u':');
    if (lastQualifier != -1)
        s << QStringView{qualifiedCppName}.mid(lastQualifier + 1);
    else
        s << qualifiedCppName;
    s << ";\n";
}

// Helpers for writing out namespaces hierarchically when writing class
// forward declarations to the module header. Ensure inline namespaces
// are marked as such (else clang complains) and namespaces are ordered.
struct NameSpace {
    AbstractMetaClassCPtr nameSpace;
    AbstractMetaClassCList classes;
};

static bool operator<(const NameSpace &n1, const NameSpace &n2)
{
    return n1.nameSpace->name() < n2.nameSpace->name();
}

using NameSpaces = QList<NameSpace>;

static qsizetype indexOf(const NameSpaces &nsps, const AbstractMetaClassCPtr &needle)
{
    for (qsizetype i = 0, count = nsps.size(); i < count; ++i) {
        if (nsps.at(i).nameSpace == needle)
            return i;
    }
    return -1;
}

static void writeNamespaceForwardDeclarationRecursion(TextStream &s, qsizetype idx,
                                                      const NameSpaces &nameSpaces)
{
    auto &root = nameSpaces.at(idx);
    s << '\n';
    if (root.nameSpace->isInlineNamespace())
        s << "inline ";
    s << "namespace " << root.nameSpace->name() << " {\n" << indent;
    for (const auto &c : root.classes)
        writeForwardDeclaration(s, c);

    for (qsizetype i = 0, count = nameSpaces.size(); i < count; ++i) {
        if (i != idx && nameSpaces.at(i).nameSpace->enclosingClass() == root.nameSpace)
            writeNamespaceForwardDeclarationRecursion(s, i, nameSpaces);
    }
    s << outdent << "}\n";
}

static void writeForwardDeclarations(TextStream &s,
                                     const AbstractMetaClassCList &classList)
{
    NameSpaces nameSpaces;

    for (const auto &c : classList) {
        if (auto encl = c->enclosingClass()) {
            Q_ASSERT(encl->isNamespace());
            auto idx = indexOf(nameSpaces, encl);
            if (idx != -1) {
                nameSpaces[idx].classes.append(c);
            } else {
                nameSpaces.append(NameSpace{encl, {c}});
                for (auto enclNsp = encl->enclosingClass(); enclNsp;
                     enclNsp = enclNsp->enclosingClass()) {
                    idx = indexOf(nameSpaces, enclNsp);
                    if (idx == -1)
                        nameSpaces.append(NameSpace{enclNsp, {}});
                }
            }
        } else {
            writeForwardDeclaration(s, c);
        }
    }

    std::sort(nameSpaces.begin(), nameSpaces.end());

    // Recursively write out namespaces starting at the root elements.
    for (qsizetype i = 0, count = nameSpaces.size(); i < count; ++i) {
        const auto &nsp = nameSpaces.at(i);
        if (nsp.nameSpace->enclosingClass() == nullptr)
            writeNamespaceForwardDeclarationRecursion(s, i, nameSpaces);
    }
}

// Include parameters required for the module/private module header

using ConditionalIncludeMap = QMap<QString, IncludeGroup>;

static TextStream &operator<<(TextStream &s, const ConditionalIncludeMap &m)
{
    for (auto it = m.cbegin(), end = m.cend(); it != end; ++it)
        s << it.key() << '\n' << it.value() << "#endif\n";
    return s;
}

struct ModuleHeaderParameters
{
    AbstractMetaClassCList forwardDeclarations;
    std::set<Include> includes;
    ConditionalIncludeMap conditionalIncludes;
    QString typeFunctions;
};

bool HeaderGenerator::finishGeneration()
{
    // Generate the main header for this module. This header should be included
    // by binding modules extending on top of this one.
    ModuleHeaderParameters parameters;
    ModuleHeaderParameters privateParameters;
    StringStream macrosStream(TextStream::Language::Cpp);

    const auto snips = TypeDatabase::instance()->defaultTypeSystemType()->codeSnips();
    if (!snips.isEmpty()) {
        writeCodeSnips(macrosStream, snips, TypeSystem::CodeSnipPositionDeclaration,
                       TypeSystem::TargetLangCode);
    }

    macrosStream << "// Type indices\nenum : int {\n";
    auto classList = api().classes();

    std::sort(classList.begin(), classList.end(),
              [](const AbstractMetaClassCPtr &a, const AbstractMetaClassCPtr &b) {
                  return a->typeEntry()->sbkIndex() < b->typeEntry()->sbkIndex();
              });

    for (const auto &metaClass : classList)
        writeTypeIndexValueLines(macrosStream, api(), metaClass);

    for (const AbstractMetaEnum &metaEnum : api().globalEnums())
        writeTypeIndexValueLine(macrosStream, api(), metaEnum.typeEntry());

    // Write the smart pointer define indexes.
    int smartPointerCountIndex = getMaxTypeIndex();
    int smartPointerCount = 0;
    for (const auto &smp : api().instantiatedSmartPointers()) {
        QString indexName = getTypeIndexVariableName(smp.type);
        _writeTypeIndexValue(macrosStream, indexName, smartPointerCountIndex);
        macrosStream << ", // " << smp.type.cppSignature() << '\n';
        // Add a the same value for const pointees (shared_ptr<const Foo>).
        const auto ptrName = smp.type.typeEntry()->entryName();
        int pos = indexName.indexOf(ptrName, 0, Qt::CaseInsensitive);
        if (pos >= 0) {
            indexName.insert(pos + ptrName.size() + 1, u"CONST"_s);
            _writeTypeIndexValue(macrosStream, indexName, smartPointerCountIndex);
            macrosStream << ", //   (const)\n";
        }
        ++smartPointerCountIndex;
        ++smartPointerCount;
    }

    _writeTypeIndexValue(macrosStream,
                         u"SBK_"_s + moduleName() + u"_IDX_COUNT"_s,
                         getMaxTypeIndex() + smartPointerCount);
    macrosStream << "\n};\n";

    macrosStream << "// This variable stores all Python types exported by this module.\n";
    macrosStream << "extern PyTypeObject **" << cppApiVariableName() << ";\n\n";
    macrosStream << "// This variable stores the Python module object exported by this module.\n";
    macrosStream << "extern PyObject *" << pythonModuleObjectName() << ";\n\n";
    macrosStream << "// This variable stores all type converters exported by this module.\n";
    macrosStream << "extern SbkConverter **" << convertersVariableName() << ";\n\n";

    // TODO-CONVERTER ------------------------------------------------------------------------------
    // Using a counter would not do, a fix must be made to APIExtractor's getTypeIndex().
    macrosStream << "// Converter indices\nenum : int {\n";
    const auto &primitives = primitiveTypes();
    int pCount = 0;
    for (const auto &ptype : primitives) {
        /* Note: do not generate indices for typedef'd primitive types
         * as they'll use the primitive type converters instead, so we
         * don't need to create any other.
         */
        if (!ptype->generateCode() || !ptype->customConversion())
            continue;

        _writeTypeIndexValueLine(macrosStream, getTypeIndexVariableName(ptype), pCount++);
    }

    for (const AbstractMetaType &container : api().instantiatedContainers()) {
        _writeTypeIndexValue(macrosStream, getTypeIndexVariableName(container), pCount);
        macrosStream << ", // " << container.cppSignature() << '\n';
        pCount++;
    }

    // Because on win32 the compiler will not accept a zero length array.
    if (pCount == 0)
        pCount++;
    _writeTypeIndexValue(macrosStream, QStringLiteral("SBK_%1_CONVERTERS_IDX_COUNT")
                                       .arg(moduleName()), pCount);
    macrosStream << "\n};\n";

    formatTypeDefEntries(macrosStream);

    // TODO-CONVERTER ------------------------------------------------------------------------------

    macrosStream << "// Macros for type check\n";

    TextStream typeFunctions(&parameters.typeFunctions, TextStream::Language::Cpp);
    TextStream privateTypeFunctions(&privateParameters.typeFunctions, TextStream::Language::Cpp);

    for (const AbstractMetaEnum &cppEnum : api().globalEnums()) {
        if (!cppEnum.isAnonymous()) {
            const auto te = cppEnum.typeEntry();
            if (te->hasConfigCondition())
                parameters.conditionalIncludes[te->configCondition()].append(te->include());
            else
                parameters.includes.insert(cppEnum.typeEntry()->include());
            writeSbkTypeFunction(typeFunctions, cppEnum);
        }
    }

    StringStream protEnumsSurrogates(TextStream::Language::Cpp);
    for (const auto &metaClass : classList) {
        const auto classType = metaClass->typeEntry();
        if (!shouldGenerate(classType))
            continue;

        //Includes
        const bool isPrivate = classType->isPrivate();
        auto &par = isPrivate ? privateParameters : parameters;
        const auto classInclude = classType->include();
        const bool hasConfigCondition = classType->hasConfigCondition();
        if (leanHeaders() && canForwardDeclare(metaClass))
            par.forwardDeclarations.append(metaClass);
        else if (hasConfigCondition)
            par.conditionalIncludes[classType->configCondition()].append(classInclude);
        else
            par.includes.insert(classInclude);

        auto &typeFunctionsStr = isPrivate ? privateTypeFunctions : typeFunctions;

        ConfigurableScope configScope(typeFunctionsStr, classType);
        for (const AbstractMetaEnum &cppEnum : metaClass->enums()) {
            if (cppEnum.isAnonymous() || cppEnum.isPrivate())
                continue;
            if (const auto inc = cppEnum.typeEntry()->include(); inc != classInclude)
                par.includes.insert(inc);
            writeProtectedEnumSurrogate(protEnumsSurrogates, cppEnum);
            writeSbkTypeFunction(typeFunctionsStr, cppEnum);
        }

        if (!metaClass->isNamespace())
            writeSbkTypeFunction(typeFunctionsStr, metaClass);
    }

    for (const auto &smp : api().instantiatedSmartPointers()) {
        parameters.includes.insert(smp.type.typeEntry()->include());
        writeSbkTypeFunction(typeFunctions, smp.type);
    }

    const QString moduleHeaderDir = outputDirectory() + u'/'
        + subDirectoryForPackage(packageName()) + u'/';
    const QString moduleHeaderFileName(moduleHeaderDir + getModuleHeaderFileName());

    QString includeShield(u"SBK_"_s + moduleName().toUpper() + u"_PYTHON_H"_s);

    FileOut file(moduleHeaderFileName);
    TextStream &s = file.stream;
    s.setLanguage(TextStream::Language::Cpp);

    // write license comment
    s << licenseComment()<< "\n\n";

    s << "#ifndef " << includeShield<< '\n';
    s << "#define " << includeShield<< "\n\n";
    if (!avoidProtectedHack()) {
        s << "//workaround to access protected functions\n";
        s << "#define protected public\n\n";
    }

    s << "#include <sbkpython.h>\n";
    s << "#include <sbkconverter.h>\n";

    QStringList requiredTargetImports = TypeDatabase::instance()->requiredTargetImports();
    if (!requiredTargetImports.isEmpty()) {
        s << "// Module Includes\n";
        for (const QString &requiredModule : std::as_const(requiredTargetImports))
            s << "#include <" << getModuleHeaderFileName(requiredModule) << ">\n";
        s<< '\n';
    }

    s << "// Bound library includes\n";
    for (const Include &include : parameters.includes)
        s << include;
    s << parameters.conditionalIncludes;

    if (leanHeaders()) {
        writeForwardDeclarations(s, parameters.forwardDeclarations);
    } else {
        if (!primitiveTypes().isEmpty()) {
            s << "// Conversion Includes - Primitive Types\n";
            const auto &primitiveTypeList = primitiveTypes();
            for (const auto &ptype : primitiveTypeList)
                s << ptype->include();
            s<< '\n';
        }

        if (!containerTypes().isEmpty()) {
            s << "// Conversion Includes - Container Types\n";
            const ContainerTypeEntryCList &containerTypeList = containerTypes();
            for (const auto &ctype : containerTypeList)
                s << ctype->include();
            s<< '\n';
        }
    }

    s << macrosStream.toString() << '\n';

    if (protEnumsSurrogates.size() > 0) {
        s << "// Protected enum surrogates\n"
            << protEnumsSurrogates.toString() << '\n';
    }

    writeTypeFunctions(s, parameters.typeFunctions);

    s << "#endif // " << includeShield << "\n\n";

    file.done();

    if (hasPrivateClasses())
        writePrivateHeader(moduleHeaderDir, includeShield, privateParameters);

    return true;
}

void HeaderGenerator::writePrivateHeader(const QString &moduleHeaderDir,
                                         const QString &publicIncludeShield,
                                         const ModuleHeaderParameters &parameters)
{
    // Write includes and type functions of private classes

    FileOut privateFile(moduleHeaderDir + getPrivateModuleHeaderFileName());
    TextStream &ps = privateFile.stream;
    ps.setLanguage(TextStream::Language::Cpp);
    QString privateIncludeShield =
        publicIncludeShield.left(publicIncludeShield.size() - 2)
        + QStringLiteral("_P_H");

    ps << licenseComment()<< "\n\n";

    ps << "#ifndef " << privateIncludeShield << '\n';
    ps << "#define " << privateIncludeShield << "\n\n";

    for (const Include &include : parameters.includes)
        ps << include;
    ps << parameters.conditionalIncludes;
    ps << '\n';

    if (leanHeaders())
        writeForwardDeclarations(ps, parameters.forwardDeclarations);

    writeTypeFunctions(ps, parameters.typeFunctions);

    ps << "#endif\n";
    privateFile.done();
}

void HeaderGenerator::writeTypeFunctions(TextStream &s, const QString &typeFunctions)
{
    if (typeFunctions.isEmpty())
        return;

    if (usePySideExtensions())
        s << "QT_WARNING_PUSH\nQT_WARNING_DISABLE_DEPRECATED\n";

    s << "namespace Shiboken\n{\n\n"
        << "// PyType functions, to get the PyObjectType for a type T\n"
        << typeFunctions << '\n'
        << "} // namespace Shiboken\n\n";

    if (usePySideExtensions())
        s << "QT_WARNING_POP\n";
}

void HeaderGenerator::writeProtectedEnumSurrogate(TextStream &s, const AbstractMetaEnum &cppEnum) const
{
    if (avoidProtectedHack() && cppEnum.isProtected())
        s << "enum " << protectedEnumSurrogateName(cppEnum) << " {};\n";
}

void HeaderGenerator::writeSbkTypeFunction(TextStream &s, const AbstractMetaEnum &cppEnum) const
{
     const QString enumName = avoidProtectedHack() && cppEnum.isProtected()
        ? protectedEnumSurrogateName(cppEnum)
        : cppEnum.qualifiedCppName();
    const auto te = cppEnum.typeEntry();
    ConfigurableScope configScope(s, te);
    s << "template<> inline PyTypeObject *SbkType< ::" << enumName << " >() ";
    s << "{ return " << cpythonTypeNameExt(te) << "; }\n";

    const auto flag = cppEnum.typeEntry()->flags();
    if (flag) {
        s <<  "template<> inline PyTypeObject *SbkType< ::" << flag->name() << " >() "
          << "{ return " << cpythonTypeNameExt(flag) << "; }\n";
    }
}

void HeaderGenerator::writeSbkTypeFunction(TextStream &s, const AbstractMetaClassCPtr &cppClass)
{
    s <<  "template<> inline PyTypeObject *SbkType< ::" << cppClass->qualifiedCppName() << " >() "
      <<  "{ return reinterpret_cast<PyTypeObject *>(" << cpythonTypeNameExt(cppClass->typeEntry()) << "); }\n";
}

void HeaderGenerator::writeSbkTypeFunction(TextStream &s, const AbstractMetaType &metaType)
{
    s <<  "template<> inline PyTypeObject *SbkType< ::" << metaType.cppSignature() << " >() "
      <<  "{ return " << cpythonTypeNameExt(metaType) << "; }\n";
}
