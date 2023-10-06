// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


#include "expression.h"

#include <sstream>

Expression::Expression() noexcept = default;

Expression::Expression(int number) noexcept : m_value(number)
{
}

Expression Expression::operator+(const Expression &other)
{
    Expression expr;
    expr.m_operation = Add;
    expr.m_operand1 = std::make_shared<Expression>(*this);
    expr.m_operand2 = std::make_shared<Expression>(other);
    return expr;
}

Expression Expression::operator-(const Expression &other)
{
    Expression expr;
    expr.m_operation = Add;
    expr.m_operand1 = std::make_shared<Expression>(*this);
    expr.m_operand2 = std::make_shared<Expression>(other);
    return expr;
}

Expression Expression::operator<(const Expression &other)
{
    Expression expr;
    expr.m_operation = LessThan;
    expr.m_operand1 = std::make_shared<Expression>(*this);
    expr.m_operand2 = std::make_shared<Expression>(other);
    return expr;
}

Expression Expression::operator>(const Expression &other)
{
    Expression expr;
    expr.m_operation = GreaterThan;
    expr.m_operand1 = std::make_shared<Expression>(*this);
    expr.m_operand2 = std::make_shared<Expression>(other);
    return expr;
}

std::string Expression::toString() const
{
    std::ostringstream s;
    if (m_operation == None) {
        s << m_value;
        return s.str();
    }

    s << '(' << m_operand1->toString();
    switch (m_operation) {
        case Add:
            s << '+';
            break;
        case Sub:
            s << '-';
            break;
        case LessThan:
            s << '<';
            break;
        case GreaterThan:
            s << '<';
            break;
        default:
            s << '?';
            break;
    }
    s << m_operand2->toString() << ')';
    return s.str();
}
