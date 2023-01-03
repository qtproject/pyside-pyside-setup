// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETALANG_TYPEDEFS_H
#define ABSTRACTMETALANG_TYPEDEFS_H

#include <QtCore/QList>

#include <memory>

class AbstractMetaClass;
class AbstractMetaField;
class AbstractMetaArgument;
class AbstractMetaEnum;
class AbstractMetaEnumValue;
class AbstractMetaFunction;
class AbstractMetaType;
struct UsingMember;

using AbstractMetaFunctionPtr = std::shared_ptr<AbstractMetaFunction>;
using AbstractMetaFunctionCPtr = std::shared_ptr<const AbstractMetaFunction>;
using AbstractMetaClassPtr = std::shared_ptr<AbstractMetaClass>;
using AbstractMetaClassCPtr = std::shared_ptr<const AbstractMetaClass>;

using AbstractMetaArgumentList = QList<AbstractMetaArgument>;
using AbstractMetaClassList = QList<AbstractMetaClassPtr>;
using AbstractMetaClassCList = QList<AbstractMetaClassCPtr>;
using AbstractMetaEnumList = QList<AbstractMetaEnum>;
using AbstractMetaEnumValueList = QList<AbstractMetaEnumValue>;
using AbstractMetaFieldList = QList<AbstractMetaField>;
using AbstractMetaFunctionRawPtrList = QList<AbstractMetaFunction *>;
using AbstractMetaFunctionCList = QList<AbstractMetaFunctionCPtr>;
using AbstractMetaTypeList = QList<AbstractMetaType>;
using UsingMembers = QList<UsingMember>;

#endif // ABSTRACTMETALANG_TYPEDEFS_H
