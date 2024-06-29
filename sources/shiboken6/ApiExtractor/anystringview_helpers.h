// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ANYSTRINGVIEW_STREAM_H
#define ANYSTRINGVIEW_STREAM_H

#include <QtCore/QtTypes>
#include <QtCore/QtClassHelperMacros>

QT_FORWARD_DECLARE_CLASS(QAnyStringView)
QT_FORWARD_DECLARE_CLASS(QTextStream)
QT_FORWARD_DECLARE_CLASS(QDebug)

QTextStream &operator<<(QTextStream &str, QAnyStringView asv);

bool asv_contains(QAnyStringView asv, char needle);
bool asv_contains(QAnyStringView asv, const char *needle);

#endif // ANYSTRINGVIEW_STREAM_H
