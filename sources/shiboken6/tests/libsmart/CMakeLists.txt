# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(libsmart)

set(libsmart_SRC
libsmartmacros.h
smart.cpp smart.h
smart_integer.h
smart_obj.h
smart_registry.h
smart_sharedptr.h
smart_test.h
stdoptionaltestbench.cpp stdoptionaltestbench.h
stdsharedptrtestbench.cpp stdsharedptrtestbench.h
stduniqueptrtestbench.cpp stduniqueptrtestbench.h
)

add_library(libsmart SHARED ${libsmart_SRC})
target_include_directories(libsmart PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_definitions(libsmart PRIVATE LIBSMART_BUILD)
set_property(TARGET libsmart PROPERTY PREFIX "")

