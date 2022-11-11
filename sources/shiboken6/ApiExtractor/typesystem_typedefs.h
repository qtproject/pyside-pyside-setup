// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPESYSTEM_TYPEDEFS_H
#define TYPESYSTEM_TYPEDEFS_H

#include <QtCore/QList>
#include <QtCore/QSharedPointer>

class ArrayTypeEntry;
class ComplexTypeEntry;
class ConstantValueTypeEntry;
class ContainerTypeEntry;
class CustomTypeEntry;
class EnumTypeEntry;
class EnumValueTypeEntry;
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
class ValueTypeEntry;

using ArrayTypeEntryPtr = QSharedPointer<ArrayTypeEntry>;
using ComplexTypeEntryPtr = QSharedPointer<ComplexTypeEntry>;
using ConstantValueTypeEntryPtr = QSharedPointer<ConstantValueTypeEntry>;
using ContainerTypeEntryPtr = QSharedPointer<ContainerTypeEntry>;
using CustomTypeEntryPtr = QSharedPointer<CustomTypeEntry>;
using EnumTypeEntryPtr = QSharedPointer<EnumTypeEntry>;
using EnumValueTypeEntryPtr = QSharedPointer<EnumValueTypeEntry>;
using FlagsTypeEntryPtr = QSharedPointer<FlagsTypeEntry>;
using FunctionTypeEntryPtr = QSharedPointer<FunctionTypeEntry>;
using NamespaceTypeEntryPtr = QSharedPointer<NamespaceTypeEntry>;
using ObjectTypeEntryPtr = QSharedPointer<ObjectTypeEntry>;
using PrimitiveTypeEntryPtr = QSharedPointer<PrimitiveTypeEntry>;
using SmartPointerTypeEntryPtr = QSharedPointer<SmartPointerTypeEntry>;
using TemplateEntryPtr = QSharedPointer<TemplateEntry>;
using TypeEntryPtr = QSharedPointer<TypeEntry>;
using TypedefEntryPtr = QSharedPointer<TypedefEntry>;
using TypeSystemTypeEntryPtr = QSharedPointer<TypeSystemTypeEntry>;
using ValueTypeEntryPtr = QSharedPointer<ValueTypeEntry>;

using ArrayTypeEntryCPtr = QSharedPointer<const ArrayTypeEntry>;
using ComplexTypeEntryCPtr = QSharedPointer<const ComplexTypeEntry>;
using ConstantValueTypeEntryCPtr = QSharedPointer<const ConstantValueTypeEntry>;
using ContainerTypeEntryCPtr = QSharedPointer<const ContainerTypeEntry>;
using CustomTypeEntryCPtr = QSharedPointer<const CustomTypeEntry>;
using EnumTypeEntryCPtr = QSharedPointer<const EnumTypeEntry>;
using EnumValueTypeEntryCPtr = QSharedPointer<const EnumValueTypeEntry>;
using FlagsTypeEntryCPtr = QSharedPointer<const FlagsTypeEntry>;
using FunctionTypeEntryCPtr = QSharedPointer<const FunctionTypeEntry>;
using NamespaceTypeEntryCPtr = QSharedPointer<const NamespaceTypeEntry>;
using ObjectTypeEntryCPtr = QSharedPointer<const ObjectTypeEntry>;
using PrimitiveTypeEntryCPtr = QSharedPointer<const PrimitiveTypeEntry>;
using SmartPointerTypeEntryCPtr = QSharedPointer<const SmartPointerTypeEntry>;
using TemplateEntryCPtr = QSharedPointer<const TemplateEntry>;
using TypeEntryCPtr = QSharedPointer<const TypeEntry>;
using TypedefEntryCPtr = QSharedPointer<const TypedefEntry>;
using TypeSystemTypeEntryCPtr = QSharedPointer<const TypeSystemTypeEntry>;
using ValueTypeEntryCPtr = QSharedPointer<const ValueTypeEntry>;

using ContainerTypeEntryCList = QList<ContainerTypeEntryCPtr>;
using NamespaceTypeEntryList = QList<NamespaceTypeEntryPtr>;
using PrimitiveTypeEntryCList = QList<PrimitiveTypeEntryCPtr>;
using SmartPointerTypeEntryList = QList<SmartPointerTypeEntryCPtr>;
using TypeEntryList = QList<TypeEntryPtr>;
using TypeEntryCList = QList<TypeEntryCPtr>;

#endif // TYPESYSTEM_TYPEDEFS_H
