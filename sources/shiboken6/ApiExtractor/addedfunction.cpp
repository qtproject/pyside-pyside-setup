// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "addedfunction.h"
#include "addedfunction_p.h"
#include "typeparser.h"

#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

static inline QString callOperator() { return QStringLiteral("operator()"); }

// Helpers to split a parameter list of <add-function>, <declare-function>
// (@ denoting names), like
// "void foo(QList<X,Y> &@list@ = QList<X,Y>{1,2}, int @b@=5, ...)"
namespace AddedFunctionParser {

bool Argument::equals(const Argument &rhs) const
{
    return type == rhs.type && name == rhs.name && defaultValue == rhs.defaultValue;
}

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
        const int equalPos = t.lastIndexOf(u'=');
        if (equalPos != -1) {
            const int defaultValuePos = equalPos + 1;
            argument.defaultValue =
                t.mid(defaultValuePos, t.size() - defaultValuePos).trimmed().toString();
        }
        QString typeString = (equalPos != -1 ? t.left(equalPos) : t).trimmed().toString();
        // Check @name@
        const int atPos = typeString.indexOf(u'@');
        if (atPos != -1) {
            const int namePos = atPos + 1;
            const int nameEndPos = typeString.indexOf(u'@', namePos);
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

    QStringView signature = QStringView{signatureIn}.trimmed();

    // Skip past "operator()(...)"
    const int parenSearchStartPos = signature.startsWith(callOperator())
        ? callOperator().size() : 0;
    const int openParenPos = signature.indexOf(u'(', parenSearchStartPos);
    if (openParenPos < 0) {
        return AddedFunctionPtr(new AddedFunction(signature.toString(),
                                                  arguments, returnType));
    }

    const QString name = signature.left(openParenPos).trimmed().toString();
    const int closingParenPos = signature.lastIndexOf(u')');
    if (closingParenPos < 0) {
        *errorMessage = u"Missing closing parenthesis"_s;
        return {};
    }

    // Check for "foo() const"
    bool isConst = false;
    const int signatureLength = signature.length();
    const int qualifierLength = signatureLength - closingParenPos - 1;
    if (qualifierLength >= 5
        && signature.right(qualifierLength).contains(u"const")) {
        isConst = true;
    }

    const auto paramString = signature.mid(openParenPos + 1, closingParenPos - openParenPos - 1);
    const auto params = AddedFunctionParser::splitParameters(paramString, errorMessage);
    if (params.isEmpty() && !errorMessage->isEmpty())
        return {};
    for (const auto &p : params) {
        TypeInfo type = p.type == u"..."
            ? TypeInfo::varArgsType() : TypeParser::parse(p.type, errorMessage);
        if (!errorMessage->isEmpty()) {
            errorMessage->prepend(u"Unable to parse added function "_s + signatureIn
                                  + u": "_s);
            return {};
        }
        arguments.append({type, p.name, p.defaultValue});
    }

    auto result = std::make_shared<AddedFunction>(name, arguments, returnType);
    result->setConstant(isConst);
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
