// Copyright (C) 2016 The Qt Company Ltd.
// Copyright (C) 2002-2005 Roberto Raggi <roberto@kdevelop.org>
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


#ifndef CODEMODEL_FWD_H
#define CODEMODEL_FWD_H

#include <QtCore/QList>

#include <memory>

// forward declarations
class CodeModel;
class _ArgumentModelItem;
class _ClassModelItem;
class _CodeModelItem;
class _EnumModelItem;
class _EnumeratorModelItem;
class _FileModelItem;
class _FunctionModelItem;
class _NamespaceModelItem;
class _ScopeModelItem;
class _TemplateParameterModelItem;
class _TypeDefModelItem;
class _TemplateTypeAliasModelItem;
class _VariableModelItem;
class _MemberModelItem;
class TypeInfo;

using ArgumentModelItem = std::shared_ptr<_ArgumentModelItem>;
using ClassModelItem = std::shared_ptr<_ClassModelItem>;
using CodeModelItem = std::shared_ptr<_CodeModelItem>;
using EnumModelItem = std::shared_ptr<_EnumModelItem>;
using EnumeratorModelItem = std::shared_ptr<_EnumeratorModelItem>;
using FileModelItem = std::shared_ptr<_FileModelItem>;
using FunctionModelItem = std::shared_ptr<_FunctionModelItem>;
using NamespaceModelItem = std::shared_ptr<_NamespaceModelItem>;
using ScopeModelItem = std::shared_ptr<_ScopeModelItem>;
using TemplateParameterModelItem = std::shared_ptr<_TemplateParameterModelItem>;
using TypeDefModelItem = std::shared_ptr<_TypeDefModelItem>;
using TemplateTypeAliasModelItem = std::shared_ptr<_TemplateTypeAliasModelItem>;
using VariableModelItem = std::shared_ptr<_VariableModelItem>;
using MemberModelItem = std::shared_ptr<_MemberModelItem>;

using ArgumentList = QList<ArgumentModelItem>;
using ClassList = QList<ClassModelItem>;
using ItemList = QList<CodeModelItem>;
using EnumList = QList<EnumModelItem>;
using EnumeratorList = QList<EnumeratorModelItem>;
using FileList = QList<FileModelItem>;
using FunctionList = QList<FunctionModelItem>;
using NamespaceList = QList<NamespaceModelItem>;
using ScopeList = QList<ScopeModelItem>;
using TemplateParameterList = QList<TemplateParameterModelItem>;
using TypeDefList = QList<TypeDefModelItem>;
using TemplateTypeAliasList = QList<TemplateTypeAliasModelItem>;
using VariableList = QList<VariableModelItem>;
using MemberList = QList<MemberModelItem>;

#endif // CODEMODEL_FWD_H
