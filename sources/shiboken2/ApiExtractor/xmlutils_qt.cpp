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

#include "xmlutils.h"
#include "xmlutils_qt.h"

#include <QtXmlPatterns/QXmlQuery>

#include <QtCore/QDir>
#include <QtCore/QUrl>

class QtXQuery : public XQuery
{
public:
    QtXQuery() = default;

    bool setFocus(const QString &fileName)
    { return m_xquery.setFocus(QUrl::fromLocalFile(fileName)); }

protected:
    QString doEvaluate(const QString &xPathExpression, QString *errorMessage) override;

private:
    QXmlQuery m_xquery;
};

QString QtXQuery::doEvaluate(const QString &xPathExpression, QString *errorMessage)
{
     m_xquery.setQuery(xPathExpression);
    if (!m_xquery.isValid()) {
        *errorMessage = QLatin1String("QXmlQuery: Bad query: \"") + xPathExpression
                        + QLatin1Char('"');
        return QString();
    }

    QString result;
    m_xquery.evaluateTo(&result);
    return result;
}

QSharedPointer<XQuery> qt_createXQuery(const QString &focus, QString *errorMessage)
{
    QSharedPointer<QtXQuery> result(new QtXQuery);
    if (!result->setFocus(focus)) {
        *errorMessage = QLatin1String("QXmlQuery: Cannot set focus to ") + QDir::toNativeSeparators(focus);
        result.reset();
    }
    return std::move(result);
}

// XSLT transformation

static const char xsltPrefix[] = R"(<?xml version="1.0" encoding="UTF-8"?>
    <xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
)";

QString qt_xsl_transform(const QString &xml, QString xsl, QString *errorMessage)
{
    QXmlQuery query(QXmlQuery::XSLT20);
    if (!xsl.startsWith(QLatin1String("<?xml"))) {
        xsl.prepend(QLatin1String(xsltPrefix));
        xsl.append(QLatin1String("</xsl:stylesheet>"));
    }
    query.setFocus(xml);
    query.setQuery(xsl);
    if (!query.isValid()) {
        *errorMessage = QLatin1String("QXmlQuery: Invalid query \"") + xsl
                        + QLatin1String("\".");
        return xml;
    }
    QString result;
    if (!query.evaluateTo(&result)) {
        *errorMessage = QLatin1String("QXmlQuery: evaluate() failed.");
        return xml;
    }
    return result.trimmed();
}
