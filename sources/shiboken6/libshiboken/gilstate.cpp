// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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

