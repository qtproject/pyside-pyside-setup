// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef GILSTATE_H
#define GILSTATE_H

#include <shibokenmacros.h>
#include "shibokenclasshelpermacros.h"
#include "sbkpython.h"

namespace Shiboken
{

class LIBSHIBOKEN_API GilState
{
public:
    LIBSHIBOKEN_DISABLE_COPY_MOVE(GilState)

    explicit GilState(bool acquire=true);
    ~GilState();
    void acquire();
    void release();
    void abandon();
private:
    PyGILState_STATE m_gstate;
    bool m_locked = false;
};

} // namespace Shiboken

#endif // GILSTATE_H
