// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef APIEXTRACTORRESULT_H
#define APIEXTRACTORRESULT_H

#include "abstractmetalang.h"
#include "apiextractorflags.h"
#include "abstractmetaenum.h"
#include "abstractmetatype.h"
#include "typesystem_typedefs.h"

#include <QtCore/QHash>
#include <QtCore/QExplicitlySharedDataPointer>

#include <optional>

class ApiExtractorResultData;

struct InstantiatedSmartPointer
{
    const AbstractMetaClass *smartPointer = nullptr; // Template class
    const AbstractMetaClass *specialized = nullptr; // Specialized for type
    AbstractMetaType type;
};

using InstantiatedSmartPointers = QList<InstantiatedSmartPointer>;

/// Result of an ApiExtractor run.
class ApiExtractorResult
{
public:
    ApiExtractorResult();
    explicit ApiExtractorResult(ApiExtractorResultData *data);
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
    std::optional<AbstractMetaEnum> findAbstractMetaEnum(const TypeEntry* typeEntry) const;

    /// Retrieves a list of constructors used in implicit conversions
    /// available on the given type. The TypeEntry must be a value-type
    /// or else it will return an empty list.
    ///  \param type a TypeEntry that is expected to be a value-type
    /// \return a list of constructors that could be used as implicit converters
    AbstractMetaFunctionCList implicitConversions(const TypeEntry *type) const;
    AbstractMetaFunctionCList implicitConversions(const AbstractMetaType &metaType) const;

    ApiExtractorFlags flags() const;
    void setFlags(ApiExtractorFlags f);

private:
    QExplicitlySharedDataPointer<ApiExtractorResultData> d;
};

#endif // APIEXTRACTORRESULT_H
