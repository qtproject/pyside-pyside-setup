# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

project(shibokengenerator)
set(package_name "Shiboken6Tools")

set(CMAKE_AUTOMOC ON)

if(NOT (Qt${QT_MAJOR_VERSION}Core_FOUND AND Python_Interpreter_FOUND))
    message(WARNING "Some dependencies were not found: shiboken6 generator compilation disabled!")
    return()
endif()

set(shiboken6_SRC
defaultvalue.cpp defaultvalue.h
generator.cpp generator.h
generatorcontext.cpp generatorcontext.h
main.cpp
shiboken/configurablescope.h
shiboken/cppgenerator.cpp shiboken/cppgenerator.h
shiboken/cppgenerator_container.cpp
shiboken/cppgenerator_smartpointer.cpp
shiboken/ctypenames.h
shiboken/generatorargument.cpp shiboken/generatorargument.h shiboken/generatorstrings.h
shiboken/headergenerator.cpp shiboken/headergenerator.h
shiboken/overloaddata.cpp shiboken/overloaddata.h
shiboken/pytypenames.h
shiboken/shibokengenerator.cpp shiboken/shibokengenerator.h
)

find_libclang()

if(${STANDALONE})
        list(APPEND CMAKE_INSTALL_RPATH ${base}/Qt/lib)
else()
        list(APPEND CMAKE_INSTALL_RPATH ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_LIBS}
             ${libclang_lib_dir})
endif()

add_executable(shiboken6 ${shiboken6_SRC})
add_executable(Shiboken6::shiboken6 ALIAS shiboken6)
add_dependencies(shiboken6 apiextractor)

set_target_properties(shiboken6 PROPERTIES OUTPUT_NAME shiboken6${shiboken6_SUFFIX})
target_include_directories(shiboken6 PRIVATE
                    ${CMAKE_CURRENT_SOURCE_DIR}/shiboken
                    ${CMAKE_CURRENT_SOURCE_DIR}/qtdoc
                    ${CMAKE_CURRENT_SOURCE_DIR}
                    ${CMAKE_CURRENT_BINARY_DIR}
                    ${apiextractor_SOURCE_DIR}
                    )
target_link_libraries(shiboken6 apiextractor Qt::Core)
if (NOT DISABLE_DOCSTRINGS)
    target_sources(shiboken6 PRIVATE
                   qtdoc/qtdocgenerator.cpp qtdoc/qtdocgenerator.h
                   qtdoc/qtxmltosphinx.cpp qtdoc/qtxmltosphinx.h
                   qtdoc/qtxmltosphinxinterface.h
                   qtdoc/rstformat.h)
    target_compile_definitions(shiboken6 PUBLIC DOCSTRINGS_ENABLED QT_LEAN_HEADERS=1)
endif()

configure_file(shibokenconfig.h.in "${CMAKE_CURRENT_BINARY_DIR}/shibokenconfig.h" @ONLY)

install(TARGETS shiboken6
        EXPORT "${package_name}Targets"
        DESTINATION "bin")
install(EXPORT "${package_name}Targets"
        NAMESPACE "Shiboken6::"
        DESTINATION ${LIB_INSTALL_DIR}/cmake/${package_name})

set(shiboken_generator_package_name "shiboken6_generator")

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/_config.py.in"
               "${CMAKE_CURRENT_BINARY_DIR}/_config.py" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/_config.py"
        DESTINATION "${PYTHON_SITE_PACKAGES}/${shiboken_generator_package_name}")

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/__init__.py.in"
               "${CMAKE_CURRENT_BINARY_DIR}/__init__.py" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/__init__.py"
       DESTINATION "${PYTHON_SITE_PACKAGES}/${shiboken_generator_package_name}")

# shiboken6 setuptools entry point
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/../shiboken_tool.py
        DESTINATION bin
        PERMISSIONS
        OWNER_EXECUTE OWNER_WRITE OWNER_READ
        GROUP_EXECUTE GROUP_READ
        WORLD_EXECUTE WORLD_READ)

# Use absolute path instead of relative path, to avoid ninja build errors due to
# duplicate file dependency inconsistency.
set(shiboken_version_relative_path "${CMAKE_CURRENT_SOURCE_DIR}/../shiboken_version.py")
get_filename_component(shiboken_version_path ${shiboken_version_relative_path} ABSOLUTE)
configure_file("${shiboken_version_path}"
               "${CMAKE_CURRENT_BINARY_DIR}/_git_shiboken_generator_version.py" @ONLY)

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/_git_shiboken_generator_version.py"
        DESTINATION "${PYTHON_SITE_PACKAGES}/${shiboken_generator_package_name}")

include(CMakePackageConfigHelpers)

# Single build-tree and install-tree Config file. There's no need for separate ones because we
# don't specify any PATH_VARS, so the relative path of PACKAGE_PREFIX_DIR does not really matter.
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/../data/${package_name}Config.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/${package_name}Config.cmake"
     INSTALL_DESTINATION "${LIB_INSTALL_DIR}/cmake/${package_name}"
)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/${package_name}ConfigVersion.cmake"
    VERSION "${shiboken6_VERSION}"
    COMPATIBILITY AnyNewerVersion
    ARCH_INDEPENDENT
)

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/${package_name}Config.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/${package_name}")

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/${package_name}ConfigVersion.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/${package_name}")
