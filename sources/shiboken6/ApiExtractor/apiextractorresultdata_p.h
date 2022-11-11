// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef APIEXTRACTORRESULTDATA_P_H
#define APIEXTRACTORRESULTDATA_P_H

#include "apiextractorresult.h"

#include <QtCore/QHash>
#include <QtCore/QSharedData>

class ApiExtractorResultData : public QSharedData
{
public:
    ApiExtractorResultData();
    ~ApiExtractorResultData();

    AbstractMetaClassCList m_metaClasses;
    AbstractMetaClassCList m_templates; // not exposed, just for ownership
    AbstractMetaClassCList m_smartPointers;
    AbstractMetaFunctionCList m_globalFunctions;
    AbstractMetaEnumList m_globalEnums;
    AbstractMetaTypeList m_instantiatedContainers;
    InstantiatedSmartPointers m_instantiatedSmartPointers;
    QHash<TypeEntryCPtr, AbstractMetaEnum> m_enums;
    ApiExtractorFlags m_flags;
};

#endif // APIEXTRACTORRESULTDATA_P_H
