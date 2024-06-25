// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "anystringview_helpers.h"

#include <QtCore/QString> // Must go before QAnyStringView for operator<<(QTextStream,QASV)!
#include <QtCore/QAnyStringView>
#include <QtCore/QDebug>
#include <QtCore/QTextStream>

#include <cstring>

QTextStream &operator<<(QTextStream &str, QAnyStringView asv)
{
    asv.visit([&str](auto s) { str << s; });
    return str;
}

static bool asv_containsImpl(QLatin1StringView v, char c)
{
    return v.contains(uint16_t(c));
}

static bool asv_containsImpl(QUtf8StringView v, char c)
{
    return std::strchr(v.data(), c) != nullptr;
}

static bool asv_containsImpl(QStringView v, char c)
{
    return v.contains(uint16_t(c));
}

bool asv_contains(QAnyStringView asv, char needle)
{
    return asv.visit([needle](auto s) { return asv_containsImpl(s, needle); });
}

static bool asv_containsImpl(QLatin1StringView v, const char *c)
{
    return v.contains(QLatin1StringView(c));
}
static bool asv_containsImpl(QUtf8StringView v, const char *c)
{
    return std::strstr(v.data(), c) != nullptr;
}

static bool asv_containsImpl(QStringView v, const char *c)
{
    return v.contains(QLatin1StringView(c));
}

bool asv_contains(QAnyStringView asv, const char *needle)
{
    return asv.visit([needle](auto s) { return asv_containsImpl(s, needle); });
}

static qsizetype asv_indexOfImpl(QLatin1StringView v, const char *needle)
{
    return v.indexOf(QLatin1StringView(needle));
}

static qsizetype asv_indexOfImpl(QUtf8StringView v, const char *needle)
{
    const char *data = v.data();
    const char *match = std::strstr(data, needle);
    return match != nullptr ? qsizetype(match - data) : qsizetype(-1);
}

static qsizetype asv_indexOfImpl(QStringView v, const char *needle)
{
    return v.indexOf(QLatin1StringView(needle));
}

qsizetype asv_indexOf(QAnyStringView asv, const char *needle)
{
    return asv.visit([needle](auto s) { return asv_indexOfImpl(s, needle); });
}
