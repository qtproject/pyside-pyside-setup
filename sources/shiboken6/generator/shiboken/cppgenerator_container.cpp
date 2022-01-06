/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
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

#include "cppgenerator.h"
#include <abstractmetalang.h>
#include "apiextractorresult.h"
#include "ctypenames.h"
#include "textstream.h"

#include <QtCore/QDebug>

#include <algorithm>

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
static void writeContainerCreationFunc(TextStream &s,
                                       const QString &funcName,
                                       const QString &typeFName,
                                       const QString &containerSignature,
                                       bool isConst = false)
{

    // creation function from C++ reference, used by field accessors
    // which are within extern "C"
    s << "extern \"C\" PyObject *" << funcName << '(';
    if (isConst)
        s << "const ";
    s << containerSignature << "* ct)\n{\n" << indent
        << "auto *container = PyObject_New(ShibokenContainer, " << typeFName << "());\n"
        << "auto *d = new ShibokenSequenceContainerPrivate<"
        << containerSignature << ">();\n";
    if (isConst) {
        s << "d->m_list = const_cast<" << containerSignature << " *>(ct);\n"
            << "d->m_const = true;\n";
    } else {
        s << "d->m_list = ct;\n";
    }
    s << "container->d = d;\n";
    s << "return reinterpret_cast<PyObject *>(container);\n" << outdent
        << "}\n\n";
}

// Generate code for a type wrapping a C++ container instantiation
CppGenerator::OpaqueContainerData
   CppGenerator::writeOpaqueContainerConverterFunctions(TextStream &s,
                                                        const AbstractMetaType &containerType) const
{
    OpaqueContainerData result;
    const auto &valueType = containerType.instantiations().constFirst();
    const auto *containerTypeEntry = static_cast<const ContainerTypeEntry *>(containerType.typeEntry());
    result.name = containerTypeEntry->opaqueContainerName(valueType.typeEntry()->name());

    const auto cppSignature = containerType.cppSignature();
    s << "\n// Binding for " << cppSignature << "\n\n";

    // Generate template specialization of value converter helper unless it is already there
    const QString pyArg = u"pyArg"_qs;
    const QString cppArg = u"cppArg"_qs;

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
        << "PyErr_SetString(PyExc_TypeError, \"Wrong type passed to container conversion.\");\n"
        << "return {};\n" << outdent << "}\n";
        writePythonToCppTypeConversion(s, valueType, pyArg, cppArg, nullptr, {});
    s << "return " << cppArg << ";\n" << outdent << "}\n" << outdent << "};\n\n";

    const QString privateObjType = u"ShibokenSequenceContainerPrivate<"_qs
        + cppSignature + u'>';

    // methods
    const bool isStdVector = containerType.name() == u"std::vector";
    const QString methods = result.name + u"_methods"_qs;
    s << "static PyMethodDef " << methods << "[] = {\n" << indent;
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
    writeMethod(s, privateObjType, "reserve");
    writeNoArgsMethod(s, privateObjType, "capacity");
    s << "{nullptr, nullptr, 0, nullptr} // Sentinel\n"
        << outdent << "};\n\n";

    // slots
    const QString slotsList = result.name + u"_slots"_qs;
    s << "static PyType_Slot " << slotsList << "[] = {\n" << indent;
    writeSlot(s, privateObjType, "Py_tp_init", "tpInit");
    writeSlot(s, privateObjType, "Py_tp_new", "tpNew");
    writeSlot(s, privateObjType, "Py_tp_free", "tpFree");
    writeSlot(s, "Py_tp_dealloc", "Sbk_object_dealloc"); // FIXME?
    writeSlot(s, "Py_tp_methods", methods.toUtf8().constData());
    writeSlot(s, privateObjType, "Py_sq_ass_item", "sqSetItem");
    writeSlot(s, privateObjType, "Py_sq_length", "sqLen");
    writeSlot(s, privateObjType, "Py_sq_item", "sqGetItem");
    s << "{0, nullptr}\n" << outdent << "};\n\n";

    // spec
    const QString specName = result.name + u"_spec"_qs;
    const QString name = moduleName() + u'.' + result.name;
    s << "static PyType_Spec " << specName << " = {\n" << indent
        << "\"" << name.count(u'.') << ':' << name << "\",\n"
        << "sizeof(ShibokenContainer),\n0,\nPy_TPFLAGS_DEFAULT,\n"
        <<  slotsList << outdent << "\n};\n\n";

    // type creation function that sets a key in the type dict.
    const QString typeCreationFName =  u"create"_qs + result.name + u"Type"_qs;
    s << "static inline PyTypeObject *" << typeCreationFName << "()\n{\n" << indent
        << "auto *result = reinterpret_cast<PyTypeObject *>(SbkType_FromSpec(&"
        << specName <<  "));\nPy_INCREF(Py_True);\n"
        << "PyDict_SetItem(result->tp_dict, "
           "Shiboken::PyMagicName::opaque_container(), Py_True);\n"
        << "return result;\n" << outdent << "}\n\n";

    // typeF() function
    const QString typeFName =  result.name + u"_TypeF"_qs;
    s << "static PyTypeObject *" << typeFName << "()\n{\n" << indent
        << "static PyTypeObject *type = " << typeCreationFName
        << "();\nreturn type;\n" << outdent << "}\n\n";

    // creation functions from C++ references
    writeContainerCreationFunc(s, u"create"_qs + result.name, typeFName,
                               containerType.cppSignature());
    writeContainerCreationFunc(s, u"createConst"_qs + result.name, typeFName,
                               containerType.cppSignature(), true);

    // Check function
    result.checkFunctionName = result.name + u"_Check"_qs;
    s << "extern \"C\" int " << result.checkFunctionName << "(PyObject *" << pyArg
        << ")\n{\n" << indent << "return " << pyArg << " != nullptr && "
        << pyArg << " != Py_None && " << pyArg << "->ob_type == "
        << typeFName << "();\n" << outdent << "}\n\n";

    // SBK converter Python to C++
    result.pythonToConverterFunctionName = u"PythonToCpp"_qs + result.name;
    s << "extern \"C\" void " << result.pythonToConverterFunctionName
        << "(PyObject *" << pyArg << ", void *cppOut)\n{\n" << indent
        << "auto *d = ShibokenSequenceContainerPrivate<" << cppSignature
        << ">::get(" << pyArg << ");\n"
        << "*reinterpret_cast<" << cppSignature << "**>(cppOut) = d->m_list;\n"
        << outdent << "}\n\n";

    // SBK check function for converting Python to C++ that returns the converter
    result.converterCheckFunctionName = u"is"_qs + result.name + u"PythonToCppConvertible"_qs;
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
