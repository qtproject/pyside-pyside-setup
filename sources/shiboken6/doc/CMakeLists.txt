cmake_minimum_required(VERSION 3.16)

if(FULLDOCSBUILD EQUAL 0)
    project(shiboken6_doc)
endif()

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/../cmake")
include(FindDocTools)

# Generate html by default.
if(NOT DOC_OUTPUT_FORMAT)
    set(DOC_OUTPUT_FORMAT "html")
endif()

if(SPHINX_BUILD)
    message(STATUS "sphinx-build - found")
    configure_file(conf.py.in conf.py @ONLY)
    # conditional tag for sphinx build
    #string(JOIN "_" SPHINX_TAG ${DOC_OUTPUT_FORMAT} "format")
    add_custom_target(doc
        COMMAND ${SPHINX_BUILD} -b ${DOC_OUTPUT_FORMAT} -c . ${CMAKE_CURRENT_SOURCE_DIR} html
        COMMENT "Generating shiboken documentation HTML files"
        VERBATIM)

    # Attach a POST_BUILD step to the 'doc' custom target to generate a QCH file.
    if(DOC_OUTPUT_FORMAT STREQUAL "qthelp")
        if(qhelpgenerator_binary)
            message(STATUS "qhelpgenerator - found")

            # Python script that will be called to update the QHP
            set(PATCH_QHP_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/../../shiboken6/doc/scripts/patch_qhp.py")
            file(TO_NATIVE_PATH ${CMAKE_CURRENT_BINARY_DIR}/html/Shiboken.qhp QHP_FILE)

            if(SHIBOKEN_IS_CROSS_BUILD)
                set(python_executable "${QFP_PYTHON_HOST_PATH}")
            else()
                set(python_executable "${PYTHON_EXECUTABLE}")
            endif()
            if(NOT python_executable OR NOT EXISTS "${python_executable}")
                message(FATAL_ERROR "No python executable found to build documentation.")
            endif()

            add_custom_command(TARGET doc POST_BUILD
                COMMAND "${python_executable}" ${PATCH_QHP_SCRIPT} -f ${QHP_FILE} -v shiboken6
                COMMAND "${qhelpgenerator_binary}" ${QHP_FILE}
                COMMENT "Generating shiboken documentation QCH files based on the QHP files"
                VERBATIM)
        else()
            message(WARNING "qhelpgenerator - not found! qch generation disabled")
        endif()
    endif()
else()
    if(NOT SPHINX_BUILD)
        message(WARNING "sphinx-build - not found! doc target disabled")
    endif()
    if (WIN32)
        # if jom is used and we have no sphinx, then jom will crash.
        # so for windows, we always create a doc target (until jom gets fixed...)
        add_custom_target(doc echo.
            COMMAND echo +++ This is a fake build, to make 'jom' happy.
            COMMAND echo +++ The documentation was _not_ built!
            COMMAND echo.
        )
    endif()
endif()

if (NOT WIN32)
    file(GLOB manpages "${CMAKE_CURRENT_SOURCE_DIR}/*.1")
    install(FILES ${manpages} DESTINATION share/man/man1)
endif()
