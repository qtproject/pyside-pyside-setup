# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

# toolchain file to cross compile Qt for Python wheels for iOS

# Include Qt's own iOS kit toolchain file.
set(_qt_ios_toolchain "{{ qt_cmake_dir }}/Qt6/qt.toolchain.cmake")
include("${_qt_ios_toolchain}")

set(CMAKE_SYSTEM_PROCESSOR {{ arch }})

{% if simulator %}
set(CMAKE_OSX_SYSROOT iphonesimulator)
{% else %}
set(CMAKE_OSX_SYSROOT iphoneos)
{% endif %}
set(CMAKE_OSX_ARCHITECTURES "{{ arch }}")

set(BUILD_SHARED_LIBS OFF CACHE BOOL "iOS requires static libs" FORCE)

set(_PYTHON_SLICE "{{ python_xcframework }}/{{ python_slice_dir }}")

set(Python_INCLUDE_DIR  "${_PYTHON_SLICE}/include/python{{ python_version }}"        CACHE PATH "")
set(Python_LIBRARY      "${_PYTHON_SLICE}/lib/libpython{{ python_version }}.dylib"   CACHE FILEPATH "")
set(PYTHON_EXECUTABLE   "{{ host_python }}"       CACHE FILEPATH "")

string(REPLACE "." "" _PYTHON_VERSION_NODOT "{{ python_version }}")
{% if simulator %}
set(Python_SOABI "cpython-${_PYTHON_VERSION_NODOT}-iphonesimulator" CACHE STRING "")
{% else %}
set(Python_SOABI "cpython-${_PYTHON_VERSION_NODOT}-iphoneos" CACHE STRING "")
{% endif %}
