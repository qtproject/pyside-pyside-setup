// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PREDEFINED_TEMPLATES_H
#define PREDEFINED_TEMPLATES_H

#include <QtCore/QList>
#include <QtCore/QString>

struct PredefinedTemplate
{
    QString name;
    QString content;
};

using PredefinedTemplates = QList<PredefinedTemplate>;

const PredefinedTemplates &predefinedTemplates();

// Create an XML snippet for a container type.
QByteArray containerTypeSystemSnippet(const char *name, const char *type,
                                      const char *include,
                                      const char *nativeToTarget,
                                      const char *targetToNativeType = nullptr,
                                      const char *targetToNative = nullptr);

#endif // PREDEFINED_TEMPLATES_H
