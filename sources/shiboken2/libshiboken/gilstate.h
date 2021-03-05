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

#ifndef GILSTATE_H
#define GILSTATE_H

#include <shibokenmacros.h>
#include "sbkpython.h"

namespace Shiboken
{

class LIBSHIBOKEN_API GilState
{
public:
    GilState(const GilState &) = delete;
    GilState(GilState &&) = delete;
    GilState &operator=(const GilState &) = delete;
    GilState &operator=(GilState &&) = delete;

    GilState();
    ~GilState();
    void release();
    void abandon();
private:
    PyGILState_STATE m_gstate;
    bool m_locked = false;
};

} // namespace Shiboken

#endif // GILSTATE_H

