// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "apiextractorresult.h"
#include "abstractmetalang.h"
#include "abstractmetaenum.h"

#include "enumtypeentry.h"
#include "flagstypeentry.h"

ApiExtractorResult::ApiExtractorResult() = default;

ApiExtractorResult::ApiExtractorResult(const ApiExtractorResult &) = default;

ApiExtractorResult &ApiExtractorResult::operator=(const ApiExtractorResult &) = default;

ApiExtractorResult::ApiExtractorResult(ApiExtractorResult &&) = default;

ApiExtractorResult &ApiExtractorResult::operator=(ApiExtractorResult &&) = default;

ApiExtractorResult::~ApiExtractorResult() = default;

const AbstractMetaEnumList &ApiExtractorResult::globalEnums() const
{
    return m_globalEnums;
}

const AbstractMetaFunctionCList &ApiExtractorResult::globalFunctions() const
{
    return m_globalFunctions;
}

const AbstractMetaClassCList &ApiExtractorResult::classes() const
{
    return m_metaClasses;
}

const AbstractMetaClassCList &ApiExtractorResult::smartPointers() const
{
    return m_smartPointers;
}

const AbstractMetaTypeList &ApiExtractorResult::instantiatedContainers() const
{
    return m_instantiatedContainers;
}

const InstantiatedSmartPointers &ApiExtractorResult::instantiatedSmartPointers() const
{
    return m_instantiatedSmartPointers;
}

ApiExtractorFlags ApiExtractorResult::flags() const
{
    return m_flags;
}

void ApiExtractorResult::setFlags(ApiExtractorFlags f)
{
    m_flags = f;
}

std::optional<AbstractMetaEnum>
    ApiExtractorResult::findAbstractMetaEnum(TypeEntryCPtr typeEntry) const
{
    if (typeEntry && typeEntry->isFlags())
        typeEntry = std::static_pointer_cast<const FlagsTypeEntry>(typeEntry)->originator();
    const auto it = m_enums.constFind(typeEntry);
    if (it == m_enums.constEnd())
        return {};
    return it.value();
}

AbstractMetaFunctionCList ApiExtractorResult::implicitConversions(const TypeEntryCPtr &type) const
{
    if (type->isValue()) {
        if (auto metaClass = AbstractMetaClass::findClass(m_metaClasses, type))
            return metaClass->implicitConversions();
    }
    return {};
}

AbstractMetaFunctionCList ApiExtractorResult::implicitConversions(const AbstractMetaType &metaType) const
{
    return implicitConversions(metaType.typeEntry());
}
