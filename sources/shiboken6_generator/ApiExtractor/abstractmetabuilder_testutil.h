// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETABUILDER_TESTUTIL_H
#define ABSTRACTMETABUILDER_TESTUTIL_H

#include "clangparser/compilersupport.h"

class _FileModelItem;
class AbstractMetaBuilder;

#include <memory>

namespace TestUtil
{
    std::shared_ptr<_FileModelItem>
        buildDom(const char *cppCode, bool silent = true,
                 LanguageLevel languageLevel = LanguageLevel::Default);

    std::unique_ptr<AbstractMetaBuilder>
        parse(const char *cppCode, const char *xmlCode, bool silent = true,
              const QString &apiVersion = {}, const QStringList &dropTypeEntries = {},
              LanguageLevel languageLevel = LanguageLevel::Default);

} // namespace TestUtil

#endif // ABSTRACTMETABUILDER_TESTUTIL_H
