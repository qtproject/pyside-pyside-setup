# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

a = 7

if a > 5:
    for f in [1, 2]:
        print(f)
elif a == 2:
    print(2)
elif not a:
    print(0)
else:
    for i in range(5):
        print(i)
    for i in range(2, 5):
        print(i)
