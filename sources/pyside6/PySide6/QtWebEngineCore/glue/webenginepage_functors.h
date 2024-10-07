// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef WEBENGINEPAGE_FUNCTORS_H
#define WEBENGINEPAGE_FUNCTORS_H

#include "pyobjectholder.h"

#include <QtCore/QtClassHelperMacros>

QT_FORWARD_DECLARE_CLASS(QByteArray)
QT_FORWARD_DECLARE_CLASS(QVariant)

QT_BEGIN_NAMESPACE

struct RunJavascriptFunctor : public Shiboken::PyObjectHolder
{
    using Shiboken::PyObjectHolder::PyObjectHolder;

    void operator()(const QVariant &result);
};

struct PrintToPdfFunctor : public Shiboken::PyObjectHolder
{
    using Shiboken::PyObjectHolder::PyObjectHolder;

    void operator()(const QByteArray &pdf);
};

QT_END_NAMESPACE

#endif // WEBENGINEPAGE_FUNCTORS_H
