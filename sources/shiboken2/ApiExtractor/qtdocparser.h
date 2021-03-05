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

#ifndef QTDOCPARSER_H
#define QTDOCPARSER_H

#include "docparser.h"

class QtDocParser : public DocParser
{
public:
    QtDocParser() = default;
    void fillDocumentation(AbstractMetaClass* metaClass) override;
    Documentation retrieveModuleDocumentation() override;
    Documentation retrieveModuleDocumentation(const QString& name) override;

private:
    QString queryFunctionDocumentation(const QString &sourceFileName,
                                       const AbstractMetaClass* metaClass,
                                       const QString &classQuery,
                                       const  AbstractMetaFunction *func,
                                       const DocModificationList &signedModifs,
                                       const XQueryPtr &xquery,
                                       QString *errorMessage);
};

#endif // QTDOCPARSER_H

