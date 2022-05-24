// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBKARRAYCONVERTER_P_H
#define SBKARRAYCONVERTER_P_H

#include "sbkconverter_p.h"
#include <vector>

extern "C"
{

typedef PythonToCppFunc (*IsArrayConvertibleToCppFunc)(PyObject *, int dim1, int dim2);
/**
 *  \internal
 *  Private structure of SbkArrayConverter.
 */

struct SbkArrayConverter
{
    std::vector<IsArrayConvertibleToCppFunc> toCppConversions;
};

} // extern "C"

#endif // SBKARRAYCONVERTER_P_H
