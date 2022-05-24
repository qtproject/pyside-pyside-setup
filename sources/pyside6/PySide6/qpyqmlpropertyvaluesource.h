// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QPYQMLPROPERTYVALUESOURCE_H
#define QPYQMLPROPERTYVALUESOURCE_H

#include <QtQml/QQmlPropertyValueSource>

#ifdef Q_MOC_RUN
Q_DECLARE_INTERFACE(QQmlPropertyValueSource, "org.qt-project.Qt.QQmlPropertyValueSource")
#endif

// Inherit from QObject such that QQmlPropertyValueSource can be found at
// a fixed offset (RegisterType::valueSourceCast).
class QPyQmlPropertyValueSource : public QObject, public QQmlPropertyValueSource
{
    Q_OBJECT
    Q_INTERFACES(QQmlPropertyValueSource)
public:
    explicit QPyQmlPropertyValueSource(QObject *parent = nullptr) : QObject(parent) {}
};

#endif // QPYQMLPROPERTYVALUESOURCE_H
