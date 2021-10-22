/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "abstractmetabuilder.h"
#include "abstractmetabuilder_p.h"
#include "abstractmetaenum.h"
#include "abstractmetalang.h"
#include "typesystem.h"

using QStringViewList = QList<QStringView>;

// Return a prefix to fully qualify value, eg:
// resolveScopePrefix("Class::NestedClass::Enum::Value1", "Enum::Value1")
//     -> "Class::NestedClass::")
static QString resolveScopePrefixHelper(const QStringViewList &scopeList,
                                        QStringView value)
{
    QString name;
    for (qsizetype i = scopeList.size() - 1 ; i >= 0; --i) {
        const QString prefix = scopeList.at(i).toString() + u"::"_qs;
        if (value.startsWith(prefix))
            name.clear();
        else
            name.prepend(prefix);
    }
    return name;
}

QString AbstractMetaBuilder::resolveScopePrefix(const AbstractMetaClass *scope,
                                                QStringView value)
{
    if (!scope)
        return {};
    const QString &qualifiedCppName = scope->qualifiedCppName();
    const QStringViewList scopeList =
        QStringView{qualifiedCppName}.split(u"::"_qs, Qt::SkipEmptyParts);
    return resolveScopePrefixHelper(scopeList, value);
}

// Return the scope for fully qualifying the enumeration value
static QString resolveEnumValueScopePrefix(const AbstractMetaEnum &metaEnum,
                                           QStringView value)
{
    const AbstractMetaClass *scope = metaEnum.enclosingClass();
    if (!scope)
        return {}; // global enum, value should work as is
    const QString &qualifiedCppName = scope->qualifiedCppName();
    const QString &enumName = metaEnum.name();
    QStringViewList parts =
        QStringView{qualifiedCppName}.split(u"::"_qs, Qt::SkipEmptyParts);
    // Append the type (as required for enum classes) unless it is an anonymous enum.
    if (!metaEnum.isAnonymous())
        parts.append(QStringView{enumName});
    return resolveScopePrefixHelper(parts, value);
}

// Return the scope for fully qualifying an enumeration value from
// an unknown enum in the class scope including trailing "::".
QString AbstractMetaBuilder::searchForEnumScope(const AbstractMetaClass *metaClass,
                                                QStringView value)
{
    if (!metaClass)
        return QString();
    for (const AbstractMetaEnum &metaEnum : metaClass->enums()) {
        auto v = metaEnum.findEnumValue(value);
        if (v.has_value())
            return resolveEnumValueScopePrefix(metaEnum, value);
    }
    // PYSIDE-331: We need to also search the base classes.
    QString ret = searchForEnumScope(metaClass->enclosingClass(), value);
    if (ret.isEmpty())
        ret = searchForEnumScope(metaClass->baseClass(), value);
    return ret;
}

static bool isQualifiedCppIdentifier(QStringView e)
{
    return !e.isEmpty() && e.at(0).isLetter()
           && std::all_of(e.cbegin() + 1, e.cend(),
                          [](QChar c) { return c.isLetterOrNumber() || c == u'_' || c == u':'; });
}

static bool isIntegerConstant(const QStringView expr)
{
    bool isNumber;
    auto n = expr.toInt(&isNumber, /* guess base: 0x or decimal */ 0);
    Q_UNUSED(n);
    return isNumber;
}

static bool isFloatConstant(const QStringView expr)
{
    bool isNumber;
    auto d = expr.toDouble(&isNumber);
    Q_UNUSED(d);
    return isNumber;
}

// Fix an enum default value: Add the enum/flag scope or fully qualified name
// to the default value, making it usable from Python wrapper code outside the
// owner class hierarchy. See TestEnum::testEnumDefaultValues().
QString AbstractMetaBuilderPrivate::fixEnumDefault(const AbstractMetaType &type,
                                                   const QString &expr) const
{
    // QFlags construct from integers, do not fix that
    if (isIntegerConstant(expr))
        return expr;

    const auto *typeEntry = type.typeEntry();
    const EnumTypeEntry *enumTypeEntry = nullptr;
    const FlagsTypeEntry *flagsTypeEntry = nullptr;
    if (typeEntry->isFlags()) {
        flagsTypeEntry = static_cast<const FlagsTypeEntry *>(typeEntry);
        enumTypeEntry = flagsTypeEntry->originator();
    } else {
        Q_ASSERT(typeEntry->isEnum());
        enumTypeEntry = static_cast<const EnumTypeEntry *>(typeEntry);
    }
    // Use the enum's qualified name (would otherwise be "QFlags<Enum>")
    if (!enumTypeEntry->qualifiedCppName().contains(u"::"))
        return expr; // Global enum, nothing to fix here

    // This is a somehow scoped enum
    AbstractMetaEnum metaEnum = m_enums.value(enumTypeEntry);

    if (isQualifiedCppIdentifier(expr)) // A single enum value
        return resolveEnumValueScopePrefix(metaEnum, expr) + expr;

    QString result;
    // Is this a cast from integer or other type ("Enum(-1)" or "Options(0x10|0x20)"?
    // Prepend the scope (assuming enum and flags are in the same scope).
    auto parenPos = expr.indexOf(u'(');
    const bool typeCast = parenPos != -1 && expr.endsWith(u')')
                          && isQualifiedCppIdentifier(QStringView{expr}.left(parenPos));
    if (typeCast) {
        const QString prefix =
            AbstractMetaBuilder::resolveScopePrefix(metaEnum.enclosingClass(), expr);
        result += prefix;
        parenPos += prefix.size();
    }
    result += expr;

    // Extract "Option1 | Option2" from "Options(Option1 | Option2)"
    QStringView innerExpression = typeCast
        ? QStringView{result}.mid(parenPos + 1, result.size() - parenPos - 2)
        : QStringView{result};

    // Quick check for number "Options(0x4)"
    if (isIntegerConstant(innerExpression))
        return result;

    // Quick check for single enum value "Options(Option1)"
    if (isQualifiedCppIdentifier(innerExpression)) {
        const QString prefix = resolveEnumValueScopePrefix(metaEnum, innerExpression);
        result.insert(parenPos + 1, prefix);
        return result;
    }

    // Tokenize simple "A | B" expressions and qualify the enum values therein.
    // Anything more complicated is left as is ATM.
    if (!innerExpression.contains(u'|') || innerExpression.contains(u'&')
        || innerExpression.contains(u'^') || innerExpression.contains(u'(')
        || innerExpression.contains(u'~')) {
        return result;
    }

    const QList<QStringView> tokens = innerExpression.split(u'|', Qt::SkipEmptyParts);
    QStringList qualifiedTokens;
    qualifiedTokens.reserve(tokens.size());
    for (const auto &tokenIn : tokens) {
        const auto token = tokenIn.trimmed();
        QString qualified = token.toString();
        if (!isIntegerConstant(token) && isQualifiedCppIdentifier(token))
            qualified.prepend(resolveEnumValueScopePrefix(metaEnum, token));
        qualifiedTokens.append(qualified);
    }
    const QString qualifiedExpression = qualifiedTokens.join(u" | "_qs);
    if (!typeCast)
        return qualifiedExpression;

    result.replace(parenPos + 1, innerExpression.size(), qualifiedExpression);
    return result;
}

bool AbstractMetaBuilder::dontFixDefaultValue(QStringView expr)
{
    return expr.isEmpty() || expr == u"{}" || expr == u"nullptr"
        || expr == u"NULL" || expr == u"true" || expr == u"false"
        || (expr.startsWith(u'{') && expr.startsWith(u'}')) // initializer list
        || (expr.startsWith(u'[') && expr.startsWith(u']')) // array
        || isIntegerConstant(expr) || isFloatConstant(expr);
}
