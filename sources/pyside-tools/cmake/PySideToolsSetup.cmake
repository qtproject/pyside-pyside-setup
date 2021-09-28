list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}")

include(PySideToolsHelpers)

pyside_tools_internal_detect_if_cross_building()
pyside_tools_internal_set_up_extra_dependency_paths()

find_package(Qt6 REQUIRED COMPONENTS Core HostInfo)

# Don't display "up-to-date / install" messages when installing, to reduce visual clutter.
if (QUIET_BUILD)
    set(CMAKE_INSTALL_MESSAGE NEVER)
endif()
