# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(smart)

set(smart_TYPESYSTEM
${CMAKE_CURRENT_SOURCE_DIR}/typesystem_smart.xml
)

set(smart_SRC
${CMAKE_CURRENT_BINARY_DIR}/smart/smart_module_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/obj_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/integer_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/sharedptr_obj_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/sharedptr_integer_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/registry_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/smart_integer2_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/sharedptr_integer2_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/stdsharedptrtestbench_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/stdsharedptrvirtualmethodtester_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/std_shared_ptr_integer_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/std_shared_ptr_int_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/std_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/std_optional_int_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/std_optional_integer_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/std_unique_ptr_integer_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/std_unique_ptr_integer2_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/std_unique_ptr_int_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/stdoptionaltestbench_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/stduniqueptrtestbench_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/stduniqueptrvirtualmethodtester_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/smart/test_wrapper.cpp
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/smart-binding.txt.in"
               "${CMAKE_CURRENT_BINARY_DIR}/smart-binding.txt" @ONLY)

shiboken_get_tool_shell_wrapper(shiboken tool_wrapper)

add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/mjb_rejected_classes.log"
    BYPRODUCTS ${smart_SRC}
    COMMAND
        ${tool_wrapper}
        $<TARGET_FILE:Shiboken6::shiboken6>
        --project-file=${CMAKE_CURRENT_BINARY_DIR}/smart-binding.txt
        ${GENERATOR_EXTRA_FLAGS}
    DEPENDS ${smart_TYPESYSTEM} ${CMAKE_CURRENT_SOURCE_DIR}/global.h Shiboken6::shiboken6
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running generator for 'smart' test binding..."
)

add_library(smart MODULE ${smart_SRC})
target_include_directories(smart PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(smart PUBLIC libsmart libshiboken)
set_property(TARGET smart PROPERTY PREFIX "")
set_property(TARGET smart PROPERTY OUTPUT_NAME "smart${PYTHON_EXTENSION_SUFFIX}")

if(WIN32)
    set_property(TARGET smart PROPERTY SUFFIX ".pyd")
endif()

create_generator_target(smart)
