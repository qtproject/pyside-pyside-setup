# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(libminimal)

set(libminimal_SRC
containeruser.cpp containeruser.h
libminimalmacros.h
listuser.cpp listuser.h
minbool.h
obj.cpp obj.h
spanuser.cpp spanuser.h
typedef.cpp typedef.h
val.h
)

add_library(libminimal SHARED ${libminimal_SRC})
target_include_directories(libminimal PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_definitions(libminimal PRIVATE LIBMINIMAL_BUILD)
set_property(TARGET libminimal PROPERTY PREFIX "")

