/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef INDENTOR_H
#define INDENTOR_H

#include <QtCore/QTextStream>

/**
* Utility class to store the indentation level, use it in a QTextStream.
*/

template <int tabWidth>
class IndentorBase
{
public:
    int total() const { return tabWidth * indent; }

    int indent = 0;
};

using Indentor = IndentorBase<4>;
using Indentor1 = IndentorBase<1>;

/**
*   Class that use the RAII idiom to set and unset the indentation level.
*/

template <int tabWidth>
class IndentationBase
{
public:
    using Indentor = IndentorBase<tabWidth>;

    IndentationBase(Indentor &indentor, int count = 1) : m_count(count), indentor(indentor)
    {
        indentor.indent += m_count;
    }

    ~IndentationBase()
    {
        indentor.indent -= m_count;
    }

private:
    const int m_count;
    Indentor &indentor;
};

using Indentation = IndentationBase<4>;

template <int tabWidth>
inline QTextStream &operator <<(QTextStream &s, const IndentorBase<tabWidth> &indentor)
{
    for (int i = 0, total = indentor.total(); i < total; ++i)
        s << ' ';
    return s;
}

template <int tabWidth>
const char *indent(IndentorBase<tabWidth> &indentor)
{
    ++indentor.indent;
    return "";
}

template <int tabWidth>
const char *outdent(IndentorBase<tabWidth> &indentor)
{
    --indentor.indent;
    return "";
}

#endif // GENERATOR_H
