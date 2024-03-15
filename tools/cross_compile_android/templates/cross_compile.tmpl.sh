#!/bin/bash
# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
set -x -e
export HOST_ARCH={{ plat_name }}-linux-android
export TOOLCHAIN={{ ndk_path }}/toolchains/llvm/prebuilt/{{ host_platform_name }}-x86_64/bin
export TOOL_PREFIX=$TOOLCHAIN/$HOST_ARCH
export PLATFORM_API={{ api_level }}
{% if plat_name == "armv7a" -%}
export CXX=${TOOL_PREFIX}eabi${PLATFORM_API}-clang++
export CPP="${TOOL_PREFIX}eabi${PLATFORM_API}-clang++ -E"
export CC=${TOOL_PREFIX}eabi${PLATFORM_API}-clang
{% else %}
export CXX=${TOOL_PREFIX}${PLATFORM_API}-clang++
export CPP="${TOOL_PREFIX}${PLATFORM_API}-clang++ -E"
export CC=${TOOL_PREFIX}${PLATFORM_API}-clang
{% endif %}
export AR=$TOOLCHAIN/llvm-ar
export RANLIB=$TOOLCHAIN/llvm-ranlib
export LD=$TOOLCHAIN/ld
export READELF=$TOOLCHAIN/llvm-readelf
export CFLAGS='-fPIC -DANDROID'
./configure --host=$HOST_ARCH --target=$HOST_ARCH --build={{ host_system_name }} \
--with-build-python={{ host_python_path }}  --enable-shared \
--enable-ipv6 ac_cv_file__dev_ptmx=yes ac_cv_file__dev_ptc=no --without-ensurepip \
ac_cv_little_endian_double=yes
make BLDSHARED="$CC -shared" CROSS-COMPILE=$TOOL_PREFIX- CROSS_COMPILE_TARGET=yes \
INSTSONAME=libpython{{ python_version }}.so
make install prefix={{ android_py_install_path_prefix }}/Python-$HOST_ARCH/_install
