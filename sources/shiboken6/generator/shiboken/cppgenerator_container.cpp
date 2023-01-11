// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "cppgenerator.h"
#include <abstractmetalang.h>
#include "apiextractorresult.h"
#include "ctypenames.h"
#include "containertypeentry.h"
#include "textstream.h"
#include "typedatabase.h"

#include <QtCore/QDebug>

#include <algorithm>

using namespace Qt::StringLiterals;

// Write a PyMethodDef entry, allowing for registering C++ functions
// under different names for Python.
static void writeMethod(TextStream &s, const QString &privateObjType,
                        const char *cppName, const char *pythonName,
                        const char *flags)
{
    if (pythonName == nullptr)
        pythonName = cppName;
    s << "{\"" << pythonName << "\", reinterpret_cast<PyCFunction>("
       << privateObjType << "::" << cppName << "), "<< flags
       << ", \"" << /* doc */ pythonName << "\"},\n";
}

static inline void writeMethod(TextStream &s, const QString &privateObjType,
                               const char *cppName, const char *pythonName = nullptr)
{
    writeMethod(s, privateObjType, cppName, pythonName, "METH_O");
}

static inline void writeNoArgsMethod(TextStream &s, const QString &privateObjType,
                                     const char *cppName, const char *pythonName = nullptr)
{
    writeMethod(s, privateObjType, cppName, pythonName, "METH_NOARGS");
}

static void writeSlot(TextStream &s, const char *tpName, const char *value)
{
    s << '{' << tpName << ", reinterpret_cast<void *>(" << value << ")},\n";
}

static void writeSlot(TextStream &s, const QString &privateObjType,
                      const char *tpName, const char *methodName)
{
    s << '{' << tpName << ", reinterpret_cast<void *>(" << privateObjType
      << "::" << methodName << ")},\n";
}

// Write creation function from C++ reference, used by field accessors
// and getters which are within extern "C"

enum ContainerCreationFlag
{
    None = 0,
    Const = 0x1,
    Allocate = 0x2
};

Q_DECLARE_FLAGS(ContainerCreationFlags, ContainerCreationFlag)
Q_DECLARE_OPERATORS_FOR_FLAGS(ContainerCreationFlags)

static void writeContainerCreationFunc(TextStream &s,
                                       const QString &funcName,
                                       const QString &typeFName,
                                       const QString &containerSignature,
                                       ContainerCreationFlags flags = {})
{

    // creation function from C++ reference, used by field accessors
    // which are within extern "C"
    s << "extern \"C\" PyObject *" << funcName << '(';
    if (flags.testFlag(ContainerCreationFlag::Const))
        s << "const ";
    s << containerSignature << "* ct)\n{\n" << indent
        << "auto *container = PyObject_New(ShibokenContainer, " << typeFName << "());\n"
        << "auto *d = new ShibokenSequenceContainerPrivate<"
        << containerSignature << ">();\n";
    if (flags.testFlag(ContainerCreationFlag::Allocate)) {
        s << "d->m_list = new " << containerSignature << "(*ct);\n"
            << "d->m_ownsList = true;\n";
    } else if (flags.testFlag(ContainerCreationFlag::Const)) {
        s << "d->m_list = const_cast<" << containerSignature << " *>(ct);\n"
            << "d->m_const = true;\n";
    } else {
        s << "d->m_list = ct;\n";
    }
    s << "container->d = d;\n";
    s << "return reinterpret_cast<PyObject *>(container);\n" << outdent
        << "}\n\n";
}

// Generate template specialization of value converter helper
void CppGenerator::writeOpaqueContainerValueConverter(TextStream &s,
                                                      const AbstractMetaType &valueType) const
{
    // Generate template specialization of value converter helper unless it is already there
    const QString pyArg = u"pyArg"_s;
    const QString cppArg = u"cppArg"_s;

    const QString valueTypeName = valueType.cppSignature();
    const QString checkFunction = cpythonCheckFunction(valueType);

    s << "template <>\nstruct ShibokenContainerValueConverter<"
      << valueTypeName << ">\n{\n";
    // Type check
    s << indent << "static bool checkValue(PyObject *" << pyArg << ")\n{\n"
        << indent << "return " << checkFunction;
    if (!checkFunction.contains(u'('))
        s << '(';
    s << pyArg << ");\n"
        << outdent << "}\n\n";

    // C++ to Python
    const bool passByConstRef = valueType.indirectionsV().isEmpty()
        && !valueType.isCppPrimitive();
    s << "static PyObject *convertValueToPython(";
    if (passByConstRef)
        s << "const ";
    s << valueTypeName << ' ';
    if (passByConstRef)
        s << '&';
    s << cppArg << ")\n{\n" << indent << "return ";
    writeToPythonConversion(s, valueType, nullptr, cppArg);
    s << ";\n" << outdent << "}\n\n";

    // Python to C++
    s << "static std::optional<" << valueTypeName << "> convertValueToCpp(PyObject *"
        << pyArg << ")\n{\n" << indent;
    s << PYTHON_TO_CPPCONVERSION_STRUCT << ' ' << PYTHON_TO_CPP_VAR << ";\n"
        << "if (!(";
    writeTypeCheck(s, valueType, pyArg), isNumber(valueType.typeEntry());
    s << ")) {\n" << indent
        << "Shiboken::Errors::setWrongContainerType();\n"
        << "return {};\n" << outdent << "}\n";
    writePythonToCppTypeConversion(s, valueType, pyArg, cppArg, nullptr, {});
    s << "return " << cppArg << ";\n" << outdent << "}\n" << outdent << "};\n\n";
}

// Generate code for a type wrapping a C++ container instantiation
CppGenerator::OpaqueContainerData
   CppGenerator::writeOpaqueContainerConverterFunctions(TextStream &s,
                                                        const AbstractMetaType &containerType,
                                                        QSet<AbstractMetaType> *valueTypes) const
{
    OpaqueContainerData result;
    const auto &valueType = containerType.instantiations().constFirst();
    const auto containerTypeEntry = std::static_pointer_cast<const ContainerTypeEntry>(containerType.typeEntry());
    result.name =
        containerTypeEntry->opaqueContainerName(containerType.instantiationCppSignatures());

    const auto cppSignature = containerType.cppSignature();
    s << "\n// Binding for " << cppSignature << "\n\n";

    if (!valueTypes->contains(valueType)) {
        valueTypes->insert(valueType);
        writeOpaqueContainerValueConverter(s, valueType);
    }

    const QString privateObjType = u"ShibokenSequenceContainerPrivate<"_s
        + cppSignature + u'>';

    // methods
    const QString &containerName = containerType.name();
    const bool isStdVector = containerName  == u"std::vector";
    const auto kind = containerTypeEntry->containerKind();
    const bool isFixed = kind == ContainerTypeEntry::SpanContainer || containerName == u"std::array";
    const QString methods = result.name + u"_methods"_s;
    s << "static PyMethodDef " << methods << "[] = {\n" << indent;
    if (!isFixed) {
        writeMethod(s, privateObjType, "push_back");
        writeMethod(s, privateObjType, "push_back", "append"); // Qt convention
        writeNoArgsMethod(s, privateObjType, "clear");
        writeNoArgsMethod(s, privateObjType, "pop_back");
        writeNoArgsMethod(s, privateObjType, "pop_back", "removeLast"); // Qt convention
        if (!isStdVector) {
            writeMethod(s, privateObjType, "push_front");
            writeMethod(s, privateObjType, "push_front", "prepend"); // Qt convention
            writeNoArgsMethod(s, privateObjType, "pop_front");
            writeMethod(s, privateObjType, "pop_front", "removeFirst"); // Qt convention
        }
        writeMethod(s, privateObjType, "reserve"); // SFINAE'd out for list
        writeNoArgsMethod(s, privateObjType, "capacity");
    }
    writeNoArgsMethod(s, privateObjType, "data");
    writeNoArgsMethod(s, privateObjType, "constData");
    s << "{nullptr, nullptr, 0, nullptr} // Sentinel\n"
        << outdent << "};\n\n";

    // slots
    const QString slotsList = result.name + u"_slots"_s;
    s << "static PyType_Slot " << slotsList << "[] = {\n" << indent;
    writeSlot(s, privateObjType, "Py_tp_init", "tpInit");
    const auto *tpNew = containerTypeEntry->viewOn() == nullptr ? "tpNew" : "tpNewInvalid";
    writeSlot(s, privateObjType, "Py_tp_new", tpNew);
    writeSlot(s, privateObjType, "Py_tp_free", "tpFree");
    writeSlot(s, "Py_tp_dealloc", "Sbk_object_dealloc"); // FIXME?
    writeSlot(s, "Py_tp_methods", methods.toUtf8().constData());
    writeSlot(s, privateObjType, "Py_sq_ass_item", "sqSetItem");
    writeSlot(s, privateObjType, "Py_sq_length", "sqLen");
    writeSlot(s, privateObjType, "Py_sq_item", "sqGetItem");
    s << "{0, nullptr}\n" << outdent << "};\n\n";

    // spec
    const QString specName = result.name + u"_spec"_s;
    const QString name = TypeDatabase::instance()->defaultPackageName()
        + u'.' + result.name;
    s << "static PyType_Spec " << specName << " = {\n" << indent
        << "\"" << name.count(u'.') << ':' << name << "\",\n"
        << "sizeof(ShibokenContainer),\n0,\nPy_TPFLAGS_DEFAULT,\n"
        <<  slotsList << outdent << "\n};\n\n";

    // type creation function that sets a key in the type dict.
    const QString typeCreationFName =  u"create"_s + result.name + u"Type"_s;
    s << "static inline PyTypeObject *" << typeCreationFName << "()\n{\n" << indent
        << "auto *result = reinterpret_cast<PyTypeObject *>(SbkType_FromSpec(&"
        << specName <<  "));\nPy_INCREF(Py_True);\n"
        << "PyDict_SetItem(result->tp_dict, "
           "Shiboken::PyMagicName::opaque_container(), Py_True);\n"
        << "return result;\n" << outdent << "}\n\n";

    // _TypeF() function
    const QString typeFName =  result.name + u"_TypeF"_s;
    s << "static PyTypeObject *" << typeFName << "()\n{\n" << indent
        << "static PyTypeObject *type = " << typeCreationFName
        << "();\nreturn type;\n" << outdent << "}\n\n";

    // creation functions from C++ references
    ContainerCreationFlags flags;
    if (kind == ContainerTypeEntry::SpanContainer)
        flags.setFlag(ContainerCreationFlag::Allocate);

    writeContainerCreationFunc(s, u"create"_s + result.name, typeFName,
                               containerType.cppSignature(), flags);
    flags.setFlag(ContainerCreationFlag::Const);
    writeContainerCreationFunc(s, u"createConst"_s + result.name, typeFName,
                               containerType.cppSignature(), flags);

    // Check function
    result.checkFunctionName = result.name + u"_Check"_s;
    const QString pyArg = u"pyArg"_s;
    s << "extern \"C\" int " << result.checkFunctionName << "(PyObject *" << pyArg
        << ")\n{\n" << indent << "return " << pyArg << " != nullptr && "
        << pyArg << " != Py_None && " << pyArg << "->ob_type == "
        << typeFName << "();\n" << outdent << "}\n\n";

    // SBK converter Python to C++
    result.pythonToConverterFunctionName = u"PythonToCpp"_s + result.name;
    s << "extern \"C\" void " << result.pythonToConverterFunctionName
        << "(PyObject *" << pyArg << ", void *cppOut)\n{\n" << indent
        << "auto *d = ShibokenSequenceContainerPrivate<" << cppSignature
        << ">::get(" << pyArg << ");\n"
        << "*reinterpret_cast<" << cppSignature << "**>(cppOut) = d->m_list;\n"
        << outdent << "}\n\n";

    // SBK check function for converting Python to C++ that returns the converter
    result.converterCheckFunctionName = u"is"_s + result.name + u"PythonToCppConvertible"_s;
    s << "extern \"C\" PythonToCppFunc " << result.converterCheckFunctionName
        << "(PyObject *" << pyArg << ")\n{\n" << indent << "if ("
        << result.checkFunctionName << '(' << pyArg << "))\n" << indent
        << "return " << result.pythonToConverterFunctionName << ";\n"
        << outdent << "return {};\n" << outdent << "}\n\n";

    QTextStream(&result.registrationCode) << "ob_type = reinterpret_cast<PyObject *>("
        << typeFName
        << "());\nPy_XINCREF(ob_type);\nPyModule_AddObject(module, \""
        << result.name << "\", ob_type);\n";
    return result;
}
