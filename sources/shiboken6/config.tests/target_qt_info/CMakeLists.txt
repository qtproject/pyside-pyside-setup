cmake_minimum_required(VERSION 3.16)
project(proj LANGUAGES CXX)

include("${CMAKE_CURRENT_LIST_DIR}/../../cmake/ShibokenHelpers.cmake")

shiboken_internal_detect_if_cross_building()
shiboken_internal_set_up_extra_dependency_paths()
find_package(Qt6 REQUIRED COMPONENTS Core)

include(FeatureSummary)

feature_summary(INCLUDE_QUIET_PACKAGES
                WHAT PACKAGES_FOUND
                     REQUIRED_PACKAGES_NOT_FOUND
                     RECOMMENDED_PACKAGES_NOT_FOUND
                     OPTIONAL_PACKAGES_NOT_FOUND
                     RUNTIME_PACKAGES_NOT_FOUND
                     FATAL_ON_MISSING_REQUIRED_PACKAGES)

message(STATUS "qfp:qt_info:QT_VERSION: ${Qt6_VERSION}")
message(STATUS "qfp:qt_info:QT_INSTALL_PREFIX: ${QT6_INSTALL_PREFIX}")
message(STATUS "qfp:qt_info:QT_INSTALL_ARCHDATA: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_ARCHDATA}")
message(STATUS "qfp:qt_info:QT_INSTALL_BINS: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_BINS}")
message(STATUS "qfp:qt_info:QT_INSTALL_CONFIGURATION: ${QT6_INSTALL_CONFIGURATION}")
message(STATUS "qfp:qt_info:QT_INSTALL_DATA: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_DATA}")
message(STATUS "qfp:qt_info:QT_INSTALL_DOCS: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_DOCS}")
message(STATUS "qfp:qt_info:QT_INSTALL_EXAMPLES: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_EXAMPLES}")
message(STATUS "qfp:qt_info:QT_INSTALL_HEADERS: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_HEADERS}")
message(STATUS "qfp:qt_info:QT_INSTALL_LIBS: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_LIBS}")
message(STATUS "qfp:qt_info:QT_INSTALL_LIBEXECS: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_LIBEXECS}")
message(STATUS "qfp:qt_info:QT_INSTALL_PLUGINS: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_PLUGINS}")
message(STATUS "qfp:qt_info:QT_INSTALL_QML: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_QML}")
message(STATUS "qfp:qt_info:QT_INSTALL_TESTS: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_TESTS}")
message(STATUS "qfp:qt_info:QT_INSTALL_TRANSLATIONS: ${QT6_INSTALL_PREFIX}/${QT6_INSTALL_TRANSLATIONS}")
message(STATUS "qfp:qt_info:is_shared: ${QT6_IS_SHARED_LIBS_BUILD}")

