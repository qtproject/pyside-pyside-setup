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

#ifndef THREADSTATESAVER_H
#define THREADSTATESAVER_H

#include "sbkpython.h"
#include <shibokenmacros.h>

namespace Shiboken
{

class LIBSHIBOKEN_API ThreadStateSaver
{
public:
    ThreadStateSaver(const ThreadStateSaver &) = delete;
    ThreadStateSaver(ThreadStateSaver &&) = delete;
    ThreadStateSaver &operator=(const ThreadStateSaver &) = delete;
    ThreadStateSaver &operator=(ThreadStateSaver &&) = delete;

    ThreadStateSaver();
    ~ThreadStateSaver();
    void save();
    void restore();
private:
    PyThreadState *m_threadState = nullptr;
};

} // namespace Shiboken

#endif // THREADSTATESAVER_H

