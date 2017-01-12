/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Copyright (C) 2002-2005 Roberto Raggi <roberto@kdevelop.org>
** Contact: https://www.qt.io/licensing/
**
** This file is part of PySide2.
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

#include "binder.h"
#include "lexer.h"
#include "control.h"
#include "symbol.h"
#include "codemodel_finder.h"
#include "class_compiler.h"
#include "compiler_utils.h"
#include "tokens.h"
#include "dumptree.h"

#include <iostream>
#include <QDebug>

Binder::Binder(CodeModel *__model, LocationManager &__location, Control *__control)
        : _M_model(__model),
        _M_location(__location),
        _M_token_stream(&_M_location.token_stream),
        _M_control(__control),
        _M_current_function_type(CodeModel::Normal),
        type_cc(this),
        name_cc(this),
        decl_cc(this)
{
    _M_qualified_types.insert(QLatin1String("char"), QString());
    _M_qualified_types.insert(QLatin1String("double"), QString());
    _M_qualified_types.insert(QLatin1String("float"), QString());
    _M_qualified_types.insert(QLatin1String("int"), QString());
    _M_qualified_types.insert(QLatin1String("long"), QString());
    _M_qualified_types.insert(QLatin1String("short"), QString());
    _M_qualified_types.insert(QLatin1String("void"), QString());
}

Binder::~Binder()
{
}

FileModelItem Binder::run(AST *node)
{
    FileModelItem old = _M_current_file;
    _M_current_access = CodeModel::Public;

    _M_current_file.reset(new _FileModelItem(model()));
    updateItemPosition(_M_current_file, node);
    visit(node);
    FileModelItem result = _M_current_file;

    _M_current_file = old; // restore

    return result;
}

ScopeModelItem Binder::currentScope()
{
    if (_M_current_class)
        return _M_current_class;
    else if (_M_current_namespace)
        return _M_current_namespace;

    return _M_current_file;
}

TemplateParameterList Binder::changeTemplateParameters(TemplateParameterList templateParameters)
{
    TemplateParameterList old = _M_current_template_parameters;
    _M_current_template_parameters = templateParameters;
    return old;
}

CodeModel::FunctionType Binder::changeCurrentFunctionType(CodeModel::FunctionType functionType)
{
    CodeModel::FunctionType old = _M_current_function_type;
    _M_current_function_type = functionType;
    return old;
}

CodeModel::AccessPolicy Binder::changeCurrentAccess(CodeModel::AccessPolicy accessPolicy)
{
    CodeModel::AccessPolicy old = _M_current_access;
    _M_current_access = accessPolicy;
    return old;
}

NamespaceModelItem Binder::changeCurrentNamespace(NamespaceModelItem item)
{
    NamespaceModelItem old = _M_current_namespace;
    _M_current_namespace = item;
    return old;
}

ClassModelItem Binder::changeCurrentClass(ClassModelItem item)
{
    ClassModelItem old = _M_current_class;
    _M_current_class = item;
    return old;
}

FunctionDefinitionModelItem Binder::changeCurrentFunction(FunctionDefinitionModelItem item)
{
    FunctionDefinitionModelItem old = _M_current_function;
    _M_current_function = item;
    return old;
}

int Binder::decode_token(std::size_t index) const
{
    return _M_token_stream->kind(index);
}

CodeModel::AccessPolicy Binder::decode_access_policy(std::size_t index) const
{
    switch (decode_token(index)) {
    case Token_class:
        return CodeModel::Private;

    case Token_struct:
    case Token_union:
        return CodeModel::Public;

    default:
        return CodeModel::Public;
    }
}

CodeModel::ClassType Binder::decode_class_type(std::size_t index) const
{
    switch (decode_token(index)) {
    case Token_class:
        return CodeModel::Class;
    case Token_struct:
        return CodeModel::Struct;
    case Token_union:
        return CodeModel::Union;
    default:
        std::cerr << "** WARNING unrecognized class type" << std::endl;
    }
    return CodeModel::Class;
}

const NameSymbol *Binder::decode_symbol(std::size_t index) const
{
    return _M_token_stream->symbol(index);
}

void Binder::visitAccessSpecifier(AccessSpecifierAST *node)
{
    const ListNode<std::size_t> *it =  node->specs;
    if (!it)
        return;

    it = it->toFront();
    const ListNode<std::size_t> *end = it;

    do {
        switch (decode_token(it->element)) {
        default:
            break;

        case Token_public:
            changeCurrentAccess(CodeModel::Public);
            changeCurrentFunctionType(CodeModel::Normal);
            break;
        case Token_protected:
            changeCurrentAccess(CodeModel::Protected);
            changeCurrentFunctionType(CodeModel::Normal);
            break;
        case Token_private:
            changeCurrentAccess(CodeModel::Private);
            changeCurrentFunctionType(CodeModel::Normal);
            break;
        case Token_signals:
            changeCurrentAccess(CodeModel::Protected);
            changeCurrentFunctionType(CodeModel::Signal);
            break;
        case Token_slots:
            changeCurrentFunctionType(CodeModel::Slot);
            break;
        }
        it = it->next;
    } while (it != end);
}

void Binder::visitSimpleDeclaration(SimpleDeclarationAST *node)
{
    visit(node->type_specifier);

    if (const ListNode<InitDeclaratorAST*> *it = node->init_declarators) {
        it = it->toFront();
        const ListNode<InitDeclaratorAST*> *end = it;
        do {
            InitDeclaratorAST *init_declarator = it->element;
            declare_symbol(node, init_declarator);
            it = it->next;
        } while (it != end);
    }
}

void Binder::declare_symbol(SimpleDeclarationAST *node, InitDeclaratorAST *init_declarator)
{
    DeclaratorAST *declarator = init_declarator->declarator;

    while (declarator && declarator->sub_declarator)
        declarator = declarator->sub_declarator;

    NameAST *id = declarator->id;
    if (!declarator->id) {
        std::cerr << "** WARNING expected a declarator id" << std::endl;
        return;
    }

    CodeModelFinder finder(model(), this);
    ScopeModelItem symbolScope = finder.resolveScope(id, currentScope());
    if (!symbolScope) {
        name_cc.run(id);
        std::cerr << "** WARNING scope not found for symbol:"
                  << qPrintable(name_cc.name()) << std::endl;
        return;
    }

    decl_cc.run(declarator);

    if (decl_cc.isFunction()) {
        name_cc.run(id->unqualified_name);

        FunctionModelItem fun(new _FunctionModelItem(model(), name_cc.name()));
        updateItemPosition(fun, node);
        fun->setAccessPolicy(_M_current_access);
        fun->setFunctionType(_M_current_function_type);
        fun->setAbstract(init_declarator->initializer != 0);
        fun->setConstant(declarator->fun_cv != 0);
        fun->setTemplateParameters(_M_current_template_parameters);
        applyStorageSpecifiers(node->storage_specifiers, fun);
        applyFunctionSpecifiers(node->function_specifiers, fun);

        // build the type
        TypeInfo typeInfo = CompilerUtils::typeDescription(node->type_specifier,
                                                           declarator,
                                                           this);

        fun->setType(qualifyType(typeInfo, symbolScope->qualifiedName()));


        fun->setVariadics(decl_cc.isVariadics());

        // ... and the signature
        foreach (const DeclaratorCompiler::Parameter &p, decl_cc.parameters()) {
            ArgumentModelItem arg(new _ArgumentModelItem(model(), p.name));
            arg->setType(qualifyType(p.type, _M_context));
            arg->setDefaultValue(p.defaultValue);
            if (p.defaultValue)
                arg->setDefaultValueExpression(p.defaultValueExpression);
            fun->addArgument(arg);
        }

        fun->setScope(symbolScope->qualifiedName());
        symbolScope->addFunction(fun);
    } else {
        VariableModelItem var(new _VariableModelItem(model()));
        updateItemPosition(var, node);
        var->setTemplateParameters(_M_current_template_parameters);
        var->setAccessPolicy(_M_current_access);
        name_cc.run(id->unqualified_name);
        var->setName(name_cc.name());
        // Possible bug, because second parameter uses declarator instead of
        // init_declarator->declarator like in DeclaratorCompiler::visitParameterDeclaration,
        // but it doesn't seem to affect anything because the generator doesn't currently use
        // variable declarations, only function declarations (because it cares about the API only,
        // variable declarations are not exposed to the target language).
        // See PYSIDE-455.
        TypeInfo typeInfo = CompilerUtils::typeDescription(node->type_specifier,
                                                           declarator,
                                                           this);
        if (declarator != init_declarator->declarator
            && init_declarator->declarator->parameter_declaration_clause) {
            typeInfo.setFunctionPointer(true);
            decl_cc.run(init_declarator->declarator);
            foreach (const DeclaratorCompiler::Parameter &p, decl_cc.parameters())
            typeInfo.addArgument(p.type);
        }

        var->setType(qualifyType(typeInfo, _M_context));
        applyStorageSpecifiers(node->storage_specifiers, var);

        var->setScope(symbolScope->qualifiedName());
        symbolScope->addVariable(var);
    }
}

void Binder::visitFunctionDefinition(FunctionDefinitionAST *node)
{
    Q_ASSERT(node->init_declarator);

    ScopeModelItem scope = currentScope();

    InitDeclaratorAST *init_declarator = node->init_declarator;
    DeclaratorAST *declarator = init_declarator->declarator;

    // in the case of "void (func)()" or "void ((func))()" we need to
    // skip to the inner most.  This is in line with how the declarator
    // node is generated in 'parser.cpp'
    while (declarator && declarator->sub_declarator)
        declarator = declarator->sub_declarator;
    if (!declarator->id) {
        std::cerr << "** WARNING temp hack for Qt 5.6.0: "
                  << "skipped a class that inherits from a private class"
                  << std::endl;
        return;
    }
    Q_ASSERT(declarator->id);

    CodeModelFinder finder(model(), this);

    ScopeModelItem functionScope = finder.resolveScope(declarator->id, scope);
    if (!functionScope) {
        name_cc.run(declarator->id);
        std::cerr << "** WARNING scope not found for function definition:"
                  << qPrintable(name_cc.name()) << std::endl
                  << "\tdefinition *ignored*"
                  << std::endl;
        return;
    }

    decl_cc.run(declarator);

    Q_ASSERT(!decl_cc.id().isEmpty());

    FunctionDefinitionModelItem
    old = changeCurrentFunction(FunctionDefinitionModelItem(new _FunctionDefinitionModelItem(_M_model)));
    _M_current_function->setScope(functionScope->qualifiedName());
    updateItemPosition(_M_current_function, node);

    Q_ASSERT(declarator->id->unqualified_name);
    name_cc.run(declarator->id->unqualified_name);
    QString unqualified_name = name_cc.name();

    _M_current_function->setName(unqualified_name);
    TypeInfo tmp_type = CompilerUtils::typeDescription(node->type_specifier,
                                                       declarator, this);

    _M_current_function->setType(qualifyType(tmp_type, _M_context));
    _M_current_function->setAccessPolicy(_M_current_access);
    _M_current_function->setFunctionType(_M_current_function_type);
    _M_current_function->setConstant(declarator->fun_cv);
    _M_current_function->setTemplateParameters(_M_current_template_parameters);

    applyStorageSpecifiers(node->storage_specifiers,
                           _M_current_function);
    applyFunctionSpecifiers(node->function_specifiers,
                            _M_current_function);

    _M_current_function->setVariadics(decl_cc.isVariadics());

    foreach (const DeclaratorCompiler::Parameter &p, decl_cc.parameters()) {
        ArgumentModelItem arg(new _ArgumentModelItem(model(), p.name));
        arg->setType(qualifyType(p.type, functionScope->qualifiedName()));
        arg->setDefaultValue(p.defaultValue);
        if (p.defaultValue)
            arg->setDefaultValueExpression(p.defaultValueExpression);
        _M_current_function->addArgument(arg);
    }

    functionScope->addFunctionDefinition(_M_current_function);

    FunctionModelItem prototype = _M_current_function;
    FunctionModelItem declared = functionScope->declaredFunction(prototype);

    // try to find a function declaration for this definition..
    if (!declared) {
        functionScope->addFunction(prototype);
    } else {
        applyFunctionSpecifiers(node->function_specifiers, declared);

        // fix the function type and the access policy
        _M_current_function->setAccessPolicy(declared->accessPolicy());
        _M_current_function->setFunctionType(declared->functionType());
    }

    changeCurrentFunction(old);
}

void Binder::visitTemplateDeclaration(TemplateDeclarationAST *node)
{
    const ListNode<TemplateParameterAST*> *it = node->template_parameters;
    if (!it) {
        // QtScript: we want to visit the declaration still, so that
        // e.g. QMetaTypeId<Foo> is added to the code model
        visit(node->declaration);
        return;
    }

    TemplateParameterList savedTemplateParameters = changeTemplateParameters(TemplateParameterList());

    it = it->toFront();
    const ListNode<TemplateParameterAST*> *end = it;

    TemplateParameterList templateParameters;
    do {
        TemplateParameterAST *parameter = it->element;
        TypeParameterAST *type_parameter = parameter->type_parameter;

        NameAST *name;
        if (!type_parameter) {
            // A hacky hack to work around missing support for parameter declarations in
            // templates. We just need the to get the name of the variable, since we
            // aren't actually compiling these anyway. We are still not supporting much
            // more, but we are refusing to fail for a few more declarations
            if (!parameter->parameter_declaration ||
                !parameter->parameter_declaration->declarator ||
                !parameter->parameter_declaration->declarator->id) {

                /*std::cerr << "** WARNING template declaration not supported ``";
                Token const &tk = _M_token_stream->token ((int) node->start_token);
                Token const &end_tk = _M_token_stream->token ((int) node->declaration->start_token);

                std::cerr << std::string (&tk.text[tk.position], (end_tk.position) - tk.position) << "''"
                    << std::endl << std::endl;*/

                changeTemplateParameters(savedTemplateParameters);
                return;

            }

            name = parameter->parameter_declaration->declarator->id;
        } else {
            int tk = decode_token(type_parameter->type);
            if (tk != Token_typename && tk != Token_class) {
                /*std::cerr << "** WARNING template declaration not supported ``";
                Token const &tk = _M_token_stream->token ((int) node->start_token);
                Token const &end_tk = _M_token_stream->token ((int) node->declaration->start_token);

                std::cerr << std::string (&tk.text[tk.position], (end_tk.position) - tk.position) << "''"
                << std::endl << std::endl;*/

                changeTemplateParameters(savedTemplateParameters);
                return;
            }
            assert(tk == Token_typename || tk == Token_class);

            name = type_parameter->name;
        }


        name_cc.run(name);
        const TemplateParameterModelItem p(new _TemplateParameterModelItem(model(), name_cc.name()));
        _M_current_template_parameters.append(p);
        it = it->next;
    } while (it != end);

    visit(node->declaration);

    changeTemplateParameters(savedTemplateParameters);
}

void Binder::visitTypedef(TypedefAST *node)
{
    const ListNode<InitDeclaratorAST*> *it = node->init_declarators;
    if (!it)
        return;

    it = it->toFront();
    const ListNode<InitDeclaratorAST*> *end = it;

    do {
        InitDeclaratorAST *init_declarator = it->element;
        it = it->next;

        Q_ASSERT(init_declarator->declarator);

        // the name
        decl_cc.run(init_declarator->declarator);
        QString alias_name = decl_cc.id();

        if (alias_name.isEmpty()) {
            std::cerr << "** WARNING anonymous typedef not supported! ``";
            Token const &tk = _M_token_stream->token((int) node->start_token);
            Token const &end_tk = _M_token_stream->token((int) node->end_token);

            std::cerr << std::string(&tk.text[tk.position], end_tk.position - tk.position) << "''"
                      << std::endl << std::endl;
            continue;
        }

        // build the type
        TypeInfo typeInfo = CompilerUtils::typeDescription(node->type_specifier,
                                                           init_declarator->declarator,
                                                           this);
        DeclaratorAST *decl = init_declarator->declarator;
        while (decl && decl->sub_declarator)
            decl = decl->sub_declarator;

        if (decl != init_declarator->declarator
            && init_declarator->declarator->parameter_declaration_clause) {
            typeInfo.setFunctionPointer(true);
            decl_cc.run(init_declarator->declarator);
            foreach (const DeclaratorCompiler::Parameter &p, decl_cc.parameters())
                typeInfo.addArgument(p.type);
        }

        ScopeModelItem scope = currentScope();
        DeclaratorAST *declarator = init_declarator->declarator;
        CodeModelFinder finder(model(), this);
        ScopeModelItem typedefScope = finder.resolveScope(declarator->id, scope);

        TypeAliasModelItem typeAlias(new _TypeAliasModelItem(model()));
        updateItemPosition(typeAlias, node);
        typeAlias->setName(alias_name);
        typeAlias->setType(qualifyType(typeInfo, currentScope()->qualifiedName()));
        typeAlias->setScope(typedefScope->qualifiedName());
        _M_qualified_types[typeAlias->qualifiedName().join(QLatin1Char('.'))] = QString();
        currentScope()->addTypeAlias(typeAlias);
    } while (it != end);
}

void Binder::visitNamespace(NamespaceAST *node)
{
    bool anonymous = (node->namespace_name == 0);

    ScopeModelItem scope = currentScope();

    NamespaceModelItem old;
    if (!anonymous) {
        QString name = decode_symbol(node->namespace_name)->as_string();

        QStringList qualified_name = scope->qualifiedName();
        qualified_name += name;
        const CodeModelItem nsI = _M_model->findItem(qualified_name, _M_current_file);
        NamespaceModelItem ns = qSharedPointerDynamicCast<_NamespaceModelItem>(nsI);
        if (!ns) {
            ns.reset(new _NamespaceModelItem(_M_model));
            updateItemPosition(ns, node);
            ns->setName(name);
            ns->setScope(scope->qualifiedName());
        }
        old = changeCurrentNamespace(ns);

        _M_context.append(name);
    }

    DefaultVisitor::visitNamespace(node);

    if (!anonymous) {
        Q_ASSERT(scope->kind() == _CodeModelItem::Kind_Namespace
                 || scope->kind() == _CodeModelItem::Kind_File);

        _M_context.removeLast();

        if (const NamespaceModelItem ns = qSharedPointerDynamicCast<_NamespaceModelItem>(scope))
            ns->addNamespace(_M_current_namespace);

        changeCurrentNamespace(old);
    }
}

void Binder::visitForwardDeclarationSpecifier(ForwardDeclarationSpecifierAST *node)
{
    name_cc.run(node->name);
    if (name_cc.name().isEmpty())
        return;

    ScopeModelItem scope = currentScope();
    _M_qualified_types[(scope->qualifiedName() + name_cc.qualifiedName()).join(QLatin1Char('.'))] = QString();
}

void Binder::visitClassSpecifier(ClassSpecifierAST *node)
{
    ClassCompiler class_cc(this);
    class_cc.run(node);

    if (class_cc.name().isEmpty()) {
        // anonymous not supported
        return;
    }

    Q_ASSERT(node->name && node->name->unqualified_name);

    ScopeModelItem scope = currentScope();

    ClassModelItem old = changeCurrentClass(ClassModelItem(new _ClassModelItem(_M_model)));
    updateItemPosition(_M_current_class, node);
    _M_current_class->setName(class_cc.name());

    QStringList baseClasses = class_cc.baseClasses();
    TypeInfo info;
    for (int i = 0; i < baseClasses.size(); ++i) {
        info.setQualifiedName(baseClasses.at(i).split(QLatin1String("::")));
        baseClasses[i] = qualifyType(info, scope->qualifiedName()).qualifiedName().join(QLatin1String("::"));
    }

    _M_current_class->setBaseClasses(baseClasses);
    _M_current_class->setClassType(decode_class_type(node->class_key));
    _M_current_class->setTemplateParameters(_M_current_template_parameters);

    if (!_M_current_template_parameters.isEmpty()) {
        QString name = _M_current_class->name();
        name += QLatin1Char('<');
        for (int i = 0; i < _M_current_template_parameters.size(); ++i) {
            if (i > 0)
                name += QLatin1Char(',');

            name += _M_current_template_parameters.at(i)->name();
        }

        name += QLatin1Char('>');
        _M_current_class->setName(name);
    }

    CodeModel::AccessPolicy oldAccessPolicy = changeCurrentAccess(decode_access_policy(node->class_key));
    CodeModel::FunctionType oldFunctionType = changeCurrentFunctionType(CodeModel::Normal);

    _M_current_class->setScope(scope->qualifiedName());
    _M_qualified_types[_M_current_class->qualifiedName().join(QLatin1Char('.'))] = QString();

    scope->addClass(_M_current_class);

    name_cc.run(node->name->unqualified_name);
    _M_context.append(name_cc.name());
    visitNodes(this, node->member_specs);
    _M_context.removeLast();

    changeCurrentClass(old);
    changeCurrentAccess(oldAccessPolicy);
    changeCurrentFunctionType(oldFunctionType);
}

void Binder::visitLinkageSpecification(LinkageSpecificationAST *node)
{
    DefaultVisitor::visitLinkageSpecification(node);
}

void Binder::visitUsing(UsingAST *node)
{
    DefaultVisitor::visitUsing(node);
}

void Binder::visitEnumSpecifier(EnumSpecifierAST *node)
{
    CodeModelFinder finder(model(), this);
    ScopeModelItem scope = currentScope();
    ScopeModelItem enumScope = finder.resolveScope(node->name, scope);

    name_cc.run(node->name);
    QString name = name_cc.name();

    bool isAnonymous = name.isEmpty();
    if (isAnonymous) {
        // anonymous enum
        QString key = _M_context.join(QLatin1String("::"));
        int current = ++_M_anonymous_enums[key];
        name += QLatin1String("enum_");
        name += QString::number(current);
    }

    _M_current_enum.reset(new _EnumModelItem(model()));
    _M_current_enum->setAccessPolicy(_M_current_access);
    updateItemPosition(_M_current_enum, node);
    _M_current_enum->setName(name);
    _M_current_enum->setAnonymous(isAnonymous);
    _M_current_enum->setScope(enumScope->qualifiedName());

    _M_qualified_types[_M_current_enum->qualifiedName().join(QLatin1Char('.'))] = QString();

    enumScope->addEnum(_M_current_enum);

    DefaultVisitor::visitEnumSpecifier(node);

    _M_current_enum.clear();
}

static QString strip_preprocessor_lines(const QString &name)
{
    QStringList lst = name.split(QLatin1Char('\n'));
    QString s;
    for (int i = 0; i < lst.size(); ++i) {
        if (!lst.at(i).startsWith(QLatin1Char('#')))
            s += lst.at(i);
    }
    return s.trimmed();
}

void Binder::visitEnumerator(EnumeratorAST *node)
{
    Q_ASSERT(_M_current_enum);
    EnumeratorModelItem e(new _EnumeratorModelItem(model()));
    updateItemPosition(e, node);
    e->setName(decode_symbol(node->id)->as_string());

    if (ExpressionAST *expr = node->expression) {
        const Token &start_token = _M_token_stream->token((int) expr->start_token);
        const Token &end_token = _M_token_stream->token((int) expr->end_token);
        const QString token = QString::fromUtf8(&start_token.text[start_token.position],
                                                (int)(end_token.position - start_token.position));
        QString lines = strip_preprocessor_lines(token.trimmed());
        lines.remove(QLatin1Char(' '));
        e->setValue(lines);
    }

    _M_current_enum->addEnumerator(e);
}

void Binder::visitUsingDirective(UsingDirectiveAST *node)
{
    DefaultVisitor::visitUsingDirective(node);
}

void Binder::visitQEnums(QEnumsAST *node)
{
    const Token &start = _M_token_stream->token((int) node->start_token);
    const Token &end = _M_token_stream->token((int) node->end_token);
    QStringList enum_list = QString::fromLatin1(start.text + start.position,
                                                end.position - start.position).split(QLatin1Char(' '));

    ScopeModelItem scope = currentScope();
    for (int i = 0; i < enum_list.size(); ++i)
        scope->addEnumsDeclaration(enum_list.at(i));
}

void Binder::visitQProperty(QPropertyAST *node)
{
    const Token &start = _M_token_stream->token((int) node->start_token);
    const Token &end = _M_token_stream->token((int) node->end_token);
    QString property = QString::fromLatin1(start.text + start.position,
                                           end.position - start.position);
    _M_current_class->addPropertyDeclaration(property);
}

void Binder::applyStorageSpecifiers(const ListNode<std::size_t> *it, MemberModelItem item)
{
    if (!it)
        return;

    it = it->toFront();
    const ListNode<std::size_t> *end = it;

    do {
        switch (decode_token(it->element)) {
        default:
            break;

        case Token_friend:
            item->setFriend(true);
            break;
        case Token_auto:
            item->setAuto(true);
            break;
        case Token_register:
            item->setRegister(true);
            break;
        case Token_static:
            item->setStatic(true);
            break;
        case Token_extern:
            item->setExtern(true);
            break;
        case Token_mutable:
            item->setMutable(true);
            break;
        }
        it = it->next;
    } while (it != end);
}

void Binder::applyFunctionSpecifiers(const ListNode<std::size_t> *it, FunctionModelItem item)
{
    if (!it)
        return;

    it = it->toFront();
    const ListNode<std::size_t> *end = it;

    do {
        switch (decode_token(it->element)) {
        default:
            break;

        case Token_inline:
            item->setInline(true);
            break;

        case Token_virtual:
            item->setVirtual(true);
            break;

        case Token_explicit:
            item->setExplicit(true);
            break;

        case Token_Q_INVOKABLE:
            item->setInvokable(true);
            break;
        }
        it = it->next;
    } while (it != end);
}

TypeInfo Binder::qualifyType(const TypeInfo &type, const QStringList &context) const
{
    // ### Potentially improve to use string list in the name table to
    if (!context.size()) {
        // ### We can assume that this means global namespace for now...
        return type;
    } else if (_M_qualified_types.contains(type.qualifiedName().join(QLatin1Char('.')))) {
        return type;
    } else {
        QStringList expanded = context;
        expanded << type.qualifiedName();
        if (_M_qualified_types.contains(expanded.join(QLatin1Char('.')))) {
            TypeInfo modified_type = type;
            modified_type.setQualifiedName(expanded);
            return modified_type;
        } else {
            CodeModelItem scope = model()->findItem(context, _M_current_file);

            if (ClassModelItem klass = qSharedPointerDynamicCast<_ClassModelItem>(scope)) {
                foreach (const QString &base, klass->baseClasses()) {
                    QStringList ctx = context;
                    ctx.removeLast();
                    ctx.append(base);

                    TypeInfo qualified = qualifyType(type, ctx);
                    if (qualified != type)
                        return qualified;
                }
            }

            QStringList copy = context;
            copy.removeLast();
            return qualifyType(type, copy);
        }
    }
}

void Binder::updateItemPosition(CodeModelItem item, AST *node)
{
    QString filename;
    int line, column;

    assert(node);
    _M_location.positionAt(_M_token_stream->position(node->start_token), &line, &column, &filename);
    item->setFileName(filename);
}
