// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ENCLOSINGCLASSMIXIN_H
#define ENCLOSINGCLASSMIXIN_H

#include "abstractmetalang_typedefs.h"

class AbstractMetaClass;

class EnclosingClassMixin {
public:

    const AbstractMetaClassCPtr enclosingClass() const
        { return m_enclosingClass.lock(); }
    void setEnclosingClass(const AbstractMetaClassCPtr &cls)
        { m_enclosingClass = cls; }
    AbstractMetaClassCPtr targetLangEnclosingClass() const;

private:
    std::weak_ptr<const AbstractMetaClass> m_enclosingClass;
};

#endif // ENCLOSINGCLASSMIXIN_H
