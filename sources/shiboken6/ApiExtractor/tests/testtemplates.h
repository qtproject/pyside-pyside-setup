// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTTEMPLATES_H
#define TESTTEMPLATES_H

#include <QtCore/QObject>

class TestTemplates : public QObject
{
    Q_OBJECT
private slots:
    void testTemplateOnContainers();
    void testTemplateWithNamespace();
    void testTemplateValueAsArgument();
    void testTemplatePointerAsArgument();
    void testTemplateReferenceAsArgument();
    void testTemplateParameterFixup();
    void testInheritanceFromContainterTemplate();
    void testTemplateInheritanceMixedWithForwardDeclaration();
    void testTemplateInheritanceMixedWithNamespaceAndForwardDeclaration();
    void testTypedefOfInstantiationOfTemplateClass();
    void testContainerTypeIncompleteArgument();
    void testNonTypeTemplates();
    void testTemplateTypeDefs_data();
    void testTemplateTypeDefs();
    void testTemplateTypeAliases();
};

#endif
