cmake_minimum_required(VERSION 3.16)
project(pyside-tools)

# Don't display "up-to-date / install" messages when installing, to reduce visual clutter.
if (QUIET_BUILD)
    set(CMAKE_INSTALL_MESSAGE NEVER)
endif()

find_package(Qt6 COMPONENTS Core HostInfo)

set(files ${CMAKE_CURRENT_SOURCE_DIR}/pyside_tool.py
          ${CMAKE_CURRENT_SOURCE_DIR}/metaobjectdump.py)
set(directories)

if(NOT NO_QT_TOOLS STREQUAL "yes")
    set(TOOLS_PATH "${QT6_INSTALL_PREFIX}/${QT6_HOST_INFO_BINDIR}")
    set(LIBEXEC_PATH "${QT6_INSTALL_PREFIX}/${QT6_HOST_INFO_LIBEXECDIR}")

    list(APPEND files "${LIBEXEC_PATH}/uic${CMAKE_EXECUTABLE_SUFFIX}"
                      "${LIBEXEC_PATH}/rcc${CMAKE_EXECUTABLE_SUFFIX}"
                      "${LIBEXEC_PATH}/qmltyperegistrar${CMAKE_EXECUTABLE_SUFFIX}"
                      "${TOOLS_PATH}/lrelease${CMAKE_EXECUTABLE_SUFFIX}"
                      "${TOOLS_PATH}/lupdate${CMAKE_EXECUTABLE_SUFFIX}"
                      "${TOOLS_PATH}/qmllint${CMAKE_EXECUTABLE_SUFFIX}")

    if (APPLE)
        list(APPEND directories "${TOOLS_PATH}/Assistant.app"
                                "${TOOLS_PATH}/Designer.app"
                                "${TOOLS_PATH}/Linguist.app")
    else()
        list(APPEND files "${TOOLS_PATH}/assistant${CMAKE_EXECUTABLE_SUFFIX}"
                          "${TOOLS_PATH}/designer${CMAKE_EXECUTABLE_SUFFIX}"
                          "${TOOLS_PATH}/linguist${CMAKE_EXECUTABLE_SUFFIX}")
    endif()
endif()

# pyside6-rcc, pyside6-uic, pyside6-designer, shiboken and pyside6-lupdate entrypoints

foreach(file ${files})
    install(FILES "${file}"
            DESTINATION bin
            PERMISSIONS
            OWNER_EXECUTE OWNER_WRITE OWNER_READ
            GROUP_EXECUTE GROUP_READ
            WORLD_EXECUTE WORLD_READ)
endforeach()

foreach(directory ${directories})
    install(DIRECTORY "${directory}"
            DESTINATION bin
            FILE_PERMISSIONS
            OWNER_EXECUTE OWNER_WRITE OWNER_READ
            GROUP_EXECUTE GROUP_READ
            WORLD_EXECUTE WORLD_READ)
endforeach()
