// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "cppgenerator.h"
#include "headergenerator.h"

EXPORT_GENERATOR_PLUGIN(new CppGenerator << new HeaderGenerator)
