// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef EXCEPTION_H
#define EXCEPTION_H

#include <QtCore/QString>

#include <string>
#include <exception>

class Exception : public std::exception
{
public:
    explicit Exception(const QString &message) : m_message(message.toUtf8()) {}
    explicit Exception(const char *message) : m_message(message) {}

    const char *what() const noexcept override
    {
        return m_message.c_str();
    }

private:
    const std::string m_message;
};

#endif // EXCEPTION
