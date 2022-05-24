// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ENCLOSINGCLASSMIXIN_H
#define ENCLOSINGCLASSMIXIN_H

class AbstractMetaClass;

class EnclosingClassMixin {
public:
    const AbstractMetaClass *enclosingClass() const { return m_enclosingClass; }
    void setEnclosingClass(const AbstractMetaClass *cls) { m_enclosingClass = cls; }
    const AbstractMetaClass *targetLangEnclosingClass() const;

private:
     const AbstractMetaClass *m_enclosingClass = nullptr;
};

#endif // ENCLOSINGCLASSMIXIN_H
