/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef SBKENUM_P_H
#define SBKENUM_P_H

#include "sbkpython.h"
#include "shibokenmacros.h"

struct SbkEnumTypePrivate
{
    SbkConverter *converter;
    const char *cppName;
    PyTypeObject *replacementType;
};

extern "C" {

/// PYSIDE-1735: Pass on the Python enum/flag information.
LIBSHIBOKEN_API void initEnumFlagsDict(PyTypeObject *type);

/// PYSIDE-1735: Patching the Enum / Flags implementation. Remove in 6.4
LIBSHIBOKEN_API PyTypeObject *morphLastEnumToPython();
LIBSHIBOKEN_API PyTypeObject *mapFlagsToSameEnum(PyTypeObject *FType, PyTypeObject *EType);

/// PYSIDE-1735: Make sure that we can import the Python enum implementation.
LIBSHIBOKEN_API PyTypeObject *getPyEnumMeta();
/// PYSIDE-1735: Helper function supporting QEnum
LIBSHIBOKEN_API int enumIsFlag(PyObject *ob_enum);
/// PYSIDE-1735: Helper function to ask what enum we are using
LIBSHIBOKEN_API bool usingNewEnum();

}

namespace Shiboken { namespace Enum {

enum : int {
    ENOPT_OLD_ENUM        = 0x00,
    ENOPT_NEW_ENUM        = 0x01,
    ENOPT_INHERIT_INT     = 0x02,
    ENOPT_GLOBAL_SHORTCUT = 0x04,
    ENOPT_SCOPED_SHORTCUT = 0x08,
    ENOPT_NO_FAKESHORTCUT = 0x10,
    ENOPT_NO_FAKERENAMES  = 0x20,
    ENOPT_NO_ZERODEFAULT  = 0x40,
    ENOPT_NO_MISSING      = 0x80,
};

LIBSHIBOKEN_API extern int enumOption;

}}

#endif // SBKENUM_P_H
