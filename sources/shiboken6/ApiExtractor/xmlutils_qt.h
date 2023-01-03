// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
#ifndef XMLUTILS_QT_H
#define XMLUTILS_QT_H

#include <QtCore/QString>

#include <memory>

class XQuery;

std::shared_ptr<XQuery> qt_createXQuery(const QString &focus, QString *errorMessage);

QString qt_xsl_transform(const QString &xml, QString xsl, QString *errorMessage);

#endif // XMLUTILS_QT_H
