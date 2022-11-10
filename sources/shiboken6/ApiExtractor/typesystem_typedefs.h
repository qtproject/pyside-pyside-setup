// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPESYSTEM_TYPEDEFS_H
#define TYPESYSTEM_TYPEDEFS_H

#include <QtCore/QList>

class ComplexTypeEntry;
class ConstantValueTypeEntry;
class ContainerTypeEntry;
class FlagsTypeEntry;
class FunctionTypeEntry;
class NamespaceTypeEntry;
class ObjectTypeEntry;
class PrimitiveTypeEntry;
class SmartPointerTypeEntry;
class TemplateEntry;
class TypeEntry;
class TypedefEntry;
class TypeSystemTypeEntry;

using ContainerTypeEntryCList = QList<const ContainerTypeEntry *>;
using NamespaceTypeEntryList = QList<NamespaceTypeEntry *>;
using PrimitiveTypeEntryCList = QList<const PrimitiveTypeEntry *>;
using SmartPointerTypeEntryList = QList<const SmartPointerTypeEntry *>;
using TypeEntryList = QList<TypeEntry *>;
using TypeEntryCList = QList<const TypeEntry *>;

#endif // TYPESYSTEM_TYPEDEFS_H
