// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPESYSTEM_TYPEDEFS_H
#define TYPESYSTEM_TYPEDEFS_H

#include <QtCore/QList>

#include <memory>

class ArrayTypeEntry;
class ComplexTypeEntry;
class ConfigurableTypeEntry;
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

using ArrayTypeEntryPtr = std::shared_ptr<ArrayTypeEntry>;
using ComplexTypeEntryPtr = std::shared_ptr<ComplexTypeEntry>;
using ConfigurableTypeEntryPtr = std::shared_ptr<ConfigurableTypeEntry>;
using ConstantValueTypeEntryPtr = std::shared_ptr<ConstantValueTypeEntry>;
using ContainerTypeEntryPtr = std::shared_ptr<ContainerTypeEntry>;
using CustomTypeEntryPtr = std::shared_ptr<CustomTypeEntry>;
using EnumTypeEntryPtr = std::shared_ptr<EnumTypeEntry>;
using EnumValueTypeEntryPtr = std::shared_ptr<EnumValueTypeEntry>;
using FlagsTypeEntryPtr = std::shared_ptr<FlagsTypeEntry>;
using FunctionTypeEntryPtr = std::shared_ptr<FunctionTypeEntry>;
using NamespaceTypeEntryPtr = std::shared_ptr<NamespaceTypeEntry>;
using ObjectTypeEntryPtr = std::shared_ptr<ObjectTypeEntry>;
using PrimitiveTypeEntryPtr = std::shared_ptr<PrimitiveTypeEntry>;
using SmartPointerTypeEntryPtr = std::shared_ptr<SmartPointerTypeEntry>;
using TemplateEntryPtr = std::shared_ptr<TemplateEntry>;
using TypeEntryPtr = std::shared_ptr<TypeEntry>;
using TypedefEntryPtr = std::shared_ptr<TypedefEntry>;
using TypeSystemTypeEntryPtr = std::shared_ptr<TypeSystemTypeEntry>;
using ValueTypeEntryPtr = std::shared_ptr<ValueTypeEntry>;

using ArrayTypeEntryCPtr = std::shared_ptr<const ArrayTypeEntry>;
using ComplexTypeEntryCPtr = std::shared_ptr<const ComplexTypeEntry>;
using ConstantValueTypeEntryCPtr = std::shared_ptr<const ConstantValueTypeEntry>;
using ConfigurableTypeEntryCPtr = std::shared_ptr<const ConfigurableTypeEntry>;
using ContainerTypeEntryCPtr = std::shared_ptr<const ContainerTypeEntry>;
using CustomTypeEntryCPtr = std::shared_ptr<const CustomTypeEntry>;
using EnumTypeEntryCPtr = std::shared_ptr<const EnumTypeEntry>;
using EnumValueTypeEntryCPtr = std::shared_ptr<const EnumValueTypeEntry>;
using FlagsTypeEntryCPtr = std::shared_ptr<const FlagsTypeEntry>;
using FunctionTypeEntryCPtr = std::shared_ptr<const FunctionTypeEntry>;
using NamespaceTypeEntryCPtr = std::shared_ptr<const NamespaceTypeEntry>;
using ObjectTypeEntryCPtr = std::shared_ptr<const ObjectTypeEntry>;
using PrimitiveTypeEntryCPtr = std::shared_ptr<const PrimitiveTypeEntry>;
using SmartPointerTypeEntryCPtr = std::shared_ptr<const SmartPointerTypeEntry>;
using TemplateEntryCPtr = std::shared_ptr<const TemplateEntry>;
using TypeEntryCPtr = std::shared_ptr<const TypeEntry>;
using TypedefEntryCPtr = std::shared_ptr<const TypedefEntry>;
using TypeSystemTypeEntryCPtr = std::shared_ptr<const TypeSystemTypeEntry>;
using ValueTypeEntryCPtr = std::shared_ptr<const ValueTypeEntry>;

using ContainerTypeEntryCList = QList<ContainerTypeEntryCPtr>;
using NamespaceTypeEntryList = QList<NamespaceTypeEntryPtr>;
using PrimitiveTypeEntryCList = QList<PrimitiveTypeEntryCPtr>;
using SmartPointerTypeEntryList = QList<SmartPointerTypeEntryCPtr>;
using TypeEntryList = QList<TypeEntryPtr>;
using TypeEntryCList = QList<TypeEntryCPtr>;

#endif // TYPESYSTEM_TYPEDEFS_H
