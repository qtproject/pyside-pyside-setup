// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CTYPENAMES_H
#define CTYPENAMES_H

#include <QtCore/QString>

static inline QString boolT() { return QStringLiteral("bool"); }
static inline QString intT() { return QStringLiteral("int"); }
static inline QString unsignedT() { return QStringLiteral("unsigned"); }
static inline QString unsignedIntT() { return QStringLiteral("unsigned int"); }
static inline QString longT() { return QStringLiteral("long"); }
static inline QString unsignedLongT() { return QStringLiteral("unsigned long"); }
static inline QString shortT() { return QStringLiteral("short"); }
static inline QString unsignedShortT() { return QStringLiteral("unsigned short"); }
static inline QString unsignedCharT() { return QStringLiteral("unsigned char"); }
static inline QString longLongT() { return QStringLiteral("long long"); }
static inline QString unsignedLongLongT() { return QStringLiteral("unsigned long long"); }
static inline QString charT() { return QStringLiteral("char"); }
static inline QString floatT() { return QStringLiteral("float"); }
static inline QString doubleT() { return QStringLiteral("double"); }
static inline QString constCharPtrT() { return QStringLiteral("const char*"); }

static inline QString qByteArrayT() { return QStringLiteral("QByteArray"); }
static inline QString qMetaObjectT() { return QStringLiteral("QMetaObject"); }
static inline QString qObjectT() { return QStringLiteral("QObject"); }
static inline QString qStringT() { return QStringLiteral("QString"); }
static inline QString qVariantT() { return QStringLiteral("QVariant"); }

#endif // CTYPENAMES_H
