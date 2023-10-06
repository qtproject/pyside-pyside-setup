// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef HIDDENOBJECT_H
#define HIDDENOBJECT_H

#include "pysidetest_macros.h"

#include <QtCore/QObject>

// This class shouldn't be exported!
class HiddenObject : public QObject
{
    Q_OBJECT
public:
    HiddenObject() noexcept = default;
    Q_INVOKABLE void callMe();
public Q_SLOTS:
    bool wasCalled() const;
private:
    bool m_called = false;
};

// Return a instance of HiddenObject
PYSIDETEST_API QObject* getHiddenObject();

#endif
