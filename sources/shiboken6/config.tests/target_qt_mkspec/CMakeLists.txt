cmake_minimum_required(VERSION 3.16)
project(dummy LANGUAGES CXX)

include("${CMAKE_CURRENT_LIST_DIR}/../../cmake/ShibokenHelpers.cmake")

shiboken_internal_detect_if_cross_building()
shiboken_internal_set_up_extra_dependency_paths()
find_package(Qt6 REQUIRED COMPONENTS Core)

get_target_property(darwin_target Qt6::Core QT_DARWIN_MIN_DEPLOYMENT_TARGET)

# Get macOS minimum deployment target
message(STATUS "qfp:qt_info:QMAKE_MACOSX_DEPLOYMENT_TARGET: ${darwin_target}")

# Get Qt build type
if(QT_FEATURE_debug_and_release)
    message(STATUS "qfp:qt_info:BUILD_TYPE: debug_and_release")
elseif(QT_FEATURE_debug)
    message(STATUS "qfp:qt_info:BUILD_TYPE: debug")
else()
    message(STATUS "qfp:qt_info:BUILD_TYPE: release")
endif()
