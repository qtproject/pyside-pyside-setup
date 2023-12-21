# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

# toolchain file to cross compile Qt for Python wheels for Android
cmake_minimum_required(VERSION 3.23)
include_guard(GLOBAL)
set(CMAKE_SYSTEM_NAME Android)
{% if plat_name == "armv7a" -%}
set(CMAKE_SYSTEM_PROCESSOR armv7-a)
{% else %}
set(CMAKE_SYSTEM_PROCESSOR {{ plat_name }})
{% endif %}
set(CMAKE_ANDROID_API {{ api_level }})
set(CMAKE_ANDROID_NDK {{ ndk_path }})
set(CMAKE_ANDROID_ARCH_ABI {{ android_abi }})
set(CMAKE_ANDROID_NDK_TOOLCHAIN_VERSION clang)
set(CMAKE_ANDROID_STL_TYPE c++_shared)
if(NOT DEFINED ANDROID_PLATFORM AND NOT DEFINED ANDROID_NATIVE_API_LEVEL)
    set(ANDROID_PLATFORM "android-{{ api_level }}" CACHE STRING "")
endif()
set(ANDROID_SDK_ROOT {{ sdk_path }})
{% if plat_name == "armv7a" -%}
set(_TARGET_NAME_ENDING "eabi{{ api_level }}")
{% else %}
set(_TARGET_NAME_ENDING "{{ api_level }}")
{% endif %}
set(QT_COMPILER_FLAGS "--target={{ plat_name }}-linux-android${_TARGET_NAME_ENDING} \
                       -fomit-frame-pointer \
                       -march={{ gcc_march }} \
                       -msse4.2 \
                       -mpopcnt \
                       -m{{ plat_bits }} \
                       -fPIC \
                       -I{{ target_python_path }}/include/python{{ python_version }} \
                       -Wno-unused-command-line-argument")
set(QT_COMPILER_FLAGS_RELEASE "-O2 -pipe")

# FIXME
# https://gitlab.kitware.com/cmake/cmake/-/issues/23670
# The CMake Android toolchain does not allow RPATHS. Hence CMAKE_INSTALL_RPATH does not work.
# Currently the linker flags are set directly as -Wl,-rpath='$ORIGIN' -Wl,-rpath='$ORIGIN/Qt/lib'
# set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
# set(CMAKE_INSTALL_RPATH "$ORIGIN")

set(QT_LINKER_FLAGS "-Wl,-O1 -Wl,--hash-style=gnu -Wl,-rpath='$ORIGIN' -Wl,-rpath='$ORIGIN/Qt/lib' \
                     -Wl,--as-needed -L{{ qt_install_path }}/android_{{ qt_plat_name }}/lib \
                     -L{{ qt_install_path }}/android_{{ qt_plat_name }}/plugins/platforms \
                     -L{{ target_python_path }}/lib \
                     -lpython{{ python_version }}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

add_compile_definitions(ANDROID)

include(CMakeInitializeConfigs)
function(cmake_initialize_per_config_variable _PREFIX _DOCSTRING)
    if (_PREFIX MATCHES "CMAKE_(C|CXX|ASM)_FLAGS")
        set(CMAKE_${CMAKE_MATCH_1}_FLAGS_INIT "${QT_COMPILER_FLAGS}")
        foreach (config DEBUG RELEASE MINSIZEREL RELWITHDEBINFO)
        if (DEFINED QT_COMPILER_FLAGS_${config})
            set(CMAKE_${CMAKE_MATCH_1}_FLAGS_${config}_INIT "${QT_COMPILER_FLAGS_${config}}")
        endif()
        endforeach()
    endif()
    if (_PREFIX MATCHES "CMAKE_(SHARED|MODULE|EXE)_LINKER_FLAGS")
        foreach (config SHARED MODULE EXE)
        set(CMAKE_${config}_LINKER_FLAGS_INIT "${QT_LINKER_FLAGS}")
        endforeach()
    endif()
    _cmake_initialize_per_config_variable(${ARGV})
endfunction()
