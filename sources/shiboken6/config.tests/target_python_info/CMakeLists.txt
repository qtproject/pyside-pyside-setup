cmake_minimum_required(VERSION 3.16)
project(proj LANGUAGES CXX)

include("${CMAKE_CURRENT_LIST_DIR}/../../cmake/ShibokenHelpers.cmake")

shiboken_internal_detect_if_cross_building()
shiboken_find_required_python()
shiboken_internal_set_python_site_packages()

message(STATUS "qfp:python_info:interpreter_found: ${Python_Interpreter_FOUND}")
message(STATUS "qfp:python_info:development_found: ${Python_Development_FOUND}")
message(STATUS "qfp:python_info:version: ${Python_VERSION}")
message(STATUS "qfp:python_info:version_major: ${Python_VERSION_MAJOR}")
message(STATUS "qfp:python_info:version_minor: ${Python_VERSION_MINOR}")
message(STATUS "qfp:python_info:version_patch: ${Python_VERSION_PATCH}")
message(STATUS "qfp:python_info:executable: ${Python_EXECUTABLE}")
message(STATUS "qfp:python_info:include_dirs: ${Python_INCLUDE_DIRS}")
message(STATUS "qfp:python_info:libraries: ${Python_LIBRARIES}")
message(STATUS "qfp:python_info:library_dirs: ${Python_LIBRARY_DIRS}")
message(STATUS "qfp:python_info:runtime_library_dirs: ${Python_RUNTIME_LIBRARY_DIRS}")
# Python_SOABI will be empty with CMake < 3.17
message(STATUS "qfp:python_info:so_abi: ${Python_SOABI}")
message(STATUS "qfp:python_info:site_packages_dir: ${PYTHON_SITE_PACKAGES_WITHOUT_PREFIX}")
message(STATUS "qfp:python_info:site_packages_dir_with_prefix: ${PYTHON_SITE_PACKAGES}")

message(STATUS
        "The following values might be unstable because they depend on private FindPython API")
# This is using internal FindPython API and is subject to break.
set(_PYTHON_PREFIX Python)
if(COMMAND _python_get_config_var)
    if(_${_PYTHON_PREFIX}_CONFIG)
        message(STATUS "qfp:python_info:config_executable: ${_${_PYTHON_PREFIX}_CONFIG}")
    endif()

    _python_get_config_var(_${_PYTHON_PREFIX}_PREFIX PREFIX)
    if(_${_PYTHON_PREFIX}_PREFIX)
        message(STATUS "qfp:python_info:prefix: ${_${_PYTHON_PREFIX}_PREFIX}")
    endif()
    _python_get_config_var(_${_PYTHON_PREFIX}_CONFIGDIR CONFIGDIR)
    if(_${_PYTHON_PREFIX}_CONFIGDIR)
        message(STATUS "qfp:python_info:config_dir: ${_${_PYTHON_PREFIX}_CONFIGDIR}")
    endif()
endif()

