function(pyside_tools_internal_detect_if_cross_building)
    if(CMAKE_CROSSCOMPILING OR QFP_SHIBOKEN_HOST_PATH)
        set(is_cross_build TRUE)
    else()
        set(is_cross_build FALSE)
    endif()
    set(PYSIDE_TOOLS_IS_CROSS_BUILD "${is_cross_build}" PARENT_SCOPE)
    message(STATUS "PYSIDE_TOOLS_IS_CROSS_BUILD: ${PYSIDE_TOOLS_IS_CROSS_BUILD}")
endfunction()

function(pyside_tools_internal_set_up_extra_dependency_paths)
    set(extra_root_path_vars
        QFP_QT_TARGET_PATH
    )
    foreach(root_path IN LISTS extra_root_path_vars)
        set(new_root_path_value "${${root_path}}")
        if(new_root_path_value)
            set(new_prefix_path "${CMAKE_PREFIX_PATH}")
            list(PREPEND new_prefix_path "${new_root_path_value}/lib/cmake")
            set(CMAKE_PREFIX_PATH "${new_prefix_path}")
            set(CMAKE_PREFIX_PATH "${new_prefix_path}" PARENT_SCOPE)

            # Need to adjust the prefix and root paths so that find_package(Qt) and other 3rd
            # party packages are found successfully when they are located outside of the
            # default sysroot (whatever that maybe for the target platform).
            if(PYSIDE_TOOLS_IS_CROSS_BUILD)
                set(new_root_path "${CMAKE_FIND_ROOT_PATH}")
                list(PREPEND new_root_path "${new_root_path_value}")
                set(CMAKE_FIND_ROOT_PATH "${new_root_path}")
                set(CMAKE_FIND_ROOT_PATH "${new_root_path}" PARENT_SCOPE)
            endif()
        endif()
    endforeach()
endfunction()
