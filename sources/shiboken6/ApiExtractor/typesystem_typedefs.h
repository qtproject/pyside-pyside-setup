// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPESYSTEM_TYPEDEFS_H
#define TYPESYSTEM_TYPEDEFS_H

#include <QtCore/QHash>
#include <QtCore/QList>
#include <QtCore/QSharedPointer>
#include <QtCore/QList>

class CodeSnip;
class DocModification;

struct AddedFunction;
class CustomConversion;
class FieldModification;
class FunctionModification;
class TypeEntry;

using AddedFunctionPtr = QSharedPointer<AddedFunction>;
using AddedFunctionList = QList<AddedFunctionPtr>;
using CodeSnipList = QList<CodeSnip>;
using CustomConversionPtr = QSharedPointer<CustomConversion>;
using DocModificationList = QList<DocModification>;
using FieldModificationList = QList<FieldModification>;
using FunctionModificationList = QList<FunctionModification>;
using TypeEntries = QList<const TypeEntry *>;
#endif // TYPESYSTEM_TYPEDEFS_H
