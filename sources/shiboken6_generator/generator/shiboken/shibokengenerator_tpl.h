// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef SHIBOKENGENERATOR_TPL_H
#define SHIBOKENGENERATOR_TPL_H

#include "shibokengenerator.h"
#include "apiextractorresult.h"
#include "abstractmetalang.h"
#include "complextypeentry.h"
#include "configurablescope.h"

#include <textstream.h>

template <class F>
bool ShibokenGenerator::writeClassCode(TextStream &s, F f) const
{
    bool result = false;
    for (const auto &cls : api().classes()){
        auto te = cls->typeEntry();
        if (shouldGenerate(te)) {
            ConfigurableScope configScope(s, te);
            result = true;
            f(s, cls);
        }
    }
    return result;
}

#endif // SHIBOKENGENERATOR_TPL_H
