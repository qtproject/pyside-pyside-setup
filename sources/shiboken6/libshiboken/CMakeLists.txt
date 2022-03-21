project(libshiboken)

option(ENABLE_VERSION_SUFFIX "Used to use current version in suffix to generated files. This is used to allow multiples versions installed simultaneous." FALSE)
if(ENABLE_VERSION_SUFFIX)
    set(shiboken6_SUFFIX "-${shiboken_MAJOR_VERSION}.${shiboken_MINOR_VERSION}")
else()
    set(shiboken6_SUFFIX "")
endif()

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/sbkversion.h.in"
               "${CMAKE_CURRENT_BINARY_DIR}/sbkversion.h" @ONLY)
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/embed/signature_bootstrap.py"
               "${CMAKE_CURRENT_BINARY_DIR}/embed/signature_bootstrap.py" @ONLY)

# Variable from enclosing scope.
list(TRANSFORM shiboken_python_files
     PREPEND "${CMAKE_CURRENT_SOURCE_DIR}/../shibokenmodule/files.dir/shibokensupport/"
     OUTPUT_VARIABLE embedded_shiboken_files)

if (QUIET_BUILD)
    set(embedding_option "--quiet")
else()
    set(embedding_option "")
endif()

if(SHIBOKEN_IS_CROSS_BUILD)
    set(host_python_path "${QFP_PYTHON_HOST_PATH}")
    set(use_pyc_in_embedding FALSE)
else()
    set(host_python_path "${PYTHON_EXECUTABLE}")
    if(PYTHON_LIMITED_API)
        set(use_pyc_in_embedding FALSE)
    else()
        set(use_pyc_in_embedding TRUE)
    endif()
endif()

add_custom_command(
    OUTPUT  "${CMAKE_CURRENT_BINARY_DIR}/embed/signature_bootstrap_inc.h"
    OUTPUT  "${CMAKE_CURRENT_BINARY_DIR}/embed/signature_inc.h"
    COMMAND ${host_python_path} -E
            "${CMAKE_CURRENT_SOURCE_DIR}/embed/embedding_generator.py"
            --cmake-dir "${CMAKE_CURRENT_BINARY_DIR}/embed"
            --use-pyc ${use_pyc_in_embedding}
            ${embedding_option}
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/embed/embedding_generator.py"
            "${CMAKE_CURRENT_SOURCE_DIR}/embed/signature_bootstrap.py"
            ${embedded_shiboken_files}
    )

set(libshiboken_MAJOR_VERSION ${shiboken_MAJOR_VERSION})
set(libshiboken_MINOR_VERSION ${shiboken_MINOR_VERSION})
set(libshiboken_MICRO_VERSION ${shiboken_MICRO_VERSION})
set(libshiboken_VERSION "${libshiboken_MAJOR_VERSION}.${libshiboken_MINOR_VERSION}.${libshiboken_MICRO_VERSION}")
set(libshiboken_SOVERSION "${shiboken6_library_so_version}")

set(libshiboken_SRC
basewrapper.cpp
debugfreehook.cpp
gilstate.cpp
helper.cpp
sbkarrayconverter.cpp
sbkcontainer.cpp
sbkconverter.cpp
sbkenum.cpp
sbkfeature_base.cpp
sbkmodule.cpp
sbkcppstring.cpp
sbkstring.cpp
sbkstaticstrings.cpp
sbktypefactory.cpp
bindingmanager.cpp
threadstatesaver.cpp
shibokenbuffer.cpp
pep384impl.cpp
voidptr.cpp
bufferprocs_py37.cpp

embed/signature_bootstrap_inc.h
embed/signature_inc.h

signature/signature.cpp
signature/signature_globals.cpp
signature/signature_extend.cpp
signature/signature_helper.cpp
)

if (NOT "${NUMPY_INCLUDE_DIR}" STREQUAL "")
    message(STATUS "NUMPY_INCLUDE_DIR: " ${NUMPY_INCLUDE_DIR})
    list(APPEND libshiboken_SRC sbknumpyarrayconverter.cpp)
else()
    message(STATUS "NUMPY not found")
endif()

set(APIEXTRACTOR_EXTRA_INCLUDES ${APIEXTRACTOR_EXTRA_INCLUDES} ${LIBXSLT_INCLUDE_DIR} ${LIBXML2_INCLUDE_DIR})

add_library(libshiboken SHARED ${libshiboken_SRC})
add_library(Shiboken6::libshiboken ALIAS libshiboken)

target_include_directories(libshiboken PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
  $<INSTALL_INTERFACE:include/shiboken6>
)

if (NOT "${NUMPY_INCLUDE_DIR}" STREQUAL "")
    target_include_directories(libshiboken PRIVATE ${NUMPY_INCLUDE_DIR})
    target_compile_definitions(libshiboken PRIVATE -DHAVE_NUMPY
                                           PRIVATE -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION)

endif()

if(SHIBOKEN_IS_CROSS_BUILD)
    target_compile_definitions(libshiboken PRIVATE -DSHIBOKEN_NO_EMBEDDING_PYC=1)
endif()

shiboken_compute_python_includes()
# On Windows we need to link against the python.lib import library.
# On macOS and Linux we don't link against the python shared / static library,
# the dynamic linker will pick up the python symbols at runtime automatically.
shiboken_compute_python_libraries()

if(PYTHON_LIMITED_API)
    target_compile_definitions(libshiboken PUBLIC "-DPy_LIMITED_API=0x03060000")
endif()

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(PYTHON_WITH_DEBUG)
        target_compile_definitions(libshiboken PUBLIC "-DPy_DEBUG")
    endif()
    if (PYTHON_WITH_COUNT_ALLOCS)
        target_compile_definitions(libshiboken PUBLIC "-DCOUNT_ALLOCS")
    endif()
elseif(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_definitions(libshiboken PUBLIC "-DNDEBUG")
endif()

set_target_properties(libshiboken PROPERTIES OUTPUT_NAME "shiboken6${shiboken6_SUFFIX}${PYTHON_SHARED_LIBRARY_SUFFIX}"
                                             VERSION ${libshiboken_VERSION}
                                             SOVERSION ${libshiboken_SOVERSION}
                                             DEFINE_SYMBOL BUILD_LIBSHIBOKEN)

qfp_strip_library("libshiboken")

install(FILES
        autodecref.h
        basewrapper.h
        basewrapper_p.h
        bindingmanager.h
        gilstate.h
        helper.h
        sbkarrayconverter.h
        sbkcontainer.h
        sbkconverter.h
        sbkenum.h
        sbkenum_p.h
        sbkfeature_base.h
        sbkmodule.h
        sbkstring.h
        sbkcppstring.h
        sbkstaticstrings.h
        sbktypefactory.h
        shiboken.h
        shibokenmacros.h
        threadstatesaver.h
        shibokenbuffer.h
        sbkpython.h
        pep384impl.h
        voidptr.h
        bufferprocs_py37.h
        "${CMAKE_CURRENT_BINARY_DIR}/sbkversion.h"

        signature.h
        signature_p.h

        DESTINATION include/shiboken6${shiboken6_SUFFIX})
install(TARGETS libshiboken EXPORT Shiboken6Targets
                            LIBRARY DESTINATION "${LIB_INSTALL_DIR}"
                            ARCHIVE DESTINATION "${LIB_INSTALL_DIR}"
                            RUNTIME DESTINATION bin)
install(EXPORT Shiboken6Targets NAMESPACE Shiboken6::
        DESTINATION ${LIB_INSTALL_DIR}/cmake/Shiboken6-${shiboken6_VERSION})
