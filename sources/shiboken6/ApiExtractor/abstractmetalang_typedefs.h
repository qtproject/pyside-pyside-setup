// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETALANG_TYPEDEFS_H
#define ABSTRACTMETALANG_TYPEDEFS_H

#include <QtCore/QSharedPointer>
#include <QtCore/QList>

class AbstractMetaClass;
class AbstractMetaField;
class AbstractMetaArgument;
class AbstractMetaEnum;
class AbstractMetaEnumValue;
class AbstractMetaFunction;
class AbstractMetaType;
struct UsingMember;

using AbstractMetaFunctionPtr = QSharedPointer<AbstractMetaFunction>;
using AbstractMetaFunctionCPtr = QSharedPointer<const AbstractMetaFunction>;

using AbstractMetaArgumentList = QList<AbstractMetaArgument>;
using AbstractMetaClassList = QList<AbstractMetaClass *>;
using AbstractMetaClassCList = QList<const AbstractMetaClass *>;
using AbstractMetaEnumList = QList<AbstractMetaEnum>;
using AbstractMetaEnumValueList = QList<AbstractMetaEnumValue>;
using AbstractMetaFieldList = QList<AbstractMetaField>;
using AbstractMetaFunctionRawPtrList = QList<AbstractMetaFunction *>;
using AbstractMetaFunctionCList = QList<AbstractMetaFunctionCPtr>;
using AbstractMetaTypeList = QList<AbstractMetaType>;
using UsingMembers = QList<UsingMember>;

#endif // ABSTRACTMETALANG_TYPEDEFS_H
