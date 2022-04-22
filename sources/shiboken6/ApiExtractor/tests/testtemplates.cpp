/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the test suite of Qt for Python.
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

#include "testtemplates.h"
#include "testutil.h"
#include <abstractmetafield.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <typesystem.h>

#include <qtcompat.h>

#include <QtCore/QTemporaryFile>
#include <QtCore/QTextStream>
#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestTemplates::testTemplateWithNamespace()
{
    const char cppCode[] = R"CPP(
template<typename T> struct QList {};
struct Url {
  void name();
};
namespace Internet {
    struct Url{};
    struct Bookmarks {
        QList<Url> list();
    };
};
)CPP";

    const char xmlCode0[] = R"XML(
<typesystem package='Package.Network'>
    <value-type name='Url'/>
</typesystem>)XML";

    QTemporaryFile file;
    QVERIFY(file.open());
    file.write(xmlCode0);
    file.close();

    QString xmlCode1 = QString::fromLatin1(R"XML(
<typesystem package='Package.Internet'>
    <load-typesystem name='%1' generate='no'/>
    <container-type name='QList' type='list'/>
    <namespace-type name='Internet' generate='no'>
        <value-type name='Url'/>
        <value-type name='Bookmarks'/>
    </namespace-type>
</typesystem>)XML").arg(file.fileName());

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, qPrintable(xmlCode1), false));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();

    AbstractMetaClass* classB = AbstractMetaClass::findClass(classes, u"Bookmarks");
    QVERIFY(classB);
    const auto func = classB->findFunction(u"list");
    QVERIFY(!func.isNull());
    AbstractMetaType funcType = func->type();
    QVERIFY(!funcType.isVoid());
    QCOMPARE(funcType.cppSignature(), u"QList<Internet::Url >");
}

void TestTemplates::testTemplateOnContainers()
{
    const char cppCode[] = R"CPP(
struct Base {};
template<typename T> struct QList {};
namespace Namespace {
    enum SomeEnum { E1, E2 };
    template<SomeEnum type> struct A {
        A<type> foo(const QList<A<type> >& a);
    };
    typedef A<E1> B;
}
)CPP";

    const char xmlCode[] = R"XML(
<typesystem package="Package">
    <container-type name='QList' type='list'/>
    <namespace-type name='Namespace'>
       <enum-type name='SomeEnum'/>
       <object-type name='A' generate='no'/>
       <object-type name='B'/>
    </namespace-type>
    <object-type name='Base'/>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();

    AbstractMetaClass* classB = AbstractMetaClass::findClass(classes, u"B");
    QVERIFY(classB);
    QVERIFY(!classB->baseClass());
    QVERIFY(classB->baseClassName().isEmpty());
    const auto func = classB->findFunction(u"foo");
    QVERIFY(!func.isNull());
    AbstractMetaType argType = func->arguments().constFirst().type();
    QCOMPARE(argType.instantiations().size(), 1);
    QCOMPARE(argType.typeEntry()->qualifiedCppName(), u"QList");

    const AbstractMetaType &instance1 = argType.instantiations().constFirst();
    QCOMPARE(instance1.instantiations().size(), 1);
    QCOMPARE(instance1.typeEntry()->qualifiedCppName(), u"Namespace::A");

    const AbstractMetaType &instance2 = instance1.instantiations().constFirst();
    QCOMPARE(instance2.instantiations().size(), 0);
    QCOMPARE(instance2.typeEntry()->qualifiedCppName(), u"Namespace::E1");
}

void TestTemplates::testTemplateValueAsArgument()
{
    const char cppCode[] = R"CPP(
template<typename T> struct List {};
void func(List<int> arg) {}
)CPP";

    const char xmlCode[] = R"XML(
<typesystem package='Package'>
    <primitive-type name='int'/>
    <container-type name='List' type='list'/>
    <function signature='func(List&lt;int&gt;)'/>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    const auto globalFuncs = builder->globalFunctions();
    QCOMPARE(globalFuncs.size(), 1);

    const auto func = globalFuncs.constFirst();
    QCOMPARE(func->minimalSignature(), u"func(List<int>)");
    QCOMPARE(func->arguments().constFirst().type().cppSignature(),
             u"List<int >");
}

void TestTemplates::testTemplatePointerAsArgument()
{
    const char cppCode[] = R"CPP(
template<typename T> struct List {};
void func(List<int>* arg) {}
)CPP";

    const char xmlCode[] = R"XML(
 <typesystem package='Package'>
     <primitive-type name='int'/>
     <container-type name='List' type='list'/>
     <function signature='func(List&lt;int&gt;*)'/>
 </typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    AbstractMetaFunctionCList globalFuncs = builder->globalFunctions();
    QCOMPARE(globalFuncs.size(), 1);

    const auto func = globalFuncs.constFirst();
    QCOMPARE(func->minimalSignature(), u"func(List<int>*)");
    QCOMPARE(func->arguments().constFirst().type().cppSignature(),
             u"List<int > *");
}

void TestTemplates::testTemplateReferenceAsArgument()
{
    const char cppCode[] = R"CPP(
template<typename T> struct List {};
void func(List<int>& arg) {}
    )CPP";

    const char xmlCode[] = R"XML(
<typesystem package='Package'>
    <primitive-type name='int'/>
    <container-type name='List' type='list'/>
    <function signature='func(List&lt;int&gt;&amp;)'/>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    const auto globalFuncs = builder->globalFunctions();
    QCOMPARE(globalFuncs.size(), 1);

    const auto func = globalFuncs.constFirst();
    QCOMPARE(func->minimalSignature(), u"func(List<int>&)");
    QCOMPARE(func->arguments().constFirst().type().cppSignature(),
             u"List<int > &");
}

void TestTemplates::testTemplateParameterFixup()
{
    const char cppCode[] = R"CPP(
template<typename T>
struct List {
    struct Iterator {};
    void append(List l);
    void erase(List::Iterator it);
};
)CPP";

    const char xmlCode[] = R"XML(
 <typesystem package='Package'>
     <container-type name='List' type='list'>
         <value-type name='Iterator'/>
     </container-type>
 </typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    const AbstractMetaClassList templates = builder->templates();

    QCOMPARE(templates.size(), 1);
    const AbstractMetaClass *list = templates.constFirst();
    // Verify that the parameter of "void append(List l)" gets fixed to "List<T >"
    const auto append = list->findFunction(QStringLiteral("append"));
    QVERIFY(!append.isNull());
    QCOMPARE(append->arguments().size(), 1);
    QCOMPARE(append->arguments().at(0).type().cppSignature(), u"List<T >");
    // Verify that the parameter of "void erase(Iterator)" is not modified
    const auto erase = list->findFunction(QStringLiteral("erase"));
    QVERIFY(!erase.isNull());
    QCOMPARE(erase->arguments().size(), 1);
    QEXPECT_FAIL("", "Clang: Some other code changes the parameter type", Abort);
    QCOMPARE(erase->arguments().at(0).type().cppSignature(), u"List::Iterator");
}

void TestTemplates::testInheritanceFromContainterTemplate()
{
    const char cppCode[] = R"CPP(
template<typename T>
struct ListContainer {
    inline void push_front(const T& t);
    inline T& front();
};
struct FooBar {};
struct FooBars : public ListContainer<FooBar> {};
)CPP";

    const char xmlCode[] = R"XML(
<typesystem package='Package'>
    <container-type name='ListContainer' type='list'/>
    <value-type name='FooBar'/>
    <value-type name='FooBars'>
        <modify-function signature='push_front(FooBar)' remove='all'/>
        <modify-function signature='front()' remove='all'/>
    </value-type>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();
    AbstractMetaClassList templates = builder->templates();
    QCOMPARE(classes.size(), 2);
    QCOMPARE(templates.size(), 1);

    const AbstractMetaClass* foobars = AbstractMetaClass::findClass(classes, u"FooBars");
    QCOMPARE(foobars->functions().size(), 4);

    const AbstractMetaClass *lc = templates.constFirst();
    QCOMPARE(lc->functions().size(), 2);
}

void TestTemplates::testTemplateInheritanceMixedWithForwardDeclaration()
{
    const char cppCode[] = R"CPP(
enum SomeEnum { E1, E2 };
template<SomeEnum type> struct Future;
template<SomeEnum type>
struct A {
    A();
    void method();
    friend struct Future<type>;
};
typedef A<E1> B;
template<SomeEnum type> struct Future {};
)CPP";

    const char xmlCode[] = R"XML(
<typesystem package='Package'>
    <enum-type name='SomeEnum'/>
    <value-type name='A' generate='no'/>
    <value-type name='B'/>
    <value-type name='Future' generate='no'/>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();

    AbstractMetaClass* classB = AbstractMetaClass::findClass(classes, u"B");
    QVERIFY(classB);
    QVERIFY(!classB->baseClass());
    QVERIFY(classB->baseClassName().isEmpty());
    // 3 functions: simple constructor, copy constructor and "method()".
    QCOMPARE(classB->functions().size(), 3);
}

void TestTemplates::testTemplateInheritanceMixedWithNamespaceAndForwardDeclaration()
{
    const char cppCode[] = R"CPP(
namespace Namespace {
enum SomeEnum { E1, E2 };
template<SomeEnum type> struct Future;
template<SomeEnum type>
struct A {
    A();
    void method();
    friend struct Future<type>;
};
typedef A<E1> B;
template<SomeEnum type> struct Future {};
};
)CPP";

    const char xmlCode[] = R"XML(
<typesystem package='Package'>
    <namespace-type name='Namespace'>
        <enum-type name='SomeEnum'/>
        <value-type name='A' generate='no'/>
        <value-type name='B'/>
        <value-type name='Future' generate='no'/>
    </namespace-type>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();

    AbstractMetaClass* classB = AbstractMetaClass::findClass(classes, u"Namespace::B");
    QVERIFY(classB);
    QVERIFY(!classB->baseClass());
    QVERIFY(classB->baseClassName().isEmpty());
    // 3 functions: simple constructor, copy constructor and "method()".
    QCOMPARE(classB->functions().size(), 3);
}

void TestTemplates::testTypedefOfInstantiationOfTemplateClass()
{
    const char cppCode[] = R"CPP(
namespace NSpace {
enum ClassType {
    TypeOne
};
template<ClassType CLASS_TYPE>
struct BaseTemplateClass {
    inline ClassType getClassType() const { return CLASS_TYPE; }
};
typedef BaseTemplateClass<TypeOne> TypeOneClass;
}
)CPP";

    const char xmlCode[] = R"XML(
<typesystem package='Package'>
    <namespace-type name='NSpace'>
        <enum-type name='ClassType'/>
        <object-type name='BaseTemplateClass' generate='no'/>
        <object-type name='TypeOneClass'/>
    </namespace-type>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 3);

    const AbstractMetaClass* base = AbstractMetaClass::findClass(classes, u"BaseTemplateClass");
    QVERIFY(base);
    const AbstractMetaClass* one = AbstractMetaClass::findClass(classes, u"TypeOneClass");
    QVERIFY(one);
    QCOMPARE(one->templateBaseClass(), base);
    QCOMPARE(one->functions().size(), base->functions().size());
    QVERIFY(one->isTypeDef());
    const ComplexTypeEntry* oneType = one->typeEntry();
    const ComplexTypeEntry* baseType = base->typeEntry();
    QCOMPARE(oneType->baseContainerType(), baseType);
    QCOMPARE(one->baseClassNames(), QStringList(u"BaseTemplateClass<TypeOne>"_s));

    QVERIFY(one->hasTemplateBaseClassInstantiations());
    AbstractMetaTypeList instantiations = one->templateBaseClassInstantiations();
    QCOMPARE(instantiations.size(), 1);
    const AbstractMetaType &inst = instantiations.constFirst();
    QVERIFY(!inst.isEnum());
    QVERIFY(!inst.typeEntry()->isEnum());
    QVERIFY(inst.typeEntry()->isEnumValue());
    QCOMPARE(inst.cppSignature(), u"NSpace::TypeOne");
}

void TestTemplates::testContainerTypeIncompleteArgument()
{
    const char cppCode[] = R"CPP(
template<typename T>
class Vector {
    void method(const Vector& vector);
    Vector otherMethod();
};
template <typename T>
void Vector<T>::method(const Vector<T>& vector) {}
template <typename T>
Vector<T> Vector<T>::otherMethod() { return Vector<T>(); }
typedef Vector<int> IntVector;
)CPP";

    const char xmlCode[] = R"XML(
<typesystem package='Foo'>
    <primitive-type name='int'/>
    <container-type name='Vector' type='vector'/>
    <value-type name='IntVector'/>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, true));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 1);

    AbstractMetaClass* vector = AbstractMetaClass::findClass(classes, u"IntVector");
    QVERIFY(vector);
    auto baseContainer = vector->typeEntry()->baseContainerType();
    QVERIFY(baseContainer);
    QCOMPARE(reinterpret_cast<const ContainerTypeEntry*>(baseContainer)->containerKind(),
             ContainerTypeEntry::ListContainer);
    QCOMPARE(vector->functions().size(), 4);

    const auto method = vector->findFunction(u"method");
    QVERIFY(!method.isNull());
    QCOMPARE(method->signature(), u"method(const Vector<int > & vector)");

    const auto otherMethod = vector->findFunction(u"otherMethod");
    QVERIFY(!otherMethod.isNull());
    QCOMPARE(otherMethod->signature(), u"otherMethod()");
    QVERIFY(!otherMethod->type().isVoid());
    QCOMPARE(otherMethod->type().cppSignature(), u"Vector<int >");
}

void TestTemplates::testNonTypeTemplates()
{
    // PYSIDe-1296, functions with non type templates parameters.
    const char cppCode[] = R"CPP(
template <class T, int Size>
class Array {
    T array[Size];
};

Array<int, 2> foo();

)CPP";

    const char xmlCode[] = R"XML(
<typesystem package='Foo'>
    <primitive-type name='int'/>
    <container-type name='Array' type='vector'/>
    <function signature="foo()"/>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, true));
    QVERIFY(!builder.isNull());
    auto functions = builder->globalFunctions();
    QCOMPARE(functions.size(), 1);
    auto foo = functions.constFirst();
    QCOMPARE(foo->name(), u"foo");
    QCOMPARE(foo->type().name(), u"Array");
}

// Perform checks on template inheritance; a typedef of a template class
// should result in rewritten types.
void TestTemplates::testTemplateTypeDefs_data()
{
    QTest::addColumn<QString>("cpp");
    QTest::addColumn<QString>("xml");

    const char optionalClassDef[] = R"CPP(
template<class T> // Some value type similar to std::optional
class Optional {
public:
    T value() const { return m_value; }
    operator bool() const { return m_success; }

    T m_value;
    bool m_success  = false;
};
)CPP";

    const char xmlPrefix[] = R"XML(
<typesystem package='Foo'>
    <primitive-type name='int'/>
    <primitive-type name='bool'/>
)XML";

    const char xmlOptionalDecl[] = "<value-type name='Optional' generate='no'/>\n";
    const char xmlOptionalIntDecl[] = "<value-type name='IntOptional'/>\n";
    const char xmlPostFix[] = "</typesystem>\n";

    // Flat, global namespace
    QString cpp;
    QTextStream(&cpp) << optionalClassDef
        << "typedef Optional<int> IntOptional;\n";
    QString xml;
    QTextStream(&xml) << xmlPrefix << xmlOptionalDecl << xmlOptionalIntDecl
        << "<typedef-type name='XmlIntOptional' source='Optional&lt;int&gt;'/>"
        << xmlPostFix;
    QTest::newRow("global-namespace")
        << cpp << xml;

    // Typedef from namespace Std
    cpp.clear();
    QTextStream(&cpp) << "namespace Std {\n" << optionalClassDef << "}\n"
        << "typedef Std::Optional<int> IntOptional;\n";
    xml.clear();
    QTextStream(&xml) << xmlPrefix
        << "<namespace-type name='Std'>\n" << xmlOptionalDecl
        << "</namespace-type>\n" << xmlOptionalIntDecl
        << "<typedef-type name='XmlIntOptional' source='Std::Optional&lt;int&gt;'/>"
        << xmlPostFix;
    QTest::newRow("namespace-Std")
        << cpp << xml;

    // Typedef from nested class
    cpp.clear();
    QTextStream(&cpp) << "class Outer {\npublic:\n" << optionalClassDef << "\n};\n"
        << "typedef Outer::Optional<int> IntOptional;\n";
    xml.clear();
    QTextStream(&xml) << xmlPrefix
        << "<object-type name='Outer'>\n" << xmlOptionalDecl
        << "</object-type>\n" << xmlOptionalIntDecl
        << "<typedef-type name='XmlIntOptional' source='Outer::Optional&lt;int&gt;'/>"
        << xmlPostFix;
    QTest::newRow("nested-class")
        << cpp << xml;
}

void TestTemplates::testTemplateTypeDefs()
{
    QFETCH(QString, cpp);
    QFETCH(QString, xml);

    const QByteArray cppBa = cpp.toLocal8Bit();
    const QByteArray xmlBa = xml.toLocal8Bit();
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppBa.constData(), xmlBa.constData(), true));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();

    const AbstractMetaClass *optional = AbstractMetaClass::findClass(classes, u"Optional");
    QVERIFY(optional);

    // Find the typedef'ed class
    const AbstractMetaClass *optionalInt =
        AbstractMetaClass::findClass(classes, u"IntOptional");
    QVERIFY(optionalInt);
    QCOMPARE(optionalInt->templateBaseClass(), optional);

    // Find the class typedef'ed in the typesystem XML
    const AbstractMetaClass *xmlOptionalInt =
        AbstractMetaClass::findClass(classes, u"XmlIntOptional");
    QVERIFY(xmlOptionalInt);
    QCOMPARE(xmlOptionalInt->templateBaseClass(), optional);

    // Check whether the value() method now has an 'int' return
    const auto valueMethod = optionalInt->findFunction(u"value");
    QVERIFY(!valueMethod.isNull());
    QCOMPARE(valueMethod->type().cppSignature(), u"int");

    // ditto for typesystem XML
    const auto xmlValueMethod = xmlOptionalInt->findFunction(u"value");
    QVERIFY(!xmlValueMethod.isNull());
    QCOMPARE(xmlValueMethod->type().cppSignature(), u"int");

    // Check whether the m_value field is of type 'int'
    const auto valueField = optionalInt->findField(u"m_value");
    QVERIFY(valueField.has_value());
    QCOMPARE(valueField->type().cppSignature(), u"int");

    // ditto for typesystem XML
    const auto xmlValueField =
        xmlOptionalInt->findField(u"m_value");
    QVERIFY(xmlValueField.has_value());
    QCOMPARE(xmlValueField->type().cppSignature(), u"int");
}

void TestTemplates::testTemplateTypeAliases()
{
    // Model Qt 6's "template<typename T> using QList = QVector<T>"
    const char cppCode[] = R"CPP(
template<typename T>
class Container1 { };

template<typename T>
using Container2 = Container1<T>;

class Test
{
public:
    Container2<int> m_intContainer;
};

class Derived : public Container2<int>
{
public:
};
)CPP";

    const char xmlCode[] = R"XML(
<typesystem package='Foo'>
    <primitive-type name='int'/>
    <value-type name='Container1'/>
    <value-type name='Derived'/>
    <object-type name='Test'/>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, true));
    QVERIFY(!builder.isNull());

    AbstractMetaClassList classes = builder->classes();
    auto testClass = AbstractMetaClass::findClass(classes, u"Test");
    QVERIFY(testClass);

    auto fields = testClass->fields();
    QCOMPARE(fields.size(), 1);
    auto fieldType = testClass->fields().at(0).type();
    QCOMPARE(fieldType.name(), u"Container1");
    QCOMPARE(fieldType.instantiations().size(), 1);

    auto derived = AbstractMetaClass::findClass(classes, u"Derived");
    QVERIFY(derived);
    auto base = derived->templateBaseClass();
    QCOMPARE(base->name(), u"Container1");
}

QTEST_APPLESS_MAIN(TestTemplates)
