// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include <QtCore/qnamespace.h>

// There are symbols in Qt that exist in Debug but
// not in release
#define QT_NO_DEBUG

// Here are now all configured modules appended:
