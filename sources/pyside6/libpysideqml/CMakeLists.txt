set(libpysideqml_libraries Qt::Core Qt::CorePrivate Qt::Qml Qt::QmlPrivate)

set(libpysideqml_SRC
    pysideqml.cpp
    pysideqmlforeign.cpp
    pysideqmlextended.cpp
    pysideqmlregistertype.cpp
    pysideqmlmetacallerror.cpp
    pysideqmllistproperty.cpp
    pysideqmlnamedelement.cpp
    pysideqmluncreatable.cpp
    pysideqmltypeinfo.cpp
)

add_library(pyside6qml SHARED ${libpysideqml_SRC} ${other_files})
add_library(PySide6::pyside6qml ALIAS pyside6qml)

target_include_directories(pyside6qml PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  $<INSTALL_INTERFACE:include/PySide6Qml>
)

target_link_libraries(pyside6qml
                      PRIVATE PySide6::pyside6 Shiboken6::libshiboken ${libpysideqml_libraries})

set_target_properties(pyside6qml PROPERTIES
                      VERSION ${BINDING_API_VERSION}
                      SOVERSION "${PYSIDE_SO_VERSION}"
                      OUTPUT_NAME "pyside6qml${pyside6_SUFFIX}${SHIBOKEN_PYTHON_SHARED_LIBRARY_SUFFIX}"
                      DEFINE_SYMBOL BUILD_LIBPYSIDEQML)

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

set(libpysideqml_HEADERS
    pysideqmlmacros.h
    pysideqml.h
    pysideqmlregistertype.h
)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(LIBRARY_OUTPUT_SUFFIX ${CMAKE_DEBUG_POSTFIX})
else()
    set(LIBRARY_OUTPUT_SUFFIX ${CMAKE_RELEASE_POSTFIX})
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D QT_NO_CAST_FROM_ASCII -D QT_NO_CAST_TO_ASCII")

# Install-tree / relocatable package config file.
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/PySide6QmlConfig-spec.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/install/PySide6QmlConfig${SHIBOKEN_PYTHON_CONFIG_SUFFIX}.cmake"
     INSTALL_DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml-${BINDING_API_VERSION}"
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
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml-${BINDING_API_VERSION}")

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/PySide6QmlConfig.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml-${BINDING_API_VERSION}")

install(FILES
        "${CMAKE_CURRENT_BINARY_DIR}/install/PySide6QmlConfig${SHIBOKEN_PYTHON_CONFIG_SUFFIX}.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml-${BINDING_API_VERSION}")

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/PySide6QmlConfigVersion.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6Qml-${BINDING_API_VERSION}")
