// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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

    void setSystemIncludes(const QStringList &systemIncludes);

    bool visitLocation(const QString &fileName, LocationType locationType) const override;

    StartTokenResult startToken(const CXCursor &cursor) override;
    bool endToken(const CXCursor &cursor) override;

    FileModelItem dom() const;

private:
    BuilderPrivate *d;
};

} // namespace clang

#endif // CLANGBUILDER_H
