// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DOTVIEW_H
#define DOTVIEW_H

#include <QtCore/QString>

/// Show a dot digraph in an image viewer
/// \param name base name for files
/// \param graph graph
bool showDotGraph(const QString &name, const QString &graph);

#endif // DOTVIEW_H
