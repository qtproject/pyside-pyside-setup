# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(shibokenmodule)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/shibokenmodule.txt.in"
               "${CMAKE_CURRENT_BINARY_DIR}/shibokenmodule.txt" @ONLY)

set(sample_SRC ${CMAKE_CURRENT_BINARY_DIR}/Shiboken/shiboken_module_wrapper.cpp)

set(shibokenmodule_TYPESYSTEM ${CMAKE_CURRENT_SOURCE_DIR}/typesystem_shiboken.xml)

shiboken_get_tool_shell_wrapper(shiboken tool_wrapper)

add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/mjb_rejected_classes.log"
    BYPRODUCTS ${sample_SRC}
    COMMAND
        ${tool_wrapper}
        $<TARGET_FILE:Shiboken6::shiboken6>
        --project-file=${CMAKE_CURRENT_BINARY_DIR}/shibokenmodule.txt
        ${GENERATOR_EXTRA_FLAGS}
    DEPENDS ${shibokenmodule_TYPESYSTEM}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running generator for 'Shiboken'..."
)

add_library(shibokenmodule MODULE ${sample_SRC})
target_include_directories(shibokenmodule PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
                                                  ${CMAKE_SOURCE_DIR})
set_property(TARGET shibokenmodule PROPERTY PREFIX "")
# PYSIDE-1497: This `..` is the crucial trick to unify the path location of `Shiboken`.
set_property(TARGET shibokenmodule PROPERTY OUTPUT_NAME "../Shiboken${PYTHON_EXTENSION_SUFFIX}")

if(WIN32)
    set_property(TARGET shibokenmodule PROPERTY SUFFIX ".pyd")
endif()
target_link_libraries(shibokenmodule PUBLIC libshiboken)

create_generator_target(shibokenmodule)

qfp_strip_library("shibokenmodule")

install(TARGETS shibokenmodule DESTINATION ${PYTHON_SITE_PACKAGES}/shiboken6)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/_config.py.in"
               "${CMAKE_CURRENT_BINARY_DIR}/_config.py" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/_config.py"
        DESTINATION "${PYTHON_SITE_PACKAGES}/shiboken6")

if ("${MINIMUM_PYTHON_VERSION}" STREQUAL "")
    set(MINIMUM_PYTHON_VERSION None)
    set(MAXIMUM_PYTHON_VERSION None)
endif()

# PYSIDE-1497: This `..` is the crucial trick to unify the path location of `Shiboken`.
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/__init__.py.in"
               "${CMAKE_CURRENT_BINARY_DIR}/../__init__.py" @ONLY)
# PYSIDE-1415: Copy Shiboken.pyi into the target.
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/Shiboken.pyi"
               "${CMAKE_CURRENT_BINARY_DIR}/../Shiboken.pyi" @ONLY)
# typing support for mypy
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/py.typed.in"
               "${CMAKE_CURRENT_BINARY_DIR}/../py.typed" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/../Shiboken.pyi"
              "${CMAKE_CURRENT_BINARY_DIR}/../py.typed"
        DESTINATION "${PYTHON_SITE_PACKAGES}/shiboken6")

# PYSIDE-1497: This `..` is the crucial trick to unify the path location of `Shiboken`.
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/../__init__.py"
       DESTINATION "${PYTHON_SITE_PACKAGES}/shiboken6")

# Use absolute path instead of relative path, to avoid ninja build errors due to
# duplicate file dependency inconsistency.
set(shiboken_version_relative_path "${CMAKE_CURRENT_SOURCE_DIR}/../shiboken_version.py")
get_filename_component(shiboken_version_path ${shiboken_version_relative_path} ABSOLUTE)
configure_file("${shiboken_version_path}"
               "${CMAKE_CURRENT_BINARY_DIR}/_git_shiboken_module_version.py" @ONLY)

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/_git_shiboken_module_version.py"
        DESTINATION "${PYTHON_SITE_PACKAGES}/shiboken6")
