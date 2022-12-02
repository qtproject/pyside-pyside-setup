// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef GENERATORCONTEXT_H
#define GENERATORCONTEXT_H

#include <abstractmetalang_typedefs.h>
#include <abstractmetatype.h>
#include <QtCore/QList>

QT_FORWARD_DECLARE_CLASS(QDebug);

// A GeneratorContext object contains a pointer to an AbstractMetaClass and/or a specialized
// AbstractMetaType, for which code is currently being generated.
//
// The main case is when the context contains only an AbstractMetaClass pointer, which is used
// by different methods to generate appropriate expressions, functions, type names, etc.
//
// The second case is for generation of code for smart pointers. In this case the m_metaClass
// member contains the generic template class of the smart pointer, and the m_preciseClassType
// member contains the instantiated template type, e.g. a concrete shared_ptr<int>. To
// distinguish this case, the member m_forSmartPointer is set to true.
//
// In the future the second case might be generalized for all template type instantiations.

class GeneratorContext {
    friend class ShibokenGenerator;
    friend class Generator;
public:
    enum Type { Class, WrappedClass, SmartPointer };

    GeneratorContext() = default;

    AbstractMetaClassCPtr metaClass() const { return m_metaClass; }
    const AbstractMetaType &preciseType() const { return m_preciseClassType; }
    AbstractMetaClassCPtr pointeeClass() const { return m_pointeeClass; }

    bool forSmartPointer() const { return m_type == SmartPointer; }
    bool useWrapper() const { return m_type ==  WrappedClass; }

    QString wrapperName() const;
    /// Returns the wrapper name in case of useWrapper(), the qualified class
    /// name or the smart pointer specialization.
    QString effectiveClassName() const;

private:
    AbstractMetaClassCPtr m_metaClass;
    AbstractMetaClassCPtr m_pointeeClass;
    AbstractMetaType m_preciseClassType;
    QString m_wrappername;
    Type m_type = Class;
};

QDebug operator<<(QDebug debug, const GeneratorContext &c);

#endif // GENERATORCONTEXT_H
