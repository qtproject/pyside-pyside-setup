// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
#ifndef XMLUTILS_H
#define XMLUTILS_H

#include <QtCore/QString>

#include <memory>

class XQuery
{
public:
    Q_DISABLE_COPY(XQuery);

    virtual ~XQuery();

    QString evaluate(QString xPathExpression, QString *errorMessage);

    static std::shared_ptr<XQuery> create(const QString &focus, QString *errorMessage);

protected:
    XQuery();

    virtual QString doEvaluate(const QString &xPathExpression, QString *errorMessage) = 0;
};

QString xsl_transform(const QString &xml, const QString &xsl, QString *errorMessage);

#endif // XMLUTILS_H
