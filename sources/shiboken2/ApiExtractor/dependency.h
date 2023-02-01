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

#ifndef DEPENDENCY_H
#define DEPENDENCY_H

#include <QtCore/QVector>

#include <utility>

// Dependencies for topologically sorting classes

class AbstractMetaClass;

struct Dependency {
    AbstractMetaClass *parent;
    AbstractMetaClass *child;
};

using Dependencies = QVector<Dependency>;

#endif // DEPENDENCY_H
