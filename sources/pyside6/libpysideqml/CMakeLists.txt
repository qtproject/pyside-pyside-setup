# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

find_package(Qt6 COMPONENTS Core CorePrivate Qml QmlPrivate)

set(libpysideqml_libraries Qt::Core Qt::CorePrivate Qt::Qml Qt::QmlPrivate)

set(libpysideqml_HEADERS # installed below
    pysidechange.h
    pysidecomputed_p.h
    pysidewatch_p.h
    pysideqmlattached.h
    pysideqmlattached_p.h
    pysideqmlextended_p.h
    pysideqmlforeign_p.h
    pysideqml.h
    pysideqmllistproperty_p.h
    pysideqmllistpropertymixin.h
    pysideqmlmacros.h
    pysideqmlmetacallerror_p.h
    pysideqmlnamedelement_p.h
    pysideqmlregistertype.h
    pysideqmlregistertype_p.h
    pysideqmltypeinfo_p.h
    pysideqmluncreatable.h
)

set(libpysideqml_SRC
    pysidechange.cpp
    pysidecomputed.cpp
    pysidewatch.cpp
    pysideqml.cpp
    pysideqmlattached.cpp
    pysideqmlforeign.cpp
    pysideqmlextended.cpp
    pysideqmlregistertype.cpp
    pysideqmlmetacallerror.cpp
    pysideqmllistproperty.cpp
    pysideqmllistpropertymixin.cpp
    pysideqmlnamedelement.cpp
    pysideqmluncreatable.cpp
    pysideqmltypeinfo.cpp
    ${libpysideqml_HEADERS}
)

# Hack for // https://github.com/python/cpython/issues/86286 causes issues
set_source_files_properties(
    pysideqmlmetacallerror.cpp PROPERTIES SKIP_UNITY_BUILD_INCLUSION ON
)

if(IOS)
    set(library_type STATIC)
else()
    set(library_type SHARED)
endif()
add_library(pyside6qml ${library_type} ${libpysideqml_SRC} ${other_files})
add_library(PySide6::pyside6qml ALIAS pyside6qml)

target_include_directories(pyside6qml PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
)

target_compile_definitions(pyside6qml PRIVATE -DQT_LEAN_HEADERS=1 -DQT_NO_KEYWORDS=1)

target_link_libraries(pyside6qml
                      PRIVATE PySide6::pyside6 Shiboken6::libshiboken ${libpysideqml_libraries})

set(set_props_args DEFINE_SYMBOL BUILD_LIBPYSIDEQML)
if(IOS)
    list(APPEND set_props_args OUTPUT_NAME "pyside6qml${pyside6_SUFFIX}")
else()
    list(APPEND set_props_args
        VERSION ${BINDING_API_VERSION}
        SOVERSION "${PYSIDE_SO_VERSION}"
        OUTPUT_NAME
            "pyside6qml${pyside6_SUFFIX}${SHIBOKEN_PYTHON_SHARED_LIBRARY_SUFFIX}"
    )
endif()
set_target_properties(pyside6qml PROPERTIES ${set_props_args})

target_compile_definitions(pyside6qml PRIVATE -DQT_LEAN_HEADERS=1)

set_property(TARGET pyside6qml PROPERTY CXX_STANDARD 17)

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

install(FILES ${libpysideqml_HEADERS}
        DESTINATION include/${BINDING_NAME}${pyside6qml_SUFFIX})

#built-time installation
install(TARGETS pyside6qml EXPORT PySide6Targets
                           LIBRARY DESTINATION "${LIB_INSTALL_DIR}"
                           ARCHIVE DESTINATION "${LIB_INSTALL_DIR}"
                           RUNTIME DESTINATION bin)

# install-tree or relocatable package installation
if(NOT is_pyside6_superproject_build)
    set_target_properties(pyside6qml PROPERTIES
                        VERSION ${PYSIDE_SO_VERSION})
    install(TARGETS pyside6qml EXPORT PySide6WheelTargets
                            LIBRARY DESTINATION "PySide6"
                            ARCHIVE DESTINATION "PySide6"
                            RUNTIME DESTINATION "PySide6")
endif()
