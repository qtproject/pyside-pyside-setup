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

#include "headergenerator.h"
#include <apiextractorresult.h>
#include <abstractmetaenum.h>
#include <abstractmetafield.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetalang_helpers.h>
#include <modifications.h>
#include <typedatabase.h>
#include <reporthandler.h>
#include <textstream.h>
#include <fileout.h>
#include "parser/codemodel.h"

#include "qtcompat.h"

#include <algorithm>

#include <QtCore/QDir>
#include <QtCore/QTextStream>
#include <QtCore/QVariant>
#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

QString HeaderGenerator::headerFileNameForContext(const GeneratorContext &context)
{
    return fileNameForContextHelper(context, u"_wrapper.h"_s);
}

QString HeaderGenerator::fileNameForContext(const GeneratorContext &context) const
{
    return headerFileNameForContext(context);
}

void HeaderGenerator::writeCopyCtor(TextStream &s, const AbstractMetaClass *metaClass) const
{
    s << wrapperName(metaClass) << "(const " << metaClass->qualifiedCppName()
      << "& self) : " << metaClass->qualifiedCppName() << "(self)\n{\n}\n\n";
}

static void writeProtectedEnums(TextStream &s, const AbstractMetaClass *metaClass)
{
    const QString name = metaClass->qualifiedCppName();
    for (const auto &e : metaClass->enums()) {
        if (e.isProtected())
            s << "using " << name << "::" << e.name() << ";\n";
    }
}

void HeaderGenerator::generateClass(TextStream &s, const GeneratorContext &classContextIn)
{
    GeneratorContext classContext = classContextIn;
    const AbstractMetaClass *metaClass = classContext.metaClass();
    m_inheritedOverloads.clear();

    // write license comment
    s << licenseComment();

    QString wrapperName = classContext.effectiveClassName();
    QString outerHeaderGuard = getFilteredCppSignatureString(wrapperName).toUpper();
    QString innerHeaderGuard;

    // Header
    s << "#ifndef SBK_" << outerHeaderGuard << "_H\n";
    s << "#define SBK_" << outerHeaderGuard << "_H\n\n";

    if (!avoidProtectedHack())
        s << "#define protected public\n\n";

    //Includes
    auto typeEntry = metaClass->typeEntry();
    s << typeEntry->include() << '\n';
    if (classContext.useWrapper() && !typeEntry->extraIncludes().isEmpty()) {
        s << "\n// Extra includes\n";
        for (const Include &inc : typeEntry->extraIncludes())
            s << inc.toString() << '\n';
    }

    if (classContext.useWrapper() && usePySideExtensions() && metaClass->isQObject())
        s << "namespace PySide { class DynamicQMetaObject; }\n\n";

    while (classContext.useWrapper()) {
        if (!innerHeaderGuard.isEmpty()) {
            s << "#  ifndef SBK_" << innerHeaderGuard << "_H\n";
            s << "#  define SBK_" << innerHeaderGuard << "_H\n\n";
            s << "// Inherited base class:\n";
        }

        // Class
        s << "class " << wrapperName
           << " : public " << metaClass->qualifiedCppName()
           << "\n{\npublic:\n" << indent;

        // Make protected enums accessible
        if (avoidProtectedHack()) {
            recurseClassHierarchy(metaClass, [&s] (const AbstractMetaClass *metaClass) {
                writeProtectedEnums(s, metaClass);
                return false;
            });
        }

        if (avoidProtectedHack() && metaClass->hasProtectedFields()) {
            s << "\n// Make protected fields accessible\n";
            const QString name = metaClass->qualifiedCppName();
            for (const auto &f : metaClass->fields()) {
                if (f.isProtected())
                    s << "using " << name << "::" << f.originalName() << ";\n";
            }
            s << '\n';
        }

        const auto &funcs = filterFunctions(metaClass);
        int maxOverrides = 0;
        for (const auto &func : funcs) {
            if (!func->attributes().testFlag(AbstractMetaFunction::FinalCppMethod)) {
                writeFunction(s, func);
                // PYSIDE-803: Build a boolean cache for unused overrides.
                if (shouldWriteVirtualMethodNative(func))
                    maxOverrides++;
            }
        }
        if (!maxOverrides)
            maxOverrides = 1;

        //destructor
        // PYSIDE-504: When C++ 11 is used, then the destructor must always be declared.
        // See abstractmetalang.cpp, determineCppWrapper() and generator.h for further
        // reference.
        if (!avoidProtectedHack() || !metaClass->hasPrivateDestructor() || alwaysGenerateDestructor) {
            if (avoidProtectedHack() && metaClass->hasPrivateDestructor())
                s << "// C++11: need to declare (unimplemented) destructor because "
                     "the base class destructor is private.\n";
            s << '~' << wrapperName << "();\n";
        }

        writeClassCodeSnips(s, typeEntry->codeSnips(),
                            TypeSystem::CodeSnipPositionDeclaration, TypeSystem::NativeCode,
                            classContext);

        if ((!avoidProtectedHack() || !metaClass->hasPrivateDestructor())
            && usePySideExtensions() && metaClass->isQObject()) {
            s << outdent << "public:\n" << indent <<
R"(int qt_metacall(QMetaObject::Call call, int id, void **args) override;
void *qt_metacast(const char *_clname) override;
)";
        }

        if (!m_inheritedOverloads.isEmpty()) {
            s << "// Inherited overloads, because the using keyword sux\n";
            for (const auto &func : qAsConst(m_inheritedOverloads))
                writeMemberFunctionWrapper(s, func);
            m_inheritedOverloads.clear();
        }

        if (usePySideExtensions())
            s << "static void pysideInitQtMetaTypes();\n";

        s << "void resetPyMethodCache();\n"
            << outdent << "private:\n" << indent
            << "mutable bool m_PyMethodCache[" << maxOverrides << "];\n"
            << outdent << "};\n\n";
        if (!innerHeaderGuard.isEmpty())
            s << "#  endif // SBK_" << innerHeaderGuard << "_H\n\n";

        // PYSIDE-500: Use also includes for inherited wrapper classes, because
        // without the protected hack, we sometimes need to cast inherited wrappers.
        // But we don't use multiple include files. Instead, they are inserted as recursive
        // headers. This keeps the file structure as simple as before the enhanced inheritance.
        metaClass = metaClass->baseClass();
        if (!metaClass || !avoidProtectedHack())
            break;
        classContext = contextForClass(metaClass);
        wrapperName =  classContext.effectiveClassName();
        innerHeaderGuard = getFilteredCppSignatureString(wrapperName).toUpper();
    }

    s << "#endif // SBK_" << outerHeaderGuard << "_H\n\n";
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
        const TypeEntry *enumTypeEntry = nullptr;
        if (arg.type().isFlags())
            enumTypeEntry = static_cast<const FlagsTypeEntry *>(arg.type().typeEntry())->originator();
        else if (arg.type().isEnum())
            enumTypeEntry = arg.type().typeEntry();
        if (enumTypeEntry)
            s << arg.type().cppSignature() << '(' << arg.name() << ')';
        else
            s << arg.name();
    }
    s << "); }\n";
}

void HeaderGenerator::writeFunction(TextStream &s, const AbstractMetaFunctionCPtr &func)
{

    // do not write copy ctors here.
    if (!func->isPrivate() && func->functionType() == AbstractMetaFunction::CopyConstructorFunction) {
        writeCopyCtor(s, func->ownerClass());
        return;
    }
    if (func->isUserAdded())
        return;

    if (avoidProtectedHack() && func->isProtected() && !func->isConstructor()
        && !func->isOperatorOverload()) {
        writeMemberFunctionWrapper(s, func, u"_protected"_s);
    }

    // pure virtual functions need a default implementation
    const bool notAbstract = !func->isAbstract();
    if ((func->isPrivate() && notAbstract && !func->isVisibilityModifiedToPrivate())
        || (func->isModifiedRemoved() && notAbstract))
        return;

    if (avoidProtectedHack() && func->ownerClass()->hasPrivateDestructor()
        && (func->isAbstract() || func->isVirtual()))
        return;

    if (func->functionType() == AbstractMetaFunction::ConstructorFunction) {
        Options option =  func->hasSignatureModifications()
            ? Generator::OriginalTypeDescription : Generator::NoOption;
        s << functionSignature(func, {}, {}, option) << ";\n";
        return;
    }

    if (func->isAbstract() || func->isVirtual()) {
        s << functionSignature(func, {}, {}, Generator::OriginalTypeDescription)
            << " override;\n";
        // Check if this method hide other methods in base classes
        for (const auto &f : func->ownerClass()->functions()) {
            if (f != func
                && !f->isConstructor()
                && !f->isPrivate()
                && !f->isVirtual()
                && !f->isAbstract()
                && !f->isStatic()
                && f->name() == func->name()) {
                m_inheritedOverloads << f;
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
static const AbstractMetaClass *
    findEquivalentTemplateTypedef(const AbstractMetaClassCList &haystack,
                                  const AbstractMetaClass *needle)
{
    auto *templateBaseClass = needle->templateBaseClass();
    const auto &instantiations = needle->templateBaseClassInstantiations();
    for (auto *candidate : haystack) {
        if (candidate->isTypeDef()
            && candidate->templateBaseClass() == templateBaseClass
            && candidate->templateBaseClassInstantiations() == instantiations) {
            return candidate;
        }
    }
    return nullptr;
}

void HeaderGenerator::writeTypeIndexValueLine(TextStream &s, const ApiExtractorResult &api,
                                              const TypeEntry *typeEntry)
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
        const auto *cType = static_cast<const ComplexTypeEntry *>(typeEntry);
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
        auto ete = static_cast<const EnumTypeEntry *>(typeEntry);
        if (ete->flags())
            writeTypeIndexValueLine(s, api, ete->flags());
    }
}

void HeaderGenerator::writeTypeIndexValueLines(TextStream &s, const ApiExtractorResult &api,
                                               const AbstractMetaClass *metaClass)
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
    QList<const TypedefEntry *> entries;
    const auto typeDbEntries = TypeDatabase::instance()->typedefEntries();
    for (auto it = typeDbEntries.cbegin(), end = typeDbEntries.cend(); it != end; ++it) {
        if (it.value()->generateCode() != 0)
            entries.append(it.value());
    }
    if (entries.isEmpty())
        return;
    s << "\n// typedef entries\n";
    for (const auto e : entries) {
        const QString name = e->qualifiedCppName();
        // Fixme: simplify by using nested namespaces in C++ 17.
        const auto components = QStringView{name}.split(u"::");
        const int nameSpaceCount = components.size() -  1;
        for (int n = 0; n < nameSpaceCount; ++n)
            s << "namespace " << components.at(n) << " {\n";
        s << "using " << components.constLast() << " = " << e->sourceType() << ";\n";
        for (int n = 0; n < nameSpaceCount; ++n)
            s << "}\n";
    }
    s << '\n';
}


bool HeaderGenerator::finishGeneration()
{
    // Generate the main header for this module.
    // This header should be included by binding modules
    // extendind on top of this one.
    QSet<Include> includes;
    QSet<Include> privateIncludes;
    StringStream macrosStream(TextStream::Language::Cpp);

    const auto snips = TypeDatabase::instance()->defaultTypeSystemType()->codeSnips();
    if (!snips.isEmpty()) {
        writeCodeSnips(macrosStream, snips, TypeSystem::CodeSnipPositionDeclaration,
                       TypeSystem::TargetLangCode);
    }

    macrosStream << "// Type indices\nenum : int {\n";
    auto classList = api().classes();

    std::sort(classList.begin(), classList.end(),
              [](const AbstractMetaClass *a, const AbstractMetaClass *b) {
                  return a->typeEntry()->sbkIndex() < b->typeEntry()->sbkIndex();
              });

    for (const AbstractMetaClass *metaClass : classList)
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
    const PrimitiveTypeEntryList &primitives = primitiveTypes();
    int pCount = 0;
    for (const PrimitiveTypeEntry *ptype : primitives) {
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

    StringStream typeFunctions(TextStream::Language::Cpp);
    StringStream privateTypeFunctions(TextStream::Language::Cpp);
    if (usePySideExtensions()) {
        typeFunctions << "QT_WARNING_PUSH\n";
        typeFunctions << "QT_WARNING_DISABLE_DEPRECATED\n";
    }
    for (const AbstractMetaEnum &cppEnum : api().globalEnums()) {
        if (!cppEnum.isAnonymous()) {
            includes << cppEnum.typeEntry()->include();
            writeSbkTypeFunction(typeFunctions, cppEnum);
        }
    }

    StringStream protEnumsSurrogates(TextStream::Language::Cpp);
    for (auto metaClass : classList) {
        const TypeEntry *classType = metaClass->typeEntry();
        if (!shouldGenerate(classType))
            continue;

        //Includes
        const bool isPrivate = classType->isPrivate();
        auto &includeList = isPrivate ? privateIncludes : includes;
        includeList << classType->include();
        auto &typeFunctionsStr = isPrivate ? privateTypeFunctions : typeFunctions;

        for (const AbstractMetaEnum &cppEnum : metaClass->enums()) {
            if (cppEnum.isAnonymous() || cppEnum.isPrivate())
                continue;
            EnumTypeEntry *enumType = cppEnum.typeEntry();
            includeList << enumType->include();
            writeProtectedEnumSurrogate(protEnumsSurrogates, cppEnum);
            writeSbkTypeFunction(typeFunctionsStr, cppEnum);
        }

        if (!metaClass->isNamespace())
            writeSbkTypeFunction(typeFunctionsStr, metaClass);
    }

    for (const auto &smp : api().instantiatedSmartPointers()) {
        const TypeEntry *classType = smp.type.typeEntry();
        includes << classType->include();
        writeSbkTypeFunction(typeFunctions, smp.type);
    }
    if (usePySideExtensions())
        typeFunctions << "QT_WARNING_POP\n";

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
        for (const QString &requiredModule : qAsConst(requiredTargetImports))
            s << "#include <" << getModuleHeaderFileName(requiredModule) << ">\n";
        s<< '\n';
    }

    s << "// Bound library includes\n";
    for (const Include &include : qAsConst(includes))
        s << include;

    if (!primitiveTypes().isEmpty()) {
        s << "// Conversion Includes - Primitive Types\n";
        const PrimitiveTypeEntryList &primitiveTypeList = primitiveTypes();
        for (const PrimitiveTypeEntry *ptype : primitiveTypeList)
            s << ptype->include();
        s<< '\n';
    }

    if (!containerTypes().isEmpty()) {
        s << "// Conversion Includes - Container Types\n";
        const ContainerTypeEntryList &containerTypeList = containerTypes();
        for (const ContainerTypeEntry *ctype : containerTypeList)
            s << ctype->include();
        s<< '\n';
    }

    s << macrosStream.toString() << '\n';

    if (protEnumsSurrogates.size() > 0) {
        s << "// Protected enum surrogates\n"
            << protEnumsSurrogates.toString() << '\n';
    }

    s << "namespace Shiboken\n{\n\n"
        << "// PyType functions, to get the PyObjectType for a type T\n"
        << typeFunctions.toString() << '\n'
        << "} // namespace Shiboken\n\n"
        << "#endif // " << includeShield << "\n\n";

    file.done();

    if (hasPrivateClasses()) {
        writePrivateHeader(moduleHeaderDir, includeShield,
                           privateIncludes, privateTypeFunctions.toString());
    }
    return true;
}

void HeaderGenerator::writePrivateHeader(const QString &moduleHeaderDir,
                                         const QString &publicIncludeShield,
                                         const QSet<Include> &privateIncludes,
                                         const QString &privateTypeFunctions)
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

    for (const Include &include : qAsConst(privateIncludes))
        ps << include;
    ps << '\n';

    if (usePySideExtensions())
        ps << "QT_WARNING_PUSH\nQT_WARNING_DISABLE_DEPRECATED\n";

    ps << "namespace Shiboken\n{\n\n"
        << "// PyType functions, to get the PyObjectType for a type T\n"
        << privateTypeFunctions << '\n'
        << "} // namespace Shiboken\n\n";

    if (usePySideExtensions())
        ps << "QT_WARNING_POP\n";

    ps << "#endif\n";
    privateFile.done();
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

    s << "template<> inline PyTypeObject *SbkType< ::" << enumName << " >() ";
    s << "{ return " << cpythonTypeNameExt(cppEnum.typeEntry()) << "; }\n";

    FlagsTypeEntry *flag = cppEnum.typeEntry()->flags();
    if (flag) {
        s <<  "template<> inline PyTypeObject *SbkType< ::" << flag->name() << " >() "
          << "{ return " << cpythonTypeNameExt(flag) << "; }\n";
    }
}

void HeaderGenerator::writeSbkTypeFunction(TextStream &s, const AbstractMetaClass *cppClass)
{
    s <<  "template<> inline PyTypeObject *SbkType< ::" << cppClass->qualifiedCppName() << " >() "
      <<  "{ return reinterpret_cast<PyTypeObject *>(" << cpythonTypeNameExt(cppClass->typeEntry()) << "); }\n";
}

void HeaderGenerator::writeSbkTypeFunction(TextStream &s, const AbstractMetaType &metaType)
{
    s <<  "template<> inline PyTypeObject *SbkType< ::" << metaType.cppSignature() << " >() "
      <<  "{ return " << cpythonTypeNameExt(metaType) << "; }\n";
}
