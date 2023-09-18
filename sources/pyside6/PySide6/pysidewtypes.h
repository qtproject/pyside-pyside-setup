// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef __PYSIDEWTYPES__
#define __PYSIDEWTYPES__

using HWND = struct HWND__ *;
using UINT = unsigned;
using LONG = long;
using DWORD = unsigned long;
using WPARAM = UINT;
using LPARAM = LONG;

struct POINT
{
    LONG x;
    LONG y;
};

struct MSG
{
    HWND hwnd;
    UINT message;
    WPARAM wParam;
    LPARAM lParam;
    DWORD time;
    POINT pt;
};

#endif
