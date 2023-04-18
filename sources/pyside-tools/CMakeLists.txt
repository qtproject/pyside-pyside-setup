# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

cmake_minimum_required(VERSION 3.18)
project(pyside-tools)

include(cmake/PySideToolsSetup.cmake)

if(${CMAKE_SYSTEM_NAME} STREQUAL "Android")
    # create Qt6AndroidBindings.jar
    if (NOT DEFINED ANDROID_SDK_ROOT)
        message(FATAL_ERROR "Please provide the location of the Android SDK directory via "
                            "your toolchain file")
    endif()
    if (NOT DEFINED ANDROID_PLATFORM)
        message(FATAL_ERROR "Please provide the location of the Android Platform API level via "
                            "your toolchain file eg: android-31")
    endif()
    include(cmake/PySideAndroid.cmake)
    create_and_install_qt_javabindings()
else()
    set(files ${CMAKE_CURRENT_SOURCE_DIR}/pyside_tool.py
            ${CMAKE_CURRENT_SOURCE_DIR}/metaobjectdump.py
            ${CMAKE_CURRENT_SOURCE_DIR}/project.py
            ${CMAKE_CURRENT_SOURCE_DIR}/qml.py
            ${CMAKE_CURRENT_SOURCE_DIR}/qtpy2cpp.py
            ${CMAKE_CURRENT_SOURCE_DIR}/deploy.py
            ${CMAKE_CURRENT_SOURCE_DIR}/android_deploy.py)

    set(directories ${CMAKE_CURRENT_SOURCE_DIR}/deploy_lib
                    ${CMAKE_CURRENT_SOURCE_DIR}/project)

    if(NOT NO_QT_TOOLS STREQUAL "yes")
        set(TOOLS_PATH "${QT6_INSTALL_PREFIX}/${QT6_HOST_INFO_BINDIR}")
        set(LIBEXEC_PATH "${QT6_INSTALL_PREFIX}/${QT6_HOST_INFO_LIBEXECDIR}")

        list(APPEND files "${LIBEXEC_PATH}/uic${CMAKE_EXECUTABLE_SUFFIX}"
                        "${LIBEXEC_PATH}/rcc${CMAKE_EXECUTABLE_SUFFIX}"
                        "${LIBEXEC_PATH}/qmltyperegistrar${CMAKE_EXECUTABLE_SUFFIX}"
                        "${LIBEXEC_PATH}/qmlimportscanner${CMAKE_EXECUTABLE_SUFFIX}"
                        "${LIBEXEC_PATH}/qmlcachegen${CMAKE_EXECUTABLE_SUFFIX}"
                        "${TOOLS_PATH}/lrelease${CMAKE_EXECUTABLE_SUFFIX}"
                        "${TOOLS_PATH}/lupdate${CMAKE_EXECUTABLE_SUFFIX}"
                        "${TOOLS_PATH}/qmllint${CMAKE_EXECUTABLE_SUFFIX}"
                        "${TOOLS_PATH}/qmlformat${CMAKE_EXECUTABLE_SUFFIX}"
                        "${TOOLS_PATH}/qmlls${CMAKE_EXECUTABLE_SUFFIX}")

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

    list(APPEND directories ${CMAKE_CURRENT_SOURCE_DIR}/qtpy2cpp_lib)

    # pyside6-rcc, pyside6-uic, pyside6-designer, shiboken and pyside6-lupdate entrypoints
    foreach(file ${files})
        if(EXISTS ${file})
            install(FILES "${file}"
                    DESTINATION bin
                    PERMISSIONS
                    OWNER_EXECUTE OWNER_WRITE OWNER_READ
                    GROUP_EXECUTE GROUP_READ
                    WORLD_EXECUTE WORLD_READ)
        else()
            message(WARNING "${file} does not exist. Hence, pyside6-${file} will not work")
        endif()
    endforeach()

    foreach(directory ${directories})
        install(DIRECTORY "${directory}"
                DESTINATION bin
                FILE_PERMISSIONS
                OWNER_EXECUTE OWNER_WRITE OWNER_READ
                GROUP_EXECUTE GROUP_READ
                WORLD_EXECUTE WORLD_READ)
    endforeach()
endif()
