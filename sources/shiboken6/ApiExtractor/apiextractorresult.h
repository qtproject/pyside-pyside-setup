// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef APIEXTRACTORRESULT_H
#define APIEXTRACTORRESULT_H

#include "apiextractorflags.h"
#include "abstractmetatype.h"
#include "abstractmetalang_typedefs.h"
#include "typesystem_typedefs.h"

#include <QtCore/QHash>

#include <optional>

class ApiExtractorResultData;

struct InstantiatedSmartPointer
{
    AbstractMetaClassCPtr smartPointer; // Template class
    AbstractMetaClassCPtr specialized; // Specialized for type
    AbstractMetaType type;
};

using InstantiatedSmartPointers = QList<InstantiatedSmartPointer>;

/// Result of an ApiExtractor run.
class ApiExtractorResult
{
public:
    ApiExtractorResult();
    ApiExtractorResult(const ApiExtractorResult &);
    ApiExtractorResult &operator=(const ApiExtractorResult &);
    ApiExtractorResult(ApiExtractorResult &&);
    ApiExtractorResult &operator=(ApiExtractorResult &&);
    ~ApiExtractorResult();

    const AbstractMetaEnumList &globalEnums() const;
    const AbstractMetaFunctionCList &globalFunctions() const;
    const AbstractMetaClassCList &classes() const;
    const AbstractMetaClassCList &smartPointers() const;

    const AbstractMetaTypeList &instantiatedContainers() const;
    const InstantiatedSmartPointers &instantiatedSmartPointers() const;

    // Query functions for the generators
    std::optional<AbstractMetaEnum>
        findAbstractMetaEnum(TypeEntryCPtr typeEntry) const;

    /// Retrieves a list of constructors used in implicit conversions
    /// available on the given type. The TypeEntry must be a value-type
    /// or else it will return an empty list.
    ///  \param type a TypeEntry that is expected to be a value-type
    /// \return a list of constructors that could be used as implicit converters
    AbstractMetaFunctionCList implicitConversions(const TypeEntryCPtr &type) const;
    AbstractMetaFunctionCList implicitConversions(const AbstractMetaType &metaType) const;

    ApiExtractorFlags flags() const;
    void setFlags(ApiExtractorFlags f);

private:
    AbstractMetaClassCList m_metaClasses;
    AbstractMetaClassCList m_smartPointers;
    AbstractMetaFunctionCList m_globalFunctions;
    AbstractMetaEnumList m_globalEnums;
    AbstractMetaTypeList m_instantiatedContainers;
    InstantiatedSmartPointers m_instantiatedSmartPointers;
    QHash<TypeEntryCPtr, AbstractMetaEnum> m_enums;
    ApiExtractorFlags m_flags;

    friend class ApiExtractor;
};

#endif // APIEXTRACTORRESULT_H
