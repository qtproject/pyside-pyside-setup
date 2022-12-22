// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SHIBOKENGENERATOR_H
#define SHIBOKENGENERATOR_H

#include <generator.h>

#include "customconversion_typedefs.h"
#include "typesystem_typedefs.h"
#include "typesystem_enums.h"

#include <QtCore/QRegularExpression>

#include <array>

class EnumTypeEntry;
class FlagsTypeEntry;
class DocParser;
class CodeSnip;
class QPropertySpec;
class OverloadData;
class TargetToNativeConversion;
struct GeneratorClassInfoCacheEntry;
struct IncludeGroup;

QT_FORWARD_DECLARE_CLASS(TextStream)

/**
 * Abstract generator that contains common methods used in CppGenerator and HeaderGenerator.
 */
class ShibokenGenerator : public Generator
{
public:
    /// Besides the actual bindings (see AbstractMetaFunction::generateBinding(),
    /// some functions need to be generated into the wrapper class
    /// (virtual method/avoid protected hack expose).
    enum class FunctionGenerationFlag
    {
        None = 0x0,
        /// Virtual method overridable in Python
        VirtualMethod = 0x1,
        /// Special QObject virtuals
        QMetaObjectMethod = 0x2,
        /// Needs a protected wrapper for avoidProtectedHack()
        /// public "foo_protected()" calling "foo()"
        ProtectedWrapper = 0x4,        //
        /// Pass through constructor
        WrapperConstructor = 0x8,
        /// Generate a special copy constructor
        /// "FooBar_Wrapper(const Foo&)" for constructing a wrapper from a value
        WrapperSpecialCopyConstructor = 0x10
    };
    Q_DECLARE_FLAGS(FunctionGeneration, FunctionGenerationFlag);

    enum class AttroCheckFlag
    {
        None                   = 0x0,
        GetattroOverloads      = 0x01,
        GetattroSmartPointer   = 0x02,
        GetattroUser           = 0x04, // Injected code
        GetattroMask           = 0x0F,
        SetattroQObject        = 0x10,
        SetattroSmartPointer   = 0x20,
        SetattroMethodOverride = 0x40,
        SetattroUser           = 0x80, // Injected code
        SetattroMask           = 0xF0,
    };
    Q_DECLARE_FLAGS(AttroCheck, AttroCheckFlag);

    using FunctionGroups = QMap<QString, AbstractMetaFunctionCList>; // Sorted

    ShibokenGenerator();
    ~ShibokenGenerator() override;

    const char *name() const override { return "Shiboken"; }

    static QString minimalConstructorExpression(const ApiExtractorResult &api,
                                                const AbstractMetaType &type);
    static QString minimalConstructorExpression(const ApiExtractorResult &api,
                                                const TypeEntryCPtr &type);

protected:
    bool doSetup() override;

    GeneratorContext contextForClass(const AbstractMetaClassCPtr &c) const override;

    /**
     *   Returns a map with all functions grouped, the function name is used as key.
     *   Example of return value: { "foo" -> ["foo(int)", "foo(int, long)], "bar" -> "bar(double)"}
     *   \param scope Where to search for functions, null means all global functions.
     */
    FunctionGroups getGlobalFunctionGroups() const;
    static FunctionGroups getFunctionGroups(const AbstractMetaClassCPtr &scope);

    /**
     *   Returns all different inherited overloads of func, and includes func as well.
     *   The function can be called multiple times without duplication.
     *   \param func the metafunction to be searched in subclasses.
     *   \param seen the function's minimal signatures already seen.
     */
    static AbstractMetaFunctionCList getFunctionAndInheritedOverloads(const AbstractMetaFunctionCPtr &func,
                                                                      QSet<QString> *seen);

    /// Write user's custom code snippets at class or module level.
    void writeClassCodeSnips(TextStream &s,
                             const QList<CodeSnip> &codeSnips,
                             TypeSystem::CodeSnipPosition position,
                             TypeSystem::Language language,
                             const GeneratorContext &context) const;
    void writeCodeSnips(TextStream &s,
                        const QList<CodeSnip> &codeSnips,
                        TypeSystem::CodeSnipPosition position,
                        TypeSystem::Language language) const;
    /// Write user's custom code snippets at function level.
    void writeCodeSnips(TextStream &s,
                        const QList<CodeSnip> &codeSnips,
                        TypeSystem::CodeSnipPosition position,
                        TypeSystem::Language language,
                        const AbstractMetaFunctionCPtr &func,
                        bool usePyArgs,
                        const AbstractMetaArgument *lastArg) const;

    /// Replaces variables for the user's custom code at global or class level.
    void processCodeSnip(QString &code) const;
    void processClassCodeSnip(QString &code, const GeneratorContext &context) const;

    /**
     *   Verifies if any of the function's code injections makes a call
     *   to the C++ method. This is used by the generator to avoid writing calls
     *   to C++ when the user custom code already does this.
     *   \param func the function to check
     *   \return true if the function's code snippets call the wrapped C++ function
     */
    static bool injectedCodeCallsCppFunction(const GeneratorContext &context,
                                             const AbstractMetaFunctionCPtr &func);

    /**
     *   Function which parse the metafunction information
     *   \param func the function witch will be parserd
     *   \param option some extra options
     *   \param arg_count the number of function arguments
     */
    QString functionSignature(const AbstractMetaFunctionCPtr &func,
                              const QString &prepend = QString(),
                              const QString &append = QString(),
                              Options options = NoOption,
                              int arg_count = -1) const;

    /// Returns the top-most class that has multiple inheritance in the ancestry.
    static AbstractMetaClassCPtr
        getMultipleInheritingClass(const AbstractMetaClassCPtr &metaClass);

    static bool useOverrideCaching(const AbstractMetaClassCPtr &metaClass);
    AttroCheck checkAttroFunctionNeeds(const AbstractMetaClassCPtr &metaClass) const;

    /// Returns a list of methods of the given class where each one is part of
    /// a different overload with both static and non-static method.
    static AbstractMetaFunctionCList
        getMethodsWithBothStaticAndNonStaticMethods(const AbstractMetaClassCPtr &metaClass);

    static void writeToPythonConversion(TextStream &s,
                                        const AbstractMetaType &type,
                                        const AbstractMetaClassCPtr &context,
                                        const QString &argumentName);
    static void writeToCppConversion(TextStream &s,
                                     const AbstractMetaType &type,
                                     const AbstractMetaClassCPtr &context,
                                     const QString &inArgName,
                                     const QString &outArgName);
    static void writeToCppConversion(TextStream &s,
                                     const AbstractMetaClassCPtr &metaClass,
                                     const QString &inArgName,
                                     const QString &outArgName);

    /// Returns true if the argument is a pointer that rejects nullptr values.
    static bool shouldRejectNullPointerArgument(const AbstractMetaFunctionCPtr &func,
                                                int argIndex);

    /// Verifies if the class should have a C++ wrapper generated for it,
    /// instead of only a Python wrapper.
    bool shouldGenerateCppWrapper(const AbstractMetaClassCPtr &metaClass) const;

    /// Returns which functions need to be generated into the wrapper class
    FunctionGeneration functionGeneration(const AbstractMetaFunctionCPtr &func) const;

    // Return a list of implicit conversions if generation is enabled.
    AbstractMetaFunctionCList implicitConversions(const TypeEntryCPtr &t) const;

    QString wrapperName(const AbstractMetaClassCPtr &metaClass) const;

    static QString fullPythonClassName(const AbstractMetaClassCPtr &metaClass);

    static QString headerFileNameForContext(const GeneratorContext &context);
    IncludeGroup baseWrapperIncludes(const GeneratorContext &classContext) const;

    static QString fullPythonFunctionName(const AbstractMetaFunctionCPtr &func, bool forceFunc);

    bool wrapperDiagnostics() const { return m_wrapperDiagnostics; }

    static QString protectedEnumSurrogateName(const AbstractMetaEnum &metaEnum);

    static QString pythonPrimitiveTypeName(const QString &cppTypeName);

    static QString pythonOperatorFunctionName(const AbstractMetaFunctionCPtr &func);

    static QString fixedCppTypeName(const TargetToNativeConversion &toNative);
    static QString fixedCppTypeName(const AbstractMetaType &type);
    static QString fixedCppTypeName(const TypeEntryCPtr &type, QString typeName = {});

    static bool isNumber(const QString &cpythonApiName);
    static bool isNumber(const TypeEntryCPtr &type);
    static bool isNumber(const AbstractMetaType &type);
    static bool isPyInt(const TypeEntryCPtr &type);
    static bool isPyInt(const AbstractMetaType &type);

    static bool isNullPtr(const QString &value);

    static QString converterObject(const AbstractMetaType &type) ;
    static QString converterObject(const TypeEntryCPtr &type);

    static QString cpythonBaseName(const AbstractMetaClassCPtr &metaClass);
    static QString cpythonBaseName(const TypeEntryCPtr &type);
    static QString containerCpythonBaseName(const ContainerTypeEntryCPtr &ctype);
    static QString cpythonBaseName(const AbstractMetaType &type);
    static QString cpythonTypeName(const AbstractMetaClassCPtr &metaClass);
    static QString cpythonTypeName(const TypeEntryCPtr &type);
    static QString cpythonTypeNameExt(const TypeEntryCPtr &type);
    static QString cpythonTypeNameExt(const AbstractMetaType &type) ;
    static QString cpythonCheckFunction(TypeEntryCPtr type);
    static QString cpythonCheckFunction(AbstractMetaType metaType);
    static QString cpythonIsConvertibleFunction(const TypeEntryCPtr &type);
    static QString cpythonIsConvertibleFunction(AbstractMetaType metaType);
    static QString cpythonIsConvertibleFunction(const AbstractMetaArgument &metaArg);

    static QString cpythonToCppConversionFunction(const AbstractMetaClassCPtr &metaClass) ;
    static QString cpythonToCppConversionFunction(const AbstractMetaType &type,
                                                  AbstractMetaClassCPtr context = {});
    static QString cpythonToPythonConversionFunction(const AbstractMetaType &type,
                                                     AbstractMetaClassCPtr context = {});
    static QString cpythonToPythonConversionFunction(const AbstractMetaClassCPtr &metaClass);
    static QString cpythonToPythonConversionFunction(const TypeEntryCPtr &type);

    static QString cpythonFunctionName(const AbstractMetaFunctionCPtr &func) ;
    static QString cpythonMethodDefinitionName(const AbstractMetaFunctionCPtr &func);
    static QString cpythonGettersSettersDefinitionName(const AbstractMetaClassCPtr &metaClass);
    static QString cpythonGetattroFunctionName(const AbstractMetaClassCPtr &metaClass);
    static QString cpythonSetattroFunctionName(const AbstractMetaClassCPtr &metaClass);
    static QString cpythonGetterFunctionName(const AbstractMetaField &metaField);
    static QString cpythonSetterFunctionName(const AbstractMetaField &metaField);
    static QString cpythonGetterFunctionName(const QPropertySpec &property,
                                             const AbstractMetaClassCPtr &metaClass);
    static QString cpythonSetterFunctionName(const QPropertySpec &property,
                                             const AbstractMetaClassCPtr &metaClass);
    static QString cpythonWrapperCPtr(const AbstractMetaClassCPtr &metaClass,
                                      const QString &argName = QStringLiteral("self"));
     static QString cpythonWrapperCPtr(const AbstractMetaType &metaType,
                                      const QString &argName);
    static QString cpythonWrapperCPtr(const TypeEntryCPtr &type, const QString &argName);

    static QString cpythonEnumName(const EnumTypeEntryCPtr &enumEntry);
    static QString cpythonEnumName(const AbstractMetaEnum &metaEnum);

    static QString cpythonFlagsName(const FlagsTypeEntryCPtr &flagsEntry);
    static QString cpythonFlagsName(const AbstractMetaEnum *metaEnum);
    /// Returns the special cast function name, the function used to proper cast
    /// class with multiple inheritance.
    static QString cpythonSpecialCastFunctionName(const AbstractMetaClassCPtr &metaClass);

    /// Returns the file name for the module global header. If no module name
    /// is provided the current will be used.
    static QString getModuleHeaderFileName(const QString &moduleName = QString());
    static QString getPrivateModuleHeaderFileName(const QString &moduleName = QString());

    /// Includes for header (native wrapper class) or binding source
    QList<IncludeGroup> classIncludes(const AbstractMetaClassCPtr &metaClass) const;

    OptionDescriptions options() const override;
    bool handleOption(const QString &key, const QString &value) override;

    /// Returns true if the user enabled the so called "parent constructor heuristic".
    bool useCtorHeuristic() const;
    /// Returns true if the user enabled the so called "return value heuristic".
    bool useReturnValueHeuristic() const;
    /// Returns true if the generator should use the result of isNull()const to compute boolean casts.
    bool useIsNullAsNbNonZero() const;
    /// Whether to generate lean module headers
    bool leanHeaders() const;
    /// Returns true if the generator should use operator bool to compute boolean casts.
    bool useOperatorBoolAsNbNonZero() const;
    /// Generate implicit conversions of function arguments
    bool generateImplicitConversions() const;
    static QString cppApiVariableName(const QString &moduleName = QString());
    static QString pythonModuleObjectName(const QString &moduleName = QString());
    static QString convertersVariableName(const QString &moduleName = QString());
    /// Returns the type index variable name for a given class.
    static QString getTypeIndexVariableName(const AbstractMetaClassCPtr &metaClass);
    /// Returns the type index variable name for a given typedef for a template
    /// class instantiation made of the template class and the instantiation values
    static QString getTypeAlternateTemplateIndexVariableName(const AbstractMetaClassCPtr &metaClass);
    static QString getTypeIndexVariableName(TypeEntryCPtr type);
    static QString getTypeIndexVariableName(const AbstractMetaType &type) ;

    /// Returns true if the user don't want verbose error messages on the generated bindings.
    bool verboseErrorMessagesDisabled() const;

    void collectContainerTypesFromConverterMacros(const QString &code, bool toPythonMacro);

    static void writeFunctionCall(TextStream &s,
                                  const AbstractMetaFunctionCPtr &metaFunc,
                                  Options options = NoOption);

    // All data about extended converters: the type entries of the target type, and a
    // list of AbstractMetaClasses accepted as argument for the conversion.
    using ExtendedConverterData = QHash<TypeEntryCPtr, AbstractMetaClassCList>;
    /// Returns all extended conversions for the current module.
    ExtendedConverterData getExtendedConverters() const;

    /// Returns a list of converters for the non wrapper types of the current module.
    static QList<CustomConversionPtr> getPrimitiveCustomConversions();

    /// Returns true if the Python wrapper for the received OverloadData must accept a list of arguments.
    bool pythonFunctionWrapperUsesListOfArguments(const AbstractMetaFunctionCPtr &func) const;

    static const QRegularExpression &convertToCppRegEx()
    { return typeSystemConvRegExps()[TypeSystemToCppFunction]; }

    static QString pythonArgsAt(int i);

    /// Return the format character for C++->Python->C++ conversion (Py_BuildValue)
    static const QHash<QString, QChar> &formatUnits();

    static QString stdMove(const QString &c);

private:
    static QString getModuleHeaderFileBaseName(const QString &moduleName = QString());
    static QString cpythonGetterFunctionName(const QString &name,
                                             const AbstractMetaClassCPtr &enclosingClass);
    static QString cpythonSetterFunctionName(const QString &name,
                                             const AbstractMetaClassCPtr &enclosingClass);

    static const GeneratorClassInfoCacheEntry &
        getGeneratorClassInfo(const AbstractMetaClassCPtr &scope);
    static FunctionGroups getFunctionGroupsImpl(const AbstractMetaClassCPtr &scope);
    static bool classNeedsGetattroFunctionImpl(const AbstractMetaClassCPtr &metaClass);

    QString translateTypeForWrapperMethod(const AbstractMetaType &cType,
                                          const AbstractMetaClassCPtr &context,
                                          Options opt = NoOption) const;

    /**
     *   Returns all different inherited overloads of func.
     *   The function can be called multiple times without duplication.
     *   \param func the metafunction to be searched in subclasses.
     *   \param seen the function's minimal signatures already seen.
     */
    static void getInheritedOverloads(const AbstractMetaClassCPtr &scope,
                                      AbstractMetaFunctionCList *overloads);


    /**
     *   Write a function argument in the C++ in the text stream \p s.
     *   This function just call \code s << argumentString(); \endcode
     *   \param s text stream used to write the output.
     *   \param func the current metafunction.
     *   \param argument metaargument information to be parsed.
     *   \param options some extra options.
     */
    void writeArgument(TextStream &s,
                       const AbstractMetaFunctionCPtr &func,
                       const AbstractMetaArgument &argument,
                       Options options = NoOption) const;
    /**
     *   Create a QString in the C++ format to an function argument.
     *   \param func the current metafunction.
     *   \param argument metaargument information to be parsed.
     *   \param options some extra options.
     */
    QString argumentString(const AbstractMetaFunctionCPtr &func,
                           const AbstractMetaArgument &argument,
                           Options options = NoOption) const;

    QString functionReturnType(const AbstractMetaFunctionCPtr &func, Options options = NoOption) const;

    /// Utility function for writeCodeSnips.
    using ArgumentVarReplacementPair = QPair<AbstractMetaArgument, QString>;
    using ArgumentVarReplacementList = QList<ArgumentVarReplacementPair>;
    static ArgumentVarReplacementList
        getArgumentReplacement(const AbstractMetaFunctionCPtr &func,
                               bool usePyArgs, TypeSystem::Language language,
                               const AbstractMetaArgument *lastArg);

    /// Returns a string with the user's custom code snippets that comply with \p position and \p language.
    static QString getCodeSnippets(const QList<CodeSnip> &codeSnips,
                                   TypeSystem::CodeSnipPosition position,
                                   TypeSystem::Language language);

    enum TypeSystemConverterVariable {
        TypeSystemCheckFunction = 0,
        TypeSystemIsConvertibleFunction,
        TypeSystemToCppFunction,
        TypeSystemToPythonFunction,
        TypeSystemConverterVariables
    };
    void replaceConverterTypeSystemVariable(TypeSystemConverterVariable converterVariable,
                                            QString &code) const;

    /// Replaces the %CONVERTTOPYTHON type system variable.
    inline void replaceConvertToPythonTypeSystemVariable(QString &code) const
    {
        replaceConverterTypeSystemVariable(TypeSystemToPythonFunction, code);
    }
    /// Replaces the %CONVERTTOCPP type system variable.
    inline void replaceConvertToCppTypeSystemVariable(QString &code) const
    {
        replaceConverterTypeSystemVariable(TypeSystemToCppFunction, code);
    }
    /// Replaces the %ISCONVERTIBLE type system variable.
    inline void replaceIsConvertibleToCppTypeSystemVariable(QString &code) const
    {
        replaceConverterTypeSystemVariable(TypeSystemIsConvertibleFunction, code);
    }
    /// Replaces the %CHECKTYPE type system variable.
    inline void replaceTypeCheckTypeSystemVariable(QString &code) const
    {
        replaceConverterTypeSystemVariable(TypeSystemCheckFunction, code);
    }

    /// Return a prefix with '_' suitable for names in C++
    static QString moduleCppPrefix(const QString &moduleName = QString());

    /// Functions used to write the function arguments on the class buffer.
    /// \param s the class output buffer
    /// \param func the pointer to metafunction information
    /// \param count the number of function arguments
    /// \param options some extra options used during the parser
    static void writeArgumentNames(TextStream &s,
                                   const AbstractMetaFunctionCPtr &func,
                                   Options option);

    void writeFunctionArguments(TextStream &s,
                                const AbstractMetaFunctionCPtr &func,
                                Options options = NoOption) const;

    void replaceTemplateVariables(QString &code,
                                  const AbstractMetaFunctionCPtr &func) const;

    bool m_useCtorHeuristic = false;
    bool m_userReturnValueHeuristic = false;
    bool m_verboseErrorMessagesDisabled = false;
    bool m_useIsNullAsNbNonZero = false;
    // FIXME PYSIDE 7 Flip m_leanHeaders default or remove?
    bool m_leanHeaders = false;
    bool m_useOperatorBoolAsNbNonZero = false;
    // FIXME PYSIDE 7 Flip generateImplicitConversions default or remove?
    bool m_generateImplicitConversions = true;
    bool m_wrapperDiagnostics = false;

    /// Type system converter variable replacement names and regular expressions.
    static const QHash<int, QString> &typeSystemConvName();

    using TypeSystemConverterRegExps = std::array<QRegularExpression, TypeSystemConverterVariables>;
    static const TypeSystemConverterRegExps &typeSystemConvRegExps();
};

Q_DECLARE_OPERATORS_FOR_FLAGS(ShibokenGenerator::FunctionGeneration);
Q_DECLARE_OPERATORS_FOR_FLAGS(ShibokenGenerator::AttroCheck);

extern const QString CPP_ARG;
extern const QString CPP_ARG_REMOVED;
extern const QString CPP_RETURN_VAR;
extern const QString CPP_SELF_VAR;
extern const QString NULL_PTR;
extern const QString PYTHON_ARG;
extern const QString PYTHON_ARGS;
extern const QString PYTHON_OVERRIDE_VAR;
extern const QString PYTHON_RETURN_VAR;
extern const QString PYTHON_TO_CPP_VAR;

extern const QString CONV_RULE_OUT_VAR_SUFFIX;
extern const QString BEGIN_ALLOW_THREADS;
extern const QString END_ALLOW_THREADS;

#endif // SHIBOKENGENERATOR_H
