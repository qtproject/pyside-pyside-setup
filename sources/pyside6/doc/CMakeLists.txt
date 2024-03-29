# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

cmake_minimum_required(VERSION 3.18)
cmake_policy(VERSION 3.18)

project(doc)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/../../shiboken6/cmake")
include(FindDocTools)

# When the doc project is built as part of the pyside project, we show informational message
# and return early if requirements are not met.
if(NOT CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
    if(QT_SRC_DIR AND SPHINX_BUILD AND DOT_EXEC AND BUILD_DOCS)
        # All requirements met, proceed.
    else()
        set(reasons "")
        if(NOT QT_SRC_DIR)
            list(APPEND reasons "    QT_SRC_DIR variable not set\n")
        endif()
        if(NOT SPHINX_BUILD)
            list(APPEND reasons "    sphinx-build command not found\n")
        endif()
        if(NOT DOT_EXEC)
            list(APPEND reasons "    graphviz not found\n")
        endif()
        if(NOT BUILD_DOCS)
            list(APPEND reasons "    BUILD_DOCS was set to FALSE (default)\n")
        endif()
        message(STATUS "apidoc generation targets disabled due to the following reasons:\n"
                ${reasons})
        return()
    endif()
else()
    # We are building the docs as a standalone project, likely via setup.py build_base_docs
    # command. Perform stricter sanity checks.
    if(NOT SPHINX_BUILD)
        message(FATAL_ERROR "sphinx-build command not found. Please set the SPHINX_BUILD variable.")
    endif()
endif()

# Generate html by default.
if(NOT DOC_OUTPUT_FORMAT)
    set(DOC_OUTPUT_FORMAT "html")
endif()

if (WIN32)
    set(PATH_SEP "\;")
else()
    set(PATH_SEP ":")
endif()

set(DOC_DATA_DIR "${CMAKE_CURRENT_BINARY_DIR}/qdoc-output")
# Directory for sphinx-generated files to build the HTML website. If changed,
# update "build_scripts/main.py" in "PysideBaseDocs" class at line:
# self.sphinx_src = self.out_dir / "base".
set(DOC_BASE_DIR "base")

set(ENV_INHERITANCE_FILE "${CMAKE_CURRENT_BINARY_DIR}/inheritance.json")

get_filename_component(ROOT ${CMAKE_CURRENT_BINARY_DIR} DIRECTORY)
set(TS_ROOT "${ROOT}/PySide6")

file(REMOVE ${CMAKE_CURRENT_LIST_DIR}/pyside.qdocconf ${CMAKE_CURRENT_LIST_DIR}/pyside.qdocconf.in)

# We need to find the interpreter when running this only
# for the 'build_base_docs' case, and not a full doc build
if (NOT FULLDOCSBUILD)
    find_package(Python COMPONENTS Interpreter)
endif()

if (QT_SRC_DIR)
    file(REAL_PATH ${QT_SRC_DIR}/.. QT_ROOT_PATH)
else()
    set(QT_ROOT_PATH "")
endif()

if(PYSIDE_IS_CROSS_BUILD)
    set(python_executable "${QFP_PYTHON_HOST_PATH}")
else()
    set(python_executable "${Python_EXECUTABLE}")
endif()

set(TOOLS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../tools")

if (FULLDOCSBUILD)
    # Fetch and transform the snippets from Qt
    set(SNIPPETS_TOOL "${TOOLS_DIR}/snippets_translate/main.py")
    set(SNIPPETS_TARGET ${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/codesnippets)

    # Note QT_SRC_DIR points to 'qtbase',
    # so we use the general SRC directory to copy all the other snippets
    add_custom_target("snippets_translate" DEPENDS "${SNIPPETS_TARGET}")
    add_custom_command(OUTPUT "${SNIPPETS_TARGET}"
                       COMMAND ${python_executable} ${SNIPPETS_TOOL}
                               --qt ${QT_ROOT_PATH} --target ${SNIPPETS_TARGET} -w
                       WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
                       COMMENT "Fetching and converting snippets...")
endif()

# Generate example gallery
set(EXAMPLE_TOOL_TARGET "${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/examples")
set(EXAMPLE_TOOL_OPTIONS --target "${EXAMPLE_TOOL_TARGET}" --qt-src-dir "${QT_SRC_DIR}")
if (QUIET_BUILD)
    list(APPEND EXAMPLE_TOOL_OPTIONS "-q")
endif()
set(EXAMPLE_TOOL_DIR "${TOOLS_DIR}/example_gallery/main.py")

add_custom_target("example_gallery" DEPENDS "${EXAMPLE_TOOL_TARGET}")
add_custom_command(OUTPUT "${EXAMPLE_TOOL_TARGET}"
                   COMMAND ${python_executable} ${EXAMPLE_TOOL_DIR} ${EXAMPLE_TOOL_OPTIONS}
                   WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
                   COMMENT "Generating example gallery...")

set(SHIBOKEN_INTERSPHINX_FILE "${ROOT}/pyside6/shiboken6/objects.inv")
set(HAS_WEBENGINE_WIDGETS 0)
set(SKIP_SPHINX_WARNINGS 1)
if (FULLDOCSBUILD)
    set(SKIP_SPHINX_WARNINGS 0)
    set(SHIBOKEN_INTERSPHINX_FILE "${CMAKE_BINARY_DIR}/doc/html/shiboken6/doc/html/objects.inv")
    # For Qt modules that are part of the documentation build:
    #    - Configure the module docconf file
    #    - Write shiboken header consisting of pyside6_global.h and module includes
    #    - Build include path for qdoc for shiboken

    # The last element of the include list is the mkspec directory containing qplatformdefs.h
    list(GET Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS -1 mkspecInclude)
    set(config_docconf "${CMAKE_CURRENT_LIST_DIR}/pyside-config.qdocconf")
    configure_file("pyside-config.qdocconf.in" "${config_docconf}" @ONLY)

    set(global_header "${pyside6_BINARY_DIR}/qdoc.h")
    file(READ "${pyside6_BINARY_DIR}/pyside6_global.h" docHeaderContents)
    file(WRITE ${global_header} "${docHeaderContents}")

    set(global_typesystem "${CMAKE_CURRENT_BINARY_DIR}/typesystem_doc.xml")
    file(READ "typesystem_doc.xml.in" typeSystemDocXmlContents)
    file(WRITE ${global_typesystem} "${typeSystemDocXmlContents}")

    execute_process(
      COMMAND ${Python_EXECUTABLE} "${TOOLS_DIR}/doc_modules.py"
              -t "${global_typesystem}" -g "${global_header}" -d "${config_docconf}"
              "${QT_INCLUDE_DIR}" "${SUPPORTED_QT_VERSION}"
      OUTPUT_VARIABLE ALL_DOC_MODULES
      OUTPUT_STRIP_TRAILING_WHITESPACE)
    separate_arguments (ALL_DOC_MODULES UNIX_COMMAND "${ALL_DOC_MODULES}")

    foreach(moduleIn ${ALL_DOC_MODULES})
        string(TOLOWER "${moduleIn}" lowerModuleIn)
        set(docConf "${CMAKE_CURRENT_LIST_DIR}/qtmodules/pyside-qt${lowerModuleIn}.qdocconf.in")
        if(EXISTS "${docConf}")
            string(REGEX REPLACE "(^.*)\.in" "\\1" OUTFILE ${docConf})
            get_filename_component(BASENAME ${OUTFILE} NAME)
            configure_file(${docConf} "${CMAKE_CURRENT_LIST_DIR}/qtmodules/${BASENAME}" @ONLY)
            file(APPEND "pyside.qdocconf.in" "\@CMAKE_CURRENT_LIST_DIR\@/qtmodules/${BASENAME}\n")
        endif()
    endforeach()

    # There is no binding for the qtdoc repository, but it has some relevant documents.
    set(qtdoc_doc_conf "qtmodules/pyside-qtdoc.qdocconf")
    configure_file("${qtdoc_doc_conf}.in" "${CMAKE_CURRENT_LIST_DIR}/${qtdoc_doc_conf}" @ONLY)
    file(APPEND "pyside.qdocconf.in" "\@CMAKE_CURRENT_LIST_DIR\@/${qtdoc_doc_conf}\n")

    configure_file("pyside.qdocconf.in" "pyside.qdocconf" @ONLY)
    configure_file("qdoc_spawner.py.in" "qdoc_spawner.py" @ONLY)


    set(QDOC_TYPESYSTEM_PATH "${pyside6_SOURCE_DIR}${PATH_SEP}${pyside6_BINARY_DIR}")

    if(NOT qdoc_binary)
        message(FATAL_ERROR
                "No qdoc binary was found which full documentation generation requires. "
                "Please either add qdoc to PATH or specify the QDOC_EXECUTABLE variable."
        )
    endif()

    add_custom_target(qdoc DEPENDS "${DOC_DATA_DIR}/webxml/qtcore-index.webxml")

    add_custom_command(OUTPUT "${DOC_DATA_DIR}/webxml/qtcore-index.webxml"
                        Use dummy Qt version information, QDoc needs it but has no effect on WebXML output
                       COMMAND ${CMAKE_COMMAND} -E env ${python_executable} qdoc_spawner.py
                           --qt=${QT_VERSION_MAJOR}.${QT_VERSION_MINOR}.${QT_VERSION_PATCH}
                           --doc-data-dir=${DOC_DATA_DIR}
                           --qdoc-binary=${qdoc_binary}
                           --build-dir=${CMAKE_CURRENT_LIST_DIR}/src
                           --qt-install-docs=${QT_SRC_DIR}/doc
                           --parallel="auto"
                           --verbose
                       COMMENT "Running qdoc against Qt source code...")
endif()

# Avoid using 'auto' for '-j' option as it could lead to
# crash on some systems due to out-of-memory situation. Instead
# use a no. less than 8.
add_custom_target(apidoc
                  COMMAND ${CMAKE_COMMAND} -E env INHERITANCE_FILE=${ENV_INHERITANCE_FILE}
                          ${SHIBOKEN_PYTHON_INTERPRETER} ${SPHINX_BUILD} -b ${DOC_OUTPUT_FORMAT}
                          -j 6 ${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR} html
                  COMMENT "Generating PySide htmls..."
                 )

# create a custom commands to copy the shiboken docs
# and generate offline help based on the output format.
if(DOC_OUTPUT_FORMAT STREQUAL "html")
    add_custom_command(TARGET apidoc POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/html/shiboken6
            COMMAND ${CMAKE_COMMAND} -E copy_directory
                    ${CMAKE_CURRENT_BINARY_DIR}/../../shiboken6/doc/html
                    ${CMAKE_CURRENT_BINARY_DIR}/html/shiboken6
            COMMENT "Copying Shiboken docs..."
            DEPENDS "${DOC_DATA_DIR}/webxml/qtcore-index.webxml"
            VERBATIM)
else()
    if(qhelpgenerator_binary)
        message(STATUS "qhelpgenerator - found")
        # Python script that will be called to update the QHP
        set(PATCH_QHP_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/../../shiboken6/doc/scripts/patch_qhp.py")
        file(TO_NATIVE_PATH ${CMAKE_CURRENT_BINARY_DIR}/html/PySide.qhp QHP_FILE)
        add_custom_command(TARGET apidoc POST_BUILD
                COMMAND ${python_executable} ${PATCH_QHP_SCRIPT} -p -v pyside6 ${QHP_FILE}
                COMMAND "${qhelpgenerator_binary}" ${QHP_FILE}
                COMMENT "Generating QCH from a QHP file..."
                DEPENDS "${DOC_DATA_DIR}/webxml/qtcore-index.webxml"
                VERBATIM
        )
    else()
        message(WARNING "qhelpgenerator - not found! qch generation disabled")
    endif()
endif()

# create conf.py based on conf.py.in
configure_file("conf.py.in" "${DOC_BASE_DIR}/conf.py" @ONLY)

set(CODE_SNIPPET_ROOT "${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/codesnippets")

if (FULLDOCSBUILD)
shiboken_get_tool_shell_wrapper(shiboken tool_wrapper)

add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/PySide6/QtCore/index.rst"
                   COMMAND
                       ${tool_wrapper}
                       $<TARGET_FILE:Shiboken6::shiboken6>
                       --generator-set=qtdoc
                       ${global_header}
                       --enable-pyside-extensions
                       --include-paths="${QT_INCLUDE_DIR}${PATH_SEP}${pyside6_SOURCE_DIR}${PATH_SEP}${TS_ROOT}"
                       --api-version=${SUPPORTED_QT_VERSION}
                       --typesystem-paths="${QDOC_TYPESYSTEM_PATH}"
                       --library-source-dir=${QT_SRC_DIR}
                       --documentation-data-dir=${DOC_DATA_DIR}/webxml
                       --output-directory=${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}
                       --documentation-code-snippets-dir=${CODE_SNIPPET_ROOT}
                       --snippets-path-rewrite=${QT_ROOT_PATH}:${CODE_SNIPPET_ROOT}
                       --documentation-extra-sections-dir=${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/extras
                       --additional-documentation=${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/additionaldocs.lst
                       --inheritance-file=${ENV_INHERITANCE_FILE}
                       ${global_typesystem}
                   WORKING_DIRECTORY ${${module}_SOURCE_DIR}
                   COMMENT "Running generator to generate documentation...")
endif()

add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/extras"
                   COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}
                   COMMENT "Copying docs...")

add_custom_target("doc_copy"
                  DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/extras")

add_custom_target("docrsts"
                  DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/PySide6/QtCore/index.rst")

set(LIBEXEC_PATH "${QT6_INSTALL_PREFIX}/${QT6_INSTALL_LIBEXECS}")
add_custom_target("licensedocrsts"
    COMMAND ${python_executable}
            ${CMAKE_CURRENT_LIST_DIR}/qtattributionsscannertorst.py
            -l "${LIBEXEC_PATH}"
            ${CMAKE_CURRENT_LIST_DIR}/../../..
            ${CMAKE_CURRENT_BINARY_DIR}/${DOC_BASE_DIR}/licenses.rst
    COMMENT "Creating 3rdparty license documentation..."
)

add_dependencies(docrsts example_gallery)

if (FULLDOCSBUILD)
    add_dependencies(apidoc docrsts licensedocrsts)
    add_dependencies(licensedocrsts docrsts)
    add_dependencies(docrsts doc_copy qdoc snippets_translate)
endif()

#install files
add_custom_target(apidocinstall
    COMMAND mkdir -p ${CMAKE_INSTALL_PREFIX}/share/doc/PySide6-${BINDING_API_VERSION} && cp -rv ${CMAKE_CURRENT_BINARY_DIR}/html/* ${CMAKE_INSTALL_PREFIX}/share/doc/PySide-${BINDING_API_VERSION}
)

add_dependencies(apidocinstall apidoc)
