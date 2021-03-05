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

#include "gilstate.h"

namespace Shiboken
{

GilState::GilState()
{
    if (Py_IsInitialized()) {
        m_gstate = PyGILState_Ensure();
        m_locked = true;
    }
}

GilState::~GilState()
{
    release();
}

void GilState::release()
{
    if (m_locked && Py_IsInitialized()) {
        PyGILState_Release(m_gstate);
        m_locked = false;
    }
}

// Abandon the lock: Only for special situations, like termination of a
// POSIX thread (PYSIDE 1282).
void GilState::abandon()
{
    m_locked = false;
}

} // namespace Shiboken

