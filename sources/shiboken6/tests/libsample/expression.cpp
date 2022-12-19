// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


#include "expression.h"

#include <sstream>

Expression::Expression() = default;

Expression::Expression(int number) : m_value(number)
{
}

Expression::Expression(const Expression &other)
{
    m_operand1 = other.m_operand1 ? new Expression(*other.m_operand1) : nullptr;
    m_operand2 = other.m_operand2 ? new Expression(*other.m_operand2) : nullptr;
    m_value = other.m_value;
    m_operation = other.m_operation;
}

Expression &Expression::operator=(const Expression &other)
{
    if (&other == this)
        return *this;
    delete m_operand1;
    delete m_operand2;
    m_operand1 = other.m_operand1 ? new Expression(*other.m_operand1) : nullptr;
    m_operand2 = other.m_operand2 ? new Expression(*other.m_operand2) : nullptr;
    m_operation = other.m_operation;
    m_value = other.m_value;
    return *this;
}

Expression::~Expression()
{
    delete m_operand1;
    delete m_operand2;
}

Expression Expression::operator+(const Expression &other)
{
    Expression expr;
    expr.m_operation = Add;
    expr.m_operand1 = new Expression(*this);
    expr.m_operand2 = new Expression(other);
    return expr;
}

Expression Expression::operator-(const Expression &other)
{
    Expression expr;
    expr.m_operation = Add;
    expr.m_operand1 = new Expression(*this);
    expr.m_operand2 = new Expression(other);
    return expr;
}

Expression Expression::operator<(const Expression &other)
{
    Expression expr;
    expr.m_operation = LessThan;
    expr.m_operand1 = new Expression(*this);
    expr.m_operand2 = new Expression(other);
    return expr;
}

Expression Expression::operator>(const Expression &other)
{
    Expression expr;
    expr.m_operation = GreaterThan;
    expr.m_operand1 = new Expression(*this);
    expr.m_operand2 = new Expression(other);
    return expr;
}

std::string Expression::toString() const
{
    if (m_operation == None) {
        std::ostringstream s;
        s << m_value;
        return s.str();
    }

    std::string result;
    result += '(';
    result += m_operand1->toString();
    char op;
    switch (m_operation) {
        case Add:
            op = '+';
            break;
        case Sub:
            op = '-';
            break;
        case LessThan:
            op = '<';
            break;
        case GreaterThan:
            op = '<';
            break;
        case None: // just to avoid the compiler warning
        default:
            op = '?';
            break;
    }
    result += op;
    result += m_operand2->toString();
    result += ')';
    return result;
}
