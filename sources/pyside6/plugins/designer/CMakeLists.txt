project(PySidePlugin)

# Note: At runtime, the dependency to the shiboken library is resolved
# by the pyside_tool.py wrapper

set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_AUTOMOC ON)

find_package(Qt6 COMPONENTS Core)
find_package(Qt6 COMPONENTS Gui)
find_package(Qt6 COMPONENTS Widgets)
find_package(Qt6 COMPONENTS UiPlugin)

qt_add_plugin(PySidePlugin)

target_sources(PySidePlugin PRIVATE
    designercustomwidgets.cpp
)

# See libshiboken/CMakeLists.txt
if(PYTHON_LIMITED_API)
    target_compile_definitions(PySidePlugin PRIVATE "-DPy_LIMITED_API=0x03050000")
endif()

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(PYTHON_WITH_DEBUG)
        target_compile_definitions(PySidePlugin PRIVATE "-DPy_DEBUG")
    endif()
    if (PYTHON_WITH_COUNT_ALLOCS)
        target_compile_definitions(PySidePlugin PRIVATE "-DCOUNT_ALLOCS")
    endif()
elseif(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_definitions(PySidePlugin PRIVATE "-DNDEBUG")
endif()

target_include_directories(PySidePlugin PRIVATE ../uitools)

set_target_properties(PySidePlugin PROPERTIES
    WIN32_EXECUTABLE TRUE
    MACOSX_BUNDLE TRUE
)

get_property(SHIBOKEN_PYTHON_LIBRARIES GLOBAL PROPERTY shiboken_python_libraries)
get_property(SHIBOKEN_PYTHON_INCLUDE_DIRS GLOBAL PROPERTY shiboken_python_include_dirs)

target_include_directories(PySidePlugin PRIVATE ${SHIBOKEN_PYTHON_INCLUDE_DIRS})

target_link_libraries(PySidePlugin PRIVATE
                      Qt::Core
                      Qt::Gui
                      Qt::UiPlugin
                      Qt::Widgets
                      ${SHIBOKEN_PYTHON_LIBRARIES})

install(TARGETS PySidePlugin LIBRARY DESTINATION "plugins/designer")
