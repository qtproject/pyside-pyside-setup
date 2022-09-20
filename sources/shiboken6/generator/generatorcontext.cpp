// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "generatorcontext.h"
#include <abstractmetalang.h>

#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

QString GeneratorContext::wrapperName() const
{
    Q_ASSERT(m_type == WrappedClass);
    return m_wrappername;
}

QString GeneratorContext::effectiveClassName() const
{
    if (m_type == SmartPointer)
        return m_preciseClassType.cppSignature();
    return m_type == WrappedClass ? m_wrappername : m_metaClass->qualifiedCppName();
}

QDebug operator<<(QDebug debug, const GeneratorContext &c)
{
    QDebugStateSaver saver(debug);
    debug.noquote();
    debug.nospace();
    debug << "GeneratorContext(\"" << c.metaClass()->name() << "\" ";
    if (c.useWrapper())
        debug << "[wrapper]";
    else if (c.forSmartPointer())
        debug << "[smart pointer] \"" << c.preciseType().cppSignature() << '"';
    else
        debug << "[class]";
    debug << ')';
    return debug;
}
