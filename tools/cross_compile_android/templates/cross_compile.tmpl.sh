#!/bin/bash
# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
set -x -e
export HOST_ARCH={{ plat_name }}-linux-android
export TOOLCHAIN={{ ndk_path }}/toolchains/llvm/prebuilt/linux-x86_64/bin
export TOOL_PREFIX=$TOOLCHAIN/$HOST_ARCH
export PLATFORM_API={{ api_level }}
export CXX=${TOOL_PREFIX}${PLATFORM_API}-clang++
export CPP="${TOOL_PREFIX}${PLATFORM_API}-clang++ -E"
export AR=$TOOLCHAIN/llvm-ar
export RANLIB=$TOOLCHAIN/llvm-ranlib
export CC=$TOOL_PREFIX${PLATFORM_API}-clang
export LD=$TOOLCHAIN/ld
export READELF=$TOOLCHAIN/llvm-readelf
export CFLAGS='-fPIC -DANDROID'
./configure --host=$HOST_ARCH --target=$HOST_ARCH --build=x86_64-pc-linux-gnu --enable-shared \
--enable-ipv6 ac_cv_file__dev_ptmx=yes ac_cv_file__dev_ptc=no --without-ensurepip \
ac_cv_little_endian_double=yes
make BLDSHARED="$CC -shared" CROSS-COMPILE=$TOOL_PREFIX- CROSS_COMPILE_TARGET=yes
make install BLDSHARED="$CC -shared" CROSS-COMPILE=$TOOL_PREFIX- \
CROSS_COMPILE_TARGET=yes prefix={{ android_py_install_path_prefix }}/Python-$HOST_ARCH/_install
