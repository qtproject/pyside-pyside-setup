// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#include "typesystemparser_checks.h"

#include <algorithm>

using namespace Qt::StringLiterals;

// An approximation of "Unicode Standard Annex #31" for checking identifiers to
// prevent code injection attacks (originating from uic).
// FIXME: Simplify according to QTBUG-126860
static bool isIdStart(QChar c)
{
    bool result = false;
    switch (c.category()) {
    case QChar::Letter_Uppercase:
    case QChar::Letter_Lowercase:
    case QChar::Letter_Titlecase:
    case QChar::Letter_Modifier:
    case QChar::Letter_Other:
    case QChar::Number_Letter:
        result = true;
        break;
    default:
        result = c == u'_';
        break;
    }
    return result;
}

static bool isIdContinuation(QChar c)
{
    bool result = false;
    switch (c.category()) {
    case QChar::Letter_Uppercase:
    case QChar::Letter_Lowercase:
    case QChar::Letter_Titlecase:
    case QChar::Letter_Modifier:
    case QChar::Letter_Other:
    case QChar::Number_Letter:
    case QChar::Mark_NonSpacing:
    case QChar::Mark_SpacingCombining:
    case QChar::Number_DecimalDigit:
    case QChar::Punctuation_Connector: // '_'
        result = true;
        break;
    default:
        break;
    }
    return result;
}

static bool isPackageContinuation(QChar c)
{
    return c == u'.' || isIdContinuation(c);
}

static bool isClassContinuation(QChar c)
{
    return c == u':' || isIdContinuation(c);
}

bool isValidIdentifier(QStringView input)
{
    return !input.isEmpty() && isIdStart(input.at(0))
        && std::all_of(input.cbegin() + 1, input.cend(), isIdContinuation);
}

bool isValidPackageName(QStringView input)
{
    return !input.isEmpty() && isIdStart(input.at(0))
        && std::all_of(input.cbegin() + 1, input.cend(), isPackageContinuation);
}

// Class name with "::"
bool isValidClassName(QStringView input)
{
    return !input.isEmpty() && isIdStart(input.at(0))
        && std::all_of(input.cbegin() + 1, input.cend(), isClassContinuation);
}
