// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "cppgenerator.h"
#include "generatorargument.h"
#include "defaultvalue.h"
#include "generatorcontext.h"
#include "codesnip.h"
#include "customconversion.h"
#include "headergenerator.h"
#include "apiextractorresult.h"
#include "ctypenames.h"
#include <exception.h>
#include "pytypenames.h"
#include "fileout.h"
#include "overloaddata.h"
#include "pymethoddefentry.h"
#include <abstractmetaenum.h>
#include <abstractmetafield.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetalang_helpers.h>
#include <messages.h>
#include <modifications.h>
#include <propertyspec.h>
#include <reporthandler.h>
#include <sourcelocation.h>
#include <textstream.h>
#include <typedatabase.h>
#include <containertypeentry.h>
#include <enumtypeentry.h>
#include <flagstypeentry.h>
#include <functiontypeentry.h>
#include <namespacetypeentry.h>
#include <primitivetypeentry.h>
#include <smartpointertypeentry.h>
#include <typesystemtypeentry.h>
#include <valuetypeentry.h>
#include <parser/enumvalue.h>

#include "qtcompat.h"

#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QMetaObject>
#include <QtCore/QMetaType>
#include <QtCore/QRegularExpression>
#include <QtCore/QTextStream>

#include <algorithm>
#include <cstring>
#include <memory>
#include <set>

using namespace Qt::StringLiterals;

struct sbkUnusedVariableCast
{
    explicit sbkUnusedVariableCast(QString name) : m_name(name) {}

    const QString m_name;
};

TextStream &operator<<(TextStream &str, const sbkUnusedVariableCast &c)
{
    str << "SBK_UNUSED(" << c.m_name << ")\n";
    return str;
}

static const QString CPP_ARG0 = u"cppArg0"_s;
static const char methodDefSentinel[] = "{nullptr, nullptr, 0, nullptr} // Sentinel\n";
const char *CppGenerator::PYTHON_TO_CPPCONVERSION_STRUCT = "Shiboken::Conversions::PythonToCppConversion";

static inline QString reprFunction() { return QStringLiteral("__repr__"); }

TextStream &operator<<(TextStream &s, CppGenerator::ErrorReturn r)
{
    s << "return";
    switch (r) {
    case CppGenerator::ErrorReturn::Default:
        s << " {}";
        break;
    case CppGenerator::ErrorReturn::Zero:
        s << " 0";
        break;
    case CppGenerator::ErrorReturn::MinusOne:
        s << " -1";
        break;
    case CppGenerator::ErrorReturn::Void:
        break;
    }
    s << ";\n";
    return s;
}

// Protocol function name / function parameters / return type
struct ProtocolEntry
{
    QString name;
    QString arguments;
    QString returnType;
};

using ProtocolEntries = QList<ProtocolEntry>;

static bool contains(const ProtocolEntries &l, const QString &needle)
{
    for (const auto &m : l) {
        if (m.name == needle)
            return true;
    }
    return false;
}

// Maps special function names to function parameters and return types
// used by CPython API in the mapping protocol.
const ProtocolEntries &mappingProtocols()
{
    static const ProtocolEntries result = {
        {u"__mlen__"_s,
         u"PyObject *self"_s,
         u"Py_ssize_t"_s},
        {u"__mgetitem__"_s,
         u"PyObject *self, PyObject *_key"_s,
         u"PyObject*"_s},
        {u"__msetitem__"_s,
         u"PyObject *self, PyObject *_key, PyObject *_value"_s,
         intT()}};
    return result;
}

// Maps special function names to function parameters and return types
// used by CPython API in the sequence protocol.
const ProtocolEntries &sequenceProtocols()
{
    static const ProtocolEntries result = {
        {u"__len__"_s,
         u"PyObject *self"_s,
         u"Py_ssize_t"_s},
        {u"__getitem__"_s,
         u"PyObject *self, Py_ssize_t _i"_s,
         u"PyObject*"_s},
        {u"__setitem__"_s,
         u"PyObject *self, Py_ssize_t _i, PyObject *_value"_s,
         intT()},
        {u"__getslice__"_s,
         u"PyObject *self, Py_ssize_t _i1, Py_ssize_t _i2"_s,
         u"PyObject*"_s},
        {u"__setslice__"_s,
         u"PyObject *self, Py_ssize_t _i1, Py_ssize_t _i2, PyObject *_value"_s,
         intT()},
        {u"__contains__"_s,
         u"PyObject *self, PyObject *_value"_s,
         intT()},
        {u"__concat__"_s,
         u"PyObject *self, PyObject *_other"_s,
         u"PyObject*"_s}
    };
    return result;
}

// Return name of function to create PyObject wrapping a container
static QString opaqueContainerCreationFunc(const AbstractMetaType &type)
{
    const auto containerTypeEntry =
        std::static_pointer_cast<const ContainerTypeEntry>(type.typeEntry());
    const auto instantiationTypeEntry =
        type.instantiations().constFirst().typeEntry();
    QString result = u"create"_s;
    if (type.isConstant())
        result += u"Const"_s;
    result += containerTypeEntry->opaqueContainerName(type.instantiationCppSignatures());
    return result;
}

// Write declaration of the function to create PyObject wrapping a container
static void writeOpaqueContainerCreationFuncDecl(TextStream &s, const QString &name,
                                                 AbstractMetaType type)
{
    type.setReferenceType(NoReference);
    // Maintain const
    s << "PyObject *" << name << '(' << type.cppSignature() << "*);\n";
}

CppGenerator::CppGenerator() = default;

QString CppGenerator::fileNameForContext(const GeneratorContext &context) const
{
    return fileNameForContextHelper(context, u"_wrapper.cpp"_s);
}

static bool isInplaceAdd(const AbstractMetaFunctionCPtr &func)
{
    return func->name() == u"operator+=";
}

static bool isIncrementOperator(const AbstractMetaFunctionCPtr &func)
{
    return func->functionType() == AbstractMetaFunction::IncrementOperator;
}

static bool isDecrementOperator(const AbstractMetaFunctionCPtr &func)
{
    return func->functionType() == AbstractMetaFunction::DecrementOperator;
}

// Filter predicate for operator functions
static bool skipOperatorFunc(const AbstractMetaFunctionCPtr &func)
{
    if (func->isModifiedRemoved() || func->usesRValueReferences())
        return true;
    const auto &name = func->name();
    return name == u"operator[]" || name == u"operator->" || name == u"operator!";
}

QList<AbstractMetaFunctionCList>
    CppGenerator::filterGroupedOperatorFunctions(const AbstractMetaClassCPtr &metaClass,
                                                 OperatorQueryOptions query)
{
    // ( func_name, num_args ) => func_list
    QMap<QPair<QString, int>, AbstractMetaFunctionCList> results;

    auto funcs = metaClass->operatorOverloads(query);
    auto end = std::remove_if(funcs.begin(), funcs.end(), skipOperatorFunc);
    funcs.erase(end, funcs.end());

    // If we have operator+=, we remove the operator++/-- which would
    // otherwise be used for emulating __iadd__, __isub__.
    if (std::any_of(funcs.cbegin(), funcs.cend(), isInplaceAdd)) {
        end = std::remove_if(funcs.begin(), funcs.end(),
                             [] (const AbstractMetaFunctionCPtr &func) {
                                 return func->isIncDecrementOperator();
                             });
        funcs.erase(end, funcs.end());
    } else {
        // If both prefix/postfix ++/-- are present, remove one
        if (std::count_if(funcs.begin(), funcs.end(), isIncrementOperator) > 1)
            funcs.erase(std::find_if(funcs.begin(), funcs.end(), isIncrementOperator));
        if (std::count_if(funcs.begin(), funcs.end(), isDecrementOperator) > 1)
            funcs.erase(std::find_if(funcs.begin(), funcs.end(), isDecrementOperator));
    }

    for (const auto &func : funcs) {
        int args;
        if (func->isComparisonOperator()) {
            args = -1;
        } else {
            args = func->arguments().size();
        }
        QPair<QString, int > op(func->name(), args);
        results[op].append(func);
    }
    QList<AbstractMetaFunctionCList> result;
    result.reserve(results.size());
    for (auto it = results.cbegin(), end = results.cend(); it != end; ++it)
        result.append(it.value());
    return result;
}

CppGenerator::BoolCastFunctionOptional
    CppGenerator::boolCast(const AbstractMetaClassCPtr &metaClass) const
{
    const auto te = metaClass->typeEntry();
    if (te->isSmartPointer()) {
        auto ste = std::static_pointer_cast<const SmartPointerTypeEntry>(te);

        auto valueCheckMethod = ste->valueCheckMethod();
        if (!valueCheckMethod.isEmpty()) {
            const auto func = metaClass->findFunction(valueCheckMethod);
            if (!func)
                throw Exception(msgMethodNotFound(metaClass, valueCheckMethod));
            return BoolCastFunction{func, false};
        }

        auto nullCheckMethod = ste->nullCheckMethod();
        if (!nullCheckMethod.isEmpty()) {
            const auto func = metaClass->findFunction(nullCheckMethod);
            if (!func)
                throw Exception(msgMethodNotFound(metaClass, nullCheckMethod));
            return BoolCastFunction{func, true};
        }
    }

    auto mode = te->operatorBoolMode();
    if (useOperatorBoolAsNbNonZero()
        ? mode != TypeSystem::BoolCast::Disabled : mode == TypeSystem::BoolCast::Enabled) {
        const auto func = metaClass->findOperatorBool();
        if (func)
            return BoolCastFunction{func, false};
    }

    mode = te->isNullMode();
    if (useIsNullAsNbNonZero()
        ? mode != TypeSystem::BoolCast::Disabled : mode == TypeSystem::BoolCast::Enabled) {
        const auto func = metaClass->findQtIsNullMethod();
        if (func)
            return BoolCastFunction{func, true};
    }
    return std::nullopt;
}

std::optional<AbstractMetaType>
    CppGenerator::findSmartPointerInstantiation(const SmartPointerTypeEntryCPtr &pointer,
                                                const TypeEntryCPtr &pointee) const
{
    for (const auto &smp : api().instantiatedSmartPointers()) {
        const auto &i = smp.type;
        if (i.typeEntry() == pointer && i.instantiations().at(0).typeEntry() == pointee)
            return i;
    }
    return {};
}

void CppGenerator::clearTpFuncs()
{
    m_tpFuncs = {
        {u"__str__"_s, {}}, {u"__str__"_s, {}},
        {reprFunction(), {}}, {u"__iter__"_s, {}},
        {u"__next__"_s, {}}
    };
}

// Prevent ELF symbol qt_version_tag from being generated into the source
static const char includeQDebug[] =
"#ifndef QT_NO_VERSION_TAGGING\n"
"#  define QT_NO_VERSION_TAGGING\n"
"#endif\n"
"#include <QtCore/QDebug>\n";

static QString chopType(QString s)
{
    if (s.endsWith(u"_Type"))
        s.chop(5);
    else if (s.endsWith(u"_TypeF()"))
        s.chop(8);
    return s;
}

static bool isStdSetterName(QString setterName, QString propertyName)
{
   return setterName.size() == propertyName.size() + 3
          && setterName.startsWith(u"set")
          && setterName.endsWith(QStringView{propertyName}.right(propertyName.size() - 1))
          && setterName.at(3) == propertyName.at(0).toUpper();
}

static QString buildPropertyString(const QPropertySpec &spec)
{
    QString text = u'"' + spec.name() + u':';

    if (spec.read() != spec.name())
        text += spec.read();

    if (!spec.write().isEmpty()) {
        text += u':';
        if (!isStdSetterName(spec.write(), spec.name()))
            text += spec.write();
    }

    text += u'"';
    return text;
}

static QString _plainName(const QString &s)
{
    auto cutPos = s.lastIndexOf(u"::"_s);
    return cutPos < 0 ? s : s.right(s.length() - (cutPos + 2));
}

/**********************************************************************
 *
 * Decision whether to use an IntEnum/IntFlag
 * ------------------------------------------
 *
 * Unfortunately, all attempts to drive this decision automagically
 * did not work out. We therefore compile a list in with known
 * IntEnum and IntFlag.
 */

/*
 * This function is now unused and replaced by TypeSystem::PythonEnumType
 */
#if 0
static QSet<QString> useIntSet()
{
    static const QSet<QString> result{
        /* IntEnum */ u"PySide6.QtCore.QDataStream.Version"_s,
        /* IntEnum */ u"PySide6.QtCore.QEvent.Type"_s,
        /* IntEnum */ u"PySide6.QtCore.QLocale.FloatingPointPrecisionOption"_s,
        /* IntFlag */ u"PySide6.QtCore.QLocale.LanguageCodeType"_s,
        /* IntFlag */ u"PySide6.QtCore.QUrl.ComponentFormattingOption"_s,
        // note:  "QUrl::UrlFormattingOption" is set as IntFlag without flags
        /* IntFlag */ u"PySide6.QtCore.QUrl.UrlFormattingOption"_s,
        /* IntFlag */ u"PySide6.QtCore.Qt.AlignmentFlag"_s,
        /* IntFlag */ u"PySide6.QtCore.Qt.FocusPolicy"_s,
        /* IntEnum */ u"PySide6.QtCore.Qt.GestureType"_s,
        /* IntEnum */ u"PySide6.QtCore.Qt.ItemDataRole"_s,
        /* IntEnum */ u"PySide6.QtCore.Qt.Key"_s,
        /*    Flag */ u"PySide6.QtCore.Qt.Modifier"_s,
        // note:  "Qt::TextFlag" is set as IntFlag without flags
        /* IntFlag */ u"PySide6.QtCore.Qt.TextFlag"_s,
        /* IntFlag */ u"PySide6.QtCore.Qt.WindowType"_s,
        // This is found in QtWidgets but should be in QtGui.
        /* IntEnum */ u"PySide6.QtGui.QFileSystemModel.Roles"_s,
        /* IntEnum */ u"PySide6.QtGui.QFont.Stretch"_s,
        /* IntEnum */ u"PySide6.QtGui.QFont.Weight"_s,
        /* IntEnum */ u"PySide6.QtGui.QTextDocument.ResourceType"_s,
        /* IntEnum */ u"PySide6.QtGui.QTextFormat.FormatType"_s,
        /* IntEnum */ u"PySide6.QtGui.QTextFormat.ObjectTypes"_s,
        /* IntEnum */ u"PySide6.QtGui.QTextFormat.Property"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QDialog.DialogCode"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QFrame.Shadow"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QFrame.Shape"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QListWidgetItem.ItemType"_s,
        /* IntFlag */ u"PySide6.QtWidgets.QMessageBox.StandardButton"_s,
        // note:  "QSizePolicy::PolicyFlag" is set as IntFlag without flags
        /* IntFlag */ u"PySide6.QtWidgets.QSizePolicy.PolicyFlag"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QStyle.ComplexControl"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QStyle.ContentsType"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QStyle.ControlElement"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QStyle.PixelMetric"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QStyle.PrimitiveElement"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QStyle.StandardPixmap"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QStyle.StyleHint"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QStyle.SubElement"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QTableWidgetItem.ItemType"_s,
        /* IntEnum */ u"PySide6.QtWidgets.QTreeWidgetItem.ItemType"_s,
        /* IntEnum */ u"PySide6.QtCharts.QBoxSet.ValuePositions"_s,
        /* IntEnum */ u"PySide6.QtMultimedia.QMediaPlayer.Loops"_s,
        /* IntEnum */ u"PySide6.QtQuick.QSGGeometry.DrawingMode"_s,
        /* IntEnum */ u"PySide6.QtWebEngineCore.QWebEngineScript.ScriptWorldId"_s,
        // Added because it should really be used as number
        /* IntEnum */ u"PySide6.QtCore.QMetaType.Type"_s,
        /* IntEnum */ u"PySide6.QtSerialPort.QSerialPort.BaudRate"_s,
    };
    return result;
}
#endif

static bool _shouldInheritInt(const AbstractMetaEnum &cppEnum)
{
    if (!cppEnum.fullName().startsWith(u"PySide6."_s))
        return true;
    // static auto intSet = useIntSet();
    // return intSet.contains(cppEnum.fullName());
    return false;
}

static QString BuildEnumFlagInfo(const AbstractMetaEnum &cppEnum)
{
    auto enumType = cppEnum.typeEntry();
    QString result = _plainName(enumType->name());
    auto flags = enumType->flags();
    auto decision = enumType->pythonEnumType();
    bool _int = _shouldInheritInt(cppEnum);
    bool _flag = bool(flags);

    if (decision != TypeSystem::PythonEnumType::Unspecified) {
        _int = decision == TypeSystem::PythonEnumType::IntEnum ||
               decision == TypeSystem::PythonEnumType::IntFlag;
        _flag = decision == TypeSystem::PythonEnumType::Flag ||
                decision == TypeSystem::PythonEnumType::IntFlag;
    }
    result += _flag ? (_int ? u":IntFlag"_s : u":Flag"_s)
                    : (_int ? u":IntEnum"_s : u":Enum"_s);
    if (flags)
        result += u':' + _plainName(flags->flagsName());
    return u'"' + result + u'"';
}

static void writePyGetSetDefEntry(TextStream &s, const QString &name,
                                  const QString &getFunc, const QString &setFunc)
{
    s << "{const_cast<char *>(\"" << name << "\"), " << getFunc << ", "
        << (setFunc.isEmpty() ? NULL_PTR : setFunc) << ", nullptr, nullptr},\n";
}

static bool generateRichComparison(const GeneratorContext &c)
{
    const auto metaClass = c.metaClass();
    if (c.forSmartPointer()) {
        auto te = std::static_pointer_cast<const SmartPointerTypeEntry>(metaClass->typeEntry());
        return te->smartPointerType() == TypeSystem::SmartPointerType::Shared;
    }

    return !metaClass->isNamespace() && metaClass->hasComparisonOperatorOverload();
}

void CppGenerator::generateIncludes(TextStream &s, const GeneratorContext &classContext,
                                    const IncludeGroupList &includes,
                                    const AbstractMetaClassCList &innerClasses) const
{
    const auto metaClass = classContext.metaClass();

    // write license comment
    s << licenseComment() << '\n';

    const bool normalClass = !classContext.forSmartPointer();
    if (normalClass && !avoidProtectedHack() && !metaClass->isNamespace()
        && !metaClass->hasPrivateDestructor()) {
        s << "//workaround to access protected functions\n";
        s << "#define protected public\n\n";
    }

    QByteArrayList cppIncludes{"typeinfo", "iterator", // for containers
                               "cctype", "cstring"};
    // headers
    s << "// default includes\n";
    s << "#include <shiboken.h>\n";
    if (wrapperDiagnostics()) {
        s << "#include <helper.h>\n";
        cppIncludes << "iostream";
    }

    if (normalClass && usePySideExtensions()) {
        s << includeQDebug;
        if (metaClass->hasToStringCapability())
            s << "#include <QtCore/QBuffer>\n";
        if (isQObject(metaClass)) {
            s << "#include <pysideqobject.h>\n"
                << "#include <pysidesignal.h>\n"
                << "#include <pysideproperty.h>\n"
                << "#include <signalmanager.h>\n"
                << "#include <pysidemetafunction.h>\n";
        }
        s << "#include <pysideqenum.h>\n"
            << "#include <pysideqflags.h>\n"
            << "#include <pysideqmetatype.h>\n"
            << "#include <pysideutils.h>\n"
            << "#include <feature_select.h>\n"
            << "QT_WARNING_DISABLE_DEPRECATED\n\n";
    }

    // The multiple inheritance initialization function
    // needs the 'set' class from C++ STL.
    if (normalClass && getMultipleInheritingClass(metaClass) != nullptr)
        cppIncludes << "algorithm" << "set";
    if (normalClass && metaClass->generateExceptionHandling())
        cppIncludes << "exception";

    s << "\n// module include\n" << "#include \"" << getModuleHeaderFileName() << "\"\n";
    if (hasPrivateClasses())
        s << "#include \"" << getPrivateModuleHeaderFileName() << "\"\n";

    s << "\n// main header\n" << "#include \""
      << HeaderGenerator::headerFileNameForContext(classContext) << "\"\n";

    if (!innerClasses.isEmpty()) {
        s  << "\n// inner classes\n";
        for (const auto &innerClass : innerClasses) {
            GeneratorContext innerClassContext = contextForClass(innerClass);
            s << "#include \""
                << HeaderGenerator::headerFileNameForContext(innerClassContext) << "\"\n";
        }
    }

    if (avoidProtectedHack())
        s << baseWrapperIncludes(classContext);

    for (const auto &g : includes)
        s << g;

    // C++ includes
    std::sort(cppIncludes.begin(), cppIncludes.end());
    s << '\n';
    for (const auto &i : std::as_const(cppIncludes))
        s << "#include <" << i << ">\n";
}

static const char openTargetExternC[] =  R"(
// Target ---------------------------------------------------------

extern "C" {
)";

static const char closeExternC[] =  "} // extern \"C\"\n\n";

// Write methods definition
static void writePyMethodDefs(TextStream &s, const QString &className,
                              const QString &methodsDefinitions, bool generateCopy)
{
    s << "static PyMethodDef " << className << "_methods[] = {\n" << indent
        << methodsDefinitions << '\n';
    if (generateCopy) {
        s << "{\"__copy__\", reinterpret_cast<PyCFunction>(" << className << "___copy__)"
          << ", METH_NOARGS, nullptr},\n";
    }
    s  << methodDefSentinel << outdent
        << "};\n\n";
}

static bool hasHashFunction(const AbstractMetaClassCPtr &c)
{
    return !c->typeEntry()->hashFunction().isEmpty()
           || c->hasHashFunction();
}

static bool needsTypeDiscoveryFunction(const AbstractMetaClassCPtr &c)
{
    return c->baseClass() != nullptr
           && (c->isPolymorphic() || !c->typeEntry()->polymorphicIdValue().isEmpty());
}

static void writeAddedTypeSignatures(TextStream &s, const ComplexTypeEntryCPtr &te)
{
    for (const auto &e : te->addedPyMethodDefEntrys()) {
        if (auto count = e.signatures.size()) {
            for (qsizetype i = 0; i < count; ++i) {
                if (count > 1)
                    s << i << ':';
                s << e.signatures.at(i) << '\n';
            }
        }
    }
}

/// Function used to write the class generated binding code on the buffer
/// \param s the output buffer
/// \param classContext the pointer to metaclass information
void CppGenerator::generateClass(TextStream &s, const GeneratorContext &classContext)
{
    if (classContext.forSmartPointer()) {
        generateSmartPointerClass(s, classContext);
        return;
    }

    s.setLanguage(TextStream::Language::Cpp);
    AbstractMetaClassCPtr metaClass = classContext.metaClass();
    const auto typeEntry = metaClass->typeEntry();

    auto innerClasses = metaClass->innerClasses();
    for (auto it = innerClasses.begin(); it != innerClasses.end(); ) {
        auto innerTypeEntry = (*it)->typeEntry();
        if (shouldGenerate(innerTypeEntry) && !innerTypeEntry->isSmartPointer())
            ++it;
        else
            it = innerClasses.erase(it);
    }

    AbstractMetaEnumList classEnums = metaClass->enums();
    metaClass->getEnumsFromInvisibleNamespacesToBeGenerated(&classEnums);

    IncludeGroupList includeGroups;
    if (!classContext.useWrapper() || !avoidProtectedHack())
        includeGroups.append(classIncludes(metaClass));
    generateIncludes(s, classContext, includeGroups, innerClasses);

    if (typeEntry->typeFlags().testFlag(ComplexTypeEntry::Deprecated))
        s << "#Deprecated\n";

    // Use class base namespace
    {
        AbstractMetaClassCPtr context = metaClass->enclosingClass();
        while (context) {
            if (context->isNamespace() && !context->enclosingClass()
                && std::static_pointer_cast<const NamespaceTypeEntry>(context->typeEntry())->generateUsing()) {
                s << "\nusing namespace " << context->qualifiedCppName() << ";\n";
                break;
            }
            context = context->enclosingClass();
        }
    }

    s  << '\n';

    // class inject-code native/beginning
    if (!typeEntry->codeSnips().isEmpty()) {
        writeClassCodeSnips(s, typeEntry->codeSnips(),
                            TypeSystem::CodeSnipPositionBeginning, TypeSystem::NativeCode,
                            classContext);
        s << '\n';
    }

    // python conversion rules
    if (typeEntry->isValue()) {
        auto vte = std::static_pointer_cast<const ValueTypeEntry>(typeEntry);
        if (vte->hasTargetConversionRule()) {
            s << "// Python Conversion\n";
            s << vte->targetConversionRule() << '\n';
        }
    }

    if (classContext.useWrapper()) {
        s << "// Native ---------------------------------------------------------\n\n";

        if (avoidProtectedHack() && usePySideExtensions()) {
            s << "void " << classContext.wrapperName() << "::pysideInitQtMetaTypes()\n{\n"
                  << indent;
            writeInitQtMetaTypeFunctionBody(s, classContext);
            s << outdent << "}\n\n";
        }

        int maxOverrides = 0;
        writeCacheResetNative(s, classContext);
        for (const auto &func : metaClass->functions()) {
            const auto generation = functionGeneration(func);
            if (generation.testFlag(FunctionGenerationFlag::WrapperConstructor))
                writeConstructorNative(s, classContext, func);
            else if (generation.testFlag(FunctionGenerationFlag::VirtualMethod))
                writeVirtualMethodNative(s, func, maxOverrides++);
        }

        if (!avoidProtectedHack() || !metaClass->hasPrivateDestructor()) {
            if (usePySideExtensions() && isQObject(metaClass))
                writeMetaObjectMethod(s, classContext);
            writeDestructorNative(s, classContext);
        }
    }

    StringStream smd(TextStream::Language::Cpp);
    StringStream md(TextStream::Language::Cpp);
    StringStream signatureStream(TextStream::Language::Cpp);

    s << openTargetExternC;

    const auto &functionGroups = getFunctionGroups(metaClass);
    for (auto it = functionGroups.cbegin(), end = functionGroups.cend(); it != end; ++it) {
        if (contains(sequenceProtocols(), it.key()) || contains(mappingProtocols(), it.key()))
            continue;
        const AbstractMetaFunctionCList &overloads = it.value();
        if (overloads.isEmpty())
            continue;

        const auto rfunc = overloads.constFirst();
        OverloadData overloadData(overloads, api());

        if (rfunc->isConstructor()) {
            writeConstructorWrapper(s, overloadData, classContext);
            writeSignatureInfo(signatureStream, overloadData);
        }
        // call operators
        else if (rfunc->name() == u"operator()") {
            writeMethodWrapper(s, overloadData, classContext);
            writeSignatureInfo(signatureStream, overloadData);
        }
        else if (!rfunc->isOperatorOverload()) {
            writeMethodWrapper(s, overloadData, classContext);
            writeSignatureInfo(signatureStream, overloadData);
            // For a mixture of static and member function overloads,
            // a separate PyMethodDef entry is written which is referenced
            // in the PyMethodDef list and later in getattro() for handling
            // the non-static case.
            const auto defEntries = methodDefinitionEntries(overloadData);
            if (OverloadData::hasStaticAndInstanceFunctions(overloads)) {
                QString methDefName = cpythonMethodDefinitionName(rfunc);
                smd << "static PyMethodDef " << methDefName << " = " << indent
                    << defEntries.constFirst() << outdent << ";\n\n";
            }
            if (!m_tpFuncs.contains(rfunc->name()))
                md << defEntries;
        }
    }
    for (const auto &pyMethodDef : typeEntry->addedPyMethodDefEntrys())
        md << pyMethodDef << ",\n";
    const QString methodsDefinitions = md.toString();
    const QString singleMethodDefinitions = smd.toString();

    const QString className = chopType(cpythonTypeName(metaClass));

    if (typeEntry->isValue()) {
        writeCopyFunction(s, classContext);
        signatureStream << fullPythonClassName(metaClass) << ".__copy__()\n";
    }

    // Write single method definitions
    s << singleMethodDefinitions;

    if (usePySideExtensions()) {
        // PYSIDE-1019: Write a compressed list of all properties `name:getter[:setter]`.
        //              Default values are suppressed.
        QStringList sorter;
        for (const auto &spec : metaClass->propertySpecs()) {
            if (!spec.generateGetSetDef())
                sorter.append(buildPropertyString(spec));
        }
        sorter.sort();

        s << '\n';
        s << "static const char *" << className << "_PropertyStrings[] = {\n" << indent;
        for (const auto &entry : std::as_const(sorter))
            s << entry << ",\n";
        s << NULL_PTR << " // Sentinel\n"
            << outdent << "};\n\n";

    }
    // PYSIDE-1735: Write an EnumFlagInfo structure
    QStringList sorter;
    for (const auto &entry : std::as_const(classEnums))
        sorter.append(BuildEnumFlagInfo(entry));
    sorter.sort();
    if (!sorter.empty()) {
        s << "static const char *" << className << "_EnumFlagInfo[] = {\n" << indent;
        for (const auto &entry : std::as_const(sorter))
            s << entry << ",\n";
        s << NULL_PTR << " // Sentinel\n"
            << outdent << "};\n\n";
    }

    // Write methods definition
    writePyMethodDefs(s, className, methodsDefinitions, typeEntry->isValue());

    // Write tp_s/getattro function
    const AttroCheck attroCheck = checkAttroFunctionNeeds(metaClass);
    if ((attroCheck & AttroCheckFlag::GetattroMask) != 0)
        writeGetattroFunction(s, attroCheck, classContext);
    if ((attroCheck & AttroCheckFlag::SetattroMask) != 0)
        writeSetattroFunction(s, attroCheck, classContext);

    if (const auto f = boolCast(metaClass) ; f.has_value())
        writeNbBoolFunction(classContext, f.value(), s);

    if (supportsNumberProtocol(metaClass)) {
        const QList<AbstractMetaFunctionCList> opOverloads = filterGroupedOperatorFunctions(
                metaClass,
                OperatorQueryOption::ArithmeticOp
                | OperatorQueryOption::IncDecrementOp
                | OperatorQueryOption::LogicalOp
                | OperatorQueryOption::BitwiseOp);

        for (const AbstractMetaFunctionCList &allOverloads : opOverloads) {
            AbstractMetaFunctionCList overloads;
            for (const auto &func : allOverloads) {
                if (!func->isModifiedRemoved()
                    && !func->isPrivate()
                    && (func->ownerClass() == func->implementingClass() || func->isAbstract()))
                    overloads.append(func);
            }

            if (overloads.isEmpty())
                continue;

            OverloadData overloadData(overloads, api());
            writeMethodWrapper(s, overloadData, classContext);
            writeSignatureInfo(signatureStream, overloadData);
        }
    }

    if (supportsSequenceProtocol(metaClass)) {
        writeSequenceMethods(s, metaClass, classContext);
    }

    if (supportsMappingProtocol(metaClass)) {
        writeMappingMethods(s, metaClass, classContext);
    }

    if (generateRichComparison(classContext)) {
        s << "// Rich comparison\n";
        writeRichCompareFunction(s, classContext);
    }

    if (shouldGenerateGetSetList(metaClass)) {
        const AbstractMetaFieldList &fields = metaClass->fields();
        for (const AbstractMetaField &metaField : fields) {
            if (metaField.canGenerateGetter())
                writeGetterFunction(s, metaField, classContext);
            if (metaField.canGenerateSetter())
                writeSetterFunction(s, metaField, classContext);
            s << '\n';
        }

        for (const QPropertySpec &property : metaClass->propertySpecs()) {
            if (property.generateGetSetDef() || !usePySideExtensions()) {
                writeGetterFunction(s, property, classContext);
                if (property.hasWrite())
                    writeSetterFunction(s, property, classContext);
            }
        }

        s << "// Getters and Setters for " << metaClass->name() << '\n';
        s << "static PyGetSetDef " << cpythonGettersSettersDefinitionName(metaClass)
            << "[] = {\n" << indent;
        for (const AbstractMetaField &metaField : fields) {
            const bool canGenerateGetter = metaField.canGenerateGetter();
            const bool canGenerateSetter = metaField.canGenerateSetter();
            if (canGenerateGetter || canGenerateSetter) {
                const QString getter = canGenerateGetter
                    ? cpythonGetterFunctionName(metaField) : QString();
                const QString setter = canGenerateSetter
                    ? cpythonSetterFunctionName(metaField) : QString();
                const auto names = metaField.definitionNames();
                for (const auto &name : names)
                    writePyGetSetDefEntry(s, name, getter, setter);
            }
        }

        for (const QPropertySpec &property : metaClass->propertySpecs()) {
            if (property.generateGetSetDef() || !usePySideExtensions()) {
                const QString setter = property.hasWrite()
                    ? cpythonSetterFunctionName(property, metaClass) : QString();
                writePyGetSetDefEntry(s, property.name(),
                                      cpythonGetterFunctionName(property, metaClass), setter);
            }
        }
        s << "{nullptr, nullptr, nullptr, nullptr, nullptr} // Sentinel\n"
            << outdent << "};\n\n";
    }

    s << closeExternC;

    if (hasHashFunction(metaClass))
        writeHashFunction(s, classContext);

    // Write tp_traverse and tp_clear functions.
    writeTpTraverseFunction(s, metaClass);
    writeTpClearFunction(s, metaClass);

    writeClassDefinition(s, metaClass, classContext);
    s << '\n';

    if (needsTypeDiscoveryFunction(metaClass))
        writeTypeDiscoveryFunction(s, metaClass);

    writeFlagsNumberMethodsDefinitions(s, classEnums);
    s << '\n';

    writeConverterFunctions(s, metaClass, classContext);
    writeAddedTypeSignatures(signatureStream, typeEntry);
    writeClassRegister(s, metaClass, classContext, signatureStream);

    if (metaClass->hasStaticFields())
        writeStaticFieldInitialization(s, metaClass);

    // class inject-code native/end
    if (!typeEntry->codeSnips().isEmpty()) {
        writeClassCodeSnips(s, typeEntry->codeSnips(),
                            TypeSystem::CodeSnipPositionEnd, TypeSystem::NativeCode,
                            classContext);
        s << '\n';
    }
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
    generateIncludes(s, classContext, {includes});

    s  << '\n';

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

    const QString methodsDefinitions = md.toString();
    const QString singleMethodDefinitions = smd.toString();

    const QString className = chopType(cpythonTypeName(typeEntry));

    writeCopyFunction(s, classContext);
    signatureStream << fullPythonClassName(metaClass) << ".__copy__()\n";

    // Write single method definitions
    s << singleMethodDefinitions;

    // Write methods definition
    writePyMethodDefs(s, className, methodsDefinitions, true /* ___copy__ */);

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

void CppGenerator::writeMethodWrapper(TextStream &s, TextStream &definitionStream,
                                      TextStream &signatureStream,
                                      const AbstractMetaFunctionCList &overloads,
                                      const GeneratorContext &classContext) const
{
    OverloadData overloadData(overloads, api());
    writeMethodWrapper(s, overloadData, classContext);
    writeSignatureInfo(signatureStream, overloadData);
    definitionStream << methodDefinitionEntries(overloadData);
}

void CppGenerator::writeCacheResetNative(TextStream &s, const GeneratorContext &classContext)
{
    s << "void " << classContext.wrapperName()
        << "::resetPyMethodCache()\n{\n" << indent
        << "std::fill_n(m_PyMethodCache, sizeof(m_PyMethodCache) / sizeof(m_PyMethodCache[0]), false);\n"
        << outdent << "}\n\n";
}

void CppGenerator::writeConstructorNative(TextStream &s, const GeneratorContext &classContext,
                                          const AbstractMetaFunctionCPtr &func) const
{
    const QString qualifiedName = classContext.wrapperName() + u"::"_s;
    s << functionSignature(func, qualifiedName, QString(),
                           OriginalTypeDescription | SkipDefaultValues);
    s << " : ";
    writeFunctionCall(s, func);
    s << "\n{\n" << indent;
    if (wrapperDiagnostics())
        s << R"(std::cerr << __FUNCTION__ << ' ' << this << '\n';)" << '\n';
    const AbstractMetaArgument *lastArg = func->arguments().isEmpty() ? nullptr : &func->arguments().constLast();
    s << "resetPyMethodCache();\n";
    writeCodeSnips(s, func->injectedCodeSnips(), TypeSystem::CodeSnipPositionBeginning,
                   TypeSystem::NativeCode, func, false, lastArg);
    s << "// ... middle\n";
    writeCodeSnips(s, func->injectedCodeSnips(), TypeSystem::CodeSnipPositionEnd,
                   TypeSystem::NativeCode, func, false, lastArg);
    s << outdent << "}\n\n";
}

void CppGenerator::writeDestructorNative(TextStream &s,
                                         const GeneratorContext &classContext) const
{
    s << classContext.wrapperName() << "::~"
        << classContext.wrapperName() << "()\n{\n" << indent;
    if (wrapperDiagnostics())
        s << R"(std::cerr << __FUNCTION__ << ' ' << this << '\n';)" << '\n';
    // kill pyobject
    s << R"(SbkObject *wrapper = Shiboken::BindingManager::instance().retrieveWrapper(this);
Shiboken::Object::destroy(wrapper, this);
)" << outdent << "}\n";
}

// Return type for error messages when getting invalid types from virtual
// methods implemented in Python in C++ wrappers
QString CppGenerator::getVirtualFunctionReturnTypeName(const AbstractMetaFunctionCPtr &func) const
{
    if (func->type().isVoid())
        return u"\"\""_s;

    if (func->isTypeModified())
        return u'"' + func->modifiedTypeName() + u'"';

    // SbkType would return null when the type is a container.
    auto typeEntry = func->type().typeEntry();
    if (typeEntry->isContainer()) {
        const auto cte = std::static_pointer_cast<const ContainerTypeEntry>(typeEntry);
        switch (cte->containerKind()) {
        case ContainerTypeEntry::ListContainer:
            break;
        case ContainerTypeEntry::SetContainer:
            return uR"("set")"_s;
            break;
        case ContainerTypeEntry::MapContainer:
        case ContainerTypeEntry::MultiMapContainer:
            return uR"("dict")"_s;
            break;
        case ContainerTypeEntry::PairContainer:
            return uR"("tuple")"_s;
            break;
        }
        return uR"("list")"_s;
    }
    if (typeEntry->isSmartPointer())
        return u'"' + typeEntry->qualifiedCppName() + u'"';

    if (avoidProtectedHack()) {
        auto metaEnum = api().findAbstractMetaEnum(func->type().typeEntry());
        if (metaEnum.has_value() && metaEnum->isProtected())
            return u'"' + protectedEnumSurrogateName(metaEnum.value()) + u'"';
    }

    if (func->type().isPrimitive())
        return u'"' + func->type().name() + u'"';

    return u"reinterpret_cast<PyTypeObject *>(Shiboken::SbkType< "_s
        + typeEntry->qualifiedCppName() + u" >())->tp_name"_s;
}

// When writing an overridden method of a wrapper class, write the part
// calling the C++ function in case no overload in Python exists.
void CppGenerator::writeVirtualMethodCppCall(TextStream &s,
                                             const AbstractMetaFunctionCPtr &func,
                                             const QString &funcName,
                                             const CodeSnipList &snips,
                                             const AbstractMetaArgument *lastArg,
                                             const TypeEntryCPtr &retType,
                                             const QString &returnStatement, bool hasGil) const
{
    if (!snips.isEmpty()) {
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionBeginning,
                       TypeSystem::ShellCode, func, false, lastArg);
    }

    if (func->isAbstract()) {
        if (!hasGil)
            s << "Shiboken::GilState gil;\n";
        s << "Shiboken::Errors::setPureVirtualMethodError(\""
            << func->ownerClass()->name() << '.' << funcName << "\");\n"
            << returnStatement << '\n';
        return;
    }

    if (hasGil)
        s << "gil.release();\n";

    if (retType)
        s << "return ";
    s << "this->::" << func->implementingClass()->qualifiedCppName() << "::";
    writeFunctionCall(s, func, Generator::VirtualCall);
    s << ";\n";
    if (retType)
        return;
    if (!snips.isEmpty()) {
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionEnd,
                       TypeSystem::ShellCode, func, false, lastArg);
    }
    s << "return;\n";
}

// Determine the return statement (void or a result value).
QString CppGenerator::virtualMethodReturn(TextStream &s, const ApiExtractorResult &api,
                                          const AbstractMetaFunctionCPtr &func,
                                          const FunctionModificationList &functionModifications)
{
    if (func->isVoid())
        return u"return;"_s;
    const AbstractMetaType &returnType = func->type();
    for (const FunctionModification &mod : functionModifications) {
        for (const ArgumentModification &argMod : mod.argument_mods()) {
            if (argMod.index() == 0 && !argMod.replacedDefaultExpression().isEmpty()) {
                static const QRegularExpression regex(QStringLiteral("%(\\d+)"));
                Q_ASSERT(regex.isValid());
                QString expr = argMod.replacedDefaultExpression();
                for (int offset = 0; ; ) {
                    const QRegularExpressionMatch match = regex.match(expr, offset);
                    if (!match.hasMatch())
                        break;
                    const int argId = match.capturedView(1).toInt() - 1;
                    if (argId < 0 || argId > func->arguments().size()) {
                        qCWarning(lcShiboken, "The expression used in return value contains an invalid index.");
                        break;
                    }
                    expr.replace(match.captured(0), func->arguments().at(argId).name());
                    offset = match.capturedStart(1);
                }
                DefaultValue defaultReturnExpr(DefaultValue::Custom, expr);
                return u"return "_s + defaultReturnExpr.returnValue()
                       + u';';
            }
        }
    }
    QString errorMessage;
    const auto defaultReturnExpr = minimalConstructor(api, returnType, &errorMessage);
    if (!defaultReturnExpr.has_value()) {
        QString errorMsg = QLatin1StringView(__FUNCTION__) + u": "_s
                           + func->classQualifiedSignature();
        errorMsg = msgCouldNotFindMinimalConstructor(errorMsg,
                                                     func->type().cppSignature(),
                                                     errorMessage);
        qCWarning(lcShiboken).noquote().nospace() << errorMsg;
        s  << "\n#error " << errorMsg << '\n';
    }
    if (returnType.referenceType() == LValueReference) {
        s << "static " << returnType.typeEntry()->qualifiedCppName()
            << " result;\n";
        return u"return result;"_s;
    }
    return u"return "_s + defaultReturnExpr->returnValue()
           + u';';
}

// Create an argument for Py_BuildValue() when writing virtual methods.
// Return a pair of (argument, format-char).
QPair<QString, QChar> CppGenerator::virtualMethodNativeArg(const AbstractMetaFunctionCPtr &func,
                                                             const AbstractMetaArgument &arg)
{
    if (func->hasConversionRule(TypeSystem::TargetLangCode, arg.argumentIndex() + 1))
        return {arg.name() + CONV_RULE_OUT_VAR_SUFFIX, u'N'};

    const auto &type = arg.type();
    auto argTypeEntry = type.typeEntry();
    // Check for primitive types convertible by Py_BuildValue()
    if (argTypeEntry->isPrimitive() && !type.isCString()) {
        const auto pte = basicReferencedTypeEntry(argTypeEntry);
        auto it = formatUnits().constFind(pte->name());
        if (it != formatUnits().constEnd())
            return {arg.name(), it.value()};
    }

    // Rest: convert
    StringStream ac(TextStream::Language::Cpp);
    writeToPythonConversion(ac, type, func->ownerClass(), arg.name());
    return {ac.toString(), u'N'};
}

static const char PYTHON_ARGS_ARRAY[] = "pyArgArray";

void CppGenerator::writeVirtualMethodNativeVectorCallArgs(TextStream &s,
                                                          const AbstractMetaFunctionCPtr &func,
                                                          const AbstractMetaArgumentList &arguments,
                                                          const QList<int> &invalidateArgs) const
{
    Q_ASSERT(!arguments.isEmpty());
    s << "PyObject *" << PYTHON_ARGS_ARRAY <<'[' << arguments.size() << "] = {\n" << indent;
    const qsizetype last = arguments.size() - 1;
    for (qsizetype i = 0; i <= last; ++i) {
        const AbstractMetaArgument &arg = arguments.at(i);
        if (func->hasConversionRule(TypeSystem::TargetLangCode, arg.argumentIndex() + 1)) {
            s << arg.name() + CONV_RULE_OUT_VAR_SUFFIX;
        } else {
            writeToPythonConversion(s, arg.type(), func->ownerClass(), arg.name());
        }
        if (i < last)
            s << ',';
        s << '\n';
    }
    s << outdent << "};\n";

    if (!invalidateArgs.isEmpty())
        s << '\n';
    for (int index : invalidateArgs) {
        s << "const bool invalidateArg" << index << " = Py_REFCNT(" << PYTHON_ARGS_ARRAY <<
          '[' << index - 1 << "]) == 1;\n";
    }
}

void CppGenerator::writeVirtualMethodNativeArgs(TextStream &s,
                                                const AbstractMetaFunctionCPtr &func,
                                                const AbstractMetaArgumentList &arguments,
                                                const QList<int> &invalidateArgs) const
{
    s << "Shiboken::AutoDecRef " << PYTHON_ARGS << '(';
    if (arguments.isEmpty()) {
        s << "PyTuple_New(0));\n";
        return;
    }

    QString format;
    QStringList argConversions;
    for (const AbstractMetaArgument &arg : arguments) {
        auto argPair = virtualMethodNativeArg(func, arg);
        argConversions.append(argPair.first);
        format += argPair.second;
    }

    s << "Py_BuildValue(\"(" << format << ")\",\n"
        << indent << argConversions.join(u",\n"_s) << outdent << "\n));\n";

    for (int index : std::as_const(invalidateArgs)) {
        s << "bool invalidateArg" << index << " = Py_REFCNT(PyTuple_GET_ITEM(" << PYTHON_ARGS
            << ", " << index - 1 << ")) == 1;\n";
    }
}

static bool isArgumentNotRemoved(const AbstractMetaArgument &a)
{
    return !a.isModifiedRemoved();
}

// PyObject_Vectorcall(): since 3.9
static const char vectorCallCondition[] =
    "#if !defined(PYPY_VERSION) && !defined(Py_LIMITED_API) && PY_VERSION_HEX >= 0x03090000\n";

// PyObject_CallNoArgs(): since 3.9, stable API since 3.10
static const char noArgsCallCondition[] =
    "#if !defined(PYPY_VERSION) && ((defined(Py_LIMITED_API) && Py_LIMITED_API >= 0x030A0000) || (!defined(Py_LIMITED_API) && PY_VERSION_HEX >= 0x03090000))\n";
static const char inverseNoArgsCallCondition[] =
    "#if defined(PYPY_VERSION) || (defined(Py_LIMITED_API) && Py_LIMITED_API < 0x030A0000) || (!defined(Py_LIMITED_API) && PY_VERSION_HEX < 0x03090000)\n";

void CppGenerator::writeVirtualMethodNative(TextStream &s,
                                            const AbstractMetaFunctionCPtr &func,
                                            int cacheIndex) const
{
    TypeEntryCPtr retType = func->type().typeEntry();
    const QString funcName = func->isOperatorOverload()
        ? pythonOperatorFunctionName(func) : func->definitionNames().constFirst();

    QString prefix = wrapperName(func->ownerClass()) + u"::"_s;
    s << functionSignature(func, prefix, QString(), Generator::SkipDefaultValues |
                                                    Generator::OriginalTypeDescription)
      << "\n{\n" << indent;

    const QString returnStatement = virtualMethodReturn(s, api(), func,
                                                        func->modifications());

    const bool isAbstract = func->isAbstract();
    if (isAbstract && func->isModifiedRemoved()) {
        qCWarning(lcShiboken, "%s", qPrintable(msgPureVirtualFunctionRemoved(func.get())));
        s << returnStatement << '\n' << outdent << "}\n\n";
        return;
    }

    const CodeSnipList snips = func->hasInjectedCode()
        ? func->injectedCodeSnips() : CodeSnipList();
    const AbstractMetaArgument *lastArg = func->arguments().isEmpty()
        ?  nullptr : &func->arguments().constLast();

    // Write declaration/native injected code.
    if (!snips.isEmpty()) {
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionDeclaration,
                       TypeSystem::ShellCode, func, false, lastArg);
    }

    if (wrapperDiagnostics()) {
        s << "std::cerr << ";
#ifndef Q_CC_MSVC // g++ outputs __FUNCTION__ unqualified
        s << '"' << prefix << R"(" << )";
#endif
        s  << R"(__FUNCTION__ << ' ' << this << " m_PyMethodCache[" << )"
           << cacheIndex << R"( << "]=" << m_PyMethodCache[)" << cacheIndex
           << R"(] << '\n';)" << '\n';
    }
    // PYSIDE-803: Build a boolean cache for unused overrides
    const bool multi_line = func->isVoid() || !snips.isEmpty() || isAbstract;
    s << "if (m_PyMethodCache[" << cacheIndex << "])" << (multi_line ? " {\n" : "\n")
        << indent;
    writeVirtualMethodCppCall(s, func, funcName, snips, lastArg, retType,
                              returnStatement, false);
    s << outdent;
    if (multi_line)
        s << "}\n";

    s << "Shiboken::GilState gil;\n";

    // Get out of virtual method call if someone already threw an error.
    s << "if (PyErr_Occurred())\n" << indent
        << returnStatement << '\n' << outdent;

    // PYSIDE-1019: Add info about properties
    int propFlag = 0;
    if (func->isPropertyReader())
        propFlag |= 1;
    if (func->isPropertyWriter())
        propFlag |= 2;
    if (propFlag && func->isStatic())
        propFlag |= 4;
    QString propStr;
    if (propFlag)
        propStr = QString::number(propFlag) + u':';

    s << "static PyObject *nameCache[2] = {};\n";
    if (propFlag)
        s << "// This method belongs to a property.\n";
    s << "static const char *funcName = \"" << propStr << funcName << "\";\n"
        << "Shiboken::AutoDecRef " << PYTHON_OVERRIDE_VAR
        << "(Shiboken::BindingManager::instance().getOverride(this, nameCache, funcName));\n"
        << "if (" << PYTHON_OVERRIDE_VAR << ".isNull()) {\n" << indent;
    if (useOverrideCaching(func->ownerClass()))
        s << "m_PyMethodCache[" << cacheIndex << "] = true;\n";
    writeVirtualMethodCppCall(s, func, funcName, snips, lastArg, retType,
                              returnStatement, true);
    s << outdent << "}\n\n"; //WS

    writeConversionRule(s, func, TypeSystem::TargetLangCode, false);

    bool invalidateReturn = false;
    QList<int> invalidateArgs;
    for (const FunctionModification &funcMod : func->modifications()) {
        for (const ArgumentModification &argMod : funcMod.argument_mods()) {
            const int index = argMod.index();
            if (index == 0) {
                if (argMod.targetOwnerShip() == TypeSystem::CppOwnership)
                    invalidateReturn = true;
            } else {
                const int actualIndex = func->actualArgumentIndex(index - 1) + 1;
                if (argMod.resetAfterUse() && !invalidateArgs.contains(actualIndex))
                    invalidateArgs.append(actualIndex);
            }
        }
    }
    std::sort(invalidateArgs.begin(), invalidateArgs.end());

    auto arguments = func->arguments();
    auto removedEnd = std::stable_partition(arguments.begin(), arguments.end(),
                                            isArgumentNotRemoved);
    if (isAbstract) { // Base function is not called, indicate unused arguments.
        for (auto it = removedEnd; it != arguments.end(); ++it)
            s << sbkUnusedVariableCast(it->name());
    }
    arguments.erase(removedEnd, arguments.end());

    // FIXME PYSIDE-7: new functions PyObject_Vectorcall() (since 3.9) and
    // PyObject_CallNoArgs() (since 3.9, stable API since 3.10) might have
    // become part of the stable API?

    // Code snips might expect the args tuple, don't generate new code
    const bool generateNewCall = snips.isEmpty();
    const qsizetype argCount = arguments.size();
    const char *newCallCondition = argCount == 0 ? noArgsCallCondition : vectorCallCondition;
    if (generateNewCall) {
        if (argCount > 0) {
            s << newCallCondition;
            writeVirtualMethodNativeVectorCallArgs(s, func, arguments, invalidateArgs);
            s << "#else\n";
        } else {
            s << inverseNoArgsCallCondition;
        }
    }
    writeVirtualMethodNativeArgs(s, func, arguments, invalidateArgs);
    if (generateNewCall)
        s << "#endif\n";
    s << '\n';

    if (!snips.isEmpty()) {
        if (func->injectedCodeUsesPySelf())
            s << "PyObject *pySelf = BindingManager::instance().retrieveWrapper(this);\n";

        const AbstractMetaArgument *lastArg = func->arguments().isEmpty()
                                            ? nullptr : &func->arguments().constLast();
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionBeginning,
                       TypeSystem::NativeCode, func, false, lastArg);
    }

    qsizetype returnIndirections = 0;

    if (!func->injectedCodeCallsPythonOverride()) {
        if (generateNewCall) {
            s << newCallCondition << "Shiboken::AutoDecRef " << PYTHON_RETURN_VAR << '(';
            if (argCount > 0) {
                s << "PyObject_Vectorcall(" << PYTHON_OVERRIDE_VAR << ", "
                    << PYTHON_ARGS_ARRAY << ", " << argCount << ", nullptr));\n";
                for (int argIndex : qAsConst(invalidateArgs)) {
                    s << "if (invalidateArg" << argIndex << ")\n" << indent
                        << "Shiboken::Object::invalidate(" << PYTHON_ARGS_ARRAY
                        << '[' << (argIndex - 1) << "]);\n" << outdent;
                    }
                for (qsizetype i = 0, size = arguments.size(); i < size; ++i)
                    s << "Py_DECREF(" << PYTHON_ARGS_ARRAY << '[' << i << "]);\n";
            } else {
                s << "PyObject_CallNoArgs(" << PYTHON_OVERRIDE_VAR << "));\n";
            }
            s << "#else\n";
        }
        s << "Shiboken::AutoDecRef " << PYTHON_RETURN_VAR << "(PyObject_Call("
            << PYTHON_OVERRIDE_VAR << ", " << PYTHON_ARGS << ", nullptr));\n";

        for (int argIndex : std::as_const(invalidateArgs)) {
            s << "if (invalidateArg" << argIndex << ")\n" << indent
                << "Shiboken::Object::invalidate(PyTuple_GET_ITEM(" << PYTHON_ARGS
                << ", " << (argIndex - 1) << "));\n" << outdent;
        }
        if (generateNewCall)
            s << "#endif\n";

        s << "if (" << PYTHON_RETURN_VAR << ".isNull()) {\n" << indent
            << "// An error happened in python code!\n"
            << "Shiboken::Errors::storeError();\n"
            << returnStatement << "\n" << outdent
        << "}\n";

        if (invalidateReturn) {
            s << "bool invalidateArg0 = Py_REFCNT(" << PYTHON_RETURN_VAR << ") == 1;\n"
                << "if (invalidateArg0)\n" << indent
                << "Shiboken::Object::releaseOwnership(" << PYTHON_RETURN_VAR
                << ".object());\n" << outdent;
        }

        if (!func->isVoid()) {

            if (func->modifiedTypeName() != cPyObjectT()) {

                s << "// Check return type\n";

                if (!func->isTypeModified()) {

                    s << PYTHON_TO_CPPCONVERSION_STRUCT << ' '
                    << PYTHON_TO_CPP_VAR << " =\n" << indent
                        << cpythonIsConvertibleFunction(func->type())
                        << PYTHON_RETURN_VAR << ");\n" << outdent
                    << "if (!" << PYTHON_TO_CPP_VAR << ") {\n" << indent
                        << "Shiboken::Warnings::warnInvalidReturnValue(\""
                        << func->ownerClass()->name() << "\", \"" << funcName << "\", "
                        << getVirtualFunctionReturnTypeName(func) << ", "
                        << "Py_TYPE(" << PYTHON_RETURN_VAR << ")->tp_name);\n"
                        << returnStatement << '\n' << outdent
                    << "}\n";

                } else {

                    s << "bool typeIsValid = ";
                    if (func->isTypeModified()) {
                        writeTypeCheck(s, func->modifiedTypeName(), PYTHON_RETURN_VAR);
                    } else {
                        const bool numberType = isNumber(func->type().typeEntry());
                        writeTypeCheck(s, func->type(), PYTHON_RETURN_VAR, numberType);
                    }

                    s << ";\n";
                    s << "if (!typeIsValid";
                    if (func->type().isPointerToWrapperType())
                        s << " && " << PYTHON_RETURN_VAR << " != Py_None";
                    s << ") {\n" << indent
                        << "Shiboken::Warnings::warnInvalidReturnValue(\""
                        << func->ownerClass()->name() << "\", \"" << funcName << "\", "
                        << getVirtualFunctionReturnTypeName(func) << ", "
                        << "Py_TYPE(" << PYTHON_RETURN_VAR << ")->tp_name);\n"
                        << returnStatement << '\n' << outdent
                    << "}\n";

                }
            }

            if (func->hasConversionRule(TypeSystem::NativeCode, 0)) {
                writeConversionRule(s, func, TypeSystem::NativeCode, CPP_RETURN_VAR);
            } else if (!func->injectedCodeHasReturnValueAttribution(TypeSystem::NativeCode)) {
                returnIndirections = writePythonToCppTypeConversion(
                    s, func->type(), PYTHON_RETURN_VAR,
                    CPP_RETURN_VAR, func->implementingClass(), {});
            }
        }
    }

    for (const FunctionModification &funcMod : func->modifications()) {
        for (const ArgumentModification &argMod : funcMod.argument_mods()) {
            if (argMod.index() == 0
                && argMod.nativeOwnership() == TypeSystem::CppOwnership) {
                s << "if (Shiboken::Object::checkType(" << PYTHON_RETURN_VAR << "))\n" << indent
                    << "Shiboken::Object::releaseOwnership(" << PYTHON_RETURN_VAR << ");\n"
                    << outdent;
            }
        }
    }

    if (func->hasInjectedCode()) {
        s << '\n';
        const AbstractMetaArgument *lastArg = func->arguments().isEmpty()
                        ? nullptr : &func->arguments().constLast();
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionEnd,
                       TypeSystem::NativeCode, func, false, lastArg);
    }

    if (!func->isVoid()) {
        s << "return ";
        if (avoidProtectedHack() && retType->isEnum()) {
            auto metaEnum = api().findAbstractMetaEnum(retType);
            bool isProtectedEnum = metaEnum.has_value() && metaEnum->isProtected();
            if (isProtectedEnum) {
                QString typeCast;
                if (metaEnum->enclosingClass())
                    typeCast += u"::"_s + metaEnum->enclosingClass()->qualifiedCppName();
                typeCast += u"::"_s + metaEnum->name();
                s << '(' << typeCast << ')';
            }
        }

        if (returnIndirections > 0)
            s << QByteArray(returnIndirections, '*');
        s << CPP_RETURN_VAR << ";\n";
    }

    s << outdent << "}\n\n";
}

void CppGenerator::writeMetaObjectMethod(TextStream &s,
                                         const GeneratorContext &classContext) const
{

    const QString wrapperClassName = classContext.wrapperName();
    const QString qualifiedCppName = classContext.metaClass()->qualifiedCppName();
    s << "const QMetaObject *" << wrapperClassName << "::metaObject() const\n{\n";
    s << indent << "if (QObject::d_ptr->metaObject)\n"
        << indent << "return QObject::d_ptr->dynamicMetaObject();\n" << outdent
        << "SbkObject *pySelf = Shiboken::BindingManager::instance().retrieveWrapper(this);\n"
        << "if (pySelf == nullptr)\n"
        << indent << "return " << qualifiedCppName << "::metaObject();\n" << outdent
        << "return PySide::SignalManager::retrieveMetaObject("
                "reinterpret_cast<PyObject *>(pySelf));\n"
        << outdent << "}\n\n";

    // qt_metacall function
    s << "int " << wrapperClassName
        << "::qt_metacall(QMetaObject::Call call, int id, void **args)\n";
    s << "{\n" << indent;

    const auto list = classContext.metaClass()->queryFunctionsByName(u"qt_metacall"_s);

    CodeSnipList snips;
    if (list.size() == 1) {
        const auto &func = list.constFirst();
        snips = func->injectedCodeSnips();
        if (func->isUserAdded()) {
            CodeSnipList snips = func->injectedCodeSnips();
            const bool usePyArgs = pythonFunctionWrapperUsesListOfArguments(func);
            writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionAny,
                           TypeSystem::NativeCode, func, usePyArgs, nullptr);
        }
    }

    s << "int result = " << qualifiedCppName << "::qt_metacall(call, id, args);\n"
        << "return result < 0 ? result : PySide::SignalManager::qt_metacall("
                "this, call, id, args);\n"
        << outdent << "}\n\n";

    // qt_metacast function
    writeMetaCast(s, classContext);
}

void CppGenerator::writeMetaCast(TextStream &s,
                                 const GeneratorContext &classContext)
{
    const QString wrapperClassName = classContext.wrapperName();
    const QString qualifiedCppName = classContext.metaClass()->qualifiedCppName();
    s << "void *" << wrapperClassName << "::qt_metacast(const char *_clname)\n{\n"
        << indent << "if (!_clname)\n" << indent << "return {};\n" << outdent
        << "SbkObject *pySelf = Shiboken::BindingManager::instance().retrieveWrapper(this);\n"
        << "if (pySelf && PySide::inherits(Py_TYPE(pySelf), _clname))\n"
        << indent << "return static_cast<void *>(const_cast< "
        << wrapperClassName << " *>(this));\n" << outdent
        << "return " << qualifiedCppName << "::qt_metacast(_clname);\n"
        << outdent << "}\n\n";
}

void CppGenerator::writeFlagsConverterFunctions(TextStream &s,
                                                const FlagsTypeEntryCPtr &flagsType,
                                                const QString &enumTypeName,
                                                const QString &flagsCppTypeName,
                                                const QString &enumTypeCheck) const
{
    Q_ASSERT(flagsType);
    const QString flagsTypeName = fixedCppTypeName(flagsType);
    const QString flagsPythonType = cpythonTypeNameExt(flagsType);

    StringStream c(TextStream::Language::Cpp);
    c << "*reinterpret_cast<" << flagsCppTypeName << " *>(cppOut) =\n"
        << "    " << flagsCppTypeName
        << "(QFlag(int(PySide::QFlagsSupport::getValue(reinterpret_cast<PySideQFlagsObject *>(pyIn)))))"
        << ";\n";
    writePythonToCppFunction(s, c.toString(), flagsTypeName, flagsTypeName);

    QString pyTypeCheck = u"PyObject_TypeCheck(pyIn, "_s + flagsPythonType + u')';
    writeIsPythonConvertibleToCppFunction(s, flagsTypeName, flagsTypeName, pyTypeCheck);

    c.clear();

    c << "const int castCppIn = int(*reinterpret_cast<const "
        << flagsCppTypeName << " *>(cppIn));\n" << "return "
        << "reinterpret_cast<PyObject *>(PySide::QFlagsSupport::newObject(castCppIn, "
        << flagsPythonType << "));\n";
    writeCppToPythonFunction(s, c.toString(), flagsTypeName, flagsTypeName);
    s << '\n';

    c.clear();
    c << "*reinterpret_cast<" << flagsCppTypeName << " *>(cppOut) =\n"
      << "    " << flagsCppTypeName
      << "(QFlag(int(Shiboken::Enum::getValue(pyIn))));\n";

    writePythonToCppFunction(s, c.toString(), enumTypeName, flagsTypeName);
    writeIsPythonConvertibleToCppFunction(s, enumTypeName, flagsTypeName, enumTypeCheck);

    c.clear();
    c << "Shiboken::AutoDecRef pyLong(PyNumber_Long(pyIn));\n"
      << "*reinterpret_cast<" << flagsCppTypeName << " *>(cppOut) =\n"
      << "    " << flagsCppTypeName
      << "(QFlag(int(PyLong_AsLong(pyLong.object()))));\n";
    // PYSIDE-898: Include an additional condition to detect if the type of the
    // enum corresponds to the object that is being evaluated.
    // Using only `PyNumber_Check(...)` is too permissive,
    // then we would have been unable to detect the difference between
    // a PolarOrientation and Qt::AlignmentFlag, which was the main
    // issue of the bug.
    const QString numberCondition = u"PyNumber_Check(pyIn) && "_s + enumTypeCheck;
    writePythonToCppFunction(s, c.toString(), u"number"_s, flagsTypeName);
    writeIsPythonConvertibleToCppFunction(s, u"number"_s, flagsTypeName, numberCondition);
}

static void generateDeprecatedValueWarnings(TextStream &c,
                                            const AbstractMetaEnum &metaEnum,
                                            bool useSurrogateName)
{
    EnumTypeEntryCPtr enumType = metaEnum.typeEntry();
    const QString prefix = enumType->qualifiedCppName() + u"::"_s;
    c << "switch (value) {\n";
    const auto &deprecatedValues = metaEnum.deprecatedValues();
    for (const auto &v : deprecatedValues) {
        c << "case ";
        if (useSurrogateName)
            c << v.value().toString(); // Protected, use int representation
        else
            c << prefix << v.name();
        c << ":\n" << indent
            << "Shiboken::Warnings::warnDeprecatedEnumValue(\"" << enumType->name()
            << "\", \"" << v.name() << "\");\nbreak;\n" << outdent;
    }
    if (deprecatedValues.size() < metaEnum.values().size())
        c << "default:\n" << indent << "break;\n" << outdent << "}\n";
}

void CppGenerator::writeEnumConverterFunctions(TextStream &s, const AbstractMetaEnum &metaEnum) const
{
    if (metaEnum.isPrivate() || metaEnum.isAnonymous())
        return;
    EnumTypeEntryPtr enumType = metaEnum.typeEntry();
    Q_ASSERT(enumType);
    QString typeName = fixedCppTypeName(enumType);
    QString enumPythonType = cpythonTypeNameExt(enumType);
    const bool useSurrogateName = avoidProtectedHack() && metaEnum.isProtected();
    QString cppTypeName = useSurrogateName
        ? protectedEnumSurrogateName(metaEnum) : getFullTypeName(enumType).trimmed();

    StringStream c(TextStream::Language::Cpp);
    if (metaEnum.isDeprecated())
        c << "Shiboken::Warnings::warnDeprecatedEnum(\"" << enumType->name() << "\");\n";

    c << "const auto value = static_cast<" << cppTypeName
        << ">(Shiboken::Enum::getValue(pyIn));\n";

    // Warn about deprecated values unless it is protected+scoped (inaccessible values)
    const bool valuesAcccessible = !useSurrogateName || metaEnum.enumKind() != EnumClass;
    if (valuesAcccessible && metaEnum.hasDeprecatedValues())
        generateDeprecatedValueWarnings(c, metaEnum, useSurrogateName);

    c << "*reinterpret_cast<" << cppTypeName << " *>(cppOut) = value;\n";
    writePythonToCppFunction(s, c.toString(), typeName, typeName);

    QString pyTypeCheck = u"PyObject_TypeCheck(pyIn, "_s + enumPythonType + u')';
    writeIsPythonConvertibleToCppFunction(s, typeName, typeName, pyTypeCheck);

    c.clear();

    c << "const int castCppIn = int(*reinterpret_cast<const "
        << cppTypeName << " *>(cppIn));\n" << "return "
        << "Shiboken::Enum::newItem(" << enumPythonType << ", castCppIn);\n";
    writeCppToPythonFunction(s, c.toString(), typeName, typeName);
    s << '\n';

    // QFlags part.
    if (auto flags = enumType->flags()) {
        const QString flagsCppTypeName = useSurrogateName
            ? cppTypeName : getFullTypeName(flags).trimmed();
        writeFlagsConverterFunctions(s, flags, typeName, flagsCppTypeName, pyTypeCheck);
    }
}

void CppGenerator::writeConverterFunctions(TextStream &s, const AbstractMetaClassCPtr &metaClass,
                                           const GeneratorContext &classContext) const
{
    s << "// Type conversion functions.\n\n";

    AbstractMetaEnumList classEnums = metaClass->enums();
    auto typeEntry = metaClass->typeEntry();
    metaClass->getEnumsFromInvisibleNamespacesToBeGenerated(&classEnums);
    if (!classEnums.isEmpty())
        s << "// Python to C++ enum conversion.\n";
    for (const AbstractMetaEnum &metaEnum : std::as_const(classEnums))
        writeEnumConverterFunctions(s, metaEnum);

    if (metaClass->isNamespace())
        return;

    QString typeName;
    if (!classContext.forSmartPointer())
        typeName = getFullTypeName(metaClass);
    else
        typeName = getFullTypeName(classContext.preciseType());

    QString cpythonType = cpythonTypeName(metaClass);

    // Returns the C++ pointer of the Python wrapper.
    s << "// Python to C++ pointer conversion - returns the C++ object of the Python wrapper (keeps object identity).\n";

    QString sourceTypeName = metaClass->name();
    QString targetTypeName = metaClass->name() + u"_PTR"_s;
    StringStream c(TextStream::Language::Cpp);
    c << "Shiboken::Conversions::pythonToCppPointer(" << cpythonType << ", pyIn, cppOut);";
    writePythonToCppFunction(s, c.toString(), sourceTypeName, targetTypeName);

    // "Is convertible" function for the Python object to C++ pointer conversion.
    const QString pyTypeCheck = u"PyObject_TypeCheck(pyIn, "_s + cpythonType + u")"_s;
    writeIsPythonConvertibleToCppFunction(s, sourceTypeName, targetTypeName, pyTypeCheck, QString(), true);
    s << '\n';

    // C++ pointer to a Python wrapper, keeping identity.
    s << "// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).\n";
    c.clear();
    if (usePySideExtensions() && isQObject(metaClass)) {
        c << "return PySide::getWrapperForQObject(reinterpret_cast<"
            << typeName << " *>(const_cast<void *>(cppIn)), " << cpythonType << ");\n";
    } else {
        c << "auto pyOut = reinterpret_cast<PyObject *>(Shiboken::BindingManager::instance().retrieveWrapper(cppIn));\n"
            << "if (pyOut) {\n" << indent
            << "Py_INCREF(pyOut);\nreturn pyOut;\n" << outdent
            << "}\n"
            << "bool changedTypeName = false;\n"
            << "auto tCppIn = reinterpret_cast<const " << typeName << R"( *>(cppIn);
const char *typeName = )";

        const QString nameFunc = metaClass->typeEntry()->polymorphicNameFunction();
        if (nameFunc.isEmpty())
            c << "typeid(*tCppIn).name();\n";
        else
            c << nameFunc << "(tCppIn);\n";
        c << R"(auto sbkType = Shiboken::ObjectType::typeForTypeName(typeName);
if (sbkType && Shiboken::ObjectType::hasSpecialCastFunction(sbkType)) {
    typeName = Shiboken::typeNameOf(typeid(*tCppIn).name());
    changedTypeName = true;
}
)"
            << "PyObject *result = Shiboken::Object::newObject(" << cpythonType
            << R"(, const_cast<void *>(cppIn), false, /* exactType */ changedTypeName, typeName);
if (changedTypeName)
    delete [] typeName;
return result;)";
    }
    std::swap(targetTypeName, sourceTypeName);
    writeCppToPythonFunction(s, c.toString(), sourceTypeName, targetTypeName);

    // The conversions for an Object Type end here.
    if (!typeEntry->isValue() && !typeEntry->isSmartPointer()) {
        s << '\n';
        return;
    }

    // Always copies C++ value (not pointer, and not reference) to a new Python wrapper.
    s  << '\n' << "// C++ to Python copy conversion.\n";
    targetTypeName = metaClass->name();

    sourceTypeName = targetTypeName + u"_COPY"_s;

    c.clear();

    const bool isUniquePointer = classContext.forSmartPointer()
        && typeEntry->isUniquePointer();

    if (isUniquePointer) {
        c << "auto *source = reinterpret_cast<" << typeName
            << " *>(const_cast<void *>(cppIn));\n";
    } else {
        c << "auto *source = reinterpret_cast<const " << typeName << " *>(cppIn);\n";
    }
    c << "return Shiboken::Object::newObject(" << cpythonType
        << ", new ::" << classContext.effectiveClassName() << '('
        << (isUniquePointer ? "std::move(*source)" : "*source")
        << "), true, true);";
    writeCppToPythonFunction(s, c.toString(), sourceTypeName, targetTypeName);
    s << '\n';

    // Python to C++ copy conversion.
    s << "// Python to C++ copy conversion.\n";
    sourceTypeName = metaClass->name();

    targetTypeName = sourceTypeName + QStringLiteral("_COPY");
    c.clear();

    QString pyInVariable = u"pyIn"_s;
    const QString outPtr = u"reinterpret_cast<"_s + typeName + u" *>(cppOut)"_s;
    if (!classContext.forSmartPointer()) {
        c << '*' << outPtr << " = *"
            << cpythonWrapperCPtr(typeEntry, pyInVariable) << ';';
    } else {
        auto ste = std::static_pointer_cast<const SmartPointerTypeEntry>(typeEntry);
        const QString resetMethod = ste->resetMethod();
        c << "auto *ptr = " << outPtr << ";\n";
        c << "if (" << pyInVariable << " == Py_None)\n" << indent;
        if (resetMethod.isEmpty())
            c << "*ptr = {};\n";
        else
            c << "ptr->" << resetMethod << "();\n";
        const QString value = u'*' + cpythonWrapperCPtr(classContext.preciseType(), pyInVariable);
        c << outdent << "else\n" << indent
            << "*ptr = " << (isUniquePointer ? stdMove(value) : value) << ';';
    }

    writePythonToCppFunction(s, c.toString(), sourceTypeName, targetTypeName);

    // "Is convertible" function for the Python object to C++ value copy conversion.
    QString copyTypeCheck = pyTypeCheck;
    if (classContext.forSmartPointer())
        copyTypeCheck.prepend(pyInVariable + u" == Py_None || "_s);
    writeIsPythonConvertibleToCppFunction(s, sourceTypeName, targetTypeName, copyTypeCheck);
    s << '\n';

    // User provided implicit conversions.
    // Implicit conversions.
    const AbstractMetaFunctionCList implicitConvs = implicitConversions(typeEntry);

    if (!implicitConvs.isEmpty())
        s << "// Implicit conversions.\n";

    AbstractMetaType targetType = AbstractMetaType::fromAbstractMetaClass(metaClass);
    for (const auto &conv : std::as_const(implicitConvs)) {
        if (conv->isModifiedRemoved())
            continue;

        QString typeCheck;
        QString toCppConv;
        QString toCppPreConv;
        if (conv->isConversionOperator()) {
            const auto sourceClass = conv->ownerClass();
            typeCheck = u"PyObject_TypeCheck(pyIn, "_s
                        + cpythonTypeNameExt(sourceClass->typeEntry()) + u')';
            toCppConv = u'*' + cpythonWrapperCPtr(sourceClass->typeEntry(),
                                                  pyInVariable);
        } else {
            // Constructor that does implicit conversion.
            const auto &firstArg = conv->arguments().constFirst();
            if (firstArg.isTypeModified() || conv->isModifiedToArray(1))
                continue;
            const AbstractMetaType &sourceType = firstArg.type();
            if (sourceType.isWrapperType()) {
                if (sourceType.referenceType() == LValueReference
                    || !sourceType.isPointerToWrapperType()) {
                    toCppConv = u" *"_s;
                }
                toCppConv += cpythonWrapperCPtr(sourceType.typeEntry(), pyInVariable);
            }

            typeCheck = cpythonCheckFunction(sourceType);
            if (typeCheck.endsWith(u", ")) {
                typeCheck += pyInVariable + u')';
            } else if (typeCheck != u"true" && typeCheck != u"false") {
                typeCheck += u'(' + pyInVariable + u')';
            }

            if (sourceType.isUserPrimitive()
                || sourceType.isExtendedCppPrimitive()
                || sourceType.typeEntry()->isContainer()
                || sourceType.typeEntry()->isEnum()
                || sourceType.typeEntry()->isFlags()) {
                StringStream pc(TextStream::Language::Cpp);
                pc << getFullTypeNameWithoutModifiers(sourceType) << " cppIn"
                    << minimalConstructorExpression(api(), sourceType) << ";\n";
                writeToCppConversion(pc, sourceType, nullptr, pyInVariable,
                                     u"cppIn"_s);
                pc << ';';
                toCppPreConv = pc.toString();
                toCppConv.append(u"cppIn"_s);
            } else if (!sourceType.isWrapperType()) {
                StringStream tcc(TextStream::Language::Cpp);
                writeToCppConversion(tcc, sourceType, metaClass, pyInVariable,
                                     u"/*BOZO-1061*/"_s);
                toCppConv = tcc.toString();
            }
        }
        const AbstractMetaType sourceType = conv->isConversionOperator()
                                            ? AbstractMetaType::fromAbstractMetaClass(conv->ownerClass())
                                            : conv->arguments().constFirst().type();
        writePythonToCppConversionFunctions(s, sourceType, targetType, typeCheck, toCppConv, toCppPreConv);
    }

    if (typeEntry->isValue()) {
        auto vte = std::static_pointer_cast<const ValueTypeEntry>(typeEntry);
        writeCustomConverterFunctions(s, vte->customConversion());
    }
}

void CppGenerator::writeCustomConverterFunctions(TextStream &s,
                                                 const CustomConversionPtr &customConversion) const
{
    if (!customConversion)
        return;
    const TargetToNativeConversions &toCppConversions = customConversion->targetToNativeConversions();
    if (toCppConversions.isEmpty())
        return;
    auto ownerType = customConversion->ownerType();
    s << "// Python to C++ conversions for type '" << ownerType->qualifiedCppName() << "'.\n";
    for (const auto &toNative : toCppConversions)
        writePythonToCppConversionFunctions(s, toNative, ownerType);
    s << '\n';
}

void CppGenerator::writeConverterRegister(TextStream &s, const AbstractMetaClassCPtr &metaClass,
                                          const GeneratorContext &classContext) const
{
    const auto typeEntry = metaClass->typeEntry();
    if (typeEntry->isNamespace())
        return;
    s << "// Register Converter\n"
        << "SbkConverter *converter = Shiboken::Conversions::createConverter(pyType,\n"
        << indent;
    QString sourceTypeName = metaClass->name();
    QString targetTypeName = sourceTypeName + u"_PTR"_s;
    s << pythonToCppFunctionName(sourceTypeName, targetTypeName) << ',' << '\n'
        << convertibleToCppFunctionName(sourceTypeName, targetTypeName) << ',' << '\n';
    std::swap(targetTypeName, sourceTypeName);
    s << cppToPythonFunctionName(sourceTypeName, targetTypeName);
    if (typeEntry->isValue() || typeEntry->isSmartPointer()) {
        s << ',' << '\n';
        sourceTypeName = metaClass->name() + u"_COPY"_s;
        s << cppToPythonFunctionName(sourceTypeName, targetTypeName);
    }
    s << outdent << ");\n\n";

    auto writeConversions = [&s](const QString &signature)
    {
        s << "Shiboken::Conversions::registerConverterName(converter, \"" << signature << "\");\n"
            << "Shiboken::Conversions::registerConverterName(converter, \"" << signature << "*\");\n"
            << "Shiboken::Conversions::registerConverterName(converter, \"" << signature << "&\");\n";
    };

    auto writeConversionsForType = [writeConversions](const QString &fullTypeName)
    {
        QStringList lst = fullTypeName.split(u"::"_s,
                                               Qt::SkipEmptyParts);
        while (!lst.isEmpty()) {
            QString signature = lst.join(u"::"_s);
            writeConversions(signature);
            lst.removeFirst();
        }
    };


    if (!classContext.forSmartPointer()) {
        writeConversionsForType(metaClass->qualifiedCppName());
    } else {
        const QString &smartPointerType = classContext.preciseType().instantiations().at(0).cppSignature();
        const QString &smartPointerName = classContext.preciseType().typeEntry()->name();

        QStringList lst = smartPointerType.split(u"::"_s,
                                               Qt::SkipEmptyParts);
        while (!lst.isEmpty()) {
            QString signature = lst.join(u"::"_s);
            writeConversions(smartPointerName + u'<' + signature + u" >"_s);
            lst.removeFirst();
        }

        writeConversionsForType(smartPointerType);
    }

    s << "Shiboken::Conversions::registerConverterName(converter, typeid(::";
    QString qualifiedCppNameInvocation;
    if (!classContext.forSmartPointer())
        qualifiedCppNameInvocation = metaClass->qualifiedCppName();
    else
        qualifiedCppNameInvocation = classContext.preciseType().cppSignature();

    s << qualifiedCppNameInvocation << ").name());\n";

    if (classContext.useWrapper()) {
        s << "Shiboken::Conversions::registerConverterName(converter, typeid(::"
            << classContext.wrapperName() << ").name());\n";
    }

    s << '\n';

    if (!typeEntry->isValue() && !typeEntry->isSmartPointer())
        return;

    // Python to C++ copy (value, not pointer neither reference) conversion.
    s << "// Add Python to C++ copy (value, not pointer neither reference) conversion to type converter.\n";
    sourceTypeName = metaClass->name();
    targetTypeName = sourceTypeName + u"_COPY"_s;
    QString toCpp = pythonToCppFunctionName(sourceTypeName, targetTypeName);
    QString isConv = convertibleToCppFunctionName(sourceTypeName, targetTypeName);
    writeAddPythonToCppConversion(s, u"converter"_s, toCpp, isConv);

    // User provided implicit conversions.

    // Add implicit conversions.
    const AbstractMetaFunctionCList implicitConvs = implicitConversions(typeEntry);

    if (!implicitConvs.isEmpty())
        s << "// Add implicit conversions to type converter.\n";

    AbstractMetaType targetType = AbstractMetaType::fromAbstractMetaClass(metaClass);
    for (const auto &conv : std::as_const(implicitConvs)) {
        if (conv->isModifiedRemoved())
            continue;
        AbstractMetaType sourceType;
        if (conv->isConversionOperator()) {
            sourceType = AbstractMetaType::fromAbstractMetaClass(conv->ownerClass());
        } else {
            // Constructor that does implicit conversion.
            const auto &firstArg = conv->arguments().constFirst();
            if (firstArg.isTypeModified() || conv->isModifiedToArray(1))
                continue;
            sourceType = firstArg.type();
        }
        QString toCpp = pythonToCppFunctionName(sourceType, targetType);
        QString isConv = convertibleToCppFunctionName(sourceType, targetType);
        writeAddPythonToCppConversion(s, u"converter"_s, toCpp, isConv);
    }

    if (typeEntry->isValue()) {
        auto vte = std::static_pointer_cast<const ValueTypeEntry>(typeEntry);
        writeCustomConverterRegister(s, vte->customConversion(), u"converter"_s);
    }
}

void CppGenerator::writeCustomConverterRegister(TextStream &s,
                                                const CustomConversionPtr &customConversion,
                                                const QString &converterVar)
{
    if (!customConversion)
        return;
    const TargetToNativeConversions &toCppConversions =
        customConversion->targetToNativeConversions();
    if (toCppConversions.isEmpty())
        return;
    s << "// Add user defined implicit conversions to type converter.\n";
    for (const auto &toNative : toCppConversions) {
        QString toCpp = pythonToCppFunctionName(toNative, customConversion->ownerType());
        QString isConv = convertibleToCppFunctionName(toNative, customConversion->ownerType());
        writeAddPythonToCppConversion(s, converterVar, toCpp, isConv);
    }
}

void CppGenerator::writeContainerConverterFunctions(TextStream &s,
                                                    const AbstractMetaType &containerType) const
{
    writeCppToPythonFunction(s, containerType);
    writePythonToCppConversionFunctions(s, containerType);
}

// Helpers to collect all smart pointer pointee base classes
static AbstractMetaClassCList findSmartPointeeBaseClasses(const ApiExtractorResult &api,
                                                          const AbstractMetaType &smartPointerType)
{
    AbstractMetaClassCList result;
    auto instantiationsTe = smartPointerType.instantiations().at(0).typeEntry();
    auto targetClass = AbstractMetaClass::findClass(api.classes(), instantiationsTe);
    if (targetClass != nullptr)
        result = targetClass->allTypeSystemAncestors();
    return result;
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
            if (auto opt = findSmartPointerInstantiation(smartPointerTypeEntry, baseTe)) {
                const auto smartTargetType = opt.value();
                s << "// SmartPointer derived class: "
                    << smartTargetType.cppSignature() << "\n";
                writePythonToCppConversionFunctions(s, smartPointerType,
                                                    smartTargetType, {}, {}, {});
            }
        }
    }
}

bool CppGenerator::needsArgumentErrorHandling(const OverloadData &overloadData) const
{
    if (overloadData.maxArgs() > 0)
        return true;
    // QObject constructors need error handling when passing properties as kwarg.
    if (!usePySideExtensions())
        return false;
    auto rfunc = overloadData.referenceFunction();
    return rfunc->functionType() == AbstractMetaFunction::ConstructorFunction
        && isQObject(rfunc->ownerClass());
}

void CppGenerator::writeMethodWrapperPreamble(TextStream &s,const OverloadData &overloadData,
                                              const GeneratorContext &context,
                                              ErrorReturn errorReturn) const
{
    const auto rfunc = overloadData.referenceFunction();
    const auto ownerClass = rfunc->targetLangOwner();
    Q_ASSERT(ownerClass == context.metaClass());
    int minArgs = overloadData.minArgs();
    int maxArgs = overloadData.maxArgs();
    bool initPythonArguments;

    // If method is a constructor...
    if (rfunc->isConstructor()) {
        // Check if the right constructor was called.
        if (!ownerClass->hasPrivateDestructor()) {
            s << "if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::";
            QString qualifiedCppName;
            if (!context.forSmartPointer())
                qualifiedCppName = ownerClass->qualifiedCppName();
            else
                qualifiedCppName = context.preciseType().cppSignature();

            s << qualifiedCppName << " >()))\n" << indent << errorReturn << outdent << '\n';
        }
        // Declare pointer for the underlying C++ object.
        s << "::" << context.effectiveClassName() << " *cptr{};\n";

        initPythonArguments = maxArgs > 0;

    } else {
        if (rfunc->implementingClass() &&
            (!rfunc->implementingClass()->isNamespace() && overloadData.hasInstanceFunction())) {
            CppSelfDefinitionFlags flags;
            if (overloadData.hasStaticFunction())
                flags.setFlag(CppSelfDefinitionFlag::HasStaticOverload);
            if (overloadData.hasClassMethod())
                flags.setFlag(CppSelfDefinitionFlag::HasClassMethodOverload);
            writeCppSelfDefinition(s, rfunc, context, errorReturn, flags);
        }
        if (!rfunc->isInplaceOperator() && overloadData.hasNonVoidReturnType())
            s << "PyObject *" << PYTHON_RETURN_VAR << "{};\n";

        initPythonArguments = minArgs != maxArgs || maxArgs > 1;
    }

    if (needsArgumentErrorHandling(overloadData)) {
        s << R"(Shiboken::AutoDecRef errInfo{};
static const char fullName[] = ")" << fullPythonFunctionName(rfunc, true)
            << "\";\nSBK_UNUSED(fullName)\n";
    }
    if (maxArgs > 0) {
        s << "int overloadId = -1;\n"
            << PYTHON_TO_CPPCONVERSION_STRUCT << ' ' << PYTHON_TO_CPP_VAR;
        if (overloadData.pythonFunctionWrapperUsesListOfArguments())
            s << '[' << maxArgs << ']';
        s << ";\n" << sbkUnusedVariableCast(PYTHON_TO_CPP_VAR);
    }

    if (initPythonArguments) {
        s << "const Py_ssize_t numArgs = ";
        if (minArgs == 0 && maxArgs == 1 && !rfunc->isConstructor()
            && !overloadData.pythonFunctionWrapperUsesListOfArguments()) {
            s << "(" << PYTHON_ARG << " == 0 ? 0 : 1);\n";
        } else {
            writeArgumentsInitializer(s, overloadData, errorReturn);
        }
    }
}

void CppGenerator::writeConstructorWrapper(TextStream &s, const OverloadData &overloadData,
                                           const GeneratorContext &classContext) const
{
    const ErrorReturn errorReturn = ErrorReturn::MinusOne;

    const auto rfunc = overloadData.referenceFunction();
    const auto metaClass = rfunc->ownerClass();

    s << "static int\n";
    s << cpythonFunctionName(rfunc)
        << "(PyObject *self, PyObject *args, PyObject *kwds)\n{\n" << indent;
    if (overloadData.maxArgs() == 0 || metaClass->isAbstract())
        s << sbkUnusedVariableCast(u"args"_s);
    s << sbkUnusedVariableCast(u"kwds"_s);

    const bool needsMetaObject = usePySideExtensions() && isQObject(metaClass);
    if (needsMetaObject)
        s << "const QMetaObject *metaObject;\n";

    s << "SbkObject *sbkSelf = reinterpret_cast<SbkObject *>(self);\n";

    if (metaClass->isAbstract() || metaClass->baseClassNames().size() > 1) {
        s << "PyTypeObject *type = self->ob_type;\n"
            << "PyTypeObject *myType = "
            << cpythonTypeNameExt(metaClass->typeEntry()) << ";\n";
    }

    if (metaClass->isAbstract()) {
        // C++ Wrapper disabled: Abstract C++ class cannot be instantiated.
        if (metaClass->typeEntry()->typeFlags().testFlag(ComplexTypeEntry::DisableWrapper)) {
            s << sbkUnusedVariableCast(u"sbkSelf"_s)
                << sbkUnusedVariableCast(u"type"_s)
                << sbkUnusedVariableCast(u"myType"_s);
            if (needsMetaObject)
                s << sbkUnusedVariableCast(u"metaObject"_s);
            s << "Shiboken::Errors::setInstantiateAbstractClassDisabledWrapper(\""
                << metaClass->qualifiedCppName() << "\");\n" << errorReturn << outdent
                << "}\n\n";
            return;
        }

        // Refuse to instantiate Abstract C++ class (via C++ Wrapper) unless it is
        // a Python-derived class for which type != myType.
        s << "if (type == myType) {\n" << indent
            << "Shiboken::Errors::setInstantiateAbstractClass(\"" << metaClass->qualifiedCppName()
            << "\");\n" << errorReturn << outdent
            << "}\n\n";
    }

    if (metaClass->baseClassNames().size() > 1) {
        if (!metaClass->isAbstract())
            s << "if (type != myType)\n" << indent;
        s << "Shiboken::ObjectType::copyMultipleInheritance(type, myType);\n";
        if (!metaClass->isAbstract())
            s << outdent << '\n';
    }

    // PYSIDE-1478: Switching must also happen at object creation time.
    if (usePySideExtensions() && !classContext.forSmartPointer())
        s << "PySide::Feature::Select(self);\n";

    writeMethodWrapperPreamble(s, overloadData, classContext, errorReturn);

    s << '\n';

    if (overloadData.maxArgs() > 0)
        writeOverloadedFunctionDecisor(s, overloadData);

    writeFunctionCalls(s, overloadData, classContext, errorReturn);
    s << '\n';

    const QString typeName = classContext.forSmartPointer()
        ? classContext.preciseType().cppSignature() : metaClass->qualifiedCppName();
    s << "if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::"
        << typeName << " >(), cptr)) {\n"
        <<  indent << "delete cptr;\n" << errorReturn << outdent
        << "}\n";
    if (overloadData.maxArgs() > 0)
        s << "if (!cptr) goto " << cpythonFunctionName(rfunc) << "_TypeError;\n\n";

    s << "Shiboken::Object::setValidCpp(sbkSelf, true);\n";
    // If the created C++ object has a C++ wrapper the ownership is assigned to Python
    // (first "1") and the flag indicating that the Python wrapper holds an C++ wrapper
    // is marked as true (the second "1"). Otherwise the default values apply:
    // Python owns it and C++ wrapper is false.
    if (shouldGenerateCppWrapper(overloadData.referenceFunction()->ownerClass()))
        s << "Shiboken::Object::setHasCppWrapper(sbkSelf, true);\n";
    // Need to check if a wrapper for same pointer is already registered
    // Caused by bug PYSIDE-217, where deleted objects' wrappers are not released
    s << "if (Shiboken::BindingManager::instance().hasWrapper(cptr)) {\n" << indent
        << "Shiboken::BindingManager::instance().releaseWrapper("
           "Shiboken::BindingManager::instance().retrieveWrapper(cptr));\n" << outdent
        << "}\nShiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);\n";

    // Create metaObject and register signal/slot
    if (needsMetaObject) {
        s << "\n// QObject setup\n"
            << "PySide::Signal::updateSourceObject(self);\n"
            << "metaObject = cptr->metaObject(); // <- init python qt properties\n"
            << "if (!errInfo.isNull() && PyDict_Check(errInfo.object())) {\n" << indent
                << "if (!PySide::fillQtProperties(self, metaObject, errInfo))\n" << indent
                    << "goto " << cpythonFunctionName(rfunc) << "_TypeError;\n" << outdent << outdent
            << "};\n";
    }

    // Constructor code injections, position=end
    bool hasCodeInjectionsAtEnd = false;
    for (const auto &func : overloadData.overloads()) {
        const CodeSnipList &injectedCodeSnips = func->injectedCodeSnips();
        for (const CodeSnip &cs : injectedCodeSnips) {
            if (cs.position == TypeSystem::CodeSnipPositionEnd) {
                hasCodeInjectionsAtEnd = true;
                break;
            }
        }
    }
    if (hasCodeInjectionsAtEnd) {
        // FIXME: C++ arguments are not available in code injection on constructor when position = end.
        s << "switch (overloadId) {\n";
        for (const auto &func : overloadData.overloads()) {
            s << indent;
            const CodeSnipList &injectedCodeSnips = func->injectedCodeSnips();
            for (const CodeSnip &cs : injectedCodeSnips) {
                if (cs.position == TypeSystem::CodeSnipPositionEnd) {
                    s << "case " << metaClass->functions().indexOf(func) << ':' << '\n'
                        << "{\n" << indent;
                    writeCodeSnips(s, func->injectedCodeSnips(), TypeSystem::CodeSnipPositionEnd,
                                   TypeSystem::TargetLangCode, func,
                                   true /* usesPyArgs */, nullptr);
                    s << outdent << "}\nbreak;\n";
                    break;
                }
            }
            s << outdent;
        }
        s << "}\n";
    }

    s << "\n\nreturn 1;\n";
    if (needsArgumentErrorHandling(overloadData))
        writeErrorSection(s, overloadData, errorReturn);
    s<< outdent << "}\n\n";
}

void CppGenerator::writeMethodWrapper(TextStream &s, const OverloadData &overloadData,
                                      const GeneratorContext &classContext) const
{
    const auto rfunc = overloadData.referenceFunction();

    int maxArgs = overloadData.maxArgs();

    s << "static PyObject *";
    s << cpythonFunctionName(rfunc) << "(PyObject *self";
    bool hasKwdArgs = false;
    if (maxArgs > 0) {
        s << ", PyObject *"
            << (overloadData.pythonFunctionWrapperUsesListOfArguments() ? u"args"_s : PYTHON_ARG);
        hasKwdArgs = overloadData.hasArgumentWithDefaultValue() || rfunc->isCallOperator();
        if (hasKwdArgs)
            s << ", PyObject *kwds";
    }
    s << ")\n{\n" << indent;
    if (rfunc->ownerClass() == nullptr || overloadData.hasStaticFunction())
        s << sbkUnusedVariableCast(u"self"_s);
    if (hasKwdArgs)
        s << sbkUnusedVariableCast(u"kwds"_s);

    writeMethodWrapperPreamble(s, overloadData, classContext);

    s << '\n';

    // This code is intended for shift operations only: Make sure reverse <</>>
    // operators defined in other classes (specially from other modules)
    // are called. A proper and generic solution would require an reengineering
    // in the operator system like the extended converters.
    // Solves #119 - QDataStream <</>> operators not working for QPixmap.
    const bool hasReturnValue = overloadData.hasNonVoidReturnType();

    if (hasReturnValue && rfunc->functionType() == AbstractMetaFunction::ShiftOperator
        && rfunc->isBinaryOperator()) {
        // For custom classes, operations like __radd__ and __rmul__
        // will enter an infinite loop.
        const QString pythonOp = ShibokenGenerator::pythonOperatorFunctionName(rfunc);
        s << "static PyObject *attrName = Shiboken::PyMagicName::r"
            << pythonOp.mid(2, pythonOp.size() -4) << "();\n" // Strip __
            << "if (!isReverse\n" << indent
            << "&& Shiboken::Object::checkType(" << PYTHON_ARG << ")\n"
            << "&& !PyObject_TypeCheck(" << PYTHON_ARG << ", self->ob_type)\n"
            << "&& PyObject_HasAttr(" << PYTHON_ARG << ", attrName)) {\n"
            << "PyObject *revOpMethod = PyObject_GetAttr(" << PYTHON_ARG << ", attrName);\n"
            << "if (revOpMethod && PyCallable_Check(revOpMethod)) {\n" << indent
            << PYTHON_RETURN_VAR << " = PyObject_CallFunction(revOpMethod, \"O\", self);\n"
            << "if (PyErr_Occurred() && (PyErr_ExceptionMatches(PyExc_NotImplementedError)"
            << " || PyErr_ExceptionMatches(PyExc_AttributeError))) {\n" << indent
            << "PyErr_Clear();\n"
            << "Py_XDECREF(" << PYTHON_RETURN_VAR << ");\n"
            << PYTHON_RETURN_VAR << " = " << NULL_PTR << ";\n"
            << outdent << "}\n"
            << outdent << "}\n"
            << "Py_XDECREF(revOpMethod);\n\n"
            << outdent << "}\n\n"
            << "// Do not enter here if other object has implemented a reverse operator.\n"
            << "if (!" << PYTHON_RETURN_VAR << ") {\n" << indent;
        if (maxArgs > 0)
            writeOverloadedFunctionDecisor(s, overloadData);
        writeFunctionCalls(s, overloadData, classContext, ErrorReturn::Default);
        s  << outdent << '\n' << "} // End of \"if (!" << PYTHON_RETURN_VAR << ")\"\n";
    } else { // binary shift operator
        if (maxArgs > 0)
            writeOverloadedFunctionDecisor(s, overloadData);
        writeFunctionCalls(s, overloadData, classContext, ErrorReturn::Default);
    }

    s << '\n';

    writeFunctionReturnErrorCheckSection(s, ErrorReturn::Default,
                                         hasReturnValue && !rfunc->isInplaceOperator());

    if (hasReturnValue) {
        if (rfunc->isInplaceOperator()) {
            s << "Py_INCREF(self);\nreturn self;\n";
        } else {
            s << "return " << PYTHON_RETURN_VAR << ";\n";
        }
    } else {
        s << "Py_RETURN_NONE;\n";
    }

    if (needsArgumentErrorHandling(overloadData))
        writeErrorSection(s, overloadData, ErrorReturn::Default);

    s<< outdent << "}\n\n";
}

void CppGenerator::writeArgumentsInitializer(TextStream &s, const OverloadData &overloadData,
                                             ErrorReturn errorReturn)
{
    const auto rfunc = overloadData.referenceFunction();
    s << "PyTuple_GET_SIZE(args);\n" << sbkUnusedVariableCast(u"numArgs"_s);

    int minArgs = overloadData.minArgs();
    int maxArgs = overloadData.maxArgs();

    s << "PyObject *";
    s << PYTHON_ARGS << "[] = {"
        << QByteArrayList(maxArgs, "nullptr").join(", ")
        << "};\n\n";

    if (overloadData.hasVarargs()) {
        maxArgs--;
        if (minArgs > maxArgs)
            minArgs = maxArgs;

        s << "PyObject *nonvarargs = PyTuple_GetSlice(args, 0, " << maxArgs << ");\n"
            << "Shiboken::AutoDecRef auto_nonvarargs(nonvarargs);\n"
            << PYTHON_ARGS << '[' << maxArgs << "] = PyTuple_GetSlice(args, "
            << maxArgs << ", numArgs);\n"
            << "Shiboken::AutoDecRef auto_varargs(" << PYTHON_ARGS << "["
            << maxArgs << "]);\n\n";
    }

    bool usesNamedArguments = overloadData.hasArgumentWithDefaultValue();

    s << "// invalid argument lengths\n";

    // Disable argument count checks for QObject constructors to allow for
    // passing properties as KW args.
    const auto owner = rfunc->ownerClass();
    bool isQObjectConstructor = owner && isQObject(owner)
        && rfunc->functionType() == AbstractMetaFunction::ConstructorFunction;

    if (usesNamedArguments && !isQObjectConstructor) {
        s << "errInfo.reset(Shiboken::checkInvalidArgumentCount(numArgs, "
            <<  minArgs << ", " << maxArgs << "));\n"
            << "if (!errInfo.isNull())\n" << indent
            << "goto " << cpythonFunctionName(rfunc) << "_TypeError;\n" << outdent;
    }

    const QList<int> invalidArgsLength = overloadData.invalidArgumentLengths();
    if (!invalidArgsLength.isEmpty()) {
        s << "if (";
        for (qsizetype i = 0, size = invalidArgsLength.size(); i < size; ++i) {
            if (i)
                s << " || ";
            s << "numArgs == " << invalidArgsLength.at(i);
        }
        s << ")\n" << indent
            << "goto " << cpythonFunctionName(rfunc) << "_TypeError;\n" << outdent;
    }
    s  << '\n';

    QString funcName;
    if (rfunc->isOperatorOverload())
        funcName = ShibokenGenerator::pythonOperatorFunctionName(rfunc);
    else
        funcName = rfunc->name();

    QString argsVar = overloadData.hasVarargs() ?  u"nonvarargs"_s : u"args"_s;
    s << "if (!";
    if (usesNamedArguments) {
        s << "PyArg_ParseTuple(" << argsVar << ", \"|" << QByteArray(maxArgs, 'O')
            << ':' << funcName << '"';
    } else {
        s << "PyArg_UnpackTuple(" << argsVar << ", \"" << funcName << "\", "
            << minArgs << ", " << maxArgs;
    }
    for (int i = 0; i < maxArgs; i++)
        s << ", &(" << PYTHON_ARGS << '[' << i << "])";
    s << "))\n" << indent << errorReturn << outdent << '\n';
}

void CppGenerator::writeCppSelfConversion(TextStream &s, const GeneratorContext &context,
                                          const QString &className, bool useWrapperClass)
{
    if (context.forSmartPointer()) {
        writeSmartPointerCppSelfConversion(s, context);
        return;
    }

    static const QString pythonSelfVar = u"self"_s;
    if (useWrapperClass)
        s << "static_cast<" << className << " *>(";
    s << cpythonWrapperCPtr(context.metaClass(), pythonSelfVar);
    if (useWrapperClass)
        s << ')';
}

void CppGenerator::writeSmartPointerCppSelfConversion(TextStream &s,
                                                      const GeneratorContext &context)
{
    Q_ASSERT(context.forSmartPointer());
    s << cpythonWrapperCPtr(context.preciseType(), u"self"_s);
}

static inline void writeCppSelfVarDef(TextStream &s,
                                      CppGenerator::CppSelfDefinitionFlags flags = {})
{
    if (flags.testFlag(CppGenerator::CppSelfAsReference))
        s << "auto &" <<  CPP_SELF_VAR << " = *";
    else
        s << "auto *" << CPP_SELF_VAR << " = ";
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

void CppGenerator::writeCppSelfDefinition(TextStream &s,
                                          const GeneratorContext &context,
                                          ErrorReturn errorReturn,
                                          CppSelfDefinitionFlags flags) const
{
    Q_ASSERT(!(flags.testFlag(CppSelfAsReference) && flags.testFlag(HasStaticOverload)));
    if (context.forSmartPointer()) {
        writeSmartPointerCppSelfDefinition(s, context, errorReturn, flags);
        return;
    }

    AbstractMetaClassCPtr metaClass = context.metaClass();
    const auto cppWrapper = context.metaClass()->cppWrapper();
    // In the Python method, use the wrapper to access the protected
    // functions.
    const bool useWrapperClass = avoidProtectedHack()
        && cppWrapper.testFlag(AbstractMetaClass::CppProtectedHackWrapper);
    Q_ASSERT(!useWrapperClass || context.useWrapper());
    const QString className = useWrapperClass
        ? context.wrapperName()
        : (u"::"_s + metaClass->qualifiedCppName());

    writeInvalidPyObjectCheck(s, u"self"_s, errorReturn);

    if (flags.testFlag(CppSelfAsReference)) {
         writeCppSelfVarDef(s, flags);
         writeCppSelfConversion(s, context, className, useWrapperClass);
         s << ";\n";
         return;
    }

    if (!flags.testFlag(HasStaticOverload)) {
        if (!flags.testFlag(HasClassMethodOverload)) {
            // PYSIDE-131: The single case of a class method for now: tr().
            writeCppSelfVarDef(s, flags);
            writeCppSelfConversion(s, context, className, useWrapperClass);
            s << ";\n" << sbkUnusedVariableCast(CPP_SELF_VAR);
        }
        return;
    }

    s << className << " *" << CPP_SELF_VAR << " = nullptr;\n"
        << sbkUnusedVariableCast(CPP_SELF_VAR);

    // Checks if the underlying C++ object is valid.
    s << "if (self)\n" << indent
        << CPP_SELF_VAR << " = ";
    writeCppSelfConversion(s, context, className, useWrapperClass);
    s << ";\n"<< outdent;
}

void CppGenerator::writeCppSelfDefinition(TextStream &s,
                                          const AbstractMetaFunctionCPtr &func,
                                          const GeneratorContext &context,
                                          ErrorReturn errorReturn,
                                          CppSelfDefinitionFlags flags) const
{
    if (!func->ownerClass() || func->isConstructor())
        return;

    if (func->isOperatorOverload() && func->isBinaryOperator()) {
        QString checkFunc = cpythonCheckFunction(func->ownerClass()->typeEntry());
        s << "bool isReverse = " << checkFunc << PYTHON_ARG << ")\n"
            << "                && !" << checkFunc << "self);\n"
            << "if (isReverse)\n" << indent
            << "std::swap(self, " << PYTHON_ARG << ");\n" << outdent;
    }

    writeCppSelfDefinition(s, context, errorReturn, flags);
}

void CppGenerator::writeErrorSection(TextStream &s, const OverloadData &overloadData,
                                     ErrorReturn errorReturn)
{
    const auto rfunc = overloadData.referenceFunction();
    QString argsVar = overloadData.pythonFunctionWrapperUsesListOfArguments()
        ? u"args"_s : PYTHON_ARG;
    s << '\n' << cpythonFunctionName(rfunc) << "_TypeError:\n" << indent
        << "Shiboken::setErrorAboutWrongArguments(" << argsVar << ", fullName, errInfo);\n"
        << errorReturn << outdent;
}

void CppGenerator::writeFunctionReturnErrorCheckSection(TextStream &s,
                                                        ErrorReturn errorReturn,
                                                        bool hasReturnValue)
{
    s << "if (Shiboken::Errors::occurred()";
    if (hasReturnValue)
        s << " || !" << PYTHON_RETURN_VAR;
    s << ") {\n" << indent;
    if (hasReturnValue)
        s << "Py_XDECREF(" << PYTHON_RETURN_VAR << ");\n";
    s << errorReturn << outdent << "}\n";
}

void CppGenerator::writeInvalidPyObjectCheck(TextStream &s, const QString &pyObj,
                                             ErrorReturn errorReturn)
{
    s << "if (!Shiboken::Object::isValid(" << pyObj << "))\n"
        << indent << errorReturn << outdent;
}

static QString pythonToCppConverterForArgumentName(const QString &argumentName)
{
    static const QRegularExpression pyArgsRegex(PYTHON_ARGS
                                                + uR"((\[\d+[-]?\d*\]))"_s);
    Q_ASSERT(pyArgsRegex.isValid());
    const QRegularExpressionMatch match = pyArgsRegex.match(argumentName);
    QString result = PYTHON_TO_CPP_VAR;
    if (match.hasMatch())
        result += match.captured(1);
    return result;
}

void CppGenerator::writeTypeCheck(TextStream &s, const QString &customType,
                                  const QString &argumentName)
{
    QString errorMessage;
    const auto metaTypeOpt = AbstractMetaType::fromString(customType, &errorMessage);
    if (!metaTypeOpt.has_value())
        throw Exception(errorMessage);
    writeTypeCheck(s, metaTypeOpt.value(), argumentName,
                   ShibokenGenerator::isNumber(metaTypeOpt.value()));
}

void CppGenerator::writeTypeCheck(TextStream &s, const AbstractMetaType &argType,
                                  const QString &argumentName, bool isNumber,
                                  bool rejectNull)
{
    // TODO-CONVERTER: merge this with the code below.
    QString typeCheck = cpythonIsConvertibleFunction(argType);
    if (typeCheck != u"true") // For PyObject, which is always true
        typeCheck.append(u'(' +argumentName + u')');

    // TODO-CONVERTER -----------------------------------------------------------------------
    if (!argType.typeEntry()->isCustom()) {
        typeCheck = u'(' + pythonToCppConverterForArgumentName(argumentName)
                    + u" = "_s + typeCheck + u"))"_s;
        if (!isNumber && isCppPrimitive(argType.typeEntry())) {
            typeCheck.prepend(cpythonCheckFunction(argType) + u'('
                              + argumentName + u") && "_s);
        }
    }
    // TODO-CONVERTER -----------------------------------------------------------------------

    if (rejectNull)
        typeCheck = u'(' + argumentName +  u" != Py_None && "_s + typeCheck + u')';

    s << typeCheck;
}

static void checkTypeViability(const AbstractMetaFunctionCPtr &func,
                               const AbstractMetaType &type, int argIdx)
{
    const bool modified = argIdx == 0
        ? func->isTypeModified()
        : func->arguments().at(argIdx -1).isTypeModified();
    const bool isRemoved = argIdx == 0
        ? func->argumentRemoved(0)
        : func->arguments().at(argIdx -1).isModifiedRemoved();
    if (type.isVoid()
        || !type.typeEntry()->isPrimitive()
        || type.indirections() == 0
        || (type.indirections() == 1 && type.typeUsagePattern() == AbstractMetaType::NativePointerAsArrayPattern)
        || type.isCString()
        || isRemoved
        || modified
        || func->hasConversionRule(TypeSystem::All, argIdx)
        || func->hasInjectedCode())
        return;
    QString message;
    QTextStream str(&message);
    str << func->sourceLocation()
        << "There's no user provided way (conversion rule, argument"
           " removal, custom code, etc) to handle the primitive ";
    if (argIdx == 0)
        str << "return type '" << type.cppSignature() << '\'';
    else
        str << "type '" << type.cppSignature() << "' of argument " << argIdx;
    str << " in function '";
    if (func->ownerClass())
        str << func->ownerClass()->qualifiedCppName() << "::";
    str << func->signature() << "'.";
    qCWarning(lcShiboken).noquote().nospace() << message;
}

static void checkTypeViability(const AbstractMetaFunctionCPtr &func)
{
    if (func->isUserAdded())
        return;
    checkTypeViability(func, func->type(), 0);
    for (qsizetype i = 0; i < func->arguments().size(); ++i)
        checkTypeViability(func, func->arguments().at(i).type(), int(i + 1));
}

void CppGenerator::writeTypeCheck(TextStream &s,
                                  const std::shared_ptr<OverloadDataNode> &overloadData,
                                  const QString &argumentName)
{
    QSet<TypeEntryCPtr> numericTypes;
    const OverloadDataList &siblings = overloadData->parent()->children();
    for (const auto &sibling : siblings) {
        for (const auto &func : sibling->overloads()) {
            checkTypeViability(func);
            const AbstractMetaType &argType = sibling->overloadArgument(func)->type();
            if (!argType.isPrimitive())
                continue;
            if (ShibokenGenerator::isNumber(argType.typeEntry()))
                numericTypes << argType.typeEntry();
        }
    }

    // This condition trusts that the OverloadData object will arrange for
    // PyLong type to come after the more precise numeric types (e.g. float and bool)
    AbstractMetaType argType = overloadData->modifiedArgType();
    if (auto viewOn = argType.viewOn())
        argType = *viewOn;
    const bool numberType = numericTypes.size() == 1 || ShibokenGenerator::isPyInt(argType);
    bool rejectNull =
        shouldRejectNullPointerArgument(overloadData->referenceFunction(), overloadData->argPos());
    writeTypeCheck(s, argType, argumentName, numberType, rejectNull);
}

qsizetype CppGenerator::writeArgumentConversion(TextStream &s,
                                                const AbstractMetaType &argType,
                                                const QString &argName,
                                                const QString &pyArgName,
                                                ErrorReturn errorReturn,
                                                const AbstractMetaClassCPtr &context,
                                                const QString &defaultValue,
                                                bool castArgumentAsUnused) const
{
    qsizetype result = 0;
    if (argType.typeEntry()->isCustom() || argType.typeEntry()->isVarargs())
        return result;
    if (argType.isWrapperType())
        writeInvalidPyObjectCheck(s, pyArgName, errorReturn);
    result = writePythonToCppTypeConversion(s, argType, pyArgName, argName, context, defaultValue);
    if (castArgumentAsUnused)
        s << sbkUnusedVariableCast(argName);
    return result;
}

AbstractMetaType
    CppGenerator::getArgumentType(const AbstractMetaFunctionCPtr &func, int index)
{
    if (index < 0 || index >= func->arguments().size()) {
        qCWarning(lcShiboken).noquote().nospace()
            << "Argument index for function '" << func->signature() << "' out of range.";
        return {};
    }

    auto argType = func->arguments().at(index).modifiedType();
    return argType.viewOn() ? *argType.viewOn() : argType;
}

static inline QString arrayHandleType(const AbstractMetaTypeList &nestedArrayTypes)
{
    switch (nestedArrayTypes.size()) {
    case 1:
        return QStringLiteral("Shiboken::Conversions::ArrayHandle<")
            + nestedArrayTypes.constLast().minimalSignature() + u'>';
    case 2:
        return QStringLiteral("Shiboken::Conversions::Array2Handle<")
            + nestedArrayTypes.constLast().minimalSignature()
            + QStringLiteral(", ")
            + QString::number(nestedArrayTypes.constFirst().arrayElementCount())
            + u'>';
    }
    return QString();
}

// Helper to write argument initialization code for a function argument
// in case it has a default value.
template <class Type> // AbstractMetaType/TypeEntry
static void writeMinimalConstructorExpression(TextStream &s,
                                              const ApiExtractorResult &api,
                                              Type type,
                                              bool isPrimitive,
                                              const QString &defaultValue)
{
    if (defaultValue.isEmpty()) {
        s << ShibokenGenerator::minimalConstructorExpression(api, type);
        return;
    }
    // Use assignment to avoid "Most vexing parse" if it looks like
    // a function call, or for primitives/pointers
    const bool isDefault = defaultValue == u"{}";
    if ((isPrimitive && !isDefault)
        || defaultValue == u"nullptr" || defaultValue.contains(u'(')) {
        s << " = " << defaultValue;
        return;
    }
    if (isDefault) {
        s << defaultValue;
        return;
    }
    s << '(' << defaultValue << ')';
}

qsizetype CppGenerator::writePythonToCppTypeConversion(TextStream &s,
                                                  const AbstractMetaType &type,
                                                  const QString &pyIn,
                                                  const QString &cppOut,
                                                  const AbstractMetaClassCPtr &context,
                                                  const QString &defaultValue) const
{
    TypeEntryCPtr typeEntry = type.typeEntry();
    if (typeEntry->isCustom() || typeEntry->isVarargs())
        return 0;

    const auto arg = GeneratorArgument::fromMetaType(type);
    const bool isPrimitive = arg.type == GeneratorArgument::Type::Primitive;

    QString cppOutAux = cppOut + u"_local"_s;

    QString typeName = arg.type == GeneratorArgument::Type::CppPrimitiveArray
       ? arrayHandleType(type.nestedArrayTypes())
       : getFullTypeNameWithoutModifiers(type);

    bool isProtectedEnum = false;
    if (arg.type == GeneratorArgument::Type::Enum && avoidProtectedHack()) {
        auto metaEnum = api().findAbstractMetaEnum(type.typeEntry());
        if (metaEnum.has_value() && metaEnum->isProtected()) {
            typeName = wrapperName(context) + u"::"_s
                       + metaEnum.value().name();
            isProtectedEnum = true;
        }
    }

    s << typeName;
    switch (arg.conversion) {
    case GeneratorArgument::Conversion::CppPrimitiveArray:
        s << ' ' << cppOut;
        break;
    case GeneratorArgument::Conversion::ValueOrPointer: {
        // Generate either value conversion for &cppOutAux or pointer
        // conversion for &cppOut
        s << ' ' << cppOutAux;
        // No default value for containers which can also be passed by pointer.
        if (arg.type != GeneratorArgument::Type::Container)
            writeMinimalConstructorExpression(s, api(), type, isPrimitive, defaultValue);
        s << ";\n" << typeName << " *" << cppOut << " = &" << cppOutAux;
    }
        break;
    case GeneratorArgument::Conversion::Pointer: {
        s << " *" << cppOut;
        if (!defaultValue.isEmpty()) {
            const bool needsConstCast = !isNullPtr(defaultValue)
                && type.indirections() == 1 && type.isConstant()
                && type.referenceType() == NoReference;
            s << " = ";
            if (needsConstCast)
                s << "const_cast<" << typeName << " *>(";
            s << defaultValue;
            if (needsConstCast)
                s << ')';
        }
    }
        break;
    case GeneratorArgument::Conversion::Default:
        s << ' ' << cppOut;
        if (isProtectedEnum && avoidProtectedHack()) {
            s << " = ";
            if (defaultValue.isEmpty())
                s << "{}";
            else
                s << defaultValue;
        } else if (type.isUserPrimitive()
                   || arg.type == GeneratorArgument::Type::Enum
                   || arg.type == GeneratorArgument::Type::Flags) {
            writeMinimalConstructorExpression(s, api(), typeEntry, isPrimitive, defaultValue);
        } else if (!type.isContainer() && !type.isSmartPointer()) {
            writeMinimalConstructorExpression(s, api(), type, isPrimitive, defaultValue);
        }
        break;
    }
    s << ";\n";

    QString pythonToCppFunc = pythonToCppConverterForArgumentName(pyIn);

    QString pythonToCppCall = pythonToCppFunc + u'(' + pyIn + u", &"_s
                              + cppOut + u')';
    if (arg.conversion != GeneratorArgument::Conversion::ValueOrPointer) {
        // pythonToCppFunc may be 0 when less parameters are passed and
        // the defaultValue takes effect.
        if (!defaultValue.isEmpty())
            s << "if (" << pythonToCppFunc << ")\n" << indent;
        s << pythonToCppCall << ";\n";
        if (!defaultValue.isEmpty())
            s << outdent;
        return arg.indirections;
    }

    // pythonToCppFunc may be 0 when less parameters are passed and
    // the defaultValue takes effect.
    if (!defaultValue.isEmpty())
        s << "if (" << pythonToCppFunc << ") {\n" << indent;

    s << "if (" << pythonToCppFunc << ".isValue())\n"
        << indent << pythonToCppFunc << '(' << pyIn << ", &" << cppOutAux << ");\n"
        << outdent << "else\n" << indent
        << pythonToCppCall << ";\n" << outdent;

    if (defaultValue.isEmpty())
        s << '\n';
    else
        s << "}\n" << outdent;

    return arg.indirections;
}

static void addConversionRuleCodeSnippet(CodeSnipList &snippetList, QString &rule,
                                         TypeSystem::Language /* conversionLanguage */,
                                         TypeSystem::Language snippetLanguage,
                                         const QString &outputName = QString(),
                                         const QString &inputName = QString())
{
    if (rule.isEmpty())
        return;
    if (snippetLanguage == TypeSystem::TargetLangCode) {
        rule.replace(u"%in"_s, inputName);
        rule.replace(u"%out"_s, outputName + u"_out"_s);
    } else {
        rule.replace(u"%out"_s, outputName);
    }
    CodeSnip snip(snippetLanguage);
    snip.position = (snippetLanguage == TypeSystem::NativeCode) ? TypeSystem::CodeSnipPositionAny : TypeSystem::CodeSnipPositionBeginning;
    snip.addCode(rule);
    snippetList << snip;
}

void CppGenerator::writeConversionRule(TextStream &s, const AbstractMetaFunctionCPtr &func,
                                       TypeSystem::Language language, bool usesPyArgs) const
{

    CodeSnipList snippets;
    const AbstractMetaArgumentList &arguments = func->arguments();
    for (const AbstractMetaArgument &arg : arguments) {
        QString rule = func->conversionRule(language, arg.argumentIndex() + 1);
        addConversionRuleCodeSnippet(snippets, rule, language, TypeSystem::TargetLangCode,
                                     arg.name(), arg.name());
    }
    writeCodeSnips(s, snippets, TypeSystem::CodeSnipPositionBeginning, TypeSystem::TargetLangCode,
                   func, usesPyArgs, nullptr);
}

void CppGenerator::writeConversionRule(TextStream &s, const AbstractMetaFunctionCPtr &func,
                                       TypeSystem::Language language, const QString &outputVar) const
{
    CodeSnipList snippets;
    QString rule = func->conversionRule(language, 0);
    addConversionRuleCodeSnippet(snippets, rule, language, language, outputVar);
    writeCodeSnips(s, snippets, TypeSystem::CodeSnipPositionAny, language,
                   func, false /* uses PyArgs */, nullptr);
}

void CppGenerator::writeNoneReturn(TextStream &s, const AbstractMetaFunctionCPtr &func,
                                   bool thereIsReturnValue)
{
    if (thereIsReturnValue && (func->isVoid() || func->argumentRemoved(0))
        && !func->injectedCodeHasReturnValueAttribution()) {
        s << PYTHON_RETURN_VAR << " = Py_None;\n"
            << "Py_INCREF(Py_None);\n";
    }
}

void CppGenerator::writeOverloadedFunctionDecisor(TextStream &s, const OverloadData &overloadData) const
{
    s << "// Overloaded function decisor\n";
    const auto rfunc = overloadData.referenceFunction();
    const AbstractMetaFunctionCList &functionOverloads = overloadData.overloads();
    for (qsizetype i = 0; i < functionOverloads.size(); ++i) {
        const auto func = functionOverloads.at(i);
        s << "// " << i << ": ";
        if (func->isStatic())
            s << "static ";
        if (const auto decl = func->declaringClass())
            s << decl->name() << "::";
        s << func->signatureComment() << '\n';
    }
    writeOverloadedFunctionDecisorEngine(s, overloadData, &overloadData);
    s << '\n';

    // Ensure that the direct overload that called this reverse
    // is called.
    if (rfunc->isOperatorOverload() && !rfunc->isCallOperator()) {
        s << "if (isReverse && overloadId == -1) {\n" << indent
            << "Shiboken::Errors::setReverseOperatorNotImplemented();\n"
            << "return {};\n" << outdent
            << "}\n\n";
    }

    s << "// Function signature not found.\n"
        << "if (overloadId == -1) goto "
        << cpythonFunctionName(overloadData.referenceFunction()) << "_TypeError;\n\n";
}

void CppGenerator::writeOverloadedFunctionDecisorEngine(TextStream &s,
                                                        const OverloadData &overloadData,
                                                        const OverloadDataRootNode *node) const
{
    bool hasDefaultCall = node->nextArgumentHasDefaultValue();
    auto referenceFunction = node->referenceFunction();

    // If the next argument has not an argument with a default value, it is still possible
    // that one of the overloads for the current overload data has its final occurrence here.
    // If found, the final occurrence of a method is attributed to the referenceFunction
    // variable to be used further on this method on the conditional that identifies default
    // method calls.
    if (!hasDefaultCall) {
        for (const auto &func : node->overloads()) {
            if (node->isFinalOccurrence(func)) {
                referenceFunction = func;
                hasDefaultCall = true;
                break;
            }
        }
    }

    const int maxArgs = overloadData.maxArgs();
    // Python constructors always receive multiple arguments.
    const bool usePyArgs = overloadData.pythonFunctionWrapperUsesListOfArguments();

    // Functions without arguments are identified right away.
    if (maxArgs == 0) {
        s << "overloadId = " << overloadData.functionNumber(referenceFunction)
            << "; // " << referenceFunction->minimalSignature() << '\n';
        return;

    }
    // To decide if a method call is possible at this point the current overload
    // data object cannot be the head, since it is just an entry point, or a root,
    // for the tree of arguments and it does not represent a valid method call.
    if (!node->isRoot()) {
        const bool isLastArgument = node->children().isEmpty();
        const bool signatureFound = node->overloads().size() == 1;

        // The current overload data describes the last argument of a signature,
        // so the method can be identified right now.
        if (isLastArgument || (signatureFound && !hasDefaultCall)) {
            const auto func = node->referenceFunction();
            s << "overloadId = " << overloadData.functionNumber(func)
                << "; // " << func->minimalSignature() << '\n';
            return;
        }
    }

    bool isFirst = true;

    // If the next argument has a default value the decisor can perform a method call;
    // it just need to check if the number of arguments received from Python are equal
    // to the number of parameters preceding the argument with the default value.
    const OverloadDataList &children = node->children();
    if (hasDefaultCall) {
        isFirst = false;
        int numArgs = node->argPos() + 1;
        s << "if (numArgs == " << numArgs << ") {\n" << indent;
        auto func = referenceFunction;
        for (const auto &child : children) {
            const auto defValFunc = child->getFunctionWithDefaultValue();
            if (defValFunc) {
                func = defValFunc;
                break;
            }
        }
        s << "overloadId = " << overloadData.functionNumber(func)
            << "; // " << func->minimalSignature() << '\n' << outdent << '}';
    }

    for (auto child : children) {
        bool signatureFound = child->overloads().size() == 1
                                && !child->getFunctionWithDefaultValue()
                                && !child->findNextArgWithDefault();

        const auto refFunc = child->referenceFunction();

        QStringList typeChecks;

        QString pyArgName = (usePyArgs && maxArgs > 1)
            ? pythonArgsAt(child->argPos())
            : PYTHON_ARG;
        auto od = child;
        int startArg = od->argPos();
        int sequenceArgCount = 0;
        while (od && !od->argType().isVarargs()) {
            const bool typeReplacedByPyObject = od->isTypeModified()
                && od->modifiedArgType().name() == cPyObjectT();
            if (!typeReplacedByPyObject) {
                if (usePyArgs)
                    pyArgName = pythonArgsAt(od->argPos());
                StringStream tck(TextStream::Language::Cpp);
                auto func = od->referenceFunction();

                if (func->isConstructor() && func->arguments().size() == 1) {
                    AbstractMetaClassCPtr ownerClass = func->ownerClass();
                    ComplexTypeEntryCPtr baseContainerType = ownerClass->typeEntry()->baseContainerType();
                    if (baseContainerType && baseContainerType == func->arguments().constFirst().type().typeEntry()
                        && ownerClass->isCopyable()) {
                        tck << '!' << cpythonCheckFunction(ownerClass->typeEntry())
                            << pyArgName << ")\n" << indent << "&& " << outdent;
                    }
                }
                writeTypeCheck(tck, od, pyArgName);
                typeChecks << tck.toString();
            }

            sequenceArgCount++;

            if (od->children().isEmpty()
                || od->nextArgumentHasDefaultValue()
                || od->children().size() != 1
                || od->overloads().size() != od->children().constFirst()->overloads().size()) {
                child = od;
                od = nullptr;
            } else {
                od = od->children().constFirst();
            }
        }

        if (usePyArgs && signatureFound) {
            AbstractMetaArgumentList args = refFunc->arguments();
            const bool isVarargs = args.size() > 1 && args.constLast().type().isVarargs();
            int numArgs = args.size() - OverloadData::numberOfRemovedArguments(refFunc);
            if (isVarargs)
                --numArgs;
            QString check = (isVarargs ? u"numArgs >= "_s : u"numArgs == "_s)
                            + QString::number(numArgs);
            typeChecks.prepend(check);
        } else if (usePyArgs && sequenceArgCount > 0) {
            typeChecks.prepend(u"numArgs >= "_s + QString::number(startArg + sequenceArgCount));
        } else if (refFunc->isOperatorOverload() && !refFunc->isCallOperator()) {
            QString check;
            if (!refFunc->isReverseOperator())
                check.append(u'!');
            check.append(u"isReverse"_s);
            typeChecks.prepend(check);
        }

        if (isFirst) {
            isFirst = false;
        } else {
            s << " else ";
        }
        s << "if (";
        if (typeChecks.isEmpty()) {
            s << "true";
        } else {
            s << indent << typeChecks.join(u"\n&& "_s) << outdent;
        }
        s << ") {\n" << indent;
        writeOverloadedFunctionDecisorEngine(s, overloadData, child.get());
        s << outdent << '}';
    }
    s << '\n';
}

void CppGenerator::writeFunctionCalls(TextStream &s, const OverloadData &overloadData,
                                      const GeneratorContext &context,
                                      ErrorReturn errorReturn) const
{
    const AbstractMetaFunctionCList &overloads = overloadData.overloads();
    s << "// Call function/method\n"
        << (overloads.size() > 1 ? "switch (overloadId) " : "") << "{\n" << indent;
    if (overloads.size() == 1) {
        writeSingleFunctionCall(s, overloadData, overloads.constFirst(), context,
                                errorReturn);
    } else {
        for (qsizetype i = 0; i < overloads.size(); ++i) {
            const auto func = overloads.at(i);
            s << "case " << i << ": // " << func->signature() << "\n{\n" << indent;
            writeSingleFunctionCall(s, overloadData, func, context, errorReturn);
            s << "break;\n" << outdent << "}\n";
        }
    }
    s << outdent << "}\n";
}

static void writeDeprecationWarning(TextStream &s,
                                    const GeneratorContext &context,
                                    const AbstractMetaFunctionCPtr &func,
                                    CppGenerator::ErrorReturn errorReturn)
{
    s << "Shiboken::Warnings::warnDeprecated(\"";
    if (const auto cls = context.metaClass())
        s << cls->name() << "\", ";
    // Check error in case "warning-as-error" is set.
    s << '"' << func->signature().replace(u"::"_s, u"."_s) << "\");\n"
        << "if (PyErr_Occurred())\n" << indent << errorReturn << outdent;
}

void CppGenerator::writeSingleFunctionCall(TextStream &s,
                                           const OverloadData &overloadData,
                                           const AbstractMetaFunctionCPtr &func,
                                           const GeneratorContext &context,
                                           ErrorReturn errorReturn) const
{
    if (func->isDeprecated())
        writeDeprecationWarning(s, context, func, errorReturn);

    if (func->functionType() == AbstractMetaFunction::EmptyFunction) {
        s << "Shiboken::Errors::setPrivateMethod(\""
          << func->signature().replace(u"::"_s, u"."_s) << "\");\n"
          << errorReturn;
        return;
    }

    const bool usePyArgs = overloadData.pythonFunctionWrapperUsesListOfArguments();

    // Handle named arguments.
    writeNamedArgumentResolution(s, func, usePyArgs, overloadData);

    bool injectCodeCallsFunc = injectedCodeCallsCppFunction(context, func);
    bool mayHaveUnunsedArguments = !func->isUserAdded() && func->hasInjectedCode() && injectCodeCallsFunc;
    int removedArgs = 0;

    const auto argCount = func->arguments().size();
    QList<qsizetype> indirections(argCount, 0);
    for (qsizetype argIdx = 0; argIdx < argCount; ++argIdx) {
        const bool hasConversionRule =
            func->hasConversionRule(TypeSystem::NativeCode, int(argIdx + 1));
        const AbstractMetaArgument &arg = func->arguments().at(argIdx);
        if (arg.isModifiedRemoved()) {
            if (!arg.defaultValueExpression().isEmpty()) {
                const QString cppArgRemoved = CPP_ARG_REMOVED
                    + QString::number(argIdx);
                s << getFullTypeName(arg.type()) << ' ' << cppArgRemoved;
                s << " = " << arg.defaultValueExpression() << ";\n"
                    << sbkUnusedVariableCast(cppArgRemoved);
            } else if (!injectCodeCallsFunc && !func->isUserAdded() && !hasConversionRule) {
                // When an argument is removed from a method signature and no other means of calling
                // the method are provided (as with code injection) the generator must abort.
                QString m;
                QTextStream(&m) << "No way to call '" << func->ownerClass()->name()
                    << "::" << func->signature()
                    << "' with the modifications described in the type system.";
                throw Exception(m);
            }
            removedArgs++;
            continue;
        }
        if (hasConversionRule)
            continue;
        if (mayHaveUnunsedArguments && !func->injectedCodeUsesArgument(argIdx))
            continue;
        auto argType = getArgumentType(func, argIdx);
        int argPos = argIdx - removedArgs;
        QString argName = CPP_ARG + QString::number(argPos);
        QString pyArgName = usePyArgs ? pythonArgsAt(argPos) : PYTHON_ARG;
        indirections[argIdx] =
            writeArgumentConversion(s, argType, argName, pyArgName, errorReturn,
                                    func->implementingClass(), arg.defaultValueExpression(),
                                    func->isUserAdded());
    }

    s << '\n';

    int numRemovedArgs = OverloadData::numberOfRemovedArguments(func);

    s << "if (!PyErr_Occurred()) {\n" << indent;
    writeMethodCall(s, func, context,
                    overloadData.pythonFunctionWrapperUsesListOfArguments(),
                    func->arguments().size() - numRemovedArgs, indirections, errorReturn);

    if (!func->isConstructor())
        writeNoneReturn(s, func, overloadData.hasNonVoidReturnType());
    s << outdent << "}\n";
}

QString CppGenerator::cppToPythonFunctionName(const QString &sourceTypeName, QString targetTypeName)
{
    if (targetTypeName.isEmpty())
        targetTypeName = sourceTypeName;
    return sourceTypeName + u"_CppToPython_"_s + targetTypeName;
}

QString CppGenerator::pythonToCppFunctionName(const QString &sourceTypeName, const QString &targetTypeName)
{
    return sourceTypeName + u"_PythonToCpp_"_s + targetTypeName;
}
QString CppGenerator::pythonToCppFunctionName(const AbstractMetaType &sourceType, const AbstractMetaType &targetType)
{
    return pythonToCppFunctionName(fixedCppTypeName(sourceType), fixedCppTypeName(targetType));
}
QString CppGenerator::pythonToCppFunctionName(const TargetToNativeConversion &toNative,
                                              const TypeEntryCPtr &targetType)
{
    return pythonToCppFunctionName(fixedCppTypeName(toNative), fixedCppTypeName(targetType));
}

QString CppGenerator::convertibleToCppFunctionName(const QString &sourceTypeName, const QString &targetTypeName)
{
    return u"is_"_s + sourceTypeName + u"_PythonToCpp_"_s
            + targetTypeName + u"_Convertible"_s;
}
QString CppGenerator::convertibleToCppFunctionName(const AbstractMetaType &sourceType, const AbstractMetaType &targetType)
{
    return convertibleToCppFunctionName(fixedCppTypeName(sourceType), fixedCppTypeName(targetType));
}
QString CppGenerator::convertibleToCppFunctionName(const TargetToNativeConversion &toNative,
                                                   const TypeEntryCPtr &targetType)
{
    return convertibleToCppFunctionName(fixedCppTypeName(toNative), fixedCppTypeName(targetType));
}

void CppGenerator::writeCppToPythonFunction(TextStream &s, const QString &code, const QString &sourceTypeName,
                                            QString targetTypeName) const
{

    QString prettyCode = code;
    processCodeSnip(prettyCode);

    s << "static PyObject *" << cppToPythonFunctionName(sourceTypeName, targetTypeName)
        << "(const void *cppIn)\n{\n" << indent << prettyCode
        << ensureEndl << outdent << "}\n";
}

static QString writeCppInRef(const QString &typeName, bool constRef)
{
    QString result;
    QTextStream str(&result);
    if (constRef)
        str << "const ";
    str << "auto &cppInRef = *reinterpret_cast<";
    if (constRef)
        str << "const ";
    str << typeName << " *>("
        << (constRef ? "cppIn" : "const_cast<void *>(cppIn)") << ");";
    return result;
}

static void replaceCppToPythonVariables(QString &code, const QString &typeName,
                                        bool constRef = false)
{
    CodeSnipAbstract::prependCode(&code, writeCppInRef(typeName, constRef));
    code.replace(u"%INTYPE"_s, typeName);
    code.replace(u"%OUTTYPE"_s, u"PyObject *"_s);
    code.replace(u"%in"_s, u"cppInRef"_s);
    code.replace(u"%out"_s, u"pyOut"_s);
}

void CppGenerator::writeCppToPythonFunction(TextStream &s,
                                            const CustomConversionPtr &customConversion) const
{
    QString code = customConversion->nativeToTargetConversion();
    auto ownerType = customConversion->ownerType();
    const bool constRef = !ownerType->isPrimitive(); // PyCapsule needs a non-const ref
    replaceCppToPythonVariables(code, getFullTypeName(ownerType), constRef);
    writeCppToPythonFunction(s, code, fixedCppTypeName(customConversion->ownerType()));
}

QString CppGenerator::containerNativeToTargetTypeName(const ContainerTypeEntryCPtr &type)
{
    QString result = type->targetLangApiName();
    if (result != cPyObjectT()) {
        result = containerCpythonBaseName(type);
        if (result == cPySequenceT())
            result = cPyListT();
    }
    return result;
}

void CppGenerator::writeCppToPythonFunction(TextStream &s, const AbstractMetaType &containerType) const
{
    Q_ASSERT(containerType.typeEntry()->isContainer());
    auto cte = std::static_pointer_cast<const ContainerTypeEntry>(containerType.typeEntry());
    if (!cte->hasCustomConversion()) {
        QString m;
        QTextStream(&m) << "Can't write the C++ to Python conversion function for container type '"
             << containerType.typeEntry()->qualifiedCppName()
             << "' - no conversion rule was defined for it in the type system.";
        throw Exception(m);
    }
    const auto customConversion = cte->customConversion();
    QString code = customConversion->nativeToTargetConversion();
    for (qsizetype i = 0; i < containerType.instantiations().size(); ++i) {
        const AbstractMetaType &type = containerType.instantiations().at(i);
        QString typeName = getFullTypeName(type);
        if (type.isConstant())
            typeName = u"const "_s + typeName;
        code.replace(u"%INTYPE_"_s + QString::number(i), typeName);
    }
    replaceCppToPythonVariables(code, getFullTypeNameWithoutModifiers(containerType), true);
    processCodeSnip(code);
    writeCppToPythonFunction(s, code, fixedCppTypeName(containerType),
                             containerNativeToTargetTypeName(cte));
}

void CppGenerator::writePythonToCppFunction(TextStream &s, const QString &code, const QString &sourceTypeName,
                                            const QString &targetTypeName) const
{
    QString prettyCode = code;
    processCodeSnip(prettyCode);
    s << "static void " << pythonToCppFunctionName(sourceTypeName, targetTypeName)
        << "(PyObject *pyIn, void *cppOut)\n{\n" << indent << prettyCode
        << ensureEndl << outdent << "}\n";
}

void CppGenerator::writeIsPythonConvertibleToCppFunction(TextStream &s,
                                                         const QString &sourceTypeName,
                                                         const QString &targetTypeName,
                                                         const QString &condition,
                                                         QString pythonToCppFuncName,
                                                         bool acceptNoneAsCppNull)
{
    if (pythonToCppFuncName.isEmpty())
        pythonToCppFuncName = pythonToCppFunctionName(sourceTypeName, targetTypeName);

    s << "static PythonToCppFunc " << convertibleToCppFunctionName(sourceTypeName, targetTypeName);
    s << "(PyObject *pyIn)\n{\n" << indent;
    if (acceptNoneAsCppNull) {
        s << "if (pyIn == Py_None)\n" << indent
            << "return Shiboken::Conversions::nonePythonToCppNullPtr;\n" << outdent;
    } else {
        if (!condition.contains(u"pyIn"))
            s << sbkUnusedVariableCast(u"pyIn"_s);
    }
    s << "if (" << condition << ")\n" << indent
        << "return " << pythonToCppFuncName << ";\n" << outdent
        << "return {};\n" << outdent << "}\n";
}

void CppGenerator::writePythonToCppConversionFunctions(TextStream &s,
                                                       const AbstractMetaType &sourceType,
                                                       const AbstractMetaType &targetType,
                                                       QString typeCheck,
                                                       QString conversion,
                                                       const QString &preConversion) const
{
    QString sourcePyType = cpythonTypeNameExt(sourceType);

    // Python to C++ conversion function.
    StringStream c(TextStream::Language::Cpp);
    if (conversion.isEmpty())
        conversion = u'*' + cpythonWrapperCPtr(sourceType, u"pyIn"_s);
    if (!preConversion.isEmpty())
        c << preConversion << '\n';
    const QString fullTypeName = targetType.isSmartPointer()
        ? targetType.cppSignature()
        : getFullTypeName(targetType.typeEntry());
    c << "*reinterpret_cast<" << fullTypeName << " *>(cppOut) = "
        << fullTypeName << '('
        << (sourceType.isUniquePointer() ? stdMove(conversion) : conversion)
        << ");";
    QString sourceTypeName = fixedCppTypeName(sourceType);
    QString targetTypeName = fixedCppTypeName(targetType);
    writePythonToCppFunction(s, c.toString(), sourceTypeName, targetTypeName);

    // Python to C++ convertible check function.
    if (typeCheck.isEmpty())
        typeCheck = u"PyObject_TypeCheck(pyIn, "_s + sourcePyType + u')';
    writeIsPythonConvertibleToCppFunction(s, sourceTypeName, targetTypeName, typeCheck);
    s << '\n';
}

void CppGenerator::writePythonToCppConversionFunctions(TextStream &s,
                                                      const TargetToNativeConversion &toNative,
                                                      const TypeEntryCPtr &targetType) const
{
    // Python to C++ conversion function.
    QString code = toNative.conversion();
    QString inType;
    if (toNative.sourceType())
        inType = cpythonTypeNameExt(toNative.sourceType());
    else
        inType = u'(' + toNative.sourceTypeName() + u"_TypeF())"_s;
    code.replace(u"%INTYPE"_s, inType);
    code.replace(u"%OUTTYPE"_s, targetType->qualifiedCppName());
    code.replace(u"%in"_s, u"pyIn"_s);
    code.replace(u"%out"_s,
                 u"*reinterpret_cast<"_s + getFullTypeName(targetType) + u" *>(cppOut)"_s);

    QString sourceTypeName = fixedCppTypeName(toNative);
    QString targetTypeName = fixedCppTypeName(targetType);
    writePythonToCppFunction(s, code, sourceTypeName, targetTypeName);

    // Python to C++ convertible check function.
    QString typeCheck = toNative.sourceTypeCheck();
    if (typeCheck.isEmpty()) {
        QString pyTypeName = toNative.sourceTypeName();
        if (pyTypeName == u"Py_None" || pyTypeName == u"PyNone")
            typeCheck = u"%in == Py_None"_s;
        else if (pyTypeName == u"SbkEnumType")
            typeCheck = u"Shiboken::isShibokenEnum(%in)"_s;
        else if (pyTypeName == u"SbkObject")
            typeCheck = u"Shiboken::Object::checkType(%in)"_s;
    }
    if (typeCheck.isEmpty()) {
        if (!toNative.sourceType() || toNative.sourceType()->isPrimitive()) {
            QString m;
            QTextStream(&m) << "User added implicit conversion for C++ type '" << targetType->qualifiedCppName()
                << "' must provide either an input type check function or a non primitive type entry.";
            throw Exception(m);
        }
        typeCheck = u"PyObject_TypeCheck(%in, "_s
                    + cpythonTypeNameExt(toNative.sourceType()) + u')';
    }
    typeCheck.replace(u"%in"_s, u"pyIn"_s);
    processCodeSnip(typeCheck);
    writeIsPythonConvertibleToCppFunction(s, sourceTypeName, targetTypeName, typeCheck);
}

void CppGenerator::writePythonToCppConversionFunctions(TextStream &s, const AbstractMetaType &containerType) const
{
    Q_ASSERT(containerType.typeEntry()->isContainer());
    const auto cte = std::static_pointer_cast<const ContainerTypeEntry>(containerType.typeEntry());
    const auto customConversion = cte->customConversion();
    for (const auto &conv : customConversion->targetToNativeConversions())
        writePythonToCppConversionFunction(s, containerType, conv);
}

void CppGenerator::writePythonToCppConversionFunction(TextStream &s,
                                                      const AbstractMetaType &containerType,
                                                      const TargetToNativeConversion &conv) const
{
    // Python to C++ conversion function.
    QString cppTypeName = getFullTypeNameWithoutModifiers(containerType);
    QString code = conv.conversion();
    const QString line = u"auto &cppOutRef = *reinterpret_cast<"_s
        + cppTypeName + u" *>(cppOut);"_s;
    CodeSnipAbstract::prependCode(&code, line);
    for (qsizetype i = 0; i < containerType.instantiations().size(); ++i) {
        const AbstractMetaType &type = containerType.instantiations().at(i);
        QString typeName = getFullTypeName(type);
        // Containers of opaque containers are not handled here.
        const auto generatorArg = GeneratorArgument::fromMetaType(type);
        if (generatorArg.indirections > 0 && !type.generateOpaqueContainer()) {
            for (int pos = 0; ; ) {
                const QRegularExpressionMatch match = convertToCppRegEx().match(code, pos);
                if (!match.hasMatch())
                    break;
                pos = match.capturedEnd();
                const QString varName = match.captured(1);
                QString rightCode = code.mid(pos);
                rightCode.replace(varName, u'*' + varName);
                code.replace(pos, code.size() - pos, rightCode);
            }
            typeName.append(u" *"_s);
        }
        code.replace(u"%OUTTYPE_"_s + QString::number(i), typeName);
    }
    code.replace(u"%OUTTYPE"_s, cppTypeName);
    code.replace(u"%in"_s, u"pyIn"_s);
    code.replace(u"%out"_s, u"cppOutRef"_s);
    QString typeName = fixedCppTypeName(containerType);
    const QString &sourceTypeName = conv.sourceTypeName();
    writePythonToCppFunction(s, code, sourceTypeName, typeName);

    // Python to C++ convertible check function.
    QString typeCheck = cpythonCheckFunction(containerType);
    if (typeCheck.isEmpty())
        typeCheck = u"false"_s;
    else
        typeCheck = typeCheck + u"pyIn)"_s;
    writeIsPythonConvertibleToCppFunction(s, sourceTypeName, typeName, typeCheck);
    s << '\n';
}

static void writeSetConverterFunction(TextStream &s,
                                      const char *function,
                                      const QString &converterVar,
                                      const QString &pythonToCppFunc,
                                      const QString &isConvertibleFunc)
{
    s << "Shiboken::Conversions::" << function << '(' << converterVar << ',' << '\n'
        << indent << pythonToCppFunc << ',' << '\n' << isConvertibleFunc
        << outdent << ");\n";
}

void CppGenerator::writeAddPythonToCppConversion(TextStream &s, const QString &converterVar,
                                                 const QString &pythonToCppFunc,
                                                 const QString &isConvertibleFunc)
{
    writeSetConverterFunction(s, "addPythonToCppValueConversion",
                              converterVar, pythonToCppFunc, isConvertibleFunc);
}

void CppGenerator::writeSetPythonToCppPointerConversion(TextStream &s,
                                                        const QString &converterVar,
                                                        const QString &pythonToCppFunc,
                                                        const QString &isConvertibleFunc)
{
    writeSetConverterFunction(s, "setPythonToCppPointerFunctions",
                              converterVar, pythonToCppFunc, isConvertibleFunc);
}

// PYSIDE-1986: Some QObject derived classes, (QVBoxLayout) do not have default
// arguments, which breaks setting properties by named arguments. Force the
// handling code to be generated nevertheless for applicable widget classes,
// so that the mechanism of falling through to the error handling to set
// the properties works nevertheless.
static bool forceQObjectNamedArguments(const AbstractMetaFunctionCPtr &func)
{
    if (func->functionType() != AbstractMetaFunction::ConstructorFunction)
        return false;
    const auto owner = func->ownerClass();
    Q_ASSERT(owner);
    if (!isQObject(owner))
        return false;
    const QString &name = owner->name();
    return name == u"QVBoxLayout" || name == u"QHBoxLayout"
        || name == u"QSplitterHandle" || name == u"QSizeGrip";
}

void CppGenerator::writeNamedArgumentResolution(TextStream &s, const AbstractMetaFunctionCPtr &func,
                                                bool usePyArgs, const OverloadData &overloadData) const
{
    const AbstractMetaArgumentList &args = OverloadData::getArgumentsWithDefaultValues(func);
    const bool hasDefaultArguments = !args.isEmpty();
    const bool force = !hasDefaultArguments && usePySideExtensions()
        && forceQObjectNamedArguments(func);
    if (!hasDefaultArguments && !force) {
        if (overloadData.hasArgumentWithDefaultValue()) {
            // PySide-535: Allow for empty dict instead of nullptr in PyPy
            s << "if (kwds && PyDict_Size(kwds) > 0) {\n" << indent
                << "errInfo.reset(kwds);\n"
                << "Py_INCREF(errInfo.object());\n"
                << "goto " << cpythonFunctionName(func) << "_TypeError;\n"
                << outdent << "}\n";
        }
        return;
    }

    // PySide-535: Allow for empty dict instead of nullptr in PyPy
    s << "if (kwds && PyDict_Size(kwds) > 0) {\n" << indent;
    if (!force)
        s << "PyObject *value{};\n";
    s << "Shiboken::AutoDecRef kwds_dup(PyDict_Copy(kwds));\n";
    for (const AbstractMetaArgument &arg : args) {
        const int pyArgIndex = arg.argumentIndex()
            - OverloadData::numberOfRemovedArguments(func, arg.argumentIndex());
        QString pyArgName = usePyArgs ? pythonArgsAt(pyArgIndex)
                                      : PYTHON_ARG;
        QString pyKeyName = u"key_"_s + arg.name();
        s << "static PyObject *const " << pyKeyName
            << " = Shiboken::String::createStaticString(\"" << arg.name() << "\");\n"
            << "if (PyDict_Contains(kwds, " << pyKeyName << ")) {\n" << indent
            << "value = PyDict_GetItem(kwds, " << pyKeyName << ");\n"
            << "if (value && " << pyArgName << ") {\n" << indent
            << "errInfo.reset(" << pyKeyName << ");\n"
            << "Py_INCREF(errInfo.object());\n"
            << "goto " << cpythonFunctionName(func) << "_TypeError;\n"
            << outdent << "}\nif (value) {\n" << indent
            << pyArgName << " = value;\nif (!";
        const auto &type = arg.modifiedType();
        writeTypeCheck(s, type, pyArgName, isNumber(type.typeEntry()), {});
        s << ")\n" << indent
            << "goto " << cpythonFunctionName(func) << "_TypeError;\n" << outdent
            << outdent
            << "}\nPyDict_DelItem(kwds_dup, " << pyKeyName << ");\n"
            << outdent << "}\n";
    }
    // PYSIDE-1305: Handle keyword args correctly.
    // Normal functions handle their parameters immediately.
    // For constructors that are QObject, we need to delay that
    // until extra keyword signals and properties are handled.
    s << "if (PyDict_Size(kwds_dup) > 0) {\n" << indent
        << "errInfo.reset(kwds_dup.release());\n";
    if (!(func->isConstructor() && isQObject(func->ownerClass())))
        s << "goto " << cpythonFunctionName(func) << "_TypeError;\n";
    else
        s << "// fall through to handle extra keyword signals and properties\n";
    s << outdent << "}\n"
        << outdent << "}\n";
}

QString CppGenerator::argumentNameFromIndex(const ApiExtractorResult &api,
                                            const AbstractMetaFunctionCPtr &func, int argIndex)
{
    switch (argIndex) {
    case -1:
        return u"self"_s;
    case 0:
        return PYTHON_RETURN_VAR;
    case 1: { // Single argument?
        OverloadData data(getFunctionGroups(func->implementingClass()).value(func->name()), api);
        if (!data.pythonFunctionWrapperUsesListOfArguments())
            return PYTHON_ARG;
        break;
    }
    }
    return pythonArgsAt(argIndex - 1);
}

AbstractMetaClassCPtr
CppGenerator::argumentClassFromIndex(const ApiExtractorResult &api,
                                     const AbstractMetaFunctionCPtr &func, int argIndex)
{
    if (argIndex == -1)
        return func->implementingClass();

    AbstractMetaType type;
    if (argIndex == 0) {
        type = func->type();
    } else {
        const int arg = argIndex - 1;
        const int realIndex = arg - OverloadData::numberOfRemovedArguments(func, arg);
        type = func->arguments().at(realIndex).type();
    }

    if (type.typeEntry()->isContainer()) {
        // only support containers with 1 type
        if (type.instantiations().size() == 1)
            type = type.instantiations().constFirst();
    }

    auto te = type.typeEntry();
    if (type.isVoid() || !te->isComplex())
        throw Exception(msgInvalidArgumentModification(func, argIndex));
    const auto result = AbstractMetaClass::findClass(api.classes(), te);
    if (!result)
        throw Exception(msgClassNotFound(te));
    return result;
}

const char tryBlock[] = R"(
PyObject *errorType{};
PyObject *errorString{};
try {
)";

const char defaultExceptionHandling[] = R"(} catch (const std::exception &e) {
    errorType = PyExc_RuntimeError;
    errorString = Shiboken::String::fromCString(e.what());
} catch (...) {
    errorType = PyExc_RuntimeError;
    errorString = Shiboken::Messages::unknownException();
}
)";

const char propagateException[] = R"(
if (errorType != nullptr)
    PyErr_SetObject(errorType, errorString);
)";

static QString explicitConversion(QString v, const AbstractMetaType &t)
{
    return t.plainType().cppSignature() + u'(' + v + u')';
}

void CppGenerator::writeMethodCall(TextStream &s, const AbstractMetaFunctionCPtr &func,
                                   const GeneratorContext &context, bool usesPyArgs,
                                   int maxArgs,
                                   const QList<qsizetype> &argumentIndirections,
                                   ErrorReturn errorReturn) const
{
    s << "// " << func->minimalSignature() << (func->isReverseOperator() ? " [reverse operator]": "") << '\n';
    if (func->isConstructor()) {
        const CodeSnipList &snips = func->injectedCodeSnips();
        for (const CodeSnip &cs : snips) {
            if (cs.position == TypeSystem::CodeSnipPositionEnd) {
                auto klass = func->ownerClass();
                s << "overloadId = "
                  << klass->functions().indexOf(func)
                  << ";\n";
                break;
            }
        }
    }

    if (func->isAbstract()) {
        s << "if (Shiboken::Object::hasCppWrapper(reinterpret_cast<SbkObject *>(self))) {\n"
            << indent << "Shiboken::Errors::setPureVirtualMethodError(\""
            << func->ownerClass()->name() << '.' << func->name() << "\");\n"
            << errorReturn << outdent << "}\n";
    }

    // Used to provide contextual information to custom code writer function.
    const AbstractMetaArgument *lastArg = nullptr;

    CodeSnipList snips;
    if (func->hasInjectedCode()) {
        snips = func->injectedCodeSnips();

        // Find the last argument available in the method call to provide
        // the injected code writer with information to avoid invalid replacements
        // on the %# variable.
        if (maxArgs > 0 && maxArgs < func->arguments().size() - OverloadData::numberOfRemovedArguments(func)) {
            int removedArgs = 0;
            for (int i = 0; i < maxArgs + removedArgs; i++) {
                if (func->arguments().at(i).isModifiedRemoved())
                    removedArgs++;
            }
        } else if (maxArgs != 0 && !func->arguments().isEmpty()) {
            lastArg = &func->arguments().constLast();
        }

        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionBeginning, TypeSystem::TargetLangCode, func,
                       usesPyArgs, lastArg);
    }

    writeConversionRule(s, func, TypeSystem::NativeCode, usesPyArgs);

    bool generateExceptionHandling = false;

    if (!func->isUserAdded()) {
        QStringList userArgs;
        if (func->functionType() != AbstractMetaFunction::CopyConstructorFunction) {
            int removedArgs = 0;
            for (int i = 0; i < maxArgs + removedArgs; i++) {
                const AbstractMetaArgument &arg = func->arguments().at(i);
                const bool hasConversionRule =
                    func->hasConversionRule(TypeSystem::NativeCode, arg.argumentIndex() + 1);
                if (arg.isModifiedRemoved()) {
                    // If some argument with default value is removed from a
                    // method signature, the said value must be explicitly
                    // added to the method call.
                    removedArgs++;

                    // If have conversion rules I will use this for removed args
                    if (hasConversionRule)
                        userArgs << arg.name() + CONV_RULE_OUT_VAR_SUFFIX;
                    else if (!arg.defaultValueExpression().isEmpty())
                        userArgs.append(CPP_ARG_REMOVED + QString::number(i));
                } else {
                    if (hasConversionRule) {
                        userArgs.append(arg.name() + CONV_RULE_OUT_VAR_SUFFIX);
                    } else {
                        const int idx = arg.argumentIndex() - removedArgs;
                        const auto deRef = argumentIndirections.at(i);
                        QString argName = AbstractMetaType::dereferencePrefix(deRef)
                                          + CPP_ARG + QString::number(idx);
                        userArgs.append(argName);
                    }
                }
                // "Pass unique ptr by value" pattern: Apply std::move()
                auto type = arg.type();
                if (type.isUniquePointer() && type.passByValue())
                    userArgs.last() = stdMove(userArgs.constLast());
                else if (type.viewOn() != nullptr)
                    userArgs.last() = explicitConversion(userArgs.constLast(), type);
            }

            // If any argument's default value was modified the method must be called
            // with this new value whenever the user doesn't pass an explicit value to it.
            // Also, any unmodified default value coming after the last user specified
            // argument and before the modified argument must be explicitly stated.
            QStringList otherArgs;
            bool otherArgsModified = false;
            bool argsClear = true;
            for (auto i = func->arguments().size() - 1; i >= maxArgs + removedArgs; i--) {
                const AbstractMetaArgument &arg = func->arguments().at(i);
                const bool defValModified = arg.hasModifiedDefaultValueExpression();
                const bool hasConversionRule =
                    func->hasConversionRule(TypeSystem::NativeCode, arg.argumentIndex() + 1);
                if (argsClear && !defValModified && !hasConversionRule)
                    continue;
                argsClear = false;
                otherArgsModified |= defValModified || hasConversionRule || arg.isModifiedRemoved();
                if (hasConversionRule)
                    otherArgs.prepend(arg.name() + CONV_RULE_OUT_VAR_SUFFIX);
                else
                    otherArgs.prepend(CPP_ARG_REMOVED + QString::number(i));
            }
            if (otherArgsModified)
                userArgs << otherArgs;
        }

        bool isCtor = false;
        StringStream mc(TextStream::Language::Cpp);

        StringStream uva(TextStream::Language::Cpp);
        if (func->isOperatorOverload() && !func->isCallOperator()) {
            QString firstArg(u'(');
            if (!func->isPointerOperator()) // no de-reference operator
                firstArg += u'*';
            firstArg += CPP_SELF_VAR;
            firstArg += u')';
            QString secondArg = CPP_ARG0;
            if (!func->isUnaryOperator())
                AbstractMetaType::applyDereference(&secondArg, argumentIndirections.at(0));

            if (func->isUnaryOperator())
                std::swap(firstArg, secondArg);

            QString op = func->originalName();
            op.remove(0, int(std::strlen("operator")));

            if (func->isBinaryOperator()) {
                if (func->isReverseOperator())
                    std::swap(firstArg, secondArg);

                // Emulate operator+=/-= (__iadd__, __isub__) by using ++/--
                if (((op == u"++") || (op == u"--")) && !func->isReverseOperator())  {
                    s  << "\nfor (int i = 0; i < " << secondArg
                        << "; ++i, " << op << firstArg << ");\n";
                    mc << firstArg;
                } else {
                    mc << firstArg << ' ' << op << ' ' << secondArg;
                }
            } else {
                mc << op << ' ' << secondArg;
            }
        } else if (!injectedCodeCallsCppFunction(context, func)) {
            if (func->isConstructor()) {
                isCtor = true;
                const auto owner = func->ownerClass();
                Q_ASSERT(owner == context.metaClass());
                if (func->functionType() == AbstractMetaFunction::CopyConstructorFunction
                    && maxArgs == 1) {
                    mc << "new ::" << context.effectiveClassName()
                        << "(*" << CPP_ARG0 << ')';
                } else {
                    const QString ctorCall = context.effectiveClassName() + u'('
                                             + userArgs.join(u", "_s) + u')';
                    if (usePySideExtensions() && isQObject(owner)) {
                        s << "void *addr = PySide::nextQObjectMemoryAddr();\n";
                        uva << "if (addr) {\n" << indent
                            << "cptr = new (addr) ::" << ctorCall << ";\n"
                            << "PySide::setNextQObjectMemoryAddr(nullptr);\n" << outdent
                            << "} else {\n" << indent
                            << "cptr = new ::" << ctorCall << ";\n"
                            << outdent << "}\n";
                    } else {
                        mc << "new ::" << ctorCall;
                    }
                }
            } else {
                QString methodCallClassName;
                if (context.forSmartPointer())
                    methodCallClassName = context.preciseType().cppSignature();
                else if (func->ownerClass())
                    methodCallClassName = func->ownerClass()->qualifiedCppName();

                if (auto ownerClass = func->ownerClass()) {
                    const bool hasWrapper = shouldGenerateCppWrapper(ownerClass);
                    if (!avoidProtectedHack() || !func->isProtected() || !hasWrapper) {
                        if (func->isStatic()) {
                            mc << "::" << methodCallClassName << "::";
                        } else {
                            const QString cppSelfVar = CPP_SELF_VAR;
                            const QString selfVarCast = func->ownerClass() == func->implementingClass()
                                ? cppSelfVar
                                : u"reinterpret_cast<"_s + methodCallClassName
                                  + u" *>("_s + cppSelfVar + u')';
                            if (func->isConstant()) {
                                if (avoidProtectedHack()) {
                                    mc << "const_cast<const ::";
                                    if (ownerClass->cppWrapper().testFlag(AbstractMetaClass::CppProtectedHackWrapper)) {
                                        // PYSIDE-500: Need a special wrapper cast when inherited
                                        const QString selfWrapCast = ownerClass == func->implementingClass()
                                            ? cppSelfVar
                                            : u"reinterpret_cast<"_s + wrapperName(ownerClass)
                                              + u" *>("_s + cppSelfVar + u')';
                                        mc << wrapperName(ownerClass);
                                        mc << " *>(" << selfWrapCast << ")->";
                                    }
                                    else {
                                        mc << methodCallClassName;
                                        mc << " *>(" << selfVarCast << ")->";
                                    }
                                } else {
                                    mc << "const_cast<const ::" << methodCallClassName;
                                    mc <<  " *>(" << selfVarCast << ")->";
                                }
                            } else {
                                mc << selfVarCast << "->";
                            }
                        }

                        if (!func->isAbstract() && func->isVirtual())
                            mc << "::%CLASS_NAME::";

                        mc << func->originalName();
                    } else {
                        if (!func->isStatic()) {
                            const bool directInheritance = context.metaClass() == ownerClass;
                            mc << (directInheritance ? "static_cast" : "reinterpret_cast")
                                << "<::" << wrapperName(ownerClass) << " *>(" << CPP_SELF_VAR << ")->";
                        }

                        if (!func->isAbstract())
                            mc << (func->isProtected() ? wrapperName(func->ownerClass()) :
                                                         u"::"_s
                                                         + methodCallClassName) << "::";
                        mc << func->originalName() << "_protected";
                    }
                } else {
                    mc << func->originalName();
                }
                mc << '(' << userArgs.join(u", "_s) << ')';
                if (!func->isAbstract() && func->isVirtual()) {
                    if (!avoidProtectedHack() || !func->isProtected()) {
                        QString virtualCall = mc;
                        QString normalCall = virtualCall;
                        virtualCall.replace(u"%CLASS_NAME"_s,
                                            methodCallClassName);
                        normalCall.remove(u"::%CLASS_NAME::"_s);
                        mc.clear();
                        mc << "Shiboken::Object::hasCppWrapper(reinterpret_cast<SbkObject *>(self))\n"
                            << "    ? " << virtualCall << '\n'
                            << "    : " <<  normalCall;
                    }
                }
            }
        }

        if (!injectedCodeCallsCppFunction(context, func)) {
            const bool allowThread = func->allowThread();
            generateExceptionHandling = func->generateExceptionHandling();
            if (generateExceptionHandling) {
                s << tryBlock << indent;
                if (allowThread) {
                    s << "Shiboken::ThreadStateSaver threadSaver;\n"
                        << "threadSaver.save();\n";
                }
            } else if (allowThread) {
                s << BEGIN_ALLOW_THREADS << '\n';
            }
            if (isCtor) {
                if (uva.size() > 0)
                    s << uva.toString() << '\n';
                else
                    s << "cptr = " << mc.toString() << ";\n";
            } else if (!func->isVoid() && !func->isInplaceOperator()) {
                bool writeReturnType = true;
                if (avoidProtectedHack()) {
                    auto metaEnum = api().findAbstractMetaEnum(func->type().typeEntry());
                    if (metaEnum.has_value()) {
                        QString enumName;
                        if (metaEnum->isProtected()) {
                            enumName = context.wrapperName() + u"::"_s
                                       + metaEnum.value().name();
                        } else {
                            enumName = func->type().cppSignature();
                        }
                        const QString methodCall = enumName + u'('
                                                   + mc.toString() + u')';
                        mc.clear();
                        mc << methodCall;
                        s << enumName;
                        writeReturnType = false;
                    }
                }
                QString methodCall = mc.toString();
                if (writeReturnType) {
                    s << func->type().cppSignature();
                    if (func->type().isObjectTypeUsedAsValueType()) {
                        s << '*';
                        methodCall = u"new "_s
                                     + func->type().typeEntry()->qualifiedCppName()
                                     + u'(' + mc.toString() + u')';
                    }
                }
                s << " " << CPP_RETURN_VAR << " = " << methodCall << ";\n";
            } else {
                s << mc.toString() << ";\n";
            }

            if (allowThread) {
                s << (generateExceptionHandling
                      ? u"threadSaver.restore();"_s : END_ALLOW_THREADS) << '\n';
            }

            // Convert result
            const auto funcType = func->type();
            if (func->hasConversionRule(TypeSystem::TargetLangCode, 0)) {
                writeConversionRule(s, func, TypeSystem::TargetLangCode,
                                    PYTHON_RETURN_VAR);
            } else if (!isCtor && !func->isInplaceOperator() && !func->isVoid()
                && !func->injectedCodeHasReturnValueAttribution(TypeSystem::TargetLangCode)) {
                if (func->type().isObjectTypeUsedAsValueType()) {
                    s << PYTHON_RETURN_VAR << " = Shiboken::Object::newObject("
                        << cpythonTypeNameExt(func->type().typeEntry())
                        << ", " << CPP_RETURN_VAR << ", true, true)";
                } else if (func->generateOpaqueContainerReturn()) {
                    const QString creationFunc = opaqueContainerCreationFunc(funcType);
                    writeOpaqueContainerCreationFuncDecl(s, creationFunc, funcType);
                    s << PYTHON_RETURN_VAR << " = " << creationFunc
                        << "(&" << CPP_RETURN_VAR << ");\n";
                } else {
                    s << PYTHON_RETURN_VAR << " = ";
                    writeToPythonConversion(s, funcType, func->ownerClass(),
                                            CPP_RETURN_VAR);
                }
                s << ";\n";
            }

            if (generateExceptionHandling) { // "catch" code
                s << outdent << defaultExceptionHandling;
            }
        } // !injected code calls C++ function
    } // !userAdded

    if (func->hasInjectedCode() && !func->isConstructor())
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionEnd,
                       TypeSystem::TargetLangCode, func, usesPyArgs, lastArg);

    bool hasReturnPolicy = false;

    // Ownership transference between C++ and Python.
    QList<ArgumentModification> ownership_mods;
    // Python object reference management.
    QList<ArgumentModification> refcount_mods;
    for (const auto &func_mod : func->modifications()) {
        for (const ArgumentModification &arg_mod : func_mod.argument_mods()) {
            if (arg_mod.targetOwnerShip() != TypeSystem::UnspecifiedOwnership)
                ownership_mods.append(arg_mod);
            else if (!arg_mod.referenceCounts().isEmpty())
                refcount_mods.append(arg_mod);
        }
    }

    // If there's already a setParent(return, me), don't use the return heuristic!
    if (func->argumentOwner(func->ownerClass(), -1).index == 0)
        hasReturnPolicy = true;

    if (!ownership_mods.isEmpty()) {
        s  << '\n' << "// Ownership transferences.\n";
        for (const ArgumentModification &arg_mod : std::as_const(ownership_mods)) {
            const int argIndex = arg_mod.index();
            const QString pyArgName = argumentNameFromIndex(api(), func, argIndex);

            if (argIndex == 0 || arg_mod.owner().index == 0)
                hasReturnPolicy = true;

            // The default ownership does nothing. This is useful to avoid automatic heuristically
            // based generation of code defining parenting.
            const auto ownership = arg_mod.targetOwnerShip();
            if (ownership == TypeSystem::DefaultOwnership)
                continue;

            s << "Shiboken::Object::";
            if (ownership == TypeSystem::TargetLangOwnership) {
                s << "getOwnership(" << pyArgName << ");";
            } else if (auto ac = argumentClassFromIndex(api(), func, argIndex);
                       ac && ac->hasVirtualDestructor()) {
                s << "releaseOwnership(" << pyArgName << ");";
            } else {
                s << "invalidate(" << pyArgName << ");";
            }
            s << '\n';
        }

    } else if (!refcount_mods.isEmpty()) {
        for (const ArgumentModification &arg_mod : std::as_const(refcount_mods)) {
            ReferenceCount refCount = arg_mod.referenceCounts().constFirst();
            if (refCount.action != ReferenceCount::Set
                && refCount.action != ReferenceCount::Remove
                && refCount.action != ReferenceCount::Add) {
                qCWarning(lcShiboken) << "\"set\", \"add\" and \"remove\" are the only values supported by Shiboken for action attribute of reference-count tag.";
                continue;
            }
            const int argIndex = arg_mod.index();
            const QString pyArgName = refCount.action == ReferenceCount::Remove
                ? u"Py_None"_s : argumentNameFromIndex(api(), func, argIndex);

            if (refCount.action == ReferenceCount::Add || refCount.action == ReferenceCount::Set)
                s << "Shiboken::Object::keepReference(";
            else
                s << "Shiboken::Object::removeReference(";

            s << "reinterpret_cast<SbkObject *>(self), \"";
            QString varName = arg_mod.referenceCounts().constFirst().varName;
            if (varName.isEmpty())
                varName = func->minimalSignature() + QString::number(argIndex);

            s << varName << "\", " << pyArgName
              << (refCount.action == ReferenceCount::Add ? ", true" : "")
              << ");\n";

            if (argIndex == 0)
                hasReturnPolicy = true;
        }
    }
    writeParentChildManagement(s, func, usesPyArgs, !hasReturnPolicy);

    if (generateExceptionHandling)
        s << propagateException;
}

QStringList CppGenerator::getAncestorMultipleInheritance(const AbstractMetaClassCPtr &metaClass)
{
    QStringList result;
    const auto &baseClases = metaClass->typeSystemBaseClasses();
    if (!baseClases.isEmpty()) {
        for (const auto &baseClass : baseClases) {
            QString offset;
            QTextStream(&offset) << "reinterpret_cast<uintptr_t>(static_cast<const "
                << baseClass->qualifiedCppName() << " *>(class_ptr)) - base";
            result.append(offset);
            offset.clear();
            QTextStream(&offset) << "reinterpret_cast<uintptr_t>(static_cast<const "
                << baseClass->qualifiedCppName() << " *>(static_cast<const "
                << metaClass->qualifiedCppName()
                << " *>(static_cast<const void *>(class_ptr)))) - base";
            result.append(offset);
        }

        for (const auto &baseClass : baseClases)
            result.append(getAncestorMultipleInheritance(baseClass));
    }
    return result;
}

void CppGenerator::writeMultipleInheritanceInitializerFunction(TextStream &s,
                                                               const AbstractMetaClassCPtr &metaClass)
{
    QString className = metaClass->qualifiedCppName();
    const QStringList ancestors = getAncestorMultipleInheritance(metaClass);
    s  << "int *\n"
        << multipleInheritanceInitializerFunctionName(metaClass) << "(const void *cptr)\n"
        << "{\n" << indent;
    s << "static int mi_offsets[] = { ";
    for (qsizetype i = 0; i < ancestors.size(); i++)
        s << "-1, ";
    s << "-1 };\n"
        << "if (mi_offsets[0] == -1) {\n" << indent
        << "std::set<int> offsets;\n"
            << "const auto *class_ptr = reinterpret_cast<const " << className << " *>(cptr);\n"
            << "const auto base = reinterpret_cast<uintptr_t>(class_ptr);\n";

    for (const QString &ancestor : ancestors)
        s << "offsets.insert(int(" << ancestor << "));\n";

    s << "\noffsets.erase(0);\n\n"
        << "std::copy(offsets.cbegin(), offsets.cend(), mi_offsets);\n" << outdent
        << "}\nreturn mi_offsets;\n" << outdent << "}\n";
}

void CppGenerator::writeSpecialCastFunction(TextStream &s, const AbstractMetaClassCPtr &metaClass)
{
    QString className = metaClass->qualifiedCppName();
    s << "static void * " << cpythonSpecialCastFunctionName(metaClass)
        << "(void *obj, PyTypeObject *desiredType)\n{\n" << indent
        << "auto me = reinterpret_cast< ::" << className << " *>(obj);\n";
    bool firstClass = true;
    const auto &allAncestors = metaClass->allTypeSystemAncestors();
    for (const auto &baseClass : allAncestors) {
        if (!firstClass)
            s << "else ";
        s << "if (desiredType == " << cpythonTypeNameExt(baseClass->typeEntry())
            << ")\n" << indent
            << "return static_cast< ::" << baseClass->qualifiedCppName() << " *>(me);\n"
            << outdent;
        firstClass = false;
    }
    s << "return me;\n" << outdent << "}\n\n";
}

void CppGenerator::writePrimitiveConverterInitialization(TextStream &s,
                                                         const CustomConversionPtr &customConversion)
{
    TypeEntryCPtr type = customConversion->ownerType();
    QString converter = converterObject(type);
    s << "// Register converter for type '" << type->qualifiedTargetLangName() << "'.\n"
        << converter << " = Shiboken::Conversions::createConverter(";
    if (!type->hasTargetLangApiType())
        s << "nullptr";
    else if (type->targetLangApiName() == cPyObjectT())
        s << "&PyBaseObject_Type";
    else
        s << '&' << type->targetLangApiName() << "_Type";
    QString typeName = fixedCppTypeName(type);
    s << ", " << cppToPythonFunctionName(typeName, typeName) << ");\n"
        << "Shiboken::Conversions::registerConverterName(" << converter << ", \""
        << type->qualifiedCppName() << "\");\n";
    writeCustomConverterRegister(s, customConversion, converter);
}

static void registerEnumConverterScopes(TextStream &s, QString signature)
{
    while (true) {
        s << "Shiboken::Conversions::registerConverterName(converter, \""
          << signature << "\");\n";
        const int qualifierPos = signature.indexOf(u"::");
        if (qualifierPos != -1)
            signature.remove(0, qualifierPos + 2);
        else
            break;
    }
}

void CppGenerator::writeFlagsConverterInitialization(TextStream &s,
                                                     const FlagsTypeEntryCPtr &flags)
{
    static const char enumPythonVar[] = "FType";

    const QString qualifiedCppName = flags->qualifiedCppName();
    s << "// Register converter for flag '" << qualifiedCppName << "'.\n{\n"
        << indent;
    QString typeName = fixedCppTypeName(flags);
    s << "SbkConverter *converter = Shiboken::Conversions::createConverter("
        << enumPythonVar << ',' << '\n' << indent
        << cppToPythonFunctionName(typeName, typeName) << ");\n" << outdent;

    const QString enumTypeName = fixedCppTypeName(flags->originator());
    QString toCpp = pythonToCppFunctionName(enumTypeName, typeName);
    QString isConv = convertibleToCppFunctionName(enumTypeName, typeName);
    writeAddPythonToCppConversion(s, u"converter"_s, toCpp, isConv);
    toCpp = pythonToCppFunctionName(typeName, typeName);
    isConv = convertibleToCppFunctionName(typeName, typeName);
    writeAddPythonToCppConversion(s, u"converter"_s, toCpp, isConv);
    toCpp = pythonToCppFunctionName(u"number"_s, typeName);
    isConv = convertibleToCppFunctionName(u"number"_s, typeName);
    writeAddPythonToCppConversion(s, u"converter"_s, toCpp, isConv);
    s << "Shiboken::Enum::setTypeConverter(" << enumPythonVar
        << ", converter, true);\n";
    // Replace "QFlags<Class::Option>" by "Class::Options"
    QString signature = qualifiedCppName;
    if (qualifiedCppName.startsWith(u"QFlags<") && qualifiedCppName.endsWith(u'>')) {
        signature.chop(1);
        signature.remove(0, 7);
        const int lastQualifierPos = signature.lastIndexOf(u"::");
        if (lastQualifierPos != -1) {
            signature.replace(lastQualifierPos + 2, signature.size() - lastQualifierPos - 2,
                              flags->flagsName());
        } else {
            signature = flags->flagsName();
        }
    }

    registerEnumConverterScopes(s, signature);

    // PYSIDE-1673: Also register "QFlags<Class::Option>" purely for
    // the purpose of finding the converter by QVariant::typeName()
    // in the QVariant conversion code.
    s << "Shiboken::Conversions::registerConverterName(converter, \""
        << flags->name() << "\");\n"
        << outdent << "}\n";
}

void CppGenerator::writeEnumConverterInitialization(TextStream &s, const AbstractMetaEnum &metaEnum)
{
    if (metaEnum.isPrivate() || metaEnum.isAnonymous())
        return;
    EnumTypeEntryCPtr enumType = metaEnum.typeEntry();
    Q_ASSERT(enumType);

    static const char enumPythonVar[] = "EType";

    s << "// Register converter for enum '" << enumType->qualifiedCppName()
        << "'.\n{\n" << indent;

    const QString typeName = fixedCppTypeName(enumType);
    s << "SbkConverter *converter = Shiboken::Conversions::createConverter("
        << enumPythonVar << ',' << '\n' << indent
        << cppToPythonFunctionName(typeName, typeName) << ");\n" << outdent;

    const QString toCpp = pythonToCppFunctionName(typeName, typeName);
    const QString isConv = convertibleToCppFunctionName(typeName, typeName);
    writeAddPythonToCppConversion(s, u"converter"_s, toCpp, isConv);
    s << "Shiboken::Enum::setTypeConverter(" << enumPythonVar
        << ", converter, false);\n";

    registerEnumConverterScopes(s, enumType->qualifiedCppName());

    s << outdent << "}\n";

    if (auto flags = enumType->flags())
        writeFlagsConverterInitialization(s, flags);
}

QString CppGenerator::writeContainerConverterInitialization(TextStream &s, const AbstractMetaType &type) const
{
    QByteArray cppSignature = QMetaObject::normalizedSignature(type.cppSignature().toUtf8());
    s << "// Register converter for type '" << cppSignature << "'.\n";
    QString converter = converterObject(type);
    s << converter << " = Shiboken::Conversions::createConverter(";

    Q_ASSERT(type.typeEntry()->isContainer());
    const auto typeEntry = std::static_pointer_cast<const ContainerTypeEntry>(type.typeEntry());

    const QString targetTypeName = containerNativeToTargetTypeName(typeEntry);
    if (targetTypeName == cPyObjectT()) {
        s << "&PyBaseObject_Type";
    } else {
        s << '&' << targetTypeName << "_Type";
    }

    const QString typeName = fixedCppTypeName(type);
    s << ", " << cppToPythonFunctionName(typeName, targetTypeName) << ");\n";

    for (const auto &conv : typeEntry->customConversion()->targetToNativeConversions()) {
        const QString &sourceTypeName = conv.sourceTypeName();
        QString toCpp = pythonToCppFunctionName(sourceTypeName, typeName);
        QString isConv = convertibleToCppFunctionName(sourceTypeName, typeName);
        s << "Shiboken::Conversions::registerConverterName(" << converter
            << ", \"" << cppSignature << "\");\n";
        if (usePySideExtensions() && cppSignature.startsWith("const ")
            && cppSignature.endsWith("&")) {
            cppSignature.chop(1);
            cppSignature.remove(0, sizeof("const ") / sizeof(char) - 1);
            s << "Shiboken::Conversions::registerConverterName(" << converter
                << ", \"" << cppSignature << "\");\n";
        }
        writeAddPythonToCppConversion(s, converter, toCpp, isConv);
    }
    return converter;
}

void CppGenerator::writeSmartPointerConverterInitialization(TextStream &s, const AbstractMetaType &type) const
{
    const QByteArray cppSignature = type.cppSignature().toUtf8();
    auto writeConversionRegister = [&s](const AbstractMetaType &sourceType, const QString &targetTypeName, const QString &targetConverter)
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
        if (auto opt = findSmartPointerInstantiation(smartPointerTypeEntry, baseTe)) {
            const auto smartTargetType = opt.value();
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

void CppGenerator::writeExtendedConverterInitialization(TextStream &s,
                                                        const TypeEntryCPtr &externalType,
                                                        const AbstractMetaClassCList &conversions)
{
    s << "// Extended implicit conversions for " << externalType->qualifiedTargetLangName()
      << ".\n";
    for (const auto &sourceClass : conversions) {
        const QString converterVar = cppApiVariableName(externalType->targetLangPackage()) + u'['
            + getTypeIndexVariableName(externalType) + u']';
        QString sourceTypeName = fixedCppTypeName(sourceClass->typeEntry());
        QString targetTypeName = fixedCppTypeName(externalType);
        QString toCpp = pythonToCppFunctionName(sourceTypeName, targetTypeName);
        QString isConv = convertibleToCppFunctionName(sourceTypeName, targetTypeName);
        writeAddPythonToCppConversion(s, converterVar, toCpp, isConv);
    }
}

QString CppGenerator::multipleInheritanceInitializerFunctionName(const AbstractMetaClassCPtr &metaClass)
{
    return cpythonBaseName(metaClass->typeEntry()) + u"_mi_init"_s;
}

bool CppGenerator::supportsMappingProtocol(const AbstractMetaClassCPtr &metaClass)
{
    for (const auto &m : mappingProtocols()) {
        if (metaClass->hasFunction(m.name))
            return true;
    }

    return false;
}

bool CppGenerator::supportsNumberProtocol(const AbstractMetaClassCPtr &metaClass) const
{
    return metaClass->hasArithmeticOperatorOverload()
            || metaClass->hasIncDecrementOperatorOverload()
            || metaClass->hasLogicalOperatorOverload()
            || metaClass->hasBitwiseOperatorOverload()
            || hasBoolCast(metaClass);
}

bool CppGenerator::supportsSequenceProtocol(const AbstractMetaClassCPtr &metaClass)
{
    for (const auto &seq : sequenceProtocols()) {
        if (metaClass->hasFunction(seq.name))
            return true;
    }

    ComplexTypeEntryCPtr baseType = metaClass->typeEntry()->baseContainerType();
    return baseType && baseType->isContainer();
}

bool CppGenerator::shouldGenerateGetSetList(const AbstractMetaClassCPtr &metaClass) const
{
    for (const AbstractMetaField &f : metaClass->fields()) {
        if (!f.isStatic())
            return true;
    }
    // Generate all user-added properties unless Pyside extensions are used,
    // in which only the explicitly specified ones are generated (rest is handled
    // in libpyside).
    return usePySideExtensions()
        ? std::any_of(metaClass->propertySpecs().cbegin(), metaClass->propertySpecs().cend(),
                      [] (const QPropertySpec &s) { return s.generateGetSetDef(); })
        : !metaClass->propertySpecs().isEmpty();
    return false;
}

struct pyTypeSlotEntry
{
    explicit pyTypeSlotEntry(const char *name, const QString &function) :
        m_name(name), m_function(function) {}

    const char *m_name;
    const QString &m_function;
};

TextStream &operator<<(TextStream &str, const pyTypeSlotEntry &e)
{
    str << '{' << e.m_name << ',';
    const int padding = qMax(0, 18 - int(strlen(e.m_name)));
    for (int p = 0; p < padding; ++p)
        str << ' ';
    if (e.m_function.isEmpty())
        str << NULL_PTR;
    else
        str << "reinterpret_cast<void *>(" << e.m_function << ')';
    str << "},\n";
    return str;
}

void CppGenerator::writeClassDefinition(TextStream &s,
                                        const AbstractMetaClassCPtr &metaClass,
                                        const GeneratorContext &classContext)
{
    QString tp_init;
    QString tp_new;
    QString tp_dealloc;
    QString tp_hash;
    QString tp_call;
    const QString className = chopType(cpythonTypeName(metaClass));
    QString baseClassName;
    AbstractMetaFunctionCList ctors;
    const auto &allCtors = metaClass->queryFunctions(FunctionQueryOption::AnyConstructor);
    for (const auto &f : allCtors) {
        if (!f->isPrivate() && !f->isModifiedRemoved()
            && f->functionType() != AbstractMetaFunction::MoveConstructorFunction) {
            ctors.append(f);
        }
    }

    if (!metaClass->baseClass())
        baseClassName = u"SbkObject_TypeF()"_s;

    bool onlyPrivCtor = !metaClass->hasNonPrivateConstructor();

    const bool isQApp = usePySideExtensions()
        && inheritsFrom(metaClass, u"QCoreApplication"_s);

    QString tp_flags = u"Py_TPFLAGS_DEFAULT"_s;
    if (!metaClass->attributes().testFlag(AbstractMetaClass::FinalCppClass))
        tp_flags += u"|Py_TPFLAGS_BASETYPE"_s;
    if (metaClass->isNamespace() || metaClass->hasPrivateDestructor()) {
        tp_dealloc = metaClass->hasPrivateDestructor() ?
                     u"SbkDeallocWrapperWithPrivateDtor"_s :
                     u"Sbk_object_dealloc /* PYSIDE-832: Prevent replacement of \"0\" with subtype_dealloc. */"_s;
        tp_init.clear();
    } else {
        tp_dealloc = isQApp
            ? u"&SbkDeallocQAppWrapper"_s : u"&SbkDeallocWrapper"_s;
        if (!onlyPrivCtor && !ctors.isEmpty())
            tp_init = cpythonFunctionName(ctors.constFirst());
    }

    const AttroCheck attroCheck = checkAttroFunctionNeeds(metaClass);
    const QString tp_getattro = (attroCheck & AttroCheckFlag::GetattroMask) != 0
        ? cpythonGetattroFunctionName(metaClass) : QString();
    const QString tp_setattro = (attroCheck & AttroCheckFlag::SetattroMask) != 0
        ? cpythonSetattroFunctionName(metaClass) : QString();

    if (metaClass->hasPrivateDestructor() || onlyPrivCtor) {
        // tp_flags = u"Py_TPFLAGS_DEFAULT"_s;
        // This is not generally possible, because PySide does not care about
        // privacy the same way. This worked before the heap types were used,
        // because inheritance is not really checked for static types.
        // Instead, we check this at runtime, see SbkObjectType_tp_new.
        if (metaClass->fullName().startsWith(u"PySide6.Qt")) {
            // PYSIDE-595: No idea how to do non-inheritance correctly.
            // Since that is only relevant in shiboken, I used a shortcut for
            // PySide.
            tp_new = u"SbkObject_tp_new"_s;
        }
        else {
            tp_new = u"SbkDummyNew /* PYSIDE-595: Prevent replacement "
                      "of \"0\" with base->tp_new. */"_s;
        }
    }
    else if (isQApp) {
        tp_new = u"SbkQApp_tp_new"_s; // PYSIDE-571: need singleton app
    }
    else {
        tp_new = u"SbkObject_tp_new"_s;
    }
    tp_flags.append(u"|Py_TPFLAGS_HAVE_GC"_s);

    QString tp_richcompare;
    if (generateRichComparison(classContext))
        tp_richcompare = cpythonBaseName(metaClass) + u"_richcompare"_s;

    QString tp_getset;
    if (shouldGenerateGetSetList(metaClass) && !classContext.forSmartPointer())
        tp_getset = cpythonGettersSettersDefinitionName(metaClass);

    // search for special functions
    clearTpFuncs();
    for (const auto &func : metaClass->functions()) {
        if (m_tpFuncs.contains(func->name()))
            m_tpFuncs[func->name()] = cpythonFunctionName(func);
    }
    if (m_tpFuncs.value(reprFunction()).isEmpty()
        && metaClass->hasToStringCapability()) {
        m_tpFuncs[reprFunction()] = writeReprFunction(s,
                classContext,
                metaClass->toStringCapabilityIndirections());
    }

    // class or some ancestor has multiple inheritance
    const auto miClass = getMultipleInheritingClass(metaClass);
    if (miClass) {
        if (metaClass == miClass)
            writeMultipleInheritanceInitializerFunction(s, metaClass);
        writeSpecialCastFunction(s, metaClass);
        s << '\n';
    }

    s << "// Class Definition -----------------------------------------------\n"
         "extern \"C\" {\n";

    if (hasHashFunction(metaClass))
        tp_hash = u'&' + cpythonBaseName(metaClass) + u"_HashFunc"_s;

    const auto callOp = metaClass->findFunction(u"operator()");
    if (callOp && !callOp->isModifiedRemoved())
        tp_call = u'&' + cpythonFunctionName(callOp);

    const QString typePtr = u"_"_s + className
        + u"_Type"_s;
    s << "static PyTypeObject *" << typePtr << " = nullptr;\n"
        << "static PyTypeObject *" << className << "_TypeF(void)\n"
        << "{\n" << indent << "return " << typePtr << ";\n" << outdent
        << "}\n\nstatic PyType_Slot " << className << "_slots[] = {\n" << indent
        << "{Py_tp_base,        nullptr}, // inserted by introduceWrapperType\n"
        << pyTypeSlotEntry("Py_tp_dealloc", tp_dealloc)
        << pyTypeSlotEntry("Py_tp_repr", m_tpFuncs.value(reprFunction()))
        << pyTypeSlotEntry("Py_tp_hash", tp_hash)
        << pyTypeSlotEntry("Py_tp_call", tp_call)
        << pyTypeSlotEntry("Py_tp_str", m_tpFuncs.value(u"__str__"_s))
        << pyTypeSlotEntry("Py_tp_getattro", tp_getattro)
        << pyTypeSlotEntry("Py_tp_setattro", tp_setattro)
        << pyTypeSlotEntry("Py_tp_traverse", className + u"_traverse"_s)
        << pyTypeSlotEntry("Py_tp_clear", className + u"_clear"_s)
        << pyTypeSlotEntry("Py_tp_richcompare", tp_richcompare)
        << pyTypeSlotEntry("Py_tp_iter", m_tpFuncs.value(u"__iter__"_s))
        << pyTypeSlotEntry("Py_tp_iternext", m_tpFuncs.value(u"__next__"_s))
        << pyTypeSlotEntry("Py_tp_methods", className + u"_methods"_s)
        << pyTypeSlotEntry("Py_tp_getset", tp_getset)
        << pyTypeSlotEntry("Py_tp_init", tp_init)
        << pyTypeSlotEntry("Py_tp_new", tp_new);
    if (supportsSequenceProtocol(metaClass)) {
        s << "// type supports sequence protocol\n";
        writeTypeAsSequenceDefinition(s, metaClass);
    }
    if (supportsMappingProtocol(metaClass)) {
        s << "// type supports mapping protocol\n";
        writeTypeAsMappingDefinition(s, metaClass);
    }
    if (supportsNumberProtocol(metaClass)) {
        // This one must come last. See the function itself.
        s << "// type supports number protocol\n";
        writeTypeAsNumberDefinition(s, metaClass);
    }
    s << "{0, " << NULL_PTR << "}\n" << outdent << "};\n";

    int packageLevel = packageName().count(u'.') + 1;
    s << "static PyType_Spec " << className << "_spec = {\n" << indent
        << '"' << packageLevel << ':' << getClassTargetFullName(metaClass) << "\",\n"
        << "sizeof(SbkObject),\n0,\n" << tp_flags << ",\n"
        << className << "_slots\n" << outdent
        << "};\n\n} //extern \"C\"\n";
}

void CppGenerator::writeMappingMethods(TextStream &s,
                                       const AbstractMetaClassCPtr &metaClass,
                                       const GeneratorContext &context) const
{
    for (const auto & m : mappingProtocols()) {
        const auto func = metaClass->findFunction(m.name);
        if (!func)
            continue;
        QString funcName = cpythonFunctionName(func);
        CodeSnipList snips = func->injectedCodeSnips(TypeSystem::CodeSnipPositionAny, TypeSystem::TargetLangCode);
        s << m.returnType << ' ' << funcName << '(' << m.arguments << ")\n{\n" << indent;

        writeCppSelfDefinition(s, func, context, ErrorReturn::Default);

        const AbstractMetaArgument *lastArg = func->arguments().isEmpty()
            ? nullptr : &func->arguments().constLast();
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionAny,
                       TypeSystem::TargetLangCode, func, false, lastArg);
        s << outdent << "}\n\n";
    }
}

void CppGenerator::writeSequenceMethods(TextStream &s,
                                        const AbstractMetaClassCPtr &metaClass,
                                        const GeneratorContext &context) const
{
    bool injectedCode = false;

    for (const auto &seq : sequenceProtocols()) {
        const auto func = metaClass->findFunction(seq.name);
        if (!func)
            continue;
        injectedCode = true;
        QString funcName = cpythonFunctionName(func);

        CodeSnipList snips = func->injectedCodeSnips(TypeSystem::CodeSnipPositionAny, TypeSystem::TargetLangCode);
        s << seq.returnType << ' ' << funcName << '(' << seq.arguments << ")\n{\n" << indent;

        writeCppSelfDefinition(s, func, context, ErrorReturn::Default);

        const AbstractMetaArgument *lastArg = func->arguments().isEmpty() ? nullptr : &func->arguments().constLast();
        writeCodeSnips(s, snips,TypeSystem::CodeSnipPositionAny,
                       TypeSystem::TargetLangCode, func, false /* uses PyArgs */, lastArg);
        s<< outdent << "}\n\n";
    }

    if (!injectedCode)
        writeDefaultSequenceMethods(s, context);
}

// Sequence protocol structure member names
static const QHash<QString, QString> &sqFuncs()
{
    static const QHash<QString, QString> result = {
        {u"__concat__"_s, u"sq_concat"_s},
        {u"__contains__"_s, u"sq_contains"_s},
        {u"__getitem__"_s, u"sq_item"_s},
        {u"__getslice__"_s, u"sq_slice"_s},
        {u"__len__"_s, u"sq_length"_s},
        {u"__setitem__"_s, u"sq_ass_item"_s},
        {u"__setslice__"_s, u"sq_ass_slice"_s}
    };
    return result;
}

void CppGenerator::writeTypeAsSequenceDefinition(TextStream &s,
                                                 const AbstractMetaClassCPtr &metaClass)
{
    bool hasFunctions = false;
    QMap<QString, QString> funcs;
    for (const auto &seq : sequenceProtocols()) {
        const auto func = metaClass->findFunction(seq.name);
        if (func) {
            funcs.insert(seq.name, u'&' + cpythonFunctionName(func));
            hasFunctions = true;
        }
    }

    QString baseName = cpythonBaseName(metaClass);

    //use default implementation
    if (!hasFunctions) {
        funcs[u"__len__"_s] = baseName + u"__len__"_s;
        funcs[u"__getitem__"_s] = baseName + u"__getitem__"_s;
        funcs[u"__setitem__"_s] = baseName + u"__setitem__"_s;
    }

    for (auto it = sqFuncs().cbegin(), end = sqFuncs().cend(); it != end; ++it) {
        const QString &sqName = it.key();
        auto fit = funcs.constFind(sqName);
        if (fit != funcs.constEnd()) {
            s <<  "{Py_" << it.value() << ", reinterpret_cast<void *>("
               << fit.value() << ")},\n";
        }
    }
}

void CppGenerator::writeTypeAsMappingDefinition(TextStream &s,
                                                const AbstractMetaClassCPtr &metaClass)
{
    // Sequence protocol structure members names
    static const QHash<QString, QString> mpFuncs{
        {u"__mlen__"_s, u"mp_length"_s},
        {u"__mgetitem__"_s, u"mp_subscript"_s},
        {u"__msetitem__"_s, u"mp_ass_subscript"_s},
    };
    QMap<QString, QString> funcs;
    for (const auto &m : mappingProtocols()) {
        const auto func = metaClass->findFunction(m.name);
        if (func) {
            const QString entry = u"reinterpret_cast<void *>(&"_s
                                  + cpythonFunctionName(func) + u')';
            funcs.insert(m.name, entry);
        } else {
            funcs.insert(m.name, NULL_PTR);
        }
    }

    for (auto it = mpFuncs.cbegin(), end = mpFuncs.cend(); it != end; ++it) {
        const auto fit = funcs.constFind(it.key());
        if (fit != funcs.constEnd())
            s <<  "{Py_" << it.value() << ", " << fit.value() <<  "},\n";
    }
}

// Number protocol structure members names
static const QHash<QString, QString> &nbFuncs()
{
    static const QHash<QString, QString> result = {
        {u"__add__"_s, u"nb_add"_s},
        {u"__sub__"_s, u"nb_subtract"_s},
        {u"__mul__"_s, u"nb_multiply"_s},
        {u"__div__"_s, u"nb_divide"_s},
        {u"__mod__"_s, u"nb_remainder"_s},
        {u"__neg__"_s, u"nb_negative"_s},
        {u"__pos__"_s, u"nb_positive"_s},
        {u"__invert__"_s, u"nb_invert"_s},
        {u"__lshift__"_s, u"nb_lshift"_s},
        {u"__rshift__"_s, u"nb_rshift"_s},
        {u"__and__"_s, u"nb_and"_s},
        {u"__xor__"_s, u"nb_xor"_s},
        {u"__or__"_s, u"nb_or"_s},
        {u"__iadd__"_s, u"nb_inplace_add"_s},
        {u"__isub__"_s, u"nb_inplace_subtract"_s},
        {u"__imul__"_s, u"nb_inplace_multiply"_s},
        {u"__idiv__"_s, u"nb_inplace_divide"_s},
        {u"__imod__"_s, u"nb_inplace_remainder"_s},
        {u"__ilshift__"_s, u"nb_inplace_lshift"_s},
        {u"__irshift__"_s, u"nb_inplace_rshift"_s},
        {u"__iand__"_s, u"nb_inplace_and"_s},
        {u"__ixor__"_s, u"nb_inplace_xor"_s},
        {u"__ior__"_s, u"nb_inplace_or"_s},
        {boolT(), u"nb_nonzero"_s}
    };
    return result;
}

void CppGenerator::writeTypeAsNumberDefinition(TextStream &s, const AbstractMetaClassCPtr &metaClass) const
{
    QMap<QString, QString> nb;

    const QList<AbstractMetaFunctionCList> opOverloads =
            filterGroupedOperatorFunctions(metaClass,
                                           OperatorQueryOption::ArithmeticOp
                                           | OperatorQueryOption::IncDecrementOp
                                           | OperatorQueryOption::LogicalOp
                                           | OperatorQueryOption::BitwiseOp);

    for (const AbstractMetaFunctionCList &opOverload : opOverloads) {
        const auto rfunc = opOverload.at(0);
        QString opName = ShibokenGenerator::pythonOperatorFunctionName(rfunc);
        nb[opName] = cpythonFunctionName(rfunc);
    }

    QString baseName = cpythonBaseName(metaClass);

    if (hasBoolCast(metaClass))
        nb.insert(boolT(), baseName + u"___nb_bool"_s);

    for (auto it = nbFuncs().cbegin(), end = nbFuncs().cend(); it != end; ++it) {
        const QString &nbName = it.key();
        if (nbName == u"__div__" || nbName == u"__idiv__")
            continue; // excludeFromPy3K
        const auto nbIt = nb.constFind(nbName);
        if (nbIt != nb.constEnd()) {
            const QString fixednbName = nbName == boolT()
                ? u"nb_bool"_s : it.value();
            s <<  "{Py_" << fixednbName << ", reinterpret_cast<void *>("
               << nbIt.value() << ")},\n";
        }
    }

    auto nbIt = nb.constFind(u"__div__"_s);
    if (nbIt != nb.constEnd())
        s << "{Py_nb_true_divide, reinterpret_cast<void *>(" << nbIt.value() << ")},\n";

    nbIt = nb.constFind(u"__idiv__"_s);
    if (nbIt != nb.constEnd()) {
        s << "// This function is unused in Python 3. We reference it here.\n"
            << "{0, reinterpret_cast<void *>(" << nbIt.value() << ")},\n"
            << "// This list is ending at the first 0 entry.\n"
            << "// Therefore, we need to put the unused functions at the very end.\n";
    }
}

void CppGenerator::writeTpTraverseFunction(TextStream &s, const AbstractMetaClassCPtr &metaClass)
{
    QString baseName = cpythonBaseName(metaClass);
    s << "static int " << baseName
        << "_traverse(PyObject *self, visitproc visit, void *arg)\n{\n" << indent
        << "return SbkObject_TypeF()->tp_traverse(self, visit, arg);\n"
        << outdent << "}\n";
}

void CppGenerator::writeTpClearFunction(TextStream &s, const AbstractMetaClassCPtr &metaClass)
{
    QString baseName = cpythonBaseName(metaClass);
    s << "static int " << baseName << "_clear(PyObject *self)\n{\n" << indent
       << "return reinterpret_cast<PyTypeObject *>(SbkObject_TypeF())->tp_clear(self);\n"
       << outdent << "}\n";
}

void CppGenerator::writeCopyFunction(TextStream &s, const GeneratorContext &context) const
{
    const auto metaClass = context.metaClass();
    const QString className = chopType(cpythonTypeName(metaClass));
    s << "static PyObject *" << className << "___copy__(PyObject *self)\n"
        << "{\n" << indent;
    writeCppSelfDefinition(s, context, ErrorReturn::Default, CppSelfDefinitionFlag::CppSelfAsReference);
    QString conversionCode;
    if (!context.forSmartPointer())
        conversionCode = cpythonToPythonConversionFunction(metaClass);
    else
        conversionCode = cpythonToPythonConversionFunction(context.preciseType());

    s << "PyObject *" << PYTHON_RETURN_VAR << " = " << conversionCode
        << CPP_SELF_VAR << ");\n";
    writeFunctionReturnErrorCheckSection(s, ErrorReturn::Default);
    s << "return " << PYTHON_RETURN_VAR << ";\n" << outdent
        << "}\n\n";
}

static inline void writeGetterFunctionStart(TextStream &s, const QString &funcName)
{
    s << "static PyObject *" << funcName << "(PyObject *self, void *)\n"
       << "{\n" << indent;
}

QString CppGenerator::cppFieldAccess(const AbstractMetaField &metaField,
                                     const GeneratorContext &context) const
{
    QString result;
    QTextStream str(&result);
    if (avoidProtectedHack() && metaField.isProtected())
        str << "static_cast<" << context.wrapperName() << " *>(" << CPP_SELF_VAR << ')';
    else
        str << CPP_SELF_VAR;
    str << "->" << metaField.originalName();
    return result;
}

void CppGenerator::writeGetterFunction(TextStream &s,
                                       const AbstractMetaField &metaField,
                                       const GeneratorContext &context) const
{
    writeGetterFunctionStart(s, cpythonGetterFunctionName(metaField));

    writeCppSelfDefinition(s, context);

    const AbstractMetaType &fieldType = metaField.type();
    // Force use of pointer to return internal variable memory
    bool newWrapperSameObject = !fieldType.isConstant() && fieldType.isWrapperType()
            && !fieldType.isPointer();

    QString cppField = cppFieldAccess(metaField, context);

    if (metaField.generateOpaqueContainer()
        && fieldType.generateOpaqueContainer()) {
        const QString creationFunc = opaqueContainerCreationFunc(fieldType);
        writeOpaqueContainerCreationFuncDecl(s, creationFunc, fieldType);
        s << "PyObject *pyOut = " << creationFunc
            << "(&" << cppField << ");\nPy_IncRef(pyOut);\n"
            << "return pyOut;\n" << outdent << "}\n";
        return;
    }

    if (newWrapperSameObject) {
        cppField.prepend(u"&(");
        cppField.append(u')');
    }

    if (fieldType.isCppIntegralPrimitive() || fieldType.isEnum()) {
        s << getFullTypeNameWithoutModifiers(fieldType) << " cppOut_local = " << cppField << ";\n";
        cppField = u"cppOut_local"_s;
    }

    s << "PyObject *pyOut = {};\n";
    if (newWrapperSameObject) {
        // Special case colocated field with same address (first field in a struct)
        s << "if (reinterpret_cast<void *>("
            << cppField << ") == reinterpret_cast<void *>("
            << CPP_SELF_VAR << ")) {\n" << indent
            << "pyOut = reinterpret_cast<PyObject *>(Shiboken::Object::findColocatedChild("
            << "reinterpret_cast<SbkObject *>(self), "
            << cpythonTypeNameExt(fieldType) << "));\n"
            << "if (pyOut) {\n" << indent
            << "Py_IncRef(pyOut);\n"
            << "return pyOut;\n"
            << outdent << "}\n";
        // Check if field wrapper has already been created.
        s << outdent << "} else if (Shiboken::BindingManager::instance().hasWrapper("
            << cppField << ")) {" << "\n" << indent
            << "pyOut = reinterpret_cast<PyObject *>(Shiboken::BindingManager::instance().retrieveWrapper("
            << cppField << "));" << "\n"
            << "Py_IncRef(pyOut);" << "\n"
            << "return pyOut;" << "\n"
            << outdent << "}\n";
        // Create and register new wrapper
        s << "pyOut = "
            << "Shiboken::Object::newObject(" << cpythonTypeNameExt(fieldType)
            << ", " << cppField << ", false, true);\n"
            << "Shiboken::Object::setParent(self, pyOut)";
    } else {
        s << "pyOut = ";
        writeToPythonConversion(s, fieldType, metaField.enclosingClass(), cppField);
    }
    s << ";\nreturn pyOut;\n" << outdent << "}\n";
}

// Write a getter for QPropertySpec
void CppGenerator::writeGetterFunction(TextStream &s, const QPropertySpec &property,
                                       const GeneratorContext &context) const
{
    writeGetterFunctionStart(s, cpythonGetterFunctionName(property, context.metaClass()));
    writeCppSelfDefinition(s, context);
    const QString value = QStringLiteral("value");
    s << "auto " << value << " = " << CPP_SELF_VAR << "->" << property.read() << "();\n"
        << "auto pyResult = ";
    writeToPythonConversion(s, property.type(), context.metaClass(), value);
    s << ";\nif (PyErr_Occurred() || !pyResult) {\n" << indent
        << "Py_XDECREF(pyResult);\nreturn {};\n" << outdent
        << "}\nreturn pyResult;\n" << outdent << "}\n\n";
}

// Write setter function preamble (type checks on "pyIn")
void CppGenerator::writeSetterFunctionPreamble(TextStream &s, const QString &name,
                                               const QString &funcName,
                                               const AbstractMetaType &type,
                                               const GeneratorContext &context) const
{
    s << "static int " << funcName << "(PyObject *self, PyObject *pyIn, void *)\n"
        << "{\n" << indent;

    writeCppSelfDefinition(s, context, ErrorReturn::Zero);

    s << "if (pyIn == " << NULL_PTR << ") {\n" << indent
        << "Shiboken::Errors::setInvalidTypeDeletion(\"" << name << "\");\n"
        << "return -1;\n"
        << outdent << "}\n";

    s << PYTHON_TO_CPPCONVERSION_STRUCT << ' ' << PYTHON_TO_CPP_VAR << ";\n"
        << "if (!";
    writeTypeCheck(s, type, u"pyIn"_s, isNumber(type.typeEntry()));
    s << ") {\n" << indent
        << "Shiboken::Errors::setSetterTypeError(\"" << name << "\", \""
        << type.name() << "\");\n"
        << "return -1;\n"
        << outdent << "}\n\n";
}

void CppGenerator::writeSetterFunction(TextStream &s,
                                       const AbstractMetaField &metaField,
                                       const GeneratorContext &context) const
{
    const AbstractMetaType &fieldType = metaField.type();
    writeSetterFunctionPreamble(s, metaField.name(), cpythonSetterFunctionName(metaField),
                                fieldType, context);


    const QString cppField = cppFieldAccess(metaField, context);

    if (fieldType.isCppIntegralPrimitive() || fieldType.typeEntry()->isEnum()
               || fieldType.typeEntry()->isFlags()) {
        s << "auto cppOut_local = " << cppField << ";\n"
            << PYTHON_TO_CPP_VAR << "(pyIn, &cppOut_local);\n"
            << cppField << " = cppOut_local";
    } else {
        if (fieldType.isPointerToConst())
            s << "const ";
        s << "auto " << QByteArray(fieldType.indirections(), '*')
          << "&cppOut_ptr = " << cppField << ";\n"
          << PYTHON_TO_CPP_VAR << "(pyIn, &cppOut_ptr)";
    }
    s << ";\n\n";

    if (fieldType.isPointerToWrapperType()) {
        s << "Shiboken::Object::keepReference(reinterpret_cast<SbkObject *>(self), \""
            << metaField.name() << "\", pyIn);\n";
    }

    s << "return 0;\n" << outdent << "}\n";
}

// Write a setter for QPropertySpec
void CppGenerator::writeSetterFunction(TextStream &s, const QPropertySpec &property,
                                       const GeneratorContext &context) const
{
    writeSetterFunctionPreamble(s, property.name(),
                                cpythonSetterFunctionName(property, context.metaClass()),
                                property.type(), context);

    s << "auto cppOut = " << CPP_SELF_VAR << "->" << property.read() << "();\n"
        << PYTHON_TO_CPP_VAR << "(pyIn, &cppOut);\n"
        << "if (PyErr_Occurred())\n" << indent
        << "return -1;\n" << outdent
        << CPP_SELF_VAR << "->" << property.write() << "(cppOut);\n"
        << "return 0;\n" << outdent << "}\n\n";
}

void CppGenerator::writeRichCompareFunctionHeader(TextStream &s,
                                                  const QString &baseName,
                                                  const GeneratorContext &context) const
{
    s << "static PyObject * ";
    s << baseName << "_richcompare(PyObject *self, PyObject *" << PYTHON_ARG
        << ", int op)\n{\n" << indent;
    writeCppSelfDefinition(s, context, ErrorReturn::Default, CppSelfDefinitionFlag::CppSelfAsReference);
    s << sbkUnusedVariableCast(CPP_SELF_VAR)
        << "PyObject *" << PYTHON_RETURN_VAR << "{};\n"
        << PYTHON_TO_CPPCONVERSION_STRUCT << ' ' << PYTHON_TO_CPP_VAR << ";\n"
        << sbkUnusedVariableCast(PYTHON_TO_CPP_VAR) << '\n';
}

static bool containsGoto(const CodeSnip &s)
{
    return s.code().contains(u"goto");
}

static const char richCompareComment[] =
    "// PYSIDE-74: By default, we redirect to object's tp_richcompare (which is `==`, `!=`).\n";

void CppGenerator::writeRichCompareFunction(TextStream &s,
                                            const GeneratorContext &context) const
{
    const auto metaClass = context.metaClass();
    QString baseName = cpythonBaseName(metaClass);
    writeRichCompareFunctionHeader(s, baseName, context);

    s << "switch (op) {\n" << indent;
    const QList<AbstractMetaFunctionCList> &groupedFuncs =
        filterGroupedOperatorFunctions(metaClass, OperatorQueryOption::ComparisonOp);
    bool needErrorLabel = false;
    for (const AbstractMetaFunctionCList &overloads : groupedFuncs) {
        const auto rfunc = overloads[0];

        const auto op = rfunc->comparisonOperatorType().value();
        s << "case " << AbstractMetaFunction::pythonRichCompareOpCode(op)
            << ":\n" << indent;

        int alternativeNumericTypes = 0;
        for (const auto &func : overloads) {
            if (!func->isStatic() &&
                ShibokenGenerator::isNumber(func->arguments().at(0).type().typeEntry()))
                alternativeNumericTypes++;
        }

        bool first = true;
        OverloadData overloadData(overloads, api());
        const OverloadDataList &nextOverloads = overloadData.children();
        for (const auto &od : nextOverloads) {
            const auto func = od->referenceFunction();
            if (func->isStatic())
                continue;
            auto argType = getArgumentType(func, 0);
            if (!first) {
                s << " else ";
            } else {
                first = false;
            }
            s << "if (";
            writeTypeCheck(s, argType, PYTHON_ARG,
                           alternativeNumericTypes == 1 || isPyInt(argType));
            s << ") {\n" << indent
                << "// " << func->signature() << '\n';
            writeArgumentConversion(s, argType, CPP_ARG0,
                                    PYTHON_ARG, ErrorReturn::Default,
                                    metaClass,
                                    QString(), func->isUserAdded());
            // If the function is user added, use the inject code
            bool generateOperatorCode = true;
            if (func->isUserAdded()) {
                CodeSnipList snips = func->injectedCodeSnips();
                if (!snips.isEmpty()) {
                    writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionAny,
                                   TypeSystem::TargetLangCode, func,
                                   false /* uses PyArgs */, &func->arguments().constLast());
                    generateOperatorCode = false;
                    needErrorLabel |= std::any_of(snips.cbegin(), snips.cend(), containsGoto);
                }
            }
            if (generateOperatorCode) {
                if (!func->isVoid())
                    s << func->type().cppSignature() << " " << CPP_RETURN_VAR << " = ";
                // expression
                if (func->isPointerOperator())
                    s << '&';
                s << CPP_SELF_VAR << ' '
                    << AbstractMetaFunction::cppComparisonOperator(op) << " (";
                auto generatorArg = GeneratorArgument::fromMetaType(argType);
                if (generatorArg.indirections != 0)
                    s << QByteArray(generatorArg.indirections, '*');
                s << CPP_ARG0 << ");\n"
                    << PYTHON_RETURN_VAR << " = ";
                if (!func->isVoid()) {
                    writeToPythonConversion(s, func->type(), metaClass,
                                            CPP_RETURN_VAR);
                } else {
                    s << "Py_None;\n" << "Py_INCREF(Py_None)";
                }
                s << ";\n";
            }
            s << outdent << '}';
        }

        s << " else {\n";
        if (op == AbstractMetaFunction::OperatorEqual ||
                op == AbstractMetaFunction::OperatorNotEqual) {
            s << indent << PYTHON_RETURN_VAR << " = "
                << (op == AbstractMetaFunction::OperatorEqual ? "Py_False" : "Py_True") << ";\n"
                << "Py_INCREF(" << PYTHON_RETURN_VAR << ");\n" << outdent;
        } else {
            s << indent << "goto " << baseName << "_RichComparison_TypeError;\n" << outdent;
            needErrorLabel = true;
        }
        s << "}\n\n";

        s << "break;\n" << outdent;
    }
    s << "default:\n" << indent
        << richCompareComment
        << "return FallbackRichCompare(self, " << PYTHON_ARG << ", op);\n"
        << outdent << outdent << "}\n\n";

    writeRichCompareFunctionFooter(s, baseName, needErrorLabel);
}

void CppGenerator::writeRichCompareFunctionFooter(TextStream &s,
                                                  const QString &baseName,
                                                  bool writeErrorLabel)
{
    s << "if (" << PYTHON_RETURN_VAR << " && !PyErr_Occurred())\n" << indent
        << "return " << PYTHON_RETURN_VAR << ";\n" << outdent;
    if (writeErrorLabel)
        s << baseName << "_RichComparison_TypeError:\n";
    s << "Shiboken::Errors::setOperatorNotImplemented();\n"
        << ErrorReturn::Default << '\n' << outdent << "}\n\n";
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
        << "Py_INCREF(" << PYTHON_RETURN_VAR << ");\n";

    s << outdent << "} else {\n" << indent
      << "goto " << baseName << "_RichComparison_TypeError;\n"
      << outdent << "}\n";

    writeRichCompareFunctionFooter(s, baseName, true);
}

// Return a flag combination for PyMethodDef
QByteArrayList CppGenerator::methodDefinitionParameters(const OverloadData &overloadData) const
{
    const bool usePyArgs = overloadData.pythonFunctionWrapperUsesListOfArguments();
    int min = overloadData.minArgs();
    int max = overloadData.maxArgs();

    QByteArrayList result;
    if ((min == max) && (max < 2) && !usePyArgs) {
        result.append(max == 0 ? QByteArrayLiteral("METH_NOARGS")
                               : QByteArrayLiteral("METH_O"));
    } else {
        result.append(QByteArrayLiteral("METH_VARARGS"));
        if (overloadData.hasArgumentWithDefaultValue())
            result.append(QByteArrayLiteral("METH_KEYWORDS"));
    }
    // METH_STATIC causes a crash when used for global functions (also from
    // invisible namespaces).
    const auto ownerClass = overloadData.referenceFunction()->ownerClass();
    if (ownerClass
        && !invisibleTopNamespaces().contains(std::const_pointer_cast<AbstractMetaClass>(ownerClass))) {
        if (overloadData.hasStaticFunction())
            result.append(QByteArrayLiteral("METH_STATIC"));
        if (overloadData.hasClassMethod())
            result.append(QByteArrayLiteral("METH_CLASS"));
    }
    return result;
}

QList<PyMethodDefEntry>
    CppGenerator::methodDefinitionEntries(const OverloadData &overloadData) const
{

    const QStringList names = overloadData.referenceFunction()->definitionNames();
    const QString funcName = cpythonFunctionName(overloadData.referenceFunction());
    const QByteArrayList parameters = methodDefinitionParameters(overloadData);

    QList<PyMethodDefEntry> result;
    result.reserve(names.size());
    for (const auto &name : names)
        result.append({name, funcName, parameters, {}});
    return result;
}

// Format the type signature of a function parameter
QString CppGenerator::signatureParameter(const AbstractMetaArgument &arg) const
{
    QString result;
    QTextStream s(&result);

    auto metaType = arg.type();
    if (auto viewOn = metaType.viewOn())
        metaType = *viewOn;
    s << arg.name() << ':';

    QStringList signatures(metaType.pythonSignature());

    // Implicit conversions (C++): Check for converting constructors
    // "QColor(Qt::GlobalColor)" or conversion operators
    const AbstractMetaFunctionCList conversions =
        api().implicitConversions(metaType);
    for (const auto &f : conversions) {
        if (f->isConstructor() && !f->arguments().isEmpty())
            signatures << f->arguments().constFirst().type().pythonSignature();
        else if (f->isConversionOperator())
            signatures << f->ownerClass()->fullName();
    }

    const qsizetype size = signatures.size();
    if (size > 1)
        s << "typing.Union[";
    for (qsizetype i = 0; i < size; ++i) {
        if (i > 0)
            s << ", ";
        s << signatures.at(i);
    }
    if (size > 1)
        s << ']';

    if (!arg.defaultValueExpression().isEmpty()) {
        s << '=';
        QString e = arg.defaultValueExpression();
        e.replace(u"::"_s, u"."_s);
        s << e;
    }
    return result;
}

void CppGenerator::writeSignatureInfo(TextStream &s, const OverloadData &overloadData) const
{
    const auto rfunc = overloadData.referenceFunction();
    QString funcName = fullPythonFunctionName(rfunc, false);

    int idx = overloadData.overloads().length() - 1;
    bool multiple = idx > 0;

    for (const auto &f : overloadData.overloads()) {
        QStringList args;
        // PYSIDE-1328: `self`-ness cannot be computed in Python because there are mixed cases.
        // Toplevel functions like `PySide6.QtCore.QEnum` are always self-less.
        if (!(f->isStatic()) && f->ownerClass())
            args << u"self"_s;
        const auto &arguments = f->arguments();
        for (qsizetype i = 0, size = arguments.size(); i < size; ++i) {
            const auto n = i + 1;
            if (!f->argumentRemoved(n)) {
                QString t = f->pyiTypeReplaced(n);
                if (t.isEmpty()) {
                    t = signatureParameter(arguments.at(i));
                } else {
                    t.prepend(u':');
                    t.prepend(arguments.at(i).name());
                }
                args.append(t);
            }
        }

        // mark the multiple signatures as such, to make it easier to generate different code
        if (multiple)
            s << idx-- << ':';
        s << funcName << '(' << args.join(u',') << ')';

        QString returnType = f->pyiTypeReplaced(0); // pyi or modified type
        if (returnType.isEmpty() && !f->isVoid())
            returnType = f->type().pythonSignature();
        if (!returnType.isEmpty())
            s << "->" << returnType;

        s << '\n';
    }
}

void CppGenerator::writeEnumsInitialization(TextStream &s, AbstractMetaEnumList &enums,
                                            ErrorReturn errorReturn) const
{
    if (enums.isEmpty())
        return;
    bool preambleWrittenE = false;
    bool preambleWrittenF = false;
    for (const AbstractMetaEnum &cppEnum : std::as_const(enums)) {
        if (cppEnum.isPrivate())
            continue;
        if (!preambleWrittenE) {
            s << "// Initialization of enums.\n"
                << "PyTypeObject *EType{};\n\n";
            preambleWrittenE = true;
        }
        if (!preambleWrittenF && cppEnum.typeEntry()->flags()) {
            s << "// Initialization of enums, flags part.\n"
                << "PyTypeObject *FType{};\n\n";
            preambleWrittenF = true;
        }
        writeEnumInitialization(s, cppEnum, errorReturn);
    }
}

static QString mangleName(QString name)
{
    if (name == u"None" || name == u"False" || name == u"True")
        name += u'_';
    return name;
}

void CppGenerator::writeEnumInitialization(TextStream &s, const AbstractMetaEnum &cppEnum,
                                           ErrorReturn errorReturn) const
{
    const auto enclosingClass = cppEnum.targetLangEnclosingClass();
    const bool hasUpperEnclosingClass = enclosingClass
                                        && enclosingClass->targetLangEnclosingClass();
    EnumTypeEntryCPtr enumTypeEntry = cppEnum.typeEntry();
    QString enclosingObjectVariable;
    if (enclosingClass)
        enclosingObjectVariable = cpythonTypeName(enclosingClass);
    else if (hasUpperEnclosingClass)
        enclosingObjectVariable = u"enclosingClass"_s;
    else
        enclosingObjectVariable = u"module"_s;

    s << "// Initialization of ";
    s << (cppEnum.isAnonymous() ? "anonymous enum identified by enum value" : "enum");
    s << " '" << cppEnum.name() << "'.\n";

    QString enumVarTypeObj = cpythonTypeNameExt(enumTypeEntry);
    if (!cppEnum.isAnonymous()) {
        int packageLevel = packageName().count(u'.') + 1;
        FlagsTypeEntryPtr flags = enumTypeEntry->flags();
        if (flags) {
            // The following could probably be made nicer:
            // We need 'flags->flagsName()' with the full module/class path.
            QString fullPath = getClassTargetFullName(cppEnum);
            fullPath.truncate(fullPath.lastIndexOf(u'.') + 1);
            s << "FType = PySide::QFlagsSupport::create(\""
                << packageLevel << ':' << fullPath << flags->flagsName() << "\", \n" << indent
                << cpythonEnumName(cppEnum) << "_number_slots);\n" << outdent
                << cpythonTypeNameExt(flags) << " = FType;\n";
        }

        s << "EType = Shiboken::Enum::"
            << ((enclosingClass
                || hasUpperEnclosingClass) ? "createScopedEnum" : "createGlobalEnum")
            << '(' << enclosingObjectVariable << ',' << '\n' << indent
            << '"' << cppEnum.name() << "\",\n"
                << '"' << packageLevel << ':' << getClassTargetFullName(cppEnum) << "\",\n"
                << '"' << cppEnum.qualifiedCppName() << '"';
        if (flags)
            s << ",\nFType";
        s << ");\n" << outdent
            << "if (!EType)\n"
            << indent << errorReturn << outdent << '\n';
    }

    for (const AbstractMetaEnumValue &enumValue : cppEnum.values()) {
        if (enumTypeEntry->isEnumValueRejected(enumValue.name()))
            continue;

        QString enumValueText;
        if (!avoidProtectedHack() || !cppEnum.isProtected()) {
            enumValueText = cppEnum.typeEntry()->cppType();
            if (enumValueText.isEmpty())
                enumValueText = u"Shiboken::Enum::EnumValueType"_s;
            enumValueText += u'(';
            if (cppEnum.enclosingClass())
                enumValueText += cppEnum.enclosingClass()->qualifiedCppName() + u"::"_s;
            // Fully qualify the value which is required for C++ 11 enum classes.
            if (!cppEnum.isAnonymous())
                enumValueText += cppEnum.name() + u"::"_s;
            enumValueText += enumValue.name();
            enumValueText += u')';
        } else {
            enumValueText += enumValue.value().toString();
        }

        const QString mangledName = mangleName(enumValue.name());
        switch (cppEnum.enumKind()) {
        case AnonymousEnum:
            if (enclosingClass || hasUpperEnclosingClass) {
                s << "{\n" << indent
                    << "PyObject *anonEnumItem = PyLong_FromLong(" << enumValueText << ");\n"
                    << "if (PyDict_SetItemString(reinterpret_cast<PyTypeObject *>("
                    << enclosingObjectVariable
                    << ")->tp_dict, \"" << mangledName << "\", anonEnumItem) < 0)\n"
                    << indent << errorReturn << outdent
                    << "Py_DECREF(anonEnumItem);\n" << outdent
                    << "}\n";
            } else {
                s << "if (PyModule_AddIntConstant(module, \"" << mangledName << "\", ";
                s << enumValueText << ") < 0)\n" << indent << errorReturn << outdent;
            }
            break;
        case CEnum:
            s << "if (!Shiboken::Enum::";
            s << ((enclosingClass || hasUpperEnclosingClass) ? "createScopedEnumItem"
                                                             : "createGlobalEnumItem");
            s << '(' << "EType" << ',' << '\n' << indent
                << enclosingObjectVariable << ", \"" << mangledName << "\", "
                << enumValueText << "))\n" << errorReturn << outdent;
            break;
        case EnumClass:
            s << "if (!Shiboken::Enum::createScopedEnumItem("
                << "EType" << ",\n" << indent
                << "EType" << ", \"" << mangledName << "\", "
                << enumValueText << "))\n" << errorReturn << outdent;
            break;
        }
    }
    s << "// PYSIDE-1735: Resolving the whole enum class at the end for API compatibility.\n"
        << "EType = morphLastEnumToPython();\n"
        << enumVarTypeObj << " = EType;\n";
    if (cppEnum.typeEntry()->flags()) {
        s << "// PYSIDE-1735: Mapping the flags class to the same enum class.\n"
            << cpythonTypeNameExt(cppEnum.typeEntry()->flags()) << " =\n"
            << indent << "mapFlagsToSameEnum(FType, EType);\n" << outdent;
    }
    writeEnumConverterInitialization(s, cppEnum);

    s << "// End of '" << cppEnum.name() << "' enum";
    if (cppEnum.typeEntry()->flags())
        s << "/flags";
    s << ".\n\n";
}

void CppGenerator::writeSignalInitialization(TextStream &s, const AbstractMetaClassCPtr &metaClass)
{
    // Try to check something and print some warnings
    const auto &signalFuncs = metaClass->cppSignalFunctions();
    for (const auto &cppSignal : signalFuncs) {
        if (cppSignal->declaringClass() != metaClass)
            continue;
        const AbstractMetaArgumentList &arguments = cppSignal->arguments();
        for (const AbstractMetaArgument &arg : arguments) {
            AbstractMetaType metaType = arg.type();
            const QByteArray origType =
                QMetaObject::normalizedType(qPrintable(metaType.originalTypeDescription()));
            const QByteArray cppSig =
                QMetaObject::normalizedType(qPrintable(metaType.cppSignature()));
            if ((origType != cppSig) && (!metaType.isFlags())) {
                qCWarning(lcShiboken).noquote().nospace()
                    << "Typedef used on signal " << metaClass->qualifiedCppName() << "::"
                    << cppSignal->signature();
                }
        }
    }

    s << "PySide::Signal::registerSignals(pyType, &::"
       << metaClass->qualifiedCppName() << "::staticMetaObject);\n";
}

void CppGenerator::writeFlagsToLong(TextStream &s, const AbstractMetaEnum &cppEnum)
{
    FlagsTypeEntryPtr flagsEntry = cppEnum.typeEntry()->flags();
    if (!flagsEntry)
        return;
    s << "static PyObject *" << cpythonEnumName(cppEnum) << "_long(PyObject *self)\n"
        << "{\n" << indent
        << "int val;\n";
    AbstractMetaType flagsType = AbstractMetaType::fromTypeEntry(flagsEntry);
    s << cpythonToCppConversionFunction(flagsType) << "self, &val);\n"
        << "return Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<int>(), &val);\n"
        << outdent << "}\n";
}

void CppGenerator::writeFlagsNonZero(TextStream &s, const AbstractMetaEnum &cppEnum)
{
    FlagsTypeEntryPtr flagsEntry = cppEnum.typeEntry()->flags();
    if (!flagsEntry)
        return;
    s << "static int " << cpythonEnumName(cppEnum) << "__nonzero(PyObject *self)\n";
    s << "{\n" << indent << "int val;\n";
    AbstractMetaType flagsType = AbstractMetaType::fromTypeEntry(flagsEntry);
    s << cpythonToCppConversionFunction(flagsType) << "self, &val);\n"
        << "return val != 0;\n"
        << outdent << "}\n";
}

void CppGenerator::writeFlagsMethods(TextStream &s, const AbstractMetaEnum &cppEnum)
{
    writeFlagsBinaryOperator(s, cppEnum, u"and"_s, u"&"_s);
    writeFlagsBinaryOperator(s, cppEnum, u"or"_s, u"|"_s);
    writeFlagsBinaryOperator(s, cppEnum, u"xor"_s, u"^"_s);

    writeFlagsUnaryOperator(s, cppEnum, u"invert"_s, u"~"_s);
    writeFlagsToLong(s, cppEnum);
    writeFlagsNonZero(s, cppEnum);

    s << '\n';
}

void CppGenerator::writeFlagsNumberMethodsDefinition(TextStream &s, const AbstractMetaEnum &cppEnum)
{
    QString cpythonName = cpythonEnumName(cppEnum);

    s << "static PyType_Slot " << cpythonName << "_number_slots[] = {\n" << indent
        << "{Py_nb_bool,    reinterpret_cast<void *>(" << cpythonName << "__nonzero)},\n"
        << "{Py_nb_invert,  reinterpret_cast<void *>(" << cpythonName << "___invert__)},\n"
        << "{Py_nb_and,     reinterpret_cast<void *>(" << cpythonName  << "___and__)},\n"
        << "{Py_nb_xor,     reinterpret_cast<void *>(" << cpythonName  << "___xor__)},\n"
        << "{Py_nb_or,      reinterpret_cast<void *>(" << cpythonName  << "___or__)},\n"
        << "{Py_nb_int,     reinterpret_cast<void *>(" << cpythonName << "_long)},\n"
        << "{Py_nb_index,   reinterpret_cast<void *>(" << cpythonName << "_long)},\n"
        << "{0, " << NULL_PTR << "} // sentinel\n" << outdent
        << "};\n\n";
}

void CppGenerator::writeFlagsNumberMethodsDefinitions(TextStream &s,
                                                      const AbstractMetaEnumList &enums)
{
    for (const AbstractMetaEnum &e : enums) {
        if (!e.isAnonymous() && !e.isPrivate() && e.typeEntry()->flags()) {
            writeFlagsMethods(s, e);
            writeFlagsNumberMethodsDefinition(s, e);
            s << '\n';
        }
    }
}

void CppGenerator::writeFlagsBinaryOperator(TextStream &s, const AbstractMetaEnum &cppEnum,
                                            const QString &pyOpName, const QString &cppOpName)
{
    FlagsTypeEntryPtr flagsEntry = cppEnum.typeEntry()->flags();
    Q_ASSERT(flagsEntry);

    s << "PyObject *" << cpythonEnumName(cppEnum) << "___" << pyOpName
        << "__(PyObject *self, PyObject *" << PYTHON_ARG << ")\n{\n" << indent;

    AbstractMetaType flagsType = AbstractMetaType::fromTypeEntry(flagsEntry);
    s << "::" << flagsEntry->originalName() << " cppResult, " << CPP_SELF_VAR
        << ", cppArg;\n"
        << CPP_SELF_VAR << " = static_cast<::" << flagsEntry->originalName()
        << ">(int(PyLong_AsLong(self)));\n"
        // PYSIDE-1436: Need to error check self as well because operators are used
        //              sometimes with swapped args.
        << "if (PyErr_Occurred())\n" << indent
            << "return nullptr;\n" << outdent
        << "cppArg = static_cast<" << flagsEntry->originalName()
        << ">(int(PyLong_AsLong(" << PYTHON_ARG << ")));\n"
        << "if (PyErr_Occurred())\n" << indent
            << "return nullptr;\n" << outdent
        << "cppResult = " << CPP_SELF_VAR << " " << cppOpName << " cppArg;\n"
        << "return ";
    writeToPythonConversion(s, flagsType, nullptr, u"cppResult"_s);
    s << ";\n" << outdent << "}\n\n";
}

void CppGenerator::writeFlagsUnaryOperator(TextStream &s, const AbstractMetaEnum &cppEnum,
                                           const QString &pyOpName,
                                           const QString &cppOpName, bool boolResult)
{
    FlagsTypeEntryPtr flagsEntry = cppEnum.typeEntry()->flags();
    Q_ASSERT(flagsEntry);

    s << "PyObject *" << cpythonEnumName(cppEnum) << "___" << pyOpName
        << "__(PyObject *self, PyObject *" << PYTHON_ARG << ")\n{\n" << indent;
    if (cppOpName == u"~")
        s << sbkUnusedVariableCast(PYTHON_ARG);

    AbstractMetaType flagsType = AbstractMetaType::fromTypeEntry(flagsEntry);
    s << "::" << flagsEntry->originalName() << " " << CPP_SELF_VAR << ";\n"
        << cpythonToCppConversionFunction(flagsType) << "self, &" << CPP_SELF_VAR
        << ");\n";
    if (boolResult)
        s << "bool";
    else
        s << "::" << flagsEntry->originalName();
    s << " cppResult = " << cppOpName << CPP_SELF_VAR << ";\n"
        << "return ";
    if (boolResult)
        s << "PyBool_FromLong(cppResult)";
    else
        writeToPythonConversion(s, flagsType, nullptr, u"cppResult"_s);
    s << ";\n" << outdent << "}\n\n";
}

QString CppGenerator::getSimpleClassInitFunctionName(const AbstractMetaClassCPtr &metaClass)
{
    QString initFunctionName;
    // Disambiguate namespaces per module to allow for extending them.
    if (metaClass->isNamespace())
        initFunctionName += moduleName();
    initFunctionName += metaClass->qualifiedCppName();
    initFunctionName.replace(u"::"_s, u"_"_s);
    return initFunctionName;
}

QString
    CppGenerator::getSimpleClassStaticFieldsInitFunctionName(const AbstractMetaClassCPtr &metaClass)
{
    return u"init_"_s + getSimpleClassInitFunctionName(metaClass)
        + u"StaticFields"_s;
}

QString CppGenerator::getInitFunctionName(const GeneratorContext &context)
{
    return getSimpleClassInitFunctionName(context.metaClass());
}

void CppGenerator::writeSignatureStrings(TextStream &s,
                                         const QString &signatures,
                                         const QString &arrayName,
                                         const char *comment)
{
    s << "// The signatures string for the " << comment << ".\n"
        << "// Multiple signatures have their index \"n:\" in front.\n"
        << "static const char *" << arrayName << "_SignatureStrings[] = {\n" << indent;
    const auto lines = QStringView{signatures}.split(u'\n', Qt::SkipEmptyParts);
    for (auto line : lines) {
        // must anything be escaped?
        if (line.contains(u'"') || line.contains(u'\\'))
            s << "R\"CPP(" << line << ")CPP\",\n";
        else
            s << '"' << line << "\",\n";
    }
    s << NULL_PTR << "}; // Sentinel\n" << outdent << '\n';
}

// Return the class name for which to invoke the destructor
QString CppGenerator::destructorClassName(const AbstractMetaClassCPtr &metaClass,
                                          const GeneratorContext &classContext) const
{
    if (metaClass->isNamespace() || metaClass->hasPrivateDestructor())
        return {};
    if (classContext.forSmartPointer())
        return classContext.effectiveClassName();
    const bool isValue = metaClass->typeEntry()->isValue();
    const bool hasProtectedDestructor = metaClass->hasProtectedDestructor();
    if (((avoidProtectedHack() && hasProtectedDestructor) || isValue)
        && classContext.useWrapper()) {
        return classContext.wrapperName();
    }
    if (avoidProtectedHack() && hasProtectedDestructor)
        return {}; // Cannot call (happens with "disable-wrapper").
    return metaClass->qualifiedCppName();
}

void CppGenerator::writeClassRegister(TextStream &s,
                                      const AbstractMetaClassCPtr &metaClass,
                                      const GeneratorContext &classContext,
                                      const QString &signatures) const
{
    ComplexTypeEntryCPtr classTypeEntry = metaClass->typeEntry();

    AbstractMetaClassCPtr enc = metaClass->targetLangEnclosingClass();
    QString enclosingObjectVariable = enc ? u"enclosingClass"_s : u"module"_s;

    QString pyTypeName = cpythonTypeName(metaClass);
    QString initFunctionName = getInitFunctionName(classContext);

    // PYSIDE-510: Create a signatures string for the introspection feature.
    writeSignatureStrings(s, signatures, initFunctionName, "functions");
    s << "void init_" << initFunctionName;
    s << "(PyObject *" << enclosingObjectVariable << ")\n{\n" << indent;

    // Multiple inheritance
    QString pyTypeBasesVariable = chopType(pyTypeName) + u"_Type_bases"_s;
    const auto &baseClasses = metaClass->typeSystemBaseClasses();
    if (metaClass->baseClassNames().size() > 1) {
        s << "PyObject *" << pyTypeBasesVariable
            << " = PyTuple_Pack(" << baseClasses.size() << ',' << '\n' << indent;
        for (qsizetype i = 0, size = baseClasses.size(); i < size; ++i) {
            if (i)
                s << ",\n";
            s << "reinterpret_cast<PyObject *>("
                << cpythonTypeNameExt(baseClasses.at(i)->typeEntry()) << ')';
        }
        s << ");\n\n" << outdent;
    }

    // Create type and insert it in the module or enclosing class.
    const QString typePtr = u"_"_s + chopType(pyTypeName)
        + u"_Type"_s;

    s << typePtr << " = Shiboken::ObjectType::introduceWrapperType(\n" << indent;
    // 1:enclosingObject
    s << enclosingObjectVariable << ",\n";

    // 2:typeName
    s << "\"" << metaClass->name() << "\",\n";

    // 3:originalName
    s << "\"";
    if (!classContext.forSmartPointer()) {
        s << metaClass->qualifiedCppName();
        if (classTypeEntry->isObject())
            s << '*';
    } else {
        s << classContext.preciseType().cppSignature();
    }

    s << "\",\n";
    // 4:typeSpec
    s << '&' << chopType(pyTypeName) << "_spec,\n";

    // 5:cppObjDtor
    QString dtorClassName = destructorClassName(metaClass, classContext);
    if (dtorClassName.isEmpty())
        s << "nullptr,\n";
    else
        s << "&Shiboken::callCppDestructor< ::" << dtorClassName << " >,\n";

    // 6:baseType: Find a type that is not disabled.
    auto base = metaClass->isNamespace()
        ? metaClass->extendedNamespace() : metaClass->baseClass();
    if (!metaClass->isNamespace()) {
        for (; base != nullptr; base = base->baseClass()) {
            const auto ct = base->typeEntry()->codeGeneration();
            if (ct == TypeEntry::GenerateCode || ct == TypeEntry::GenerateForSubclass)
                break;
        }
    }
    if (base) {
        s << cpythonTypeNameExt(base->typeEntry()) << ",\n";
    } else {
        s << "0,\n";
    }

    // 7:baseTypes
    if (metaClass->baseClassNames().size() > 1)
        s << pyTypeBasesVariable << ',' << '\n';
    else
        s << "0,\n";

    // 8:wrapperflags
    QByteArrayList wrapperFlags;
    if (enc)
        wrapperFlags.append(QByteArrayLiteral("Shiboken::ObjectType::WrapperFlags::InnerClass"));
    if (metaClass->deleteInMainThread())
        wrapperFlags.append(QByteArrayLiteral("Shiboken::ObjectType::WrapperFlags::DeleteInMainThread"));
    if (wrapperFlags.isEmpty())
        s << '0';
    else
        s << wrapperFlags.join(" | ");

    s << outdent << ");\nauto *pyType = " << pyTypeName << "; // references "
        << typePtr << "\n"
        << "InitSignatureStrings(pyType, " << initFunctionName << "_SignatureStrings);\n";

    if (usePySideExtensions() && !classContext.forSmartPointer())
        s << "SbkObjectType_SetPropertyStrings(pyType, "
                    << chopType(pyTypeName) << "_PropertyStrings);\n";

    if (!classContext.forSmartPointer())
        s << cpythonTypeNameExt(classTypeEntry) << " = pyType;\n\n";
    else
        s << cpythonTypeNameExt(classContext.preciseType()) << " = pyType;\n\n";

    // Register conversions for the type.
    writeConverterRegister(s, metaClass, classContext);
    s << '\n';

    // class inject-code target/beginning
    if (!classTypeEntry->codeSnips().isEmpty()) {
        writeClassCodeSnips(s, classTypeEntry->codeSnips(),
                            TypeSystem::CodeSnipPositionBeginning, TypeSystem::TargetLangCode,
                            classContext);
        s << '\n';
    }

    // Fill multiple inheritance data, if needed.
    const auto miClass = getMultipleInheritingClass(metaClass);
    if (miClass) {
        s << "MultipleInheritanceInitFunction func = ";
        if (miClass == metaClass) {
            s << multipleInheritanceInitializerFunctionName(miClass) << ";\n";
        } else {
            s << "Shiboken::ObjectType::getMultipleInheritanceFunction("
                << cpythonTypeNameExt(miClass->typeEntry()) << ");\n";
        }
        s << "Shiboken::ObjectType::setMultipleInheritanceFunction("
            << cpythonTypeName(metaClass) << ", func);\n"
            << "Shiboken::ObjectType::setCastFunction(" << cpythonTypeName(metaClass)
            << ", &" << cpythonSpecialCastFunctionName(metaClass) << ");\n";
    }

    // Set typediscovery struct or fill the struct of another one
    if (needsTypeDiscoveryFunction(metaClass)) {
        s << "Shiboken::ObjectType::setTypeDiscoveryFunctionV2(" << cpythonTypeName(metaClass)
            << ", &" << cpythonBaseName(metaClass) << "_typeDiscovery);\n\n";
    }

    AbstractMetaEnumList classEnums = metaClass->enums();
    metaClass->getEnumsFromInvisibleNamespacesToBeGenerated(&classEnums);

    if (!classContext.forSmartPointer() && !classEnums.isEmpty())
        s << "// Pass the ..._EnumFlagInfo to the class.\n"
            << "SbkObjectType_SetEnumFlagInfo(pyType, " << chopType(pyTypeName)
            << "_EnumFlagInfo);\n\n";
    writeEnumsInitialization(s, classEnums, ErrorReturn::Void);

    if (metaClass->hasSignals())
        writeSignalInitialization(s, metaClass);

    // class inject-code target/end
    if (!classTypeEntry->codeSnips().isEmpty()) {
        s << '\n';
        writeClassCodeSnips(s, classTypeEntry->codeSnips(),
                            TypeSystem::CodeSnipPositionEnd, TypeSystem::TargetLangCode,
                            classContext);
    }

    if (usePySideExtensions()) {
        if (avoidProtectedHack() && classContext.useWrapper())
            s << classContext.wrapperName() << "::pysideInitQtMetaTypes();\n";
        else
            writeInitQtMetaTypeFunctionBody(s, classContext);
    }

    if (usePySideExtensions() && isQObject(metaClass)) {
        s << "Shiboken::ObjectType::setSubTypeInitHook(pyType, &PySide::initQObjectSubType);\n"
            << "PySide::initDynamicMetaObject(pyType, &::"
            << metaClass->qualifiedCppName() << "::staticMetaObject, sizeof(";
        if (shouldGenerateCppWrapper(metaClass))
            s << wrapperName(metaClass);
        else
            s << "::" << metaClass->qualifiedCppName();
        s << "));\n";
    }

    s << outdent << "}\n";
}

void CppGenerator::writeStaticFieldInitialization(TextStream &s,
                                                  const AbstractMetaClassCPtr &metaClass)
{
    s << "\nvoid " << getSimpleClassStaticFieldsInitFunctionName(metaClass)
        << "()\n{\n" << indent << "auto dict = reinterpret_cast<PyTypeObject *>("
        << cpythonTypeName(metaClass) << ")->tp_dict;\n";
    for (const AbstractMetaField &field : metaClass->fields()) {
        if (field.isStatic()) {
            s << "PyDict_SetItemString(dict, \"" << field.name()
                << "\",\n                     ";
            writeToPythonConversion(s, field.type(), metaClass, field.qualifiedCppName());
            s << ");\n";
        }
    }
    s << '\n' << outdent << "}\n";
}

enum class QtRegisterMetaType
{
    None, Pointer, Value
};

static bool hasQtMetaTypeRegistrationSpec(const AbstractMetaClassCPtr &c)
{
    return c->typeEntry()->qtMetaTypeRegistration() !=
           TypeSystem::QtMetaTypeRegistration::Unspecified;
}

// Returns if and how to register the Qt meta type. By default, "pointer" for
// non-QObject object types and "value" for non-abstract, default-constructible
// value types.
QtRegisterMetaType qtMetaTypeRegistration(const AbstractMetaClassCPtr &c)
{
    if (c->isNamespace())
        return QtRegisterMetaType::None;

    // Specified in type system?
    const bool isObject = c->isObjectType();
    switch (c->typeEntry()->qtMetaTypeRegistration()) {
    case TypeSystem::QtMetaTypeRegistration::Disabled:
        return QtRegisterMetaType::None;
    case TypeSystem::QtMetaTypeRegistration::Enabled:
    case TypeSystem::QtMetaTypeRegistration::BaseEnabled:
        return isObject ? QtRegisterMetaType::Pointer : QtRegisterMetaType::Value;
    case TypeSystem::QtMetaTypeRegistration::Unspecified:
        break;
    }

    // Is there a "base" specification in some base class, meaning only the
    // base class is to be registered?
    if (auto base = recurseClassHierarchy(c, hasQtMetaTypeRegistrationSpec)) {
        const auto baseSpec = base->typeEntry()->qtMetaTypeRegistration();
        if (baseSpec == TypeSystem::QtMetaTypeRegistration::BaseEnabled)
            return QtRegisterMetaType::None;
    }

    // Default.
    if (isObject)
        return isQObject(c) ? QtRegisterMetaType::None : QtRegisterMetaType::Pointer;

    return !c->isAbstract() && c->isDefaultConstructible()
        ? QtRegisterMetaType::Value : QtRegisterMetaType::None;
}

void CppGenerator::writeInitQtMetaTypeFunctionBody(TextStream &s, const GeneratorContext &context)
{
    const auto metaClass = context.metaClass();
    // Gets all class name variants used on different possible scopes
    QStringList nameVariants;
    if (!context.forSmartPointer())
        nameVariants << metaClass->name();
    else
        nameVariants << context.preciseType().cppSignature();

    AbstractMetaClassCPtr enclosingClass = metaClass->enclosingClass();
    while (enclosingClass) {
        if (enclosingClass->typeEntry()->generateCode())
            nameVariants << (enclosingClass->name() + u"::"_s + nameVariants.constLast());
        enclosingClass = enclosingClass->enclosingClass();
    }

    QString className;
    if (!context.forSmartPointer())
        className = metaClass->qualifiedCppName();
    else
        className = context.preciseType().cppSignature();

    // Register meta types for signal/slot connections to work
    // Qt metatypes are registered only on their first use, so we do this now.
    switch (qtMetaTypeRegistration(metaClass)) {
    case QtRegisterMetaType::None:
        break;
    case QtRegisterMetaType::Pointer:
        s << "qRegisterMetaType< ::" << className << " *>();\n";
        break;
    case QtRegisterMetaType::Value:
        for (const QString &name : std::as_const(nameVariants))
            s << "qRegisterMetaType< ::" << className << " >(\"" << name << "\");\n";
        break;
    }

    for (const AbstractMetaEnum &metaEnum : metaClass->enums()) {
        if (!metaEnum.isPrivate() && !metaEnum.isAnonymous()) {
            for (const QString &name : std::as_const(nameVariants)) {
                s << "qRegisterMetaType< ::"
                    << metaEnum.typeEntry()->qualifiedCppName() << " >(\""
                    << name << "::" << metaEnum.name() << "\");\n";
            }
            if (metaEnum.typeEntry()->flags()) {
                QString n = metaEnum.typeEntry()->flags()->originalName();
                s << "qRegisterMetaType< ::" << n << " >(\"" << n << "\");\n";
            }
        }
    }
}

void CppGenerator::writeTypeDiscoveryFunction(TextStream &s,
                                              const AbstractMetaClassCPtr &metaClass)
{
    QString polymorphicExpr = metaClass->typeEntry()->polymorphicIdValue();

    s << "static void *" << cpythonBaseName(metaClass)
        << "_typeDiscovery(void *cptr, PyTypeObject *instanceType)\n{\n" << indent
        << sbkUnusedVariableCast(u"cptr"_s)
        << sbkUnusedVariableCast(u"instanceType"_s);

    if (!polymorphicExpr.isEmpty()) {
        polymorphicExpr = polymorphicExpr.replace(u"%1"_s,
                                                  u" reinterpret_cast< ::"_s
                                                  + metaClass->qualifiedCppName()
                                                  + u" *>(cptr)"_s);
        s << " if (" << polymorphicExpr << ")\n" << indent
            << "return cptr;\n" << outdent;
    } else if (metaClass->isPolymorphic()) {
        const auto &ancestors = metaClass->allTypeSystemAncestors();
        for (const auto &ancestor : ancestors) {
            if (ancestor->baseClass())
                continue;
            if (ancestor->isPolymorphic()) {
                s << "if (instanceType == Shiboken::SbkType< ::"
                    << ancestor->qualifiedCppName() << " >())\n" << indent
                    << "return dynamic_cast< ::" << metaClass->qualifiedCppName()
                    << " *>(reinterpret_cast< ::"<< ancestor->qualifiedCppName()
                    << " *>(cptr));\n" << outdent;
            } else {
                qCWarning(lcShiboken).noquote().nospace()
                    << metaClass->qualifiedCppName() << " inherits from a non polymorphic type ("
                    << ancestor->qualifiedCppName() << "), type discovery based on RTTI is "
                       "impossible, write a polymorphic-id-expression for this type.";
            }

        }
    }
    s << "return {};\n" << outdent << "}\n\n";
}

void CppGenerator::writeSetattroDefinition(TextStream &s,
                                           const AbstractMetaClassCPtr &metaClass) const
{
    s << "static int " << ShibokenGenerator::cpythonSetattroFunctionName(metaClass)
        << "(PyObject *self, PyObject *name, PyObject *value)\n{\n" << indent;
    if (wrapperDiagnostics()) {
        s << R"(std::cerr << __FUNCTION__ << ' ' << Shiboken::debugPyObject(name)
        << ' ' << Shiboken::debugPyObject(value) << '\n';)" << '\n';
    }
}

inline void CppGenerator::writeSetattroDefaultReturn(TextStream &s)
{
    s << "return PyObject_GenericSetAttr(self, name, value);\n"
        << outdent << "}\n\n";
}

void CppGenerator::writeSetattroFunction(TextStream &s, AttroCheck attroCheck,
                                         const GeneratorContext &context) const
{
    Q_ASSERT(!context.forSmartPointer());
    const auto metaClass = context.metaClass();
    writeSetattroDefinition(s, metaClass);

    // PYSIDE-1019: Switch tp_dict before doing tp_setattro.
    if (usePySideExtensions())
        s << "PySide::Feature::Select(self);\n";

    // PYSIDE-803: Detect duck-punching; clear cache if a method is set.
    if (attroCheck.testFlag(AttroCheckFlag::SetattroMethodOverride)
            && context.useWrapper()) {
        s << "if (value && PyCallable_Check(value)) {\n" << indent
            << "auto plain_inst = " << cpythonWrapperCPtr(metaClass, u"self"_s) << ";\n"
            << "auto inst = dynamic_cast<" << context.wrapperName() << " *>(plain_inst);\n"
            << "if (inst)\n" << indent
            << "inst->resetPyMethodCache();\n" << outdent << outdent
            << "}\n";
    }
    if (attroCheck.testFlag(AttroCheckFlag::SetattroQObject)) {
        s << "Shiboken::AutoDecRef pp(reinterpret_cast<PyObject *>(PySide::Property::getObject(self, name)));\n"
            << "if (!pp.isNull())\n" << indent
            << "return PySide::Property::setValue(reinterpret_cast<PySideProperty *>(pp.object()), self, value);\n"
            << outdent;
    }

    if (attroCheck.testFlag(AttroCheckFlag::SetattroUser)) {
        auto func = AbstractMetaClass::queryFirstFunction(metaClass->functions(),
                                                          FunctionQueryOption::SetAttroFunction);
        Q_ASSERT(func);
        s << "{\n" << indent
            << "auto " << CPP_SELF_VAR << " = "
            << cpythonWrapperCPtr(metaClass, u"self"_s) << ";\n";
        writeClassCodeSnips(s, func->injectedCodeSnips(), TypeSystem::CodeSnipPositionAny,
                            TypeSystem::TargetLangCode, context);
        s << outdent << "}\n";
    }

    writeSetattroDefaultReturn(s);
}

static const char smartPtrComment[] =
   "// Try to find the 'name' attribute, by retrieving the PyObject for "
   "the corresponding C++ object held by the smart pointer.\n";

static QString smartPointerGetter(const GeneratorContext &context)
{
    const auto te = context.metaClass()->typeEntry();
    Q_ASSERT(te->isSmartPointer());
    return std::static_pointer_cast<const SmartPointerTypeEntry>(te)->getter();
}

void CppGenerator::writeSmartPointerSetattroFunction(TextStream &s,
                                                     const GeneratorContext &context) const
{
    Q_ASSERT(context.forSmartPointer());
    writeSetattroDefinition(s, context.metaClass());
    s << smartPtrComment
        << "if (auto *rawObj = PyObject_CallMethod(self, \""
        << smartPointerGetter(context)
        << "\", 0)) {\n" << indent
        << "if (PyObject_HasAttr(rawObj, name) != 0)\n" << indent
        << "return PyObject_GenericSetAttr(rawObj, name, value);\n" << outdent
        << "Py_DECREF(rawObj);\n" << outdent
        << "}\n";
    writeSetattroDefaultReturn(s);
}

void CppGenerator::writeGetattroDefinition(TextStream &s, const AbstractMetaClassCPtr &metaClass)
{
    s << "static PyObject *" << cpythonGetattroFunctionName(metaClass)
        << "(PyObject *self, PyObject *name)\n{\n" << indent;
}

QString CppGenerator::qObjectGetAttroFunction() const
{
    static QString result;
    if (result.isEmpty()) {
        auto qobjectClass = AbstractMetaClass::findClass(api().classes(), qObjectT());
        Q_ASSERT(qobjectClass);
        result = u"PySide::getHiddenDataFromQObject("_s
                 + cpythonWrapperCPtr(qobjectClass, u"self"_s)
                 + u", self, name)"_s;
    }
    return result;
}

void CppGenerator::writeGetattroFunction(TextStream &s, AttroCheck attroCheck,
                                         const GeneratorContext &context) const
{
    Q_ASSERT(!context.forSmartPointer());
    const auto metaClass = context.metaClass();
    writeGetattroDefinition(s, metaClass);

    // PYSIDE-1019: Switch tp_dict before doing tp_getattro.
    if (usePySideExtensions())
        s << "PySide::Feature::Select(self);\n";

    const QString getattrFunc = usePySideExtensions() && isQObject(metaClass)
        ? qObjectGetAttroFunction() : u"PyObject_GenericGetAttr(self, name)"_s;

    if (attroCheck.testFlag(AttroCheckFlag::GetattroOverloads)) {
        s << "// Search the method in the instance dict\n"
            << "auto *ob_dict = SbkObject_GetDict_NoRef(self);\n";
        s << "if (auto *meth = PyDict_GetItem(ob_dict, name)) {\n" << indent
            << "Py_INCREF(meth);\nreturn meth;\n" << outdent << "}\n"
            << "// Search the method in the type dict\n"
            << "if (Shiboken::Object::isUserType(self)) {\n" << indent;
        // PYSIDE-772: Perform optimized name mangling.
        s << "Shiboken::AutoDecRef tmp(_Pep_PrivateMangle(self, name));\n"
            << "if (auto *meth = PyDict_GetItem(Py_TYPE(self)->tp_dict, tmp)) {\n" << indent;
        // PYSIDE-1523: PyFunction_Check is not accepting compiled functions.
        s << "if (std::strcmp(Py_TYPE(meth)->tp_name, \"compiled_function\") == 0)\n" << indent
            << "return Py_TYPE(meth)->tp_descr_get(meth, self, nullptr);\n" << outdent
            << "return PyFunction_Check(meth) ? PyMethod_New(meth, self)\n"
            << "                              : " << getattrFunc << ";\n" << outdent
            << "}\n" << outdent << "}\n";

        const auto &funcs = getMethodsWithBothStaticAndNonStaticMethods(metaClass);
        for (const auto &func : funcs) {
            QString defName = cpythonMethodDefinitionName(func);
            s << "static PyMethodDef non_static_" << defName << " = {\n" << indent
                << defName << ".ml_name,\n"
                << defName << ".ml_meth,\n"
                << defName << ".ml_flags & (~METH_STATIC),\n"
                << defName << ".ml_doc,\n" << outdent
                << "};\n"
                << "if (Shiboken::String::compare(name, \""
                << func->definitionNames().constFirst() << "\") == 0)\n" << indent
                << "return PyCFunction_NewEx(&non_static_" << defName << ", self, 0);\n"
                << outdent;
        }
    }

    if (attroCheck.testFlag(AttroCheckFlag::GetattroUser)) {
        auto func = AbstractMetaClass::queryFirstFunction(metaClass->functions(),
                                                          FunctionQueryOption::GetAttroFunction);
        Q_ASSERT(func);
        s << "{\n" << indent
            << "auto " << CPP_SELF_VAR << " = "
            << cpythonWrapperCPtr(metaClass, u"self"_s) << ";\n";
        writeClassCodeSnips(s, func->injectedCodeSnips(), TypeSystem::CodeSnipPositionAny,
                            TypeSystem::TargetLangCode, context);
        s << outdent << "}\n";
    }

    s << "return " << getattrFunc << ";\n" << outdent << "}\n\n";
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
        << "if (auto *rawObj = PyObject_CallMethod(self, \""
        << smartPointerGetter(context)
        << "\", 0)) {\n" << indent
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

void CppGenerator::writeNbBoolExpression(TextStream &s, const BoolCastFunction &f,
                                         bool invert)
{
    if (f.function->isOperatorBool()) {
        if (invert)
            s << '!';
        s << '*' << CPP_SELF_VAR;
        return;
    }
    if (invert != f.invert)
        s << '!';
    s << CPP_SELF_VAR << "->" << f.function->name() << "()";
}

void CppGenerator::writeNbBoolFunction(const GeneratorContext &context,
                                       const BoolCastFunction &f,
                                       TextStream &s) const
{
    s << "static int " << cpythonBaseName(context.metaClass()) << "___nb_bool(PyObject *self)\n"
      << "{\n" << indent;
    writeCppSelfDefinition(s, context, ErrorReturn::MinusOne);

    const bool allowThread = f.function->allowThread();
    if (allowThread)
        s << "int result;\n" << BEGIN_ALLOW_THREADS << "\nresult = ";
    else
        s << "return ";

    writeNbBoolExpression(s, f);
    s << " ? 1 : 0;\n";

    if (allowThread)
        s << END_ALLOW_THREADS << "\nreturn result;\n";
    s << outdent << "}\n\n";
}

// Write declaration and invocation of the init function for the module init
// function.
void CppGenerator::writeInitFunc(TextStream &declStr, TextStream &callStr,
                                 const QString &initFunctionName,
                                 const TypeEntryCPtr &enclosingEntry)
{
    const bool hasParent =
        enclosingEntry && enclosingEntry->type() != TypeEntry::TypeSystemType;
    declStr << "void init_" << initFunctionName << "(PyObject *"
        << (hasParent ? "enclosingClass" : "module") << ");\n";
    callStr << "init_" << initFunctionName;
    if (hasParent) {
        callStr << "(reinterpret_cast<PyTypeObject *>("
            << cpythonTypeNameExt(enclosingEntry) << ")->tp_dict);\n";
    } else {
        callStr << "(module);\n";
    }
}

bool CppGenerator::finishGeneration()
{
    //Generate CPython wrapper file
    StringStream s_classInitDecl(TextStream::Language::Cpp);
    StringStream s_classPythonDefines(TextStream::Language::Cpp);

    std::set<Include> includes;
    StringStream s_globalFunctionImpl(TextStream::Language::Cpp);
    StringStream s_globalFunctionDef(TextStream::Language::Cpp);
    StringStream signatureStream(TextStream::Language::Cpp);

    const auto functionGroups = getGlobalFunctionGroups();
    for (auto it = functionGroups.cbegin(), end = functionGroups.cend(); it != end; ++it) {
        const AbstractMetaFunctionCList &overloads = it.value();
        for (const auto &func : overloads) {
            if (auto te = func->typeEntry())
                includes.insert(te->include());
        }

        if (overloads.isEmpty())
            continue;

        // Dummy context to satisfy the API.
        GeneratorContext classContext;
        OverloadData overloadData(overloads, api());

        writeMethodWrapper(s_globalFunctionImpl, overloadData, classContext);
        writeSignatureInfo(signatureStream, overloadData);
        s_globalFunctionDef << methodDefinitionEntries(overloadData);
    }

    AbstractMetaClassCList classesWithStaticFields;
    for (const auto &cls : api().classes()){
        auto te = cls->typeEntry();
        if (shouldGenerate(te)) {
            writeInitFunc(s_classInitDecl, s_classPythonDefines,
                          getSimpleClassInitFunctionName(cls),
                          targetLangEnclosingEntry(te));
            if (cls->hasStaticFields()) {
                s_classInitDecl << "void "
                    << getSimpleClassStaticFieldsInitFunctionName(cls) << "();\n";
                classesWithStaticFields.append(cls);
            }
        }
    }

    // Initialize smart pointer types.
    for (const auto &smp : api().instantiatedSmartPointers()) {
        GeneratorContext context = contextForSmartPointer(smp.specialized, smp.type);
        const auto enclosingClass = context.metaClass()->enclosingClass();
        auto enclosingTypeEntry = enclosingClass
            ? enclosingClass->typeEntry()
            : targetLangEnclosingEntry(smp.type.typeEntry());

        writeInitFunc(s_classInitDecl, s_classPythonDefines,
                      getInitFunctionName(context),
                      enclosingTypeEntry);
        includes.insert(smp.type.instantiations().constFirst().typeEntry()->include());
    }

    for (auto &instantiatedContainer : api().instantiatedContainers()) {
        includes.insert(instantiatedContainer.typeEntry()->include());
        for (const auto &inst : instantiatedContainer.instantiations())
            includes.insert(inst.typeEntry()->include());
    }

    const ExtendedConverterData extendedConverters = getExtendedConverters();
    for (auto it = extendedConverters.cbegin(), end = extendedConverters.cend(); it != end; ++it) {
        TypeEntryCPtr te = it.key();
        includes.insert(te->include());
        for (const auto &metaClass : it.value())
            includes.insert(metaClass->typeEntry()->include());
    }

    const QList<CustomConversionPtr> &typeConversions = getPrimitiveCustomConversions();
    for (const auto &c : typeConversions) {
        if (auto te = c->ownerType())
            includes.insert(te->include());
    }

    QString moduleFileName(outputDirectory() + u'/' + subDirectoryForPackage(packageName()));
    moduleFileName += u'/' + moduleName().toLower() + u"_module_wrapper.cpp"_s;

    FileOut file(moduleFileName);

    TextStream &s = file.stream;
    s.setLanguage(TextStream::Language::Cpp);

    // write license comment
    s << licenseComment() << R"(
#include <sbkpython.h>
#include <shiboken.h>
#include <algorithm>
#include <signature.h>
)";

    if (!api().instantiatedContainers().isEmpty())
        s << "#include <sbkcontainer.h>\n#include <sbkstaticstrings.h>\n";

    if (usePySideExtensions()) {
        s << includeQDebug;
        s << R"(#include <pysidecleanup.h>
#include <pysideqenum.h>
#include <feature_select.h>
#include <pysidestaticstrings.h>
)";
    }

    s << "#include \"" << getModuleHeaderFileName() << '"'  << "\n\n";
    for (const Include &include : includes)
        s << include;
    s << '\n';

    // Global enums
    AbstractMetaEnumList globalEnums = api().globalEnums();
    for (const auto &nsp : invisibleTopNamespaces()) {
        const auto oldSize = globalEnums.size();
        nsp->getEnumsToBeGenerated(&globalEnums);
        if (globalEnums.size() > oldSize)
            s << nsp->typeEntry()->include();
    }

    TypeDatabase *typeDb = TypeDatabase::instance();
    TypeSystemTypeEntryCPtr moduleEntry = typeDb->defaultTypeSystemType();
    Q_ASSERT(moduleEntry);

    s  << '\n';
    // Extra includes
    QList<Include> extraIncludes = moduleEntry->extraIncludes();
    for (const AbstractMetaEnum &cppEnum : std::as_const(globalEnums))
        extraIncludes.append(cppEnum.typeEntry()->extraIncludes());
    if (!extraIncludes.isEmpty()) {
        s << "// Extra includes\n";
        std::sort(extraIncludes.begin(), extraIncludes.end());
        for (const Include &inc : std::as_const(extraIncludes))
            s << inc;
        s << '\n';
    }

    s << "// Current module's type array.\n"
       << "PyTypeObject **" << cppApiVariableName() << " = nullptr;\n"
       << "// Current module's PyObject pointer.\n"
       << "PyObject *" << pythonModuleObjectName() << " = nullptr;\n"
       << "// Current module's converter array.\n"
       << "SbkConverter **" << convertersVariableName() << " = nullptr;\n";

    const CodeSnipList snips = moduleEntry->codeSnips();

    // module inject-code native/beginning
    if (!snips.isEmpty())
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionBeginning, TypeSystem::NativeCode);

    // cleanup staticMetaObject attribute
    if (usePySideExtensions()) {
        s << "void cleanTypesAttributes() {\n" << indent
            << "static PyObject *attrName = Shiboken::PyName::qtStaticMetaObject();\n"
            << "for (int i = 0, imax = SBK_" << moduleName()
            << "_IDX_COUNT; i < imax; i++) {\n" << indent
            << "PyObject *pyType = reinterpret_cast<PyObject *>(" << cppApiVariableName() << "[i]);\n"
            << "if (pyType && PyObject_HasAttr(pyType, attrName))\n" << indent
            << "PyObject_SetAttr(pyType, attrName, Py_None);\n" << outdent
            << outdent << "}\n" << outdent << "}\n";
    }

    s << "// Global functions "
        << "------------------------------------------------------------\n"
        << s_globalFunctionImpl.toString() << '\n'
        << "static PyMethodDef " << moduleName() << "_methods[] = {\n" << indent
        << s_globalFunctionDef.toString()
        << methodDefSentinel << outdent << "};\n\n"
        << "// Classes initialization functions "
        << "------------------------------------------------------------\n"
        << s_classInitDecl.toString() << '\n';

    if (!globalEnums.isEmpty()) {
        StringStream convImpl(TextStream::Language::Cpp);

        s << "// Enum definitions "
            << "------------------------------------------------------------\n";
        for (const AbstractMetaEnum &cppEnum : std::as_const(globalEnums))
            writeEnumConverterFunctions(s, cppEnum);

        if (convImpl.size() > 0) {
            s << "// Enum converters "
                << "------------------------------------------------------------\n"
                << "namespace Shiboken\n{\n"
                << convImpl.toString() << '\n'
                << "} // namespace Shiboken\n\n";
        }

        writeFlagsNumberMethodsDefinitions(s, globalEnums);
        s << '\n';
    }

    const QStringList &requiredModules = typeDb->requiredTargetImports();
    if (!requiredModules.isEmpty())
        s << "// Required modules' type and converter arrays.\n";
    for (const QString &requiredModule : requiredModules) {
        s << "PyTypeObject **" << cppApiVariableName(requiredModule) << ";\n"
            << "SbkConverter **" << convertersVariableName(requiredModule) << ";\n";
    }

    s << "\n// Module initialization "
        << "------------------------------------------------------------\n";
    if (!extendedConverters.isEmpty()) {
        s  << '\n' << "// Extended Converters.\n\n";
        for (ExtendedConverterData::const_iterator it = extendedConverters.cbegin(), end = extendedConverters.cend(); it != end; ++it) {
            TypeEntryCPtr externalType = it.key();
            s << "// Extended implicit conversions for "
                << externalType->qualifiedTargetLangName() << '.' << '\n';
            for (const auto &sourceClass : it.value()) {
                AbstractMetaType sourceType = AbstractMetaType::fromAbstractMetaClass(sourceClass);
                AbstractMetaType targetType = AbstractMetaType::fromTypeEntry(externalType);
                writePythonToCppConversionFunctions(s, sourceType, targetType);
            }
        }
    }

    if (!typeConversions.isEmpty()) {
        s  << "\n// Primitive Type converters.\n\n";
        for (const auto &conversion : typeConversions) {
            s << "// C++ to Python conversion for primitive type '" << conversion->ownerType()->qualifiedCppName() << "'.\n";
            writeCppToPythonFunction(s, conversion);
            writeCustomConverterFunctions(s, conversion);
        }
        s << '\n';
    }

    QHash<AbstractMetaType, OpaqueContainerData> opaqueContainers;
    const auto &containers = api().instantiatedContainers();
    QSet<AbstractMetaType> valueConverters;
    if (!containers.isEmpty()) {
        s << "// Container Type converters.\n\n";
        for (const AbstractMetaType &container : containers) {
            s << "// C++ to Python conversion for container type '"
                << container.cppSignature() << "'.\n";
            writeContainerConverterFunctions(s, container);
            if (container.generateOpaqueContainer()) {
                auto data = writeOpaqueContainerConverterFunctions(s, container,
                                                                   &valueConverters);
                opaqueContainers.insert(container, data);
            }
        }
        s << '\n';
    }

    // Implicit smart pointers conversions
    const auto &smartPointersList = api().instantiatedSmartPointers();
    if (!smartPointersList.isEmpty()) {
        s << "// SmartPointers converters.\n\n";
        for (const auto &smp : smartPointersList) {
            s << "// C++ to Python conversion for smart pointer type '"
                << smp.type.cppSignature() << "'.\n";
            writeSmartPointerConverterFunctions(s, smp.type);
        }
        s << '\n';
    }

    s << "static struct PyModuleDef moduledef = {\n"
        << "    /* m_base     */ PyModuleDef_HEAD_INIT,\n"
        << "    /* m_name     */ \"" << moduleName() << "\",\n"
        << "    /* m_doc      */ nullptr,\n"
        << "    /* m_size     */ -1,\n"
        << "    /* m_methods  */ " << moduleName() << "_methods,\n"
        << "    /* m_reload   */ nullptr,\n"
        << "    /* m_traverse */ nullptr,\n"
        << "    /* m_clear    */ nullptr,\n"
        << "    /* m_free     */ nullptr\n};\n\n";

    // PYSIDE-510: Create a signatures string for the introspection feature.
    writeSignatureStrings(s, signatureStream.toString(), moduleName(), "global functions");

    // Write module init function
    const QString globalModuleVar = pythonModuleObjectName();
    s << "extern \"C\" LIBSHIBOKEN_EXPORT PyObject *PyInit_"
        << moduleName() << "()\n{\n" << indent;
    // Guard against repeated invocation
    s << "if (" << globalModuleVar << " != nullptr)\n"
        << indent << "return " << globalModuleVar << ";\n" << outdent;

    // module inject-code target/beginning
    if (!snips.isEmpty())
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionBeginning, TypeSystem::TargetLangCode);

    for (const QString &requiredModule : requiredModules) {
        s << "{\n" << indent
             << "Shiboken::AutoDecRef requiredModule(Shiboken::Module::import(\"" << requiredModule << "\"));\n"
             << "if (requiredModule.isNull())\n" << indent
             << "return nullptr;\n" << outdent
             << cppApiVariableName(requiredModule)
             << " = Shiboken::Module::getTypes(requiredModule);\n"
             << convertersVariableName(requiredModule)
             << " = Shiboken::Module::getTypeConverters(requiredModule);\n" << outdent
             << "}\n\n";
    }

    int maxTypeIndex = getMaxTypeIndex() + api().instantiatedSmartPointers().size();
    if (maxTypeIndex) {
        s << "// Create an array of wrapper types for the current module.\n"
           << "static PyTypeObject *cppApi[SBK_" << moduleName() << "_IDX_COUNT];\n"
           << cppApiVariableName() << " = cppApi;\n\n";
    }

    s << "// Create an array of primitive type converters for the current module.\n"
        << "static SbkConverter *sbkConverters[SBK_" << moduleName()
        << "_CONVERTERS_IDX_COUNT" << "];\n"
        << convertersVariableName() << " = sbkConverters;\n\n"
        << "PyObject *module = Shiboken::Module::create(\""  << moduleName()
        << "\", &moduledef);\n\n"
        << "// Make module available from global scope\n"
        << globalModuleVar << " = module;\n\n"
        << "// Initialize classes in the type system\n"
        << s_classPythonDefines.toString();

    if (!typeConversions.isEmpty()) {
        s << '\n';
        for (const auto &conversion : typeConversions) {
            writePrimitiveConverterInitialization(s, conversion);
            s << '\n';
        }
    }

    if (!containers.isEmpty()) {
        s << '\n';
        for (const AbstractMetaType &container : containers) {
            const QString converterObj = writeContainerConverterInitialization(s, container);
            const auto it = opaqueContainers.constFind(container);
            if (it !=  opaqueContainers.constEnd()) {
                writeSetPythonToCppPointerConversion(s, converterObj,
                                                     it.value().pythonToConverterFunctionName,
                                                     it.value().converterCheckFunctionName);
            }
            s << '\n';
        }
    }

    if (!opaqueContainers.isEmpty()) {
        s << "\n// Opaque container type registration\n"
            << "PyObject *ob_type{};\n";
        for (const auto &d : opaqueContainers)
            s << d.registrationCode;
        s << '\n';
    }

    if (!smartPointersList.isEmpty()) {
        s << '\n';
        for (const auto &smp : smartPointersList) {
            writeSmartPointerConverterInitialization(s, smp.type);
            s << '\n';
        }
    }

    if (!extendedConverters.isEmpty()) {
        s << '\n';
        for (ExtendedConverterData::const_iterator it = extendedConverters.cbegin(), end = extendedConverters.cend(); it != end; ++it) {
            writeExtendedConverterInitialization(s, it.key(), it.value());
            s << '\n';
        }
    }

    writeEnumsInitialization(s, globalEnums, ErrorReturn::Default);

    s << "// Register primitive types converters.\n";
    const PrimitiveTypeEntryCList &primitiveTypeList = primitiveTypes();
    for (const auto &pte : primitiveTypeList) {
        if (!pte->generateCode() || !isCppPrimitive(pte))
            continue;
        if (!pte->referencesType())
            continue;
        TypeEntryCPtr referencedType = basicReferencedTypeEntry(pte);
        QString converter = converterObject(referencedType);
        QStringList cppSignature = pte->qualifiedCppName().split(u"::"_s, Qt::SkipEmptyParts);
        while (!cppSignature.isEmpty()) {
            QString signature = cppSignature.join(u"::"_s);
            s << "Shiboken::Conversions::registerConverterName("
                << converter << ", \"" << signature << "\");\n";
            cppSignature.removeFirst();
        }
    }

    s << '\n';
    if (maxTypeIndex)
        s << "Shiboken::Module::registerTypes(module, " << cppApiVariableName() << ");\n";
    s << "Shiboken::Module::registerTypeConverters(module, " << convertersVariableName() << ");\n";

    // Static fields are registered last since they may use converter functions
    // of the previously registered types (PYSIDE-1529).
    if (!classesWithStaticFields.isEmpty()) {
        s << "\n// Static field initialization\n";
        for (const auto &cls : std::as_const(classesWithStaticFields))
            s << getSimpleClassStaticFieldsInitFunctionName(cls) << "();\n";
    }

    s << "\nif (PyErr_Occurred()) {\n" << indent
        << "PyErr_Print();\n"
        << "Py_FatalError(\"can't initialize module " << moduleName() << "\");\n"
        << outdent << "}\n";

    // module inject-code target/end
    if (!snips.isEmpty())
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionEnd, TypeSystem::TargetLangCode);

    // module inject-code native/end
    if (!snips.isEmpty())
        writeCodeSnips(s, snips, TypeSystem::CodeSnipPositionEnd, TypeSystem::NativeCode);

    if (usePySideExtensions()) {
        for (const AbstractMetaEnum &metaEnum : std::as_const(globalEnums))
            if (!metaEnum.isAnonymous()) {
                s << "qRegisterMetaType< ::" << metaEnum.typeEntry()->qualifiedCppName()
                  << " >(\"" << metaEnum.name() << "\");\n";
            }

        // cleanup staticMetaObject attribute
        s << "PySide::registerCleanupFunction(cleanTypesAttributes);\n\n";
    }

    // finish the rest of get_signature() initialization.
    s << "FinishSignatureInitialization(module, " << moduleName()
        << "_SignatureStrings);\n"
        << "\nreturn module;\n" << outdent << "}\n";

    file.done();
    return true;
}

static ArgumentOwner getArgumentOwner(const AbstractMetaFunctionCPtr &func, int argIndex)
{
    ArgumentOwner argOwner = func->argumentOwner(func->ownerClass(), argIndex);
    if (argOwner.index == ArgumentOwner::InvalidIndex)
        argOwner = func->argumentOwner(func->declaringClass(), argIndex);
    return argOwner;
}

// Whether to enable parent ownership heuristic for a function and its argument.
// Both must belong to the same class hierarchy and have the same
// type entry enabling parent management.
static bool useParentHeuristics(const ApiExtractorResult &api,
                                const AbstractMetaFunctionCPtr &func,
                                const AbstractMetaType &argType)
{
    if (!ComplexTypeEntry::isParentManagementEnabled()) // FIXME PYSIDE 7: Remove this
        return true;
    const auto owner = func->ownerClass();
    if (!owner)
        return false;
    auto ownerEntry = parentManagementEntry(owner);
    if (!ownerEntry)
        return false;
    auto argTypeEntry = argType.typeEntry();
    if (!argTypeEntry->isComplex())
        return false;
    const auto argClass = AbstractMetaClass::findClass(api.classes(), argTypeEntry);
    return argClass && parentManagementEntry(argClass) == ownerEntry;
}

bool CppGenerator::writeParentChildManagement(TextStream &s, const AbstractMetaFunctionCPtr &func,
                                              int argIndex,
                                              bool usePyArgs, bool useHeuristicPolicy) const
{
    const int numArgs = func->arguments().size();
    bool ctorHeuristicEnabled = func->isConstructor() && useCtorHeuristic() && useHeuristicPolicy;
    bool heuristicTriggered = false;

    ArgumentOwner argOwner = getArgumentOwner(func, argIndex);
    ArgumentOwner::Action action = argOwner.action;
    int parentIndex = argOwner.index;
    int childIndex = argIndex;
    if (ctorHeuristicEnabled && argIndex > 0 && argIndex <= numArgs) {
        const AbstractMetaArgument &arg = func->arguments().at(argIndex-1);
        if (arg.name() == u"parent" && arg.type().isObjectType()
            && useParentHeuristics(api(), func, arg.type())) {
            action = ArgumentOwner::Add;
            parentIndex = argIndex;
            childIndex = -1;
            heuristicTriggered = true;
        }
    }

    QString parentVariable;
    QString childVariable;
    if (action != ArgumentOwner::Invalid) {
        if (!usePyArgs && argIndex > 1)
            qCWarning(lcShiboken).noquote().nospace()
                << "Argument index for parent tag out of bounds: " << func->signature();

        if (action == ArgumentOwner::Remove) {
            parentVariable = u"Py_None"_s;
        } else {
            if (parentIndex == 0) {
                parentVariable = PYTHON_RETURN_VAR;
            } else if (parentIndex == -1) {
                parentVariable = u"self"_s;
            } else {
                parentVariable = usePyArgs
                    ? pythonArgsAt(parentIndex - 1) : PYTHON_ARG;
            }
        }

        if (childIndex == 0) {
            childVariable = PYTHON_RETURN_VAR;
        } else if (childIndex == -1) {
            childVariable = u"self"_s;
        } else {
            childVariable = usePyArgs
                ? pythonArgsAt(childIndex - 1) : PYTHON_ARG;
        }

        s << "// Ownership transferences";
        if (heuristicTriggered)
            s << " (constructor heuristics)";
        s << ".\nShiboken::Object::setParent(" << parentVariable << ", "
            << childVariable << ");\n";
        return true;
    }

    return false;
}

void CppGenerator::writeParentChildManagement(TextStream &s, const AbstractMetaFunctionCPtr &func,
                                              bool usesPyArgs,
                                              bool useHeuristicForReturn) const
{
    const int numArgs = func->arguments().size();

    // -1    = return value
    //  0    = self
    //  1..n = func. args.
    for (int i = -1; i <= numArgs; ++i)
        writeParentChildManagement(s, func, i, usesPyArgs, useHeuristicForReturn);

    if (useHeuristicForReturn)
        writeReturnValueHeuristics(s, func);
}

void CppGenerator::writeReturnValueHeuristics(TextStream &s, const AbstractMetaFunctionCPtr &func) const
{
    const  AbstractMetaType &type = func->type();
    if (!useReturnValueHeuristic()
        || !func->ownerClass()
        || type.isVoid()
        || func->isStatic()
        || func->isConstructor()
        || func->isTypeModified()
        || !useParentHeuristics(api(), func, type)
        // Something like parent(), parentWidget(): No child relationship here.
        || (func->maybeAccessor() && func->name().startsWith(u"parent"))) {
        return;
    }

    ArgumentOwner argOwner = getArgumentOwner(func, ArgumentOwner::ReturnIndex);
    if (argOwner.action == ArgumentOwner::Invalid || argOwner.index != ArgumentOwner::ThisIndex) {
        if (type.isPointerToWrapperType()) {
            s << "// Ownership transferences (return value heuristics).\n"
                << "Shiboken::Object::setParent(self, " << PYTHON_RETURN_VAR << ");\n";
        }
    }
}

void CppGenerator::writeHashFunction(TextStream &s, const GeneratorContext &context) const
{
    const auto metaClass = context.metaClass();
    const char hashType[] = "Py_hash_t";
    s << "static " << hashType << ' ' << cpythonBaseName(metaClass)
        << "_HashFunc(PyObject *self)\n{\n" << indent;
    writeCppSelfDefinition(s, context);

    bool deref = true;
    QString name = metaClass->typeEntry()->hashFunction();
    if (name.isEmpty())
        name = metaClass->hashFunction();
    else
        deref = !metaClass->isObjectType();
    Q_ASSERT(!name.isEmpty());

    s << "return " << hashType << '(' << name << '(';
    if (deref)
        s << '*';
    s << CPP_SELF_VAR << "));\n"
        << outdent << "}\n\n";
}

void CppGenerator::writeDefaultSequenceMethods(TextStream &s,
                                               const GeneratorContext &context) const
{
    const auto metaClass = context.metaClass();
    ErrorReturn errorReturn = ErrorReturn::Zero;

    // __len__
    const QString namePrefix = cpythonBaseName(metaClass->typeEntry());
    s << "Py_ssize_t " << namePrefix
        << "__len__(PyObject *self)\n{\n" << indent;
    writeCppSelfDefinition(s, context, errorReturn);
    s << "return " << CPP_SELF_VAR << "->size();\n"
        << outdent << "}\n";

    // __getitem__
    s << "PyObject *" << namePrefix
        << "__getitem__(PyObject *self, Py_ssize_t _i)\n{\n" << indent;
    writeCppSelfDefinition(s, context, errorReturn);
    writeIndexError(s, u"index out of bounds"_s, errorReturn);

    s << metaClass->qualifiedCppName() << "::const_iterator _item = "
        << CPP_SELF_VAR << "->begin();\n"
        << "std::advance(_item, _i);\n";

    const AbstractMetaTypeList &instantiations = metaClass->templateBaseClassInstantiations();
    if (instantiations.isEmpty()) {
        QString m;
        QTextStream(&m) << "shiboken: " << __FUNCTION__
            << ": Internal error, no instantiations of \"" << metaClass->qualifiedCppName()
            << "\" were found.";
        throw Exception(m);
    }
    const AbstractMetaType &itemType = instantiations.constFirst();

    s << "return ";
    writeToPythonConversion(s, itemType, metaClass, u"*_item"_s);
    s << ";\n" << outdent << "}\n";

    // __setitem__
    s << "int " << namePrefix
        << "__setitem__(PyObject *self, Py_ssize_t _i, PyObject *pyArg)\n{\n"
        << indent;
    errorReturn = ErrorReturn::MinusOne;
    writeCppSelfDefinition(s, context, errorReturn);
    writeIndexError(s, u"list assignment index out of range"_s, errorReturn);

    s << PYTHON_TO_CPPCONVERSION_STRUCT << ' ' << PYTHON_TO_CPP_VAR << ";\n"
        << "if (!";
    writeTypeCheck(s, itemType, u"pyArg"_s, isNumber(itemType.typeEntry()));
    s << ") {\n" << indent
        << "Shiboken::Errors::setSequenceTypeError(\"" << itemType.name() << "\");\n"
        << "return -1;\n" << outdent << "}\n";
    writeArgumentConversion(s, itemType, u"cppValue"_s,
                            u"pyArg"_s, errorReturn, metaClass);

    s << metaClass->qualifiedCppName() << "::iterator _item = "
        << CPP_SELF_VAR << "->begin();\n"
        << "std::advance(_item, _i);\n"
        << "*_item = cppValue;\n";

    s << "return {};\n" << outdent << "}\n";
}
void CppGenerator::writeIndexError(TextStream &s, const QString &errorMsg,
                                   ErrorReturn errorReturn)
{
    s << "if (_i < 0 || _i >= (Py_ssize_t) " << CPP_SELF_VAR << "->size()) {\n"
        << indent << "PyErr_SetString(PyExc_IndexError, \"" << errorMsg << "\");\n"
        << errorReturn << outdent << "}\n";
}

QString CppGenerator::writeReprFunction(TextStream &s,
                                        const GeneratorContext &context,
                                        uint indirections) const
{
    const auto metaClass = context.metaClass();
    QString funcName = cpythonBaseName(metaClass) + reprFunction();
    s << "extern \"C\"\n{\n"
        << "static PyObject *" << funcName << "(PyObject *self)\n{\n" << indent;
    writeCppSelfDefinition(s, context);
    s << R"(QBuffer buffer;
buffer.open(QBuffer::ReadWrite);
QDebug dbg(&buffer);
dbg << )";
    if (metaClass->typeEntry()->isValue() || indirections == 0)
         s << '*';
    s << CPP_SELF_VAR << R"(;
buffer.close();
QByteArray str = buffer.data();
const auto idx = str.indexOf('(');
auto *typeName = Py_TYPE(self)->tp_name;
if (idx >= 0)
)" << indent << "str.replace(0, idx, typeName);\n" << outdent
       << "str = str.trimmed();\n"
        << "PyObject *mod = PyDict_GetItem(Py_TYPE(self)->tp_dict, Shiboken::PyMagicName::module());\n";
    // PYSIDE-595: The introduction of heap types has the side effect that the module name
    // is always prepended to the type name. Therefore the strchr check:
    s << "if (mod != nullptr && std::strchr(typeName, '.') == nullptr)\n" << indent
        << "return Shiboken::String::fromFormat(\"<%s.%s at %p>\","
           " Shiboken::String::toCString(mod), str.constData(), self);\n"
        << outdent
        << "return Shiboken::String::fromFormat(\"<%s at %p>\", str.constData(), self);\n"
        << outdent << "}\n} // extern C\n\n";
    return funcName;
}
