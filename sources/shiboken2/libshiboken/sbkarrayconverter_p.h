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
