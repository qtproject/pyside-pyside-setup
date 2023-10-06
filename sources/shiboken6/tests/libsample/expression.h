// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0


#ifndef EXPRESSION_H
#define EXPRESSION_H

#include "libsamplemacros.h"

#include <memory>
#include <string>

class LIBSAMPLE_API Expression
{
public:
    LIBMINIMAL_DEFAULT_COPY_MOVE(Expression)

    enum Operation {
        None, Add, Sub, LessThan, GreaterThan
    };

    explicit Expression(int number) noexcept;
    ~Expression() = default;

    Expression operator>(const Expression &other);
    Expression operator<(const Expression &other);
    Expression operator+(const Expression &other);
    Expression operator-(const Expression &other);

    std::string toString() const;
private:
    int m_value = 0;
    Operation m_operation = None;
    std::shared_ptr<Expression> m_operand1;
    std::shared_ptr<Expression> m_operand2;

    Expression() noexcept;
};

#endif // EXPRESSION_H
