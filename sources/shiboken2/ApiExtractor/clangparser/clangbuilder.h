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

#ifndef CLANGBUILDER_H
#define CLANGBUILDER_H

#include "clangparser.h"

#include <codemodel_fwd.h>

namespace clang {

class BuilderPrivate;

class Builder : public BaseVisitor {
public:
    Q_DISABLE_COPY(Builder)

    Builder();
    ~Builder();

    void setSystemIncludes(const QByteArrayList &systemIncludes);

    bool visitLocation(const CXSourceLocation &location) const override;

    StartTokenResult startToken(const CXCursor &cursor) override;
    bool endToken(const CXCursor &cursor) override;

    FileModelItem dom() const;

private:
    BuilderPrivate *d;
};

} // namespace clang

#endif // CLANGBUILDER_H
