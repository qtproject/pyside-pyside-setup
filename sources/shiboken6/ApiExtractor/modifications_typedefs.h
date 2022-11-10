// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef MODIFICATIONS_TYPEDEFS_H
#define MODIFICATIONS_TYPEDEFS_H

#include <QtCore/QList>
#include <QtCore/QSharedPointer>

class CodeSnip;
class DocModification;

struct AddedFunction;
class FieldModification;
class FunctionModification;

using AddedFunctionPtr = QSharedPointer<AddedFunction>;
using AddedFunctionList = QList<AddedFunctionPtr>;
using CodeSnipList = QList<CodeSnip>;
using DocModificationList = QList<DocModification>;
using FieldModificationList = QList<FieldModification>;
using FunctionModificationList = QList<FunctionModification>;

#endif // MODIFICATIONS_TYPEDEFS_H
