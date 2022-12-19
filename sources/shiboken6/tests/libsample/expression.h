// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


#ifndef EXPRESSION_H
#define EXPRESSION_H

#include "libsamplemacros.h"

#include <string>

class LIBSAMPLE_API Expression
{
public:
    enum Operation {
        None, Add, Sub, LessThan, GreaterThan
    };

    Expression(int number);
    Expression(const Expression &other);
    Expression &operator=(const Expression &other);

    ~Expression();

    Expression operator>(const Expression &other);
    Expression operator<(const Expression &other);
    Expression operator+(const Expression &other);
    Expression operator-(const Expression &other);

    std::string toString() const;
private:
    int m_value = 0;
    Operation m_operation = None;
    Expression *m_operand1 = nullptr;
    Expression *m_operand2 = nullptr;
    Expression();
};

#endif // EXPRESSION_H
