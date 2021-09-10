/****************************************************************************
**
** Copyright (C) 2018 The Qt Company Ltd.
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

#ifndef SBKPYTHON_H
#define SBKPYTHON_H

#include "sbkversion.h"
#define PyEnumMeta_Check(x) (strcmp(Py_TYPE(x)->tp_name, "EnumMeta") == 0)

// Qt's "slots" macro collides with the "slots" member variables
// used in some Python structs. For compilers that support push_macro,
// temporarily undefine it.
#if defined(slots) && (defined(__GNUC__) || defined(_MSC_VER) || defined(__clang__))
#  pragma push_macro("slots")
#  undef slots
/*
 * Python 2 has function _Py_Mangle directly in Python.h .
 * This creates wrong language binding unless we define 'extern "C"' here.
 */
extern "C" {
/*
 * Python 2 uses the "register" keyword, which is deprecated in C++ 11
 * and forbidden in C++17.
 */
#  if defined(__clang__)
#    pragma clang diagnostic push
#    pragma clang diagnostic ignored "-Wdeprecated-register"
#  endif

#  include <Python.h>

#  if defined(__clang__)
#    pragma clang diagnostic pop
#  endif
}
#  include <structmember.h>
// Now we have the usual variables from Python.h .
#  include "shibokenmacros.h"
// "pep384impl.h" may nowhere be included but in this file.
#  include "pep384impl.h"
#  pragma pop_macro("slots")

#else

extern "C" {
/*
 * Python 2 uses the "register" keyword, which is deprecated in C++ 11
 * and forbidden in C++17.
 */
#  if defined(__clang__)
#    pragma clang diagnostic push
#    pragma clang diagnostic ignored "-Wdeprecated-register"
#  endif

#  include <Python.h>

#  if defined(__clang__)
#    pragma clang diagnostic pop
#  endif
}
#  include <structmember.h>
// Now we have the usual variables from Python.h .
#  include "shibokenmacros.h"
// "pep384impl.h" may nowhere be included but in this file.
#  include "pep384impl.h"
#endif

// In Python 3, Py_TPFLAGS_DEFAULT contains Py_TPFLAGS_HAVE_VERSION_TAG,
// which will trigger the attribute cache, which is not intended in Qt for Python.
// Use a customized Py_TPFLAGS_DEFAULT by defining Py_TPFLAGS_HAVE_VERSION_TAG = 0.
#undef Py_TPFLAGS_HAVE_VERSION_TAG
#define Py_TPFLAGS_HAVE_VERSION_TAG  (0)

using SbkObjectType = PyTypeObject; // FIXME PYSIDE 7 remove

#endif
