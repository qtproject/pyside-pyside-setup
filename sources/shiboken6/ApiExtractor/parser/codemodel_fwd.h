// Copyright (C) 2016 The Qt Company Ltd.
// Copyright (C) 2002-2005 Roberto Raggi <roberto@kdevelop.org>
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


#ifndef CODEMODEL_FWD_H
#define CODEMODEL_FWD_H

#include <QtCore/QList>
#include <QtCore/QSharedPointer>

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

using ArgumentModelItem = QSharedPointer<_ArgumentModelItem>;
using ClassModelItem = QSharedPointer<_ClassModelItem>;
using CodeModelItem = QSharedPointer<_CodeModelItem>;
using EnumModelItem = QSharedPointer<_EnumModelItem>;
using EnumeratorModelItem = QSharedPointer<_EnumeratorModelItem>;
using FileModelItem = QSharedPointer<_FileModelItem>;
using FunctionModelItem = QSharedPointer<_FunctionModelItem>;
using NamespaceModelItem = QSharedPointer<_NamespaceModelItem>;
using ScopeModelItem = QSharedPointer<_ScopeModelItem>;
using TemplateParameterModelItem = QSharedPointer<_TemplateParameterModelItem>;
using TypeDefModelItem = QSharedPointer<_TypeDefModelItem>;
using TemplateTypeAliasModelItem = QSharedPointer<_TemplateTypeAliasModelItem>;
using VariableModelItem = QSharedPointer<_VariableModelItem>;
using MemberModelItem = QSharedPointer<_MemberModelItem>;

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
