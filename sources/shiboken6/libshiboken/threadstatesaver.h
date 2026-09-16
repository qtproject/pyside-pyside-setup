// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef THREADSTATESAVER_H
#define THREADSTATESAVER_H

#include "sbkpython.h"
#include <shibokenmacros.h>
#include "shibokenclasshelpermacros.h"

namespace Shiboken
{

class LIBSHIBOKEN_API ThreadStateSaver
{
public:
    LIBSHIBOKEN_DISABLE_COPY_MOVE(ThreadStateSaver)

    ThreadStateSaver();
    ~ThreadStateSaver();
    void save();
    void restore();
private:
    PyThreadState *m_threadState = nullptr;
};

} // namespace Shiboken

#endif // THREADSTATESAVER_H
