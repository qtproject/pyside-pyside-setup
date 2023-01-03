// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "xmlutils.h"

#include "xmlutils_libxslt.h"

#include "qtcompat.h"

using namespace Qt::StringLiterals;

XQuery::XQuery() = default;

XQuery::~XQuery() = default;

QString XQuery::evaluate(QString xPathExpression, QString *errorMessage)
{
    // XQuery can't have invalid XML characters
    xPathExpression.replace(u'&', u"&amp;"_s);
    xPathExpression.replace(u'<', u"&lt;"_s);
    return doEvaluate(xPathExpression, errorMessage);
}

std::shared_ptr<XQuery> XQuery::create(const QString &focus, QString *errorMessage)
{
#if defined(HAVE_LIBXSLT)
    return libXml_createXQuery(focus, errorMessage);
#else
    *errorMessage = QLatin1StringView(__FUNCTION__) + u" is not implemented."_s;
    return std::shared_ptr<XQuery>();
#endif
}

QString xsl_transform(const QString &xml, const QString &xsl, QString *errorMessage)
{
#if defined(HAVE_LIBXSLT)
    return libXslt_transform(xml, xsl, errorMessage);
#else
    *errorMessage = QLatin1StringView(__FUNCTION__) + u" is not implemented."_s;
    return xml;
#endif
}
