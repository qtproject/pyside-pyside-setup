// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DEPENDENCY_H
#define DEPENDENCY_H

#include <QtCore/QList>

#include <utility>

// Dependencies for topologically sorting classes

class AbstractMetaClass;

struct Dependency {
    AbstractMetaClassPtr parent;
    AbstractMetaClassPtr child;
};

using Dependencies = QList<Dependency>;

#endif // DEPENDENCY_H
