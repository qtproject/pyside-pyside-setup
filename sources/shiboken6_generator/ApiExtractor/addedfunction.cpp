// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:build-tool

#include "addedfunction.h"
#include "addedfunctionparser.h"
#include "typeparser.h"

#include <QtCore/qdebug.h>

using namespace Qt::StringLiterals;

constexpr auto callOperator = "operator()"_L1;

// Helpers to split a parameter list of <add-function>, <declare-function>
// (@ denoting names), like
// "void foo(QList<X,Y> &@list@ = QList<X,Y>{1,2}, int @b@=5, ...)"
namespace AddedFunctionParser {

QDebug operator<<(QDebug d, const Argument &a)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "Argument(type=\"" << a.type << '"';
    if (!a.name.isEmpty())
        d << ", name=\"" << a.name << '"';
    if (!a.defaultValue.isEmpty())
        d << ", defaultValue=\"" << a.defaultValue << '"';
    d << ')';
    return d;
}

QDebug operator<<(QDebug debug, const ParsedFunction &f)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "ParsedFunction(name=\"" << f.name << '"';
    if (f.constant)
        debug << ", [const]";
    if (!f.arguments.isEmpty()) {
        debug << ", arguments=";
        for (qsizetype i = 0, size = f.arguments.size(); i < size; ++i) {
            if (i > 0)
                debug << ", ";
            debug << f.arguments.at(i);
        }
    }
    debug << ')';
    return debug;
}

// Helper for finding the end of a function parameter, observing
// nested template parameters or lists.
static qsizetype parameterTokenEnd(qsizetype startPos, QStringView paramString)
{
    const auto end = paramString.size();
    int nestingLevel = 0;
    for (qsizetype p = startPos; p < end; ++p) {
        switch (paramString.at(p).toLatin1()) {
        case ',':
            if (nestingLevel == 0)
                return p;
            break;
        case '<': // templates
        case '{': // initializer lists of default values
        case '(': // initialization, function pointers
        case '[': // array dimensions
            ++nestingLevel;
            break;
        case '>':
        case '}':
        case ')':
        case ']':
            --nestingLevel;
            break;
        default:
            break;
        }
    }
    return end;
}

// Split a function parameter list into string tokens containing one
// parameters (including default value, etc).
static QList<QStringView> splitParameterTokens(QStringView paramString)
{
    QList<QStringView> result;
    qsizetype startPos = 0;
    for ( ; startPos < paramString.size(); ) {
        const auto end = parameterTokenEnd(startPos, paramString);
        result.append(paramString.mid(startPos, end - startPos).trimmed());
        startPos = end + 1;
    }
    return result;
}

// Split a function parameter list
Arguments splitParameters(QStringView paramString, QString *errorMessage)
{
    Arguments result;
    const QList<QStringView> tokens = splitParameterTokens(paramString);

    for (const auto &t : tokens) {
        Argument argument;
        // Check defaultValue, "int @b@=5"
        const auto equalPos = t.lastIndexOf(u'=');
        if (equalPos != -1) {
            const auto defaultValuePos = equalPos + 1;
            argument.defaultValue =
                t.mid(defaultValuePos, t.size() - defaultValuePos).trimmed().toString();
        }
        QString typeString = (equalPos != -1 ? t.left(equalPos) : t).trimmed().toString();
        // Check @name@
        const auto atPos = typeString.indexOf(u'@');
        if (atPos != -1) {
            const auto namePos = atPos + 1;
            const auto nameEndPos = typeString.indexOf(u'@', namePos);
            if (nameEndPos == -1) {
                if (errorMessage != nullptr) {
                    *errorMessage = u"Mismatched @ in \""_s
                                    + paramString.toString() + u'"';
                }
                return {};
            }
            argument.name = typeString.mid(namePos, nameEndPos - namePos).trimmed();
            typeString.remove(atPos, nameEndPos - atPos + 1);
        }
        argument.type = typeString.trimmed();
        result.append(argument);
    }

    return result;
}

std::optional<ParsedFunction> parse(QStringView signatureIn, QString *errorMessage)
{
    ParsedFunction result;
    QStringView signature = signatureIn.trimmed();

    // Skip past "operator()(...)"
    const auto parenSearchStartPos = signature.startsWith(callOperator)
                                         ? callOperator.size() : 0;
    const auto openParenPos = signature.indexOf(u'(', parenSearchStartPos);
    if (openParenPos < 0) {
        result.name = signature.toString();
        return result;
    }

    result.name = signature.left(openParenPos).trimmed().toString();
    const auto closingParenPos = signature.lastIndexOf(u')');
    if (closingParenPos < 0) {
        *errorMessage = u"Missing closing parenthesis"_s;
        return std::nullopt;
    }

    // Check for "foo() const"
    const auto signatureLength = signature.length();
    const auto qualifierLength = signatureLength - closingParenPos - 1;
    if (qualifierLength >= 5
        && signature.right(qualifierLength).contains(u"const")) {
        result.constant = true;
    }

    const auto paramString = signature.mid(openParenPos + 1, closingParenPos - openParenPos - 1);
    result.arguments = AddedFunctionParser::splitParameters(paramString, errorMessage);
    if (result.arguments.isEmpty() && !errorMessage->isEmpty())
        return std::nullopt;
    if (result.arguments.size() == 1 && result.arguments.constFirst().type == "void"_L1)
        result.arguments.clear(); // "void foo(void)" -> ""void foo()"
    return result;
}

} // namespace AddedFunctionParser

AddedFunction::AddedFunction(const QString &name, const QList<Argument> &arguments,
                             const TypeInfo &returnType) :
    m_name(name),
    m_arguments(arguments),
    m_returnType(returnType)
{
}

AddedFunction::AddedFunctionPtr
    AddedFunction::createAddedFunction(const QString &signatureIn, const QString &returnTypeIn,
                                       QString *errorMessage)

{
    errorMessage->clear();

    QList<Argument> arguments;
    const TypeInfo returnType = returnTypeIn.isEmpty()
                                ? TypeInfo::voidType()
                                : TypeParser::parse(returnTypeIn, errorMessage);
    if (!errorMessage->isEmpty())
        return {};

    const auto parsedFunctionOpt = AddedFunctionParser::parse(signatureIn, errorMessage);
    if (!parsedFunctionOpt.has_value())
        return {};

    // Convert arguments to typeinfo
    for (const auto &p : std::as_const(parsedFunctionOpt->arguments)) {
        TypeInfo type = p.type == u"..."
            ? TypeInfo::varArgsType() : TypeParser::parse(p.type, errorMessage);
        if (!errorMessage->isEmpty()) {
            errorMessage->prepend(u"Unable to parse added function "_s + signatureIn
                                  + u": "_s);
            return {};
        }
        arguments.append({type, p.name, p.defaultValue});
    }

    auto result = std::make_shared<AddedFunction>(parsedFunctionOpt->name, arguments, returnType);
    result->setConstant(parsedFunctionOpt->constant);
    return result;
}

QDebug operator<<(QDebug d, const AddedFunction::Argument &a)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "Argument(";
    d << a.typeInfo;
    if (!a.name.isEmpty())
        d << ' ' << a.name;
    if (!a.defaultValue.isEmpty())
        d << " = " << a.defaultValue;
    d << ')';
    return d;
}

QDebug operator<<(QDebug d, const AddedFunction &af)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "AddedFunction(";
    if (af.access() == AddedFunction::Protected)
        d << "protected";
    if (af.isStatic())
        d << " static";
    d << af.returnType() << ' ' << af.name() << '(' << af.arguments() << ')';
    if (af.isConstant())
        d << " const";
    if (af.isDeclaration())
        d << " [declaration]";
    return d;
}
