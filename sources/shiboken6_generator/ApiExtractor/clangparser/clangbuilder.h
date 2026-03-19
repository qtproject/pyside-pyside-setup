// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CLANGBUILDER_H
#define CLANGBUILDER_H

#include "clangparser.h"

#include <codemodel_fwd.h>


#if CINDEX_VERSION_MAJOR > 0 || CINDEX_VERSION_MINOR >= 63 // Clang 16
#  define CLANG_HAS_ASSIGNMENT_OPERATOR_CHECK
#endif

namespace clang {

class BuilderPrivate;

class Builder : public BaseVisitor {
public:
    Q_DISABLE_COPY_MOVE(Builder)

    Builder();
    ~Builder() override;

    void setForceProcessSystemIncludes(const QStringList &systemIncludes);

    bool visitLocation(const QString &fileName, LocationType locationType) const override;

    StartTokenResult startToken(const CXCursor &cursor) override;
    bool endToken(const CXCursor &cursor) override;

    FileModelItem dom() const;

    QStringList rejectedTypes() const;

private:
    BuilderPrivate *d;
};

} // namespace clang

#endif // CLANGBUILDER_H
