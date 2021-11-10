project(libpyside)

set(libpyside_libraries Qt::Core Qt::CorePrivate)

set(libpyside_SRC
    class_property.cpp
    dynamicqmetaobject.cpp
    feature_select.cpp
    signalmanager.cpp
    globalreceiverv2.cpp
    pysideclassinfo.cpp
    pysideqenum.cpp
    pysidemetafunction.cpp
    pysidesignal.cpp
    pysideslot.cpp
    pysideproperty.cpp
    pysideqflags.cpp
    pysideweakref.cpp
    pyside.cpp
    pyside_numpy.cpp
    pysidestaticstrings.cpp
)

qt6_add_resources(libpyside_SRC libpyside.qrc)

# Add python files to project explorer in Qt Creator, when opening the CMakeLists.txt as a project,
# so you can look up python files with the Locator.
macro(add_other_files)
     foreach(_it ${ARGN})
         if(NOT IS_DIRECTORY ${_it})
             get_filename_component(name ${_it} NAME)
             if(NOT ${_it} MATCHES "^/\\\\..*$;~$")
                 set_source_files_properties(${_it} PROPERTIES HEADER_FILE_ONLY TRUE)
             endif()
         endif()
     endforeach()
endmacro()

# Test files.
file(GLOB_RECURSE pyside_folder_py_files "../*.py")

# Mostly for setup.py.
file(GLOB setup_folder_py_files "../../../*.py")

set(other_files ${pyside_folder_py_files} ${setup_folder_py_files})
add_other_files(${other_files})

add_library(pyside6 SHARED ${libpyside_SRC} ${other_files})
add_library(PySide6::pyside6 ALIAS pyside6)

target_include_directories(pyside6 PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  $<INSTALL_INTERFACE:include/PySide6>
)

if (PYSIDE_NUMPY_SUPPORT AND NOT "${NUMPY_INCLUDE_DIR}" STREQUAL "")
    message(STATUS "Enabling experimental numpy support in libpyside.")
    target_include_directories(pyside6 PRIVATE ${NUMPY_INCLUDE_DIR})
    target_compile_definitions(pyside6 PRIVATE -DHAVE_NUMPY
                                       PRIVATE -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION)

else()
    message(STATUS "Disabled experimental numpy support in libpyside.")
endif()

target_link_libraries(pyside6
                      PRIVATE Shiboken6::libshiboken ${libpyside_libraries})

set_target_properties(pyside6 PROPERTIES
                      VERSION ${BINDING_API_VERSION}
                      SOVERSION "${PYSIDE_SO_VERSION}"
                      OUTPUT_NAME "pyside6${pyside6_SUFFIX}${SHIBOKEN_PYTHON_SHARED_LIBRARY_SUFFIX}"
                      DEFINE_SYMBOL BUILD_LIBPYSIDE)

set_property(TARGET pyside6 PROPERTY CXX_STANDARD 17)

if(PYSIDE_QT_CONF_PREFIX)
    set_property(SOURCE pyside.cpp
                 APPEND
                 PROPERTY COMPILE_DEFINITIONS
                 PYSIDE_QT_CONF_PREFIX=${PYSIDE_QT_CONF_PREFIX})
endif()

#
# install stuff
#

set(libpyside_HEADERS
    class_property.h
    dynamicqmetaobject.h
    feature_select.h
    pysideclassinfo.h
    pysideqenum.h
    pysidemacros.h
    signalmanager.h
    pyside.h
    pysidestaticstrings.h
    pysidemetafunction.h
    pysidesignal.h
    pysideproperty.h
    pysideqflags.h
    pysideweakref.h
)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(LIBRARY_OUTPUT_SUFFIX ${CMAKE_DEBUG_POSTFIX})
else()
    set(LIBRARY_OUTPUT_SUFFIX ${CMAKE_RELEASE_POSTFIX})
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D QT_NO_CAST_FROM_ASCII -D QT_NO_CAST_TO_ASCII")

# create pkg-config file
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/pyside6.pc.in"
               "${CMAKE_CURRENT_BINARY_DIR}/pyside6${pyside6_SUFFIX}.pc" @ONLY)

# for creating cmake-config files
include(CMakePackageConfigHelpers)

# Build-tree / super project package config file.
set(PYSIDE_PYTHONPATH "${pysidebindings_BINARY_DIR}/PySide6")
set(PYSIDE_TYPESYSTEMS "${pysidebindings_SOURCE_DIR}/PySide6/templates/")
set(PYSIDE_GLUE "${pysidebindings_SOURCE_DIR}/PySide6/glue")

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/PySide6Config-spec.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/PySide6Config${SHIBOKEN_PYTHON_CONFIG_SUFFIX}.cmake"
     INSTALL_DESTINATION "${CMAKE_CURRENT_BINARY_DIR}"
     PATH_VARS PYSIDE_PYTHONPATH PYSIDE_TYPESYSTEMS PYSIDE_GLUE
     INSTALL_PREFIX "${CMAKE_CURRENT_BINARY_DIR}"
)

set(PYSIDE_PYTHONPATH "${PYTHON_SITE_PACKAGES}/PySide6")
set(PYSIDE_TYPESYSTEMS "${CMAKE_INSTALL_PREFIX}/share/PySide6${pyside6_SUFFIX}/typesystems")
set(PYSIDE_GLUE "${CMAKE_INSTALL_PREFIX}/share/PySide6${pyside6_SUFFIX}/glue")

# Install-tree / relocatable package config file.
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/PySide6Config-spec.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/install/PySide6Config${SHIBOKEN_PYTHON_CONFIG_SUFFIX}.cmake"
     INSTALL_DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6-${BINDING_API_VERSION}"
     PATH_VARS PYSIDE_PYTHONPATH PYSIDE_TYPESYSTEMS PYSIDE_GLUE
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/PySide6Config.cmake.in"
               "${CMAKE_CURRENT_BINARY_DIR}/PySide6Config.cmake" @ONLY)
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/PySide6ConfigVersion.cmake.in"
               "${CMAKE_CURRENT_BINARY_DIR}/PySide6ConfigVersion.cmake" @ONLY)

install(FILES ${libpyside_HEADERS}
        DESTINATION include/${BINDING_NAME}${pyside6_SUFFIX})

install(TARGETS pyside6 EXPORT PySide6Targets
                        LIBRARY DESTINATION "${LIB_INSTALL_DIR}"
                        ARCHIVE DESTINATION "${LIB_INSTALL_DIR}"
                        RUNTIME DESTINATION bin)
install(EXPORT PySide6Targets NAMESPACE PySide6::
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6-${BINDING_API_VERSION}")

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/pyside6${pyside6_SUFFIX}.pc"
        DESTINATION "${LIB_INSTALL_DIR}/pkgconfig")

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/PySide6Config.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6-${BINDING_API_VERSION}")

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/install/PySide6Config${SHIBOKEN_PYTHON_CONFIG_SUFFIX}.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6-${BINDING_API_VERSION}")

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/PySide6ConfigVersion.cmake"
        DESTINATION "${LIB_INSTALL_DIR}/cmake/PySide6-${BINDING_API_VERSION}")
