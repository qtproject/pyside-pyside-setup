// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
#ifndef XMLUTILS_LIBXSLT_H
#define XMLUTILS_LIBXSLT_H

#include <QtCore/QString>

#include <memory>

class XQuery;

std::shared_ptr<XQuery> libXml_createXQuery(const QString &focus, QString *errorMessage);

QString libXslt_transform(const QString &xml, QString xsl, QString *errorMessage);

#endif // XMLUTILS_LIBXSLT_H
