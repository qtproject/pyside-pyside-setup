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
#ifndef XMLUTILS_QT_H
#define XMLUTILS_QT_H

#include <QtCore/QString>
#include <QtCore/QSharedPointer>

class XQuery;

QSharedPointer<XQuery> qt_createXQuery(const QString &focus, QString *errorMessage);

QString qt_xsl_transform(const QString &xml, QString xsl, QString *errorMessage);

#endif // XMLUTILS_QT_H
