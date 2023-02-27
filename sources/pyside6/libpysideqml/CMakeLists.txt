# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(libpysideqml_libraries Qt::Core Qt::CorePrivate Qt::Qml Qt::QmlPrivate)

set(libpysideqml_HEADERS # installed below
    pysideqmlattached.h
    pysideqmlattached_p.h
    pysideqmlextended_p.h
    pysideqmlforeign_p.h
    pysideqml.h
    pysideqmllistproperty_p.h
    pysideqmlmacros.h
    pysideqmlmetacallerror_p.h
    pysideqmlnamedelement_p.h
    pysideqmlregistertype.h
    pysideqmlregistertype_p.h
    pysideqmltypeinfo_p.h
    pysideqmluncreatable.h
)

set(libpysideqml_SRC
    pysideqml.cpp
    pysideqmlattached.cpp
    pysideqmlforeign.cpp
    pysideqmlextended.cpp
    pysideqmlregistertype.cpp
    pysideqmlmetacallerror.cpp
    pysideqmllistproperty.cpp
    pysideqmlnamedelement.cpp
    pysideqmluncreatable.cpp
    pysideqmltypeinfo.cpp
    ${libpysideqml_HEADERS}
)

# Hack for // https://github.com/python/cpython/issues/86286 causes issues
set_source_files_properties(
    pysideqmlmetacallerror.cpp PROPERTIES SKIP_UNITY_BUILD_INCLUSION ON
)

add_library(pyside6qml SHARED ${libpysideqml_SRC} ${other_files})
add_library(PySide6::pyside6qml ALIAS pyside6qml)

target_include_directories(pyside6qml PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  $<INSTALL_INTERFACE:include/PySide6Qml>
)

target_compile_definitions(pyside6qml PRIVATE -DQT_LEAN_HEADERS=1 -DQT_NO_KEYWORDS=1)

target_link_libraries(pyside6qml
                      PRIVATE PySide6::pyside6 Shiboken6::libshiboken ${libpysideqml_libraries})

set_target_properties(pyside6qml PROPERTIES
                      VERSION ${BINDING_API_VERSION}
                      SOVERSION "${PYSIDE_SO_VERSION}"
                      OUTPUT_NAME "pyside6qml${pyside6_SUFFIX}${SHIBOKEN_PYTHON_SHARED_LIBRARY_SUFFIX}"
                      DEFINE_SYMBOL BUILD_LIBPYSIDEQML)

target_compile_definitions(pyside6qml PRIVATE -DQT_LEAN_HEADERS=1)

set_property(TARGET pyside6 PROPERTY CXX_STANDARD 17)

if(PYSIDE_QT_CONF_PREFIX)
    set_property(SOURCE pysideqml.cpp
                 APPEND
                 PROPERTY COMPILE_DEFINITIONS
                 PYSIDE_QT_CONF_PREFIX=${PYSIDE_QT_CONF_PREFIX})
endif()

#
# install stuff
#

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(LIBRARY_OUTPUT_SUFFIX ${CMAKE_DEBUG_POSTFIX})
else()
    set(LIBRARY_OUTPUT_SUFFIX ${CMAKE_RELEASE_POSTFIX})
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D QT_NO_CAST_FROM_ASCII -D QT_NO_CAST_TO_ASCII")

qfp_strip_library("pyside6qml")

# Install-tree / relocatable package config file.
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/PySide6QmlConfig-spec.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/install/PySide6QmlConfig${SHIBOKEN_PYTHON_CONFIG_SUFFIX}.cmake"
     INSTALL_DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml"
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/PySide6QmlConfig.cmake.in"
               "${CMAKE_CURRENT_BINARY_DIR}/PySide6QmlConfig.cmake" @ONLY)
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/PySide6QmlConfigVersion.cmake.in"
               "${CMAKE_CURRENT_BINARY_DIR}/PySide6QmlConfigVersion.cmake" @ONLY)

install(FILES ${libpysideqml_HEADERS}
        DESTINATION include/${BINDING_NAME}${pyside6qml_SUFFIX})

install(TARGETS pyside6qml EXPORT PySide6QmlTargets
                           LIBRARY DESTINATION "${LIB_INSTALL_DIR}"
                           ARCHIVE DESTINATION "${LIB_INSTALL_DIR}"
                           RUNTIME DESTINATION bin)
install(EXPORT PySide6QmlTargets NAMESPACE PySide6Qml::
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml")

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/PySide6QmlConfig.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml")

install(FILES
        "${CMAKE_CURRENT_BINARY_DIR}/install/PySide6QmlConfig${SHIBOKEN_PYTHON_CONFIG_SUFFIX}.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml")

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/PySide6QmlConfigVersion.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml")
