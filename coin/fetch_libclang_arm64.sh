#!/bin/bash
# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Download the file
wget -q https://download.qt.io/development_releases/prebuilt/libclang/libclang-release_18.1.7-based-linux-Debian-11.6-gcc10.2-arm64.7z
if [ $? -ne 0 ]; then
    echo "Error: Failed to download libclang archive" >&2
    exit 1
fi

# Unzip the contents to /home/qt
7z x libclang-release_18.1.7-based-linux-Debian-11.6-gcc10.2-arm64.7z -o/home/qt
if [ $? -ne 0 ]; then
    echo "Error: Failed to extract libclang archive" >&2
    exit 1
fi

# Remove the 7z file after extraction
rm libclang-release_18.1.7-based-linux-Debian-11.6-gcc10.2-arm64.7z
if [ $? -ne 0 ]; then
    echo "Error: Failed to remove libclang archive" >&2
    exit 1
fi
