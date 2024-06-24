#!/bin/bash
# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

if [ ! -d "/Users/qt/python311/bin" ]; then
    cd /Users/qt/work
    curl -O https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tar.xz
    if [ $? -ne 0 ]; then
        echo "Failed to download Python source code."
        exit 1
    fi

    tar xJf Python-3.11.9.tar.xz
    if [ $? -ne 0 ]; then
        echo "Failed to extract Python source code."
        exit 1
    fi

    cd Python-3.11.9/
    ./configure --prefix=/Users/qt/python311 --with-openssl=/usr/local/opt/openssl --enable-optimizations
    if [ $? -ne 0 ]; then
        echo "Failed to configure Python."
        exit 1
    fi
    make
    if [ $? -ne 0 ]; then
        echo "Failed to compile Python."
        exit 1
    fi
    make install
    if [ $? -ne 0 ]; then
        echo "Failed to install Python."
        exit 1
    fi
fi
