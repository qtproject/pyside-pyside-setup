// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testaddfunction.h"
#include "testutil.h"
#include <abstractmetaargument.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetatype.h>
#include <codesnip.h>
#include <addedfunction.h>
#include <addedfunction_p.h>
#include <complextypeentry.h>
#include <primitivetypeentry.h>

#include <qtcompat.h>

#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestAddFunction::testParsingFuncNameAndConstness()
{
    // generic test...
    const char sig1[] = "func(type1, const type2, const type3* const)";
    QString errorMessage;
    auto f1 = AddedFunction::createAddedFunction(QLatin1StringView(sig1), u"void"_s,
                                                 &errorMessage);
    QVERIFY2(f1, qPrintable(errorMessage));
    QCOMPARE(f1->name(), u"func");
    QCOMPARE(f1->arguments().size(), 3);
    TypeInfo retval = f1->returnType();
    QCOMPARE(retval.qualifiedName(), QStringList{u"void"_s});
    QCOMPARE(retval.indirections(), 0);
    QCOMPARE(retval.isConstant(), false);
    QCOMPARE(retval.referenceType(), NoReference);

    // test with a ugly template as argument and other ugly stuff
    const char sig2[] = "    _fu__nc_       (  type1, const type2, const Abc<int& , C<char*> *   >  * *@my_name@, const type3* const    )   const ";
    auto f2 = AddedFunction::createAddedFunction(QLatin1StringView(sig2),
                                                 u"const Abc<int& , C<char*> *   >  * *"_s,
                                                 &errorMessage);
    QVERIFY2(f2, qPrintable(errorMessage));
    QCOMPARE(f2->name(), u"_fu__nc_");
    const auto &args = f2->arguments();
    QCOMPARE(args.size(), 4);
    retval = f2->returnType();
    QCOMPARE(retval.qualifiedName(), QStringList{u"Abc"_s});
    QCOMPARE(retval.instantiations().size(), 2);
    QCOMPARE(retval.toString(), u"const Abc<int&, C<char*>*>**");
    QCOMPARE(retval.indirections(), 2);
    QCOMPARE(retval.isConstant(), true);
    QCOMPARE(retval.referenceType(), NoReference);
    QVERIFY(args.at(0).name.isEmpty());
    QVERIFY(args.at(1).name.isEmpty());

    QCOMPARE(args.at(2).name, u"my_name");
    auto arg2Type = args.at(2).typeInfo;
    QCOMPARE(arg2Type.qualifiedName(), QStringList{u"Abc"_s});
    QCOMPARE(arg2Type.instantiations().size(), 2);
    QCOMPARE(arg2Type.toString(), u"const Abc<int&, C<char*>*>**");
    QCOMPARE(arg2Type.indirections(), 2);
    QCOMPARE(arg2Type.isConstant(), true);
    QCOMPARE(arg2Type.referenceType(), NoReference);

    QVERIFY(args.at(3).name.isEmpty());

    // function with no args.
    const char sig3[] = "func()";
    auto f3 = AddedFunction::createAddedFunction(QLatin1StringView(sig3), u"void"_s,
                                                 &errorMessage);
    QVERIFY2(f3, qPrintable(errorMessage));
    QCOMPARE(f3->name(), u"func");
    QCOMPARE(f3->arguments().size(), 0);

    // const call operator
    const char sig4[] = "operator()(int)const";
    auto f4 = AddedFunction::createAddedFunction(QLatin1StringView(sig4), u"int"_s,
                                                 &errorMessage);
    QVERIFY2(f4, qPrintable(errorMessage));
    QCOMPARE(f4->name(), u"operator()");
    QCOMPARE(f4->arguments().size(), 1);
    QVERIFY(f4->isConstant());
}

void TestAddFunction::testAddFunction()
{
    const char cppCode[] = R"CPP(
struct B {};
struct A {
    void a(int);
};)CPP";
    const char xmlCode[] = R"XML(
<typesystem package='Foo'>
    <primitive-type name='int'/>
    <primitive-type name='float'/>
    <value-type name='B'/>
    <value-type name='A'>
        <add-function signature='b(int, float = 4.6, const B&amp;)' return-type='int' access='protected'/>
        <add-function signature='operator()(int)' return-type='int' access='public'/>
    </value-type>
</typesystem>)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    auto *typeDb = TypeDatabase::instance();
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    // default ctor, default copy ctor, func a() and the added functions
    QCOMPARE(classA->functions().size(), 5);

    auto addedFunc = classA->findFunction(u"b");
    QVERIFY(addedFunc);
    QCOMPARE(addedFunc->access(), Access::Protected);
    QCOMPARE(addedFunc->functionType(), AbstractMetaFunction::NormalFunction);
    QVERIFY(addedFunc->isUserAdded());
    QCOMPARE(addedFunc->ownerClass(), classA);
    QCOMPARE(addedFunc->implementingClass(), classA);
    QCOMPARE(addedFunc->declaringClass(), classA);
    QVERIFY(!addedFunc->isVirtual());
    QVERIFY(!addedFunc->isSignal());
    QVERIFY(!addedFunc->isSlot());
    QVERIFY(!addedFunc->isStatic());

    AbstractMetaType returnType = addedFunc->type();
    QCOMPARE(returnType.typeEntry(), typeDb->findPrimitiveType(u"int"_s));
    const AbstractMetaArgumentList &args = addedFunc->arguments();
    QCOMPARE(args.size(), 3);
    QCOMPARE(args.at(0).type().typeEntry(), returnType.typeEntry());
    QCOMPARE(args.at(1).defaultValueExpression(), u"4.6");
    QCOMPARE(args.at(2).type().typeEntry(), typeDb->findType(u"B"_s));

    auto addedCallOperator = classA->findFunction(u"operator()");
    QVERIFY(addedCallOperator);
}

void TestAddFunction::testAddFunctionConstructor()
{
    const char cppCode[] = "struct A { A() {} };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <value-type name='A'>\n\
            <add-function signature='A(int)'/>\n\
        </value-type>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    QCOMPARE(classA->functions().size(), 3); // default and added ctors
    const auto addedFunc = classA->functions().constLast();
    QCOMPARE(addedFunc->access(), Access::Public);
    QCOMPARE(addedFunc->functionType(), AbstractMetaFunction::ConstructorFunction);
    QCOMPARE(addedFunc->arguments().size(), 1);
    QVERIFY(addedFunc->isUserAdded());
    QVERIFY(addedFunc->isVoid());
}

void TestAddFunction::testAddFunctionTagDefaultValues()
{
    const char cppCode[] = "struct A {};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <value-type name='A'>\n\
            <add-function signature='func()'/>\n\
        </value-type>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    // default ctor, default copy ctor and the added function
    QCOMPARE(classA->functions().size(), 3);
    const auto addedFunc = classA->functions().constLast();
    QCOMPARE(addedFunc->access(), Access::Public);
    QCOMPARE(addedFunc->functionType(), AbstractMetaFunction::NormalFunction);
    QVERIFY(addedFunc->isUserAdded());
    QVERIFY(addedFunc->isVoid());
}

void TestAddFunction::testAddFunctionCodeSnippets()
{
    const char cppCode[] = "struct A {};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <value-type name='A'>\n\
            <add-function signature='func()'>\n\
                <inject-code class='target' position='end'>Hi!, I am the code.</inject-code>\n\
            </add-function>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto addedFunc = classA->functions().constLast();
    QVERIFY(addedFunc->hasInjectedCode());
}

void TestAddFunction::testAddFunctionWithoutParenteses()
{
    const char sig1[] = "func";
    QString errorMessage;
    auto f1 = AddedFunction::createAddedFunction(QLatin1StringView(sig1), u"void"_s,
                                                 &errorMessage);
    QVERIFY2(f1, qPrintable(errorMessage));
    QCOMPARE(f1->name(), u"func");
    QCOMPARE(f1->arguments().size(), 0);
    QCOMPARE(f1->isConstant(), false);

    const char cppCode[] = "struct A {};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <value-type name='A'>\n\
            <add-function signature='func'>\n\
                <inject-code class='target' position='end'>Hi!, I am the code.</inject-code>\n\
            </add-function>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto addedFunc = classA->findFunction(u"func");
    QVERIFY(addedFunc);
    QVERIFY(addedFunc->hasInjectedCode());
    const auto snips = addedFunc->injectedCodeSnips(TypeSystem::CodeSnipPositionAny,
                                                    TypeSystem::TargetLangCode);
    QCOMPARE(snips.size(), 1);
}

void TestAddFunction::testAddFunctionWithDefaultArgs()
{
    const char sig1[] = "func";
    QString errorMessage;
    auto f1 = AddedFunction::createAddedFunction(QLatin1StringView(sig1), u"void"_s,
                                                 &errorMessage);
    QVERIFY2(f1, qPrintable(errorMessage));
    QCOMPARE(f1->name(), u"func");
    QCOMPARE(f1->arguments().size(), 0);
    QCOMPARE(f1->isConstant(), false);

    const char cppCode[] = "struct A { };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <value-type name='A'>\n\
            <add-function signature='func(int, int)'>\n\
              <modify-argument index='2'>\n\
                <replace-default-expression with='2'/>\n\
              </modify-argument>\n\
            </add-function>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto addedFunc = classA->findFunction(u"func");
    QVERIFY(addedFunc);
    const AbstractMetaArgument &arg = addedFunc->arguments().at(1);
    QCOMPARE(arg.defaultValueExpression(), u"2");
}

void TestAddFunction::testAddFunctionAtModuleLevel()
{
    const char cppCode[] = "struct A { };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <value-type name='A'/>\n\
        <add-function signature='func(int, int)'>\n\
            <inject-code class='target' position='beginning'>custom_code();</inject-code>\n\
        </add-function>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);

    auto *typeDb = TypeDatabase::instance();

    AddedFunctionList addedFuncs = typeDb->findGlobalUserFunctions(u"func"_s);

    QCOMPARE(addedFuncs.size(), 1);

    auto &mods = addedFuncs.constFirst()->modifications();

    QCOMPARE(mods.size(), 1);
    QVERIFY(mods.constFirst().isCodeInjection());
    CodeSnip snip = mods.constFirst().snips().constFirst();
    QCOMPARE(snip.code().trimmed(), u"custom_code();");
}

void TestAddFunction::testAddFunctionWithVarargs()
{
    const char sig1[] = "func(int,char,...)";
    QString errorMessage;
    auto f1 = AddedFunction::createAddedFunction(QLatin1StringView(sig1), u"void"_s,
                                                 &errorMessage);
    QVERIFY2(f1, qPrintable(errorMessage));
    QCOMPARE(f1->name(), u"func");
    QCOMPARE(f1->arguments().size(), 3);
    QVERIFY(!f1->isConstant());

    const char cppCode[] = "struct A {};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <primitive-type name='char'/>\n\
        <value-type name='A'>\n\
            <add-function signature='func(int,char,...)'/>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto addedFunc = classA->findFunction(u"func");
    QVERIFY(addedFunc);
    const AbstractMetaArgument &arg = addedFunc->arguments().constLast();
    QVERIFY(arg.type().isVarargs());
    QVERIFY(arg.type().typeEntry()->isVarargs());
}

void TestAddFunction::testAddStaticFunction()
{
    const char cppCode[] = "struct A { };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <value-type name='A'>\n\
            <add-function signature='func(int, int)' static='yes'>\n\
                <inject-code class='target' position='beginning'>custom_code();</inject-code>\n\
            </add-function>\n\
        </value-type>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto addedFunc = classA->findFunction(u"func");
    QVERIFY(addedFunc);
    QVERIFY(addedFunc->isStatic());
}

void TestAddFunction::testAddGlobalFunction()
{
    const char cppCode[] = "struct A { };struct B {};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <value-type name='A'/>\n\
        <add-function signature='globalFunc(int, int)' static='yes'>\n\
            <inject-code class='target' position='beginning'>custom_code();</inject-code>\n\
        </add-function>\n\
        <add-function signature='globalFunc2(int, int)' static='yes'>\n\
            <inject-code class='target' position='beginning'>custom_code();</inject-code>\n\
        </add-function>\n\
        <value-type name='B'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    const auto globalFuncs = builder->globalFunctions();
    QCOMPARE(globalFuncs.size(), 2);
    const auto classB = AbstractMetaClass::findClass(builder->classes(), u"B");
    QVERIFY(classB);
    QVERIFY(!classB->findFunction(u"globalFunc"));
    QVERIFY(!classB->findFunction(u"globalFunc2"));
    QVERIFY(!globalFuncs[0]->injectedCodeSnips().isEmpty());
    QVERIFY(!globalFuncs[1]->injectedCodeSnips().isEmpty());
}

void TestAddFunction::testAddFunctionWithApiVersion()
{
    const char cppCode[] = "";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <add-function signature='globalFunc(int, int)' static='yes' since='1.3'>\n\
            <inject-code class='target' position='beginning'>custom_code();</inject-code>\n\
        </add-function>\n\
        <add-function signature='globalFunc2(int, int)' static='yes' since='0.1'>\n\
            <inject-code class='target' position='beginning'>custom_code();</inject-code>\n\
        </add-function>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode,
                                                                true, u"0.1"_s));
    QVERIFY(builder);
    const auto globalFuncs = builder->globalFunctions();
    QCOMPARE(globalFuncs.size(), 1);
}

void TestAddFunction::testModifyAddedFunction()
{
    const char cppCode[] = "class Foo { };\n";
    const char xmlCode[] = R"(
<typesystem package='Package'>
    <primitive-type name='float'/>
    <primitive-type name='int'/>
    <value-type name='Foo'>
        <add-function signature='method(float, int)'>
            <inject-code class='target' position='beginning'>custom_code();</inject-code>
            <modify-argument index='2' rename='varName'>
                <replace-default-expression with='0'/>
            </modify-argument>
        </add-function>
    </value-type>
</typesystem>
)";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto foo = AbstractMetaClass::findClass(classes, u"Foo");
    const auto method = foo->findFunction(u"method");
    QVERIFY(method);
    QCOMPARE(method->arguments().size(), 2);
    const AbstractMetaArgument &arg = method->arguments().at(1);
    QCOMPARE(arg.defaultValueExpression(), u"0");
    QCOMPARE(arg.name(), u"varName");
    QCOMPARE(method->argumentName(2), u"varName");
}

void TestAddFunction::testAddFunctionOnTypedef()
{
    const char cppCode[] = "template<class T> class Foo { }; typedef Foo<int> FooInt;\n";
    const char xmlCode[] = "\
    <typesystem package='Package'>\n\
        <value-type name='FooInt'>\n\
            <add-function signature='FooInt(PySequence)'>\n\
                <inject-code class='target' position='beginning'>custom_code();</inject-code>\n\
            </add-function>\n\
            <add-function signature='method()'>\n\
                <inject-code class='target' position='beginning'>custom_code();</inject-code>\n\
            </add-function>\n\
        </value-type>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto foo = AbstractMetaClass::findClass(classes, u"FooInt");
    QVERIFY(foo);
    QVERIFY(foo->hasNonPrivateConstructor());
    const auto &lst = foo->queryFunctions(FunctionQueryOption::AnyConstructor);
    for (const auto &f : lst)
        QVERIFY(f->signature().startsWith(f->name()));
    QCOMPARE(lst.size(), 2);
    const auto method = foo->findFunction(u"method");
    QVERIFY(method);
}

void TestAddFunction::testAddFunctionWithTemplateArg()
{
    const char cppCode[] = "template<class T> class Foo { };\n";
    const char xmlCode[] = "\
    <typesystem package='Package'>\n\
        <primitive-type name='int'/>\n\
        <container-type name='Foo' type='list'/>\n\
        <add-function signature='func(Foo&lt;int>)'/>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    QCOMPARE(builder->globalFunctions().size(), 1);
    const auto func = builder->globalFunctions().constFirst();
    const AbstractMetaArgument &arg = func->arguments().constFirst();
    QCOMPARE(arg.type().instantiations().size(), 1);
}

// Test splitting of <add-function> parameter lists.

Q_DECLARE_METATYPE(AddedFunctionParser::Argument)

using Arguments = AddedFunctionParser::Arguments;

void TestAddFunction::testAddFunctionTypeParser_data()
{
    QTest::addColumn<QString>("parameterList");
    QTest::addColumn<Arguments>("expected");

    QTest::newRow("empty")
        << QString() << Arguments{};

    QTest::newRow("1-arg")
       << QString::fromLatin1("int @a@=42")
       << Arguments{{u"int"_s, u"a"_s, u"42"_s}};

    QTest::newRow("2-args")
       << QString::fromLatin1("double @d@, int @a@=42")
       << Arguments{{u"double"_s, u"d"_s, {}},
                    {u"int"_s, u"a"_s, u"42"_s}};

    QTest::newRow("template-var_args")
       << QString::fromLatin1("const QList<X,Y> &@list@ = QList<X,Y>{1,2}, int @b@=5, ...")
       << Arguments{{u"const QList<X,Y> &"_s, u"list"_s, u"QList<X,Y>{1,2}"_s},
                    {u"int"_s, u"b"_s, u"5"_s},
                    {u"..."_s, {}, {}}};
}

void TestAddFunction::testAddFunctionTypeParser()
{

    QFETCH(QString, parameterList);
    QFETCH(Arguments, expected);

    const auto actual = AddedFunctionParser::splitParameters(parameterList);
    QCOMPARE(actual, expected);
}

QTEST_APPLESS_MAIN(TestAddFunction)
