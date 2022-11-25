// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CONFIGURABLESCOPE_H
#define CONFIGURABLESCOPE_H

#include <textstream.h>
#include <configurabletypeentry.h>

/// Enclose a scope within preprocessor conditions for configurable entries
class ConfigurableScope
{
public:
    explicit ConfigurableScope(TextStream &s, const ConfigurableTypeEntryCPtr &t) :
        m_stream(s),
        m_hasConfigCondition(t->hasConfigCondition())
    {
        if (m_hasConfigCondition)
            m_stream << t->configCondition() << '\n';
    }

    ~ConfigurableScope()
    {
        if (m_hasConfigCondition)
            m_stream << "#endif\n";
    }

private:
    TextStream &m_stream;
    const bool m_hasConfigCondition;
};

#endif // CONFIGURABLESCOPE_H
