/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef ABSTRACTMETALANG_TYPEDEFS_H
#define ABSTRACTMETALANG_TYPEDEFS_H

#include <QtCore/QSharedPointer>
#include <QtCore/QVector>

class AbstractMetaClass;
class AbstractMetaField;
class AbstractMetaArgument;
class AbstractMetaEnum;
class AbstractMetaEnumValue;
class AbstractMetaFunction;
class AbstractMetaType;

using AbstractMetaArgumentList = QVector<AbstractMetaArgument *>;
using AbstractMetaClassList = QVector<AbstractMetaClass *>;
using AbstractMetaEnumList = QVector<AbstractMetaEnum *>;
using AbstractMetaEnumValueList = QVector<AbstractMetaEnumValue *>;
using AbstractMetaFieldList = QVector<AbstractMetaField *>;
using AbstractMetaFunctionList = QVector<AbstractMetaFunction *>;
using AbstractMetaTypeCPtr = QSharedPointer<const AbstractMetaType>;
using AbstractMetaTypeList = QVector<AbstractMetaType *>;
using AbstractMetaTypeCList = QVector<const AbstractMetaType *>;

#endif // ABSTRACTMETALANG_TYPEDEFS_H
