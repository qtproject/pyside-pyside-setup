// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CTYPENAMES_H
#define CTYPENAMES_H

#include <QtCore/QString>

constexpr auto boolT = QLatin1StringView("bool");
constexpr auto intT = QLatin1StringView("int");
constexpr auto unsignedT = QLatin1StringView("unsigned");
constexpr auto unsignedIntT = QLatin1StringView("unsigned int");
constexpr auto longT = QLatin1StringView("long");
constexpr auto unsignedLongT = QLatin1StringView("unsigned long");
constexpr auto shortT = QLatin1StringView("short");
constexpr auto unsignedShortT = QLatin1StringView("unsigned short");
constexpr auto unsignedCharT = QLatin1StringView("unsigned char");
constexpr auto longLongT = QLatin1StringView("long long");
constexpr auto unsignedLongLongT = QLatin1StringView("unsigned long long");
constexpr auto charT = QLatin1StringView("char");
constexpr auto floatT = QLatin1StringView("float");
constexpr auto doubleT = QLatin1StringView("double");
constexpr auto constCharPtrT = QLatin1StringView("const char*");

constexpr auto qByteArrayT = QLatin1StringView("QByteArray");
constexpr auto qMetaObjectT = QLatin1StringView("QMetaObject");
constexpr auto qObjectT = QLatin1StringView("QObject");
constexpr auto qStringT = QLatin1StringView("QString");
constexpr auto qVariantT = QLatin1StringView("QVariant");

#endif // CTYPENAMES_H
