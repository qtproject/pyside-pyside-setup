// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QPYQMLPARSERSTATUS_H
#define QPYQMLPARSERSTATUS_H

#include <QtCore/QObject>
#include <QtQml/QQmlParserStatus>

#ifdef Q_MOC_RUN
Q_DECLARE_INTERFACE(QQmlParserStatus, "org.qt-project.Qt.QQmlParserStatus")
#endif

// Inherit from QObject such that QQmlParserStatus can be found at
// a fixed offset (RegisterType::parserStatusCast).
class QPyQmlParserStatus : public QObject, public QQmlParserStatus
{
    Q_OBJECT
    Q_INTERFACES(QQmlParserStatus)
public:
    explicit QPyQmlParserStatus(QObject *parent = nullptr) : QObject(parent) {}
};

#endif // QPYQMLPARSERSTATUS_H
