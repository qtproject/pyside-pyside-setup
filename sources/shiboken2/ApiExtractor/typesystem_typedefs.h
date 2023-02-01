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

#ifndef TYPESYSTEM_TYPEDEFS_H
#define TYPESYSTEM_TYPEDEFS_H

#include <QtCore/QHash>
#include <QtCore/QList>
#include <QtCore/QSharedPointer>
#include <QtCore/QVector>

class CodeSnip;
class DocModification;

struct AddedFunction;
struct FieldModification;
struct FunctionModification;
class TypeEntry;

using AddedFunctionPtr = QSharedPointer<AddedFunction>;
using AddedFunctionList = QVector<AddedFunctionPtr>;
using CodeSnipList = QVector<CodeSnip>;
using DocModificationList = QVector<DocModification>;
using FieldModificationList = QVector<FieldModification>;
using FunctionModificationList = QVector<FunctionModification>;
using TypeEntries = QVector<const TypeEntry *>;

#endif // TYPESYSTEM_TYPEDEFS_H
