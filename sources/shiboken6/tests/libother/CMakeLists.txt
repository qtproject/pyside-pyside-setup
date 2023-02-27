# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(libother)

set(libother_SRC
extendsnoimplicitconversion.h
libothermacros.h
number.cpp number.h
otherderived.cpp otherderived.h
othermultiplederived.cpp othermultiplederived.h
otherobjecttype.cpp otherobjecttype.h
othertypesystypedef.cpp othertypesystypedef.h
smartptrtester.cpp smartptrtester.h
)

add_library(libother SHARED ${libother_SRC})
target_include_directories(libother PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_definitions(libother PRIVATE LIBOTHER_BUILD)
target_link_libraries(libother PUBLIC libsample libsmart)
set_property(TARGET libother PROPERTY PREFIX "")


