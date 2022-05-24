// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "threadstatesaver.h"

namespace Shiboken
{

ThreadStateSaver::ThreadStateSaver() = default;

ThreadStateSaver::~ThreadStateSaver()
{
    restore();
}

void ThreadStateSaver::save()
{
    if (Py_IsInitialized())
        m_threadState = PyEval_SaveThread();
}

void ThreadStateSaver::restore()
{
    if (m_threadState) {
        PyEval_RestoreThread(m_threadState);
        m_threadState = nullptr;
    }
}

} // namespace Shiboken

