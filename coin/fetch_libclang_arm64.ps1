# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Download the file

wget https://master.qt.io/development_releases/prebuilt/libclang/libclang-release_19.1.0-based-windows-vs2022_arm64.7z -o libclang.7z
# Unzip the contents to /home/qt
7z x libclang.7z -o/utils
Remove-Item libclang.7z
