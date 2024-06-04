// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "cppgenerator.h"
#include "generatorstrings.h"
#include "generatorcontext.h"
#include <apiextractorresult.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <codesnip.h>
#include <exception.h>
#include <messages.h>
#include <textstream.h>
#include <overloaddata.h>
#include <smartpointertypeentry.h>

#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

static const char smartPtrComment[] =
    "// Try to find the 'name' attribute, by retrieving the PyObject for "
    "the corresponding C++ object held by the smart pointer.\n";

static QString smartPointerGetter(const GeneratorContext &context)
{
    const auto te = context.metaClass()->typeEntry();
    Q_ASSERT(te->isSmartPointer());
    return std::static_pointer_cast<const SmartPointerTypeEntry>(te)->getter();
}

struct callGetter
{
    explicit callGetter(const GeneratorContext &context) : m_context(context) {}

    const GeneratorContext &m_context;
};

TextStream &operator<<(TextStream &str, const callGetter &c)
{
    str << "PyObject_CallMethod(self, \"" << smartPointerGetter(c.m_context) << "\", 0)";
    return str;
}

// Helpers to collect all smart pointer pointee base classes
static AbstractMetaClassCList
    findSmartPointeeBaseClasses(const ApiExtractorResult &api,
                            const AbstractMetaType &smartPointerType)
{
    AbstractMetaClassCList result;
    auto instantiationsTe = smartPointerType.instantiations().at(0).typeEntry();
    auto targetClass = AbstractMetaClass::findClass(api.classes(), instantiationsTe);
    if (targetClass != nullptr)
        result = targetClass->allTypeSystemAncestors();
    return result;
}

using ComparisonOperatorList = QList<AbstractMetaFunction::ComparisonOperatorType>;

// Return the available comparison operators for smart pointers
static ComparisonOperatorList smartPointeeComparisons(const GeneratorContext &context)
{
    Q_ASSERT(context.forSmartPointer());
    auto te = context.preciseType().instantiations().constFirst().typeEntry();
    if (isExtendedCppPrimitive(te)) { // Primitive pointee types have all
        return {AbstractMetaFunction::OperatorEqual,
                AbstractMetaFunction::OperatorNotEqual,
                AbstractMetaFunction::OperatorLess,
                AbstractMetaFunction::OperatorLessEqual,
                AbstractMetaFunction::OperatorGreater,
                AbstractMetaFunction::OperatorGreaterEqual};
    }

    const auto pointeeClass = context.pointeeClass();
    if (!pointeeClass)
        return {};

    ComparisonOperatorList result;
    const auto &comparisons =
        pointeeClass->operatorOverloads(OperatorQueryOption::SymmetricalComparisonOp);
    for (const auto &f : comparisons) {
        const auto ct = f->comparisonOperatorType().value();
        if (!result.contains(ct))
            result.append(ct);
    }
    return result;
}

static bool hasParameterPredicate(const AbstractMetaFunctionCPtr &f)
{
    return !f->arguments().isEmpty();
}

void CppGenerator::generateSmartPointerClass(TextStream &s, const GeneratorContext &classContext)
{
    s.setLanguage(TextStream::Language::Cpp);
    AbstractMetaClassCPtr metaClass = classContext.metaClass();
    const auto typeEntry = std::static_pointer_cast<const SmartPointerTypeEntry>(metaClass->typeEntry());
    const bool hasPointeeClass = classContext.pointeeClass() != nullptr;
    const auto smartPointerType = typeEntry->smartPointerType();
    const bool isValueHandle = smartPointerType ==TypeSystem::SmartPointerType::ValueHandle;

    IncludeGroup includes{u"Extra includes"_s, typeEntry->extraIncludes()};
    if (hasPointeeClass)
        includes.append(classContext.pointeeClass()->typeEntry()->include());
    includes.includes.append({Include::IncludePath, u"sbksmartpointer.h"_s});
    generateIncludes(s, classContext, {includes});

    s << '\n';

    // class inject-code native/beginning
    if (!typeEntry->codeSnips().isEmpty()) {
        writeClassCodeSnips(s, typeEntry->codeSnips(),
                            TypeSystem::CodeSnipPositionBeginning, TypeSystem::NativeCode,
                            classContext);
        s << '\n';
    }

    StringStream smd(TextStream::Language::Cpp);
    StringStream md(TextStream::Language::Cpp);
    StringStream signatureStream(TextStream::Language::Cpp);

    s << openTargetExternC;

    const auto &functionGroups = getFunctionGroups(metaClass);

    // Skip all public methods of the smart pointer except for the special
    // methods declared in the type entry.

    auto ctors = metaClass->queryFunctions(FunctionQueryOption::Constructors);
    if (!hasPointeeClass && !isValueHandle) { // Cannot generate "int*"
        auto end = std::remove_if(ctors.begin(), ctors.end(), hasParameterPredicate);
        ctors.erase(end, ctors.end());
    }

    if (!ctors.isEmpty()) {
        OverloadData overloadData(ctors, api());
        writeConstructorWrapper(s, overloadData, classContext);
        writeSignatureInfo(signatureStream, overloadData);
    }

    if (!typeEntry->resetMethod().isEmpty()) {
        auto it = functionGroups.constFind(typeEntry->resetMethod());
        if (it == functionGroups.cend())
            throw Exception(msgCannotFindSmartPointerMethod(typeEntry, typeEntry->resetMethod()));
        AbstractMetaFunctionCList resets = it.value();
        if (!hasPointeeClass && !isValueHandle) { // Cannot generate "int*"
            auto end = std::remove_if(resets.begin(), resets.end(), hasParameterPredicate);
            resets.erase(end, resets.end());
        }
        if (!resets.isEmpty())
            writeMethodWrapper(s, md, signatureStream, resets, classContext);
    }

    auto it = functionGroups.constFind(typeEntry->getter());
    if (it == functionGroups.cend() || it.value().size() != 1)
        throw Exception(msgCannotFindSmartPointerGetter(typeEntry));

    writeMethodWrapper(s, md, signatureStream, it.value(), classContext);

    QStringList optionalMethods;
    if (!typeEntry->refCountMethodName().isEmpty())
        optionalMethods.append(typeEntry->refCountMethodName());
    const QString valueCheckMethod = typeEntry->valueCheckMethod();
    if (!valueCheckMethod.isEmpty() && !valueCheckMethod.startsWith(u"operator"))
        optionalMethods.append(valueCheckMethod);
    if (!typeEntry->nullCheckMethod().isEmpty())
        optionalMethods.append(typeEntry->nullCheckMethod());

    for (const QString &optionalMethod : optionalMethods) {
        auto it = functionGroups.constFind(optionalMethod);
        if (it == functionGroups.cend() || it.value().size() != 1)
            throw Exception(msgCannotFindSmartPointerMethod(typeEntry, optionalMethod));
        writeMethodWrapper(s, md, signatureStream, it.value(), classContext);
    }

    writeCopyFunction(s, md, signatureStream, classContext);
    writeSmartPointerDirFunction(s, md, signatureStream, classContext);

    const QString methodsDefinitions = md.toString();
    const QString singleMethodDefinitions = smd.toString();

    const QString className = chopType(cpythonTypeName(typeEntry));

    // Write single method definitions
    s << singleMethodDefinitions;

    // Write methods definition
    writePyMethodDefs(s, className, methodsDefinitions);

    // Write tp_s/getattro function
    const auto boolCastOpt = boolCast(metaClass);
    writeSmartPointerGetattroFunction(s, classContext, boolCastOpt);
    writeSmartPointerSetattroFunction(s, classContext);

    if (boolCastOpt.has_value())
        writeNbBoolFunction(classContext, boolCastOpt.value(), s);

    if (smartPointerType == TypeSystem::SmartPointerType::Shared)
        writeSmartPointerRichCompareFunction(s, classContext);

    s << closeExternC;

    if (hasHashFunction(metaClass))
        writeHashFunction(s, classContext);

    // Write tp_traverse and tp_clear functions.
    writeTpTraverseFunction(s, metaClass);
    writeTpClearFunction(s, metaClass);

    writeClassDefinition(s, metaClass, classContext);

    s << '\n';

    writeConverterFunctions(s, metaClass, classContext);
    writeClassRegister(s, metaClass, classContext, signatureStream);

    // class inject-code native/end
    if (!typeEntry->codeSnips().isEmpty()) {
        writeClassCodeSnips(s, typeEntry->codeSnips(),
                            TypeSystem::CodeSnipPositionEnd, TypeSystem::NativeCode,
                            classContext);
        s << '\n';
    }
}

void CppGenerator::writeSmartPointerConverterFunctions(TextStream &s,
                                                       const AbstractMetaType &smartPointerType) const
{
    const auto baseClasses = findSmartPointeeBaseClasses(api(), smartPointerType);
    if (baseClasses.isEmpty())
        return;

    auto smartPointerTypeEntry =
        std::static_pointer_cast<const SmartPointerTypeEntry>(smartPointerType.typeEntry());

    // TODO: Missing conversion to smart pointer pointer type:

    s << "// Register smartpointer conversion for all derived classes\n";
    for (const auto &base : baseClasses) {
        auto baseTe = base->typeEntry();
        if (smartPointerTypeEntry->matchesInstantiation(baseTe)) {
            if (auto opt = api().findSmartPointerInstantiation(smartPointerTypeEntry, baseTe)) {
                const auto &smartTargetType = opt.value().type;
                s << "// SmartPointer derived class: "
                  << smartTargetType.cppSignature() << "\n";
                writePythonToCppConversionFunctions(s, smartPointerType,
                                                    smartTargetType, {}, {}, {});
            }
        }
    }
}

void CppGenerator::writeSmartPointerCppSelfConversion(TextStream &s,
                                                      const GeneratorContext &context)
{
    Q_ASSERT(context.forSmartPointer());
    s << cpythonWrapperCPtr(context.preciseType(), u"self"_s);
}

void CppGenerator::writeSmartPointerCppSelfDefinition(TextStream &s,
                                                      const GeneratorContext &context,
                                                      ErrorReturn errorReturn,
                                                      CppSelfDefinitionFlags flags)
{
    Q_ASSERT(context.forSmartPointer());
    writeInvalidPyObjectCheck(s, u"self"_s, errorReturn);
    writeCppSelfVarDef(s, flags);
    writeSmartPointerCppSelfConversion(s, context);
    s << ";\n";
}

void CppGenerator::writeSmartPointerConverterInitialization(TextStream &s,
                                                            const AbstractMetaType &type) const
{
    const QByteArray cppSignature = type.cppSignature().toUtf8();
    auto writeConversionRegister = [&s](const AbstractMetaType &sourceType,
                                        const QString &targetTypeName,
                                        const QString &targetConverter)
    {
        const QString sourceTypeName = fixedCppTypeName(sourceType);
        const QString toCpp = pythonToCppFunctionName(sourceTypeName, targetTypeName);
        const QString isConv = convertibleToCppFunctionName(sourceTypeName, targetTypeName);

        writeAddPythonToCppConversion(s, targetConverter, toCpp, isConv);
    };

    const auto classes = findSmartPointeeBaseClasses(api(), type);
    if (classes.isEmpty())
        return;

    auto smartPointerTypeEntry = std::static_pointer_cast<const SmartPointerTypeEntry>(type.typeEntry());

    s << "// Register SmartPointer converter for type '" << cppSignature << "'." << '\n'
      << "///////////////////////////////////////////////////////////////////////////////////////\n\n";

    for (const auto &base : classes) {
        auto baseTe = base->typeEntry();
        if (auto opt = api().findSmartPointerInstantiation(smartPointerTypeEntry, baseTe)) {
            const auto &smartTargetType = opt.value().type;
            s << "// Convert to SmartPointer derived class: ["
              << smartTargetType.cppSignature() << "]\n";
            const QString converter = u"Shiboken::Conversions::getConverter(\""_s
                                      + smartTargetType.cppSignature() + u"\")"_s;
            writeConversionRegister(type, fixedCppTypeName(smartTargetType), converter);
        } else {
            s << "// Class not found:" << type.instantiations().at(0).cppSignature();
        }
    }

    s << "///////////////////////////////////////////////////////////////////////////////////////" << '\n' << '\n';
}

void CppGenerator::writeSmartPointerRichCompareFunction(TextStream &s,
                                                        const GeneratorContext &context) const
{
    static const char selfPointeeVar[] = "cppSelfPointee";
    static const char cppArg0PointeeVar[] = "cppArg0Pointee";

    const auto metaClass = context.metaClass();
    QString baseName = cpythonBaseName(metaClass);
    writeRichCompareFunctionHeader(s, baseName, context);

    s << "if (";
    writeTypeCheck(s, context.preciseType(), PYTHON_ARG);
    s << ") {\n" << indent;
    writeArgumentConversion(s, context.preciseType(), CPP_ARG0,
                            PYTHON_ARG, ErrorReturn::Default, metaClass);

    const auto te = context.preciseType().typeEntry();
    Q_ASSERT(te->isSmartPointer());
    const auto ste = std::static_pointer_cast<const SmartPointerTypeEntry>(te);

    s << "const auto *" << selfPointeeVar << " = " << CPP_SELF_VAR
      << '.' << ste->getter() << "();\n";
    s << "const auto *" << cppArg0PointeeVar << " = " << CPP_ARG0
      << '.' << ste->getter() << "();\n";

    // If we have an object without any comparisons, only generate a simple
    // equality check by pointee address
    auto availableOps = smartPointeeComparisons(context);
    const bool comparePointeeAddressOnly = availableOps.isEmpty();
    if (comparePointeeAddressOnly) {
        availableOps << AbstractMetaFunction::OperatorEqual
                     << AbstractMetaFunction::OperatorNotEqual;
    } else {
        // For value types with operators, we complain about nullptr
        s << "if (" << selfPointeeVar << " == nullptr || " << cppArg0PointeeVar
          << " == nullptr) {\n" << indent
          << "PyErr_SetString(PyExc_NotImplementedError, \"nullptr passed to comparison.\");\n"
          << ErrorReturn::Default << '\n' << outdent << "}\n";
    }

    s << "bool " << CPP_RETURN_VAR << "= false;\n"
      << "switch (op) {\n";
    for (auto op : availableOps) {
        s << "case " << AbstractMetaFunction::pythonRichCompareOpCode(op) << ":\n"
          << indent << CPP_RETURN_VAR << " = ";
        if (comparePointeeAddressOnly) {
            s << selfPointeeVar << ' ' << AbstractMetaFunction::cppComparisonOperator(op)
              << ' ' << cppArg0PointeeVar << ";\n";
        } else {
            // Shortcut for equality: Check pointee address
            if (op == AbstractMetaFunction::OperatorEqual
                || op == AbstractMetaFunction::OperatorLessEqual
                || op == AbstractMetaFunction::OperatorGreaterEqual) {
                s << selfPointeeVar << " == " << cppArg0PointeeVar << " || ";
            }
            // Generate object's comparison
            s << "*" << selfPointeeVar << ' '
              << AbstractMetaFunction::cppComparisonOperator(op) << " *"
              << cppArg0PointeeVar << ";\n";
        }
        s << "break;\n" << outdent;

    }
    if (availableOps.size() < 6) {
        s << "default:\n" << indent
          << richCompareComment
          << "return FallbackRichCompare(self, " << PYTHON_ARG << ", op);\n" << outdent;
    }
    s << "}\n" << PYTHON_RETURN_VAR << " = " << CPP_RETURN_VAR
      << " ? Py_True : Py_False;\n"
      << "Py_INCREF(" << PYTHON_RETURN_VAR << ");\n"
      << outdent << "}\n"
      << "return Shiboken::returnFromRichCompare(" << PYTHON_RETURN_VAR << ");\n"
      << outdent << "}\n\n";
}

void CppGenerator::writeSmartPointerSetattroFunction(TextStream &s,
                                                     const GeneratorContext &context)
{
    Q_ASSERT(context.forSmartPointer());
    writeSetattroDefinition(s, context.metaClass());
    s << smartPtrComment
      << "if (auto *rawObj = " << callGetter(context) << ") {\n" << indent
      << "if (PyObject_HasAttr(rawObj, name) != 0)\n" << indent
      << "return PyObject_GenericSetAttr(rawObj, name, value);\n" << outdent
      << "Py_DECREF(rawObj);\n" << outdent
      << "}\n";
    writeSetattroDefaultReturn(s);
}

void CppGenerator::writeSmartPointerGetattroFunction(TextStream &s,
                                                     const GeneratorContext &context,
                                                     const BoolCastFunctionOptional &boolCast)
{
    Q_ASSERT(context.forSmartPointer());
    const auto metaClass = context.metaClass();
    writeGetattroDefinition(s, metaClass);
    s << "PyObject *tmp = PyObject_GenericGetAttr(self, name);\n"
      << "if (tmp)\n" << indent << "return tmp;\n" << outdent
      << "if (PyErr_ExceptionMatches(PyExc_AttributeError) == 0)\n"
      << indent << "return nullptr;\n" << outdent
      << "PyErr_Clear();\n";

    if (boolCast.has_value()) {
        writeSmartPointerCppSelfDefinition(s, context);
        s << "if (";
        writeNbBoolExpression(s, boolCast.value(), true /* invert */);
        s << ") {\n" << indent
          << R"(PyTypeObject *tp = Py_TYPE(self);
PyErr_Format(PyExc_AttributeError, "Attempt to retrieve '%s' from null object '%s'.",
             Shiboken::String::toCString(name), tp->tp_name);
return nullptr;
)" << outdent << "}\n";
    }

    // This generates the code which dispatches access to member functions
    // and fields from the smart pointer to its pointee.
    s << smartPtrComment
      << "if (auto *rawObj = " << callGetter(context) << ") {\n" << indent
      << "if (auto *attribute = PyObject_GetAttr(rawObj, name))\n"
      << indent << "tmp = attribute;\n" << outdent
      << "Py_DECREF(rawObj);\n" << outdent
      << "}\n"
      << "if (!tmp) {\n" << indent
      << R"(PyTypeObject *tp = Py_TYPE(self);
PyErr_Format(PyExc_AttributeError,
             "'%.50s' object has no attribute '%.400s'",
             tp->tp_name, Shiboken::String::toCString(name));
)" << outdent
      << "}\n"
      << "return tmp;\n" << outdent << "}\n\n";
}

QString CppGenerator::writeSmartPointerReprFunction(TextStream &s,
                                                    const GeneratorContext &context)
{
    const auto metaClass = context.metaClass();
    QString funcName = writeReprFunctionHeader(s, context);
    s << "Shiboken::AutoDecRef pointee(" << callGetter(context) << ");\n"
        << "return Shiboken::SmartPointer::repr(self, pointee);\n";
    writeReprFunctionFooter(s);
    return funcName;
}

QString CppGenerator::writeSmartPointerDirFunction(TextStream &s, TextStream &definitionStream,
                                                   TextStream &signatureStream,
                                                   const GeneratorContext &context)
{
    QString funcName = cpythonBaseName(context.metaClass()) + u"__dir__"_s;

    signatureStream << fullPythonClassName(context.metaClass()) << ".__dir__()\n";
    definitionStream << PyMethodDefEntry{u"__dir__"_s, funcName, {"METH_NOARGS"_ba}, {}}
        << ",\n";

    s << "extern \"C\"\n{\n"
      << "static PyObject *" << funcName << "(PyObject *self)\n{\n" << indent
      << "Shiboken::AutoDecRef pointee(" << callGetter(context) << ");\n"
      << "return Shiboken::SmartPointer::dir(self, pointee);\n"
      << outdent << "}\n} // extern C\n\n";
    return funcName;
}
