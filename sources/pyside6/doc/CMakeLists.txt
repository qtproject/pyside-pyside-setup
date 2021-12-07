cmake_minimum_required(VERSION 3.16)
cmake_policy(VERSION 3.16)

project(doc)

find_program(SPHINX_BUILD sphinx-build)

# graphviz dot appears to be used by sphinx and not by CMake directly. This is just found to check
# if it exists.
find_program(DOT_EXEC dot)

# Lookup for qdoc in multiple sources: cache var, PATH or CMake package.
set(qdoc_binary "")
find_program(QDOC_EXECUTABLE qdoc DOC "Path to qdoc binary.")
if(QDOC_EXECUTABLE)
    set(qdoc_binary "${QDOC_EXECUTABLE}")
else()
    find_package(Qt6 QUIET COMPONENTS Tools)
    if(TARGET Qt6::qdoc)
        set(qdoc_binary "$<TARGET_FILE:Qt6::qdoc>")
    endif()
endif()

# Lookup for qhelpgenerator in multiple sources: cache var, PATH or CMake package.
set(qhelpgenerator_binary "")
find_program(QHELPGENERATOR_EXECUTABLE qhelpgenerator DOC "Path to qhelpgenerator binary.")
if(QHELPGENERATOR_EXECUTABLE)
    set(qhelpgenerator_binary "${QHELPGENERATOR_EXECUTABLE}")
else()
    find_package(Qt6 QUIET COMPONENTS Tools)
    if(TARGET Qt6::qhelpgenerator)
        set(qhelpgenerator_binary "$<TARGET_FILE:Qt6::qhelpgenerator>")
    endif()
endif()

# When the doc project is built as part of the pyside project, we show informational message
# and return early if requirements are not met.
if(NOT CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
    if(QT_SRC_DIR AND SPHINX_BUILD AND DOT_EXEC AND NOT SKIP_DOCS)
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
        if(SKIP_DOCS)
            list(APPEND reasons "    SKIP_DOCS was set to TRUE\n")
        endif()
        message(STATUS "apidoc generation targets disabled due to the following reasons:\n"
                ${reasons})
        return()
    endif()
else()
    # We are building the docs as a standalone project, likely via setup.py build_rst_docs
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

get_filename_component(ROOT ${CMAKE_CURRENT_BINARY_DIR} DIRECTORY)
set(TS_ROOT "${ROOT}/PySide6")

file(REMOVE ${CMAKE_CURRENT_LIST_DIR}/pyside.qdocconf ${CMAKE_CURRENT_LIST_DIR}/pyside.qdocconf.in)

# We need to find the interpreter when running this only
# for a rst_build_docs case, and not a full doc build
if (NOT FULLDOCSBUILD)
    find_package(Python COMPONENTS Interpreter)
    set(PYTHON_EXECUTABLE ${Python_EXECUTABLE})
endif()

if (QT_SRC_DIR)
    file(REAL_PATH ${QT_SRC_DIR}/.. QT_ROOT_PATH)
else()
    set(QT_ROOT_PATH "")
endif()

if (FULLDOCSBUILD)
    # Fetch and transform the snippets from Qt
    message(STATUS "Fetching and converting snippets")
    if ("${QT_ROOT_PATH}" STREQUAL "")
        message(FATAL_ERROR "There is no value set on QT_SRC_DIR, the snippet conversion will fail")
    endif()
    set(PYSIDE_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../../")
    set(SNIPPETS_TOOL "${CMAKE_CURRENT_SOURCE_DIR}/../../../tools/snippets_translate/main.py")

    # Note QT_SRC_DIR points to 'qtbase',
    # so we use the general SRC directory to copy all the other snippets
    execute_process(COMMAND ${PYTHON_EXECUTABLE} ${SNIPPETS_TOOL}
        --qt ${QT_ROOT_PATH} --target ${CMAKE_CURRENT_BINARY_DIR}/rst/codesnippets -w
        WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
        RESULT_VARIABLE SNIPPETS_RESULT)
    if (SNIPPETS_RESULT)
        message(FATAL_ERROR
                "The 'snippets_translate' tool failed: ${SNIPPETS_ERROR} ${SNIPPET_RESULT}")
    endif()
endif()

# Generate example gallery
message(STATUS "Generating example gallery")
if (QUIET_BUILD)
    set (EXAMPLE_TOOL_OPTIONS "-q")
endif()
set(EXAMPLE_TOOL_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../tools/example_gallery/main.py")
execute_process(COMMAND ${PYTHON_EXECUTABLE} ${EXAMPLE_TOOL_DIR} ${EXAMPLE_TOOL_OPTIONS}
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR})

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
    configure_file("pyside-config.qdocconf.in" "${CMAKE_CURRENT_LIST_DIR}/pyside-config.qdocconf" @ONLY)

    file(READ "${pyside6_BINARY_DIR}/pyside6_global.h" docHeaderContents)
    file(READ "typesystem_doc.xml.in" typeSystemDocXmlContents)


    foreach(moduleIn ${all_module_shortnames})
        string(TOLOWER "${moduleIn}" lowerModuleIn)
        set(docConf "${CMAKE_CURRENT_LIST_DIR}/qtmodules/pyside-qt${lowerModuleIn}.qdocconf.in")
        if(EXISTS "${docConf}")
            string(REGEX REPLACE "(^.*)\.in" "\\1" OUTFILE ${docConf})
            get_filename_component(BASENAME ${OUTFILE} NAME)
            configure_file(${docConf} "${CMAKE_CURRENT_LIST_DIR}/qtmodules/${BASENAME}" @ONLY)
            file(APPEND "pyside.qdocconf.in" "\@CMAKE_CURRENT_LIST_DIR\@/qtmodules/${BASENAME}\n")
            # Handle docconf files in Qt that contain multiple modules
            if ("${moduleIn}" STREQUAL "3DExtras")
                set(modules 3DCore 3DRender 3DInput 3DLogic 3DAnimation "${moduleIn}")
            elseif ("${moduleIn}" STREQUAL "OpenGL")
                set(modules "${moduleIn}" OpenGLWidgets)
            elseif ("${moduleIn}" STREQUAL "QuickWidgets")
                set(modules Qml Quick "${moduleIn}")
            elseif ("${moduleIn}" STREQUAL "MultimediaWidgets")
                set(modules Multimedia "${moduleIn}")
            elseif ("${moduleIn}" STREQUAL "Scxml")
                set(modules StateMachine "${moduleIn}")
            elseif ("${moduleIn}" STREQUAL "Svg")
                set(modules "${moduleIn}" SvgWidgets)
            elseif ("${moduleIn}" STREQUAL "WebEngineWidgets")
                set(modules WebEngineCore WebEngineWidgets WebEngineQuick "${moduleIn}")
                set(HAS_WEBENGINE_WIDGETS 1)
            else()
                set(modules "${moduleIn}")
            endif()
            foreach(module ${modules})
                string(TOLOWER "${module}" lowerModule)
                # -- @TODO fix this for macOS frameworks.
                file(APPEND "${CMAKE_CURRENT_LIST_DIR}/pyside-config.qdocconf"
                     "    -I${QT_INCLUDE_DIR}/Qt${module} \\\n"
                     "    -I${QT_INCLUDE_DIR}/Qt${module}/${Qt${QT_MAJOR_VERSION}Core_VERSION} \\\n"
                     "    -I${QT_INCLUDE_DIR}/Qt${module}/${Qt${QT_MAJOR_VERSION}Core_VERSION}/Qt${module} \\\n")

                set(globalHeader "Qt${module}")
                set(docHeaderContents "${docHeaderContents}\n#include <Qt${module}/${globalHeader}>")
                set(typeSystemDocXmlContents "${typeSystemDocXmlContents}\n<load-typesystem name=\"Qt${module}/typesystem_${lowerModule}.xml\" generate=\"yes\"/>")
            endforeach()
        endif()
    endforeach()

    set(typeSystemDocXmlContents "${typeSystemDocXmlContents}\n</typesystem>\n")
    file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/typesystem_doc.xml" "${typeSystemDocXmlContents}")

    set(docHeader "${pyside6_BINARY_DIR}/qdoc.h")
    file(WRITE ${docHeader} "${docHeaderContents}")
    configure_file("pyside.qdocconf.in" "pyside.qdocconf" @ONLY)


    set(QDOC_TYPESYSTEM_PATH "${pyside6_SOURCE_DIR}${PATH_SEP}${pyside6_BINARY_DIR}")

    if(NOT qdoc_binary)
        message(FATAL_ERROR
                "No qdoc binary was found which full documentation generation requires. "
                "Please either add qdoc to PATH or specify the QDOC_EXECUTABLE variable."
        )
    endif()

    add_custom_target(qdoc DEPENDS "${DOC_DATA_DIR}/webxml/qtcore-index.webxml")

    add_custom_command(OUTPUT "${DOC_DATA_DIR}/webxml/qtcore-index.webxml"
                       # Use dummy Qt version information, QDoc needs it but has no effect on WebXML output
                       COMMAND ${CMAKE_COMMAND} -E env BUILDDIR=${CMAKE_CURRENT_LIST_DIR}/src QT_INSTALL_DOCS=${QT_SRC_DIR}/doc
                       QT_VERSION=${QT_VERSION_MAJOR}.${QT_VERSION_MINOR}.${QT_VERSION_PATCH}
                       QT_VER=${QT_VERSION_MAJOR}.${QT_VERSION_MINOR}
                       QT_VERSION_TAG=${QT_VERSION_MAJOR}.${QT_VERSION_MINOR}.${QT_VERSION_PATCH}
                       "${qdoc_binary}" pyside.qdocconf -single-exec
                           -installdir ${DOC_DATA_DIR} -outputdir ${DOC_DATA_DIR}
                       COMMENT "Running qdoc against Qt source code...")
endif()

# conditional tag for sphinx build
#string(JOIN "_" SPHINX_TAG ${DOC_OUTPUT_FORMAT} "format")
# Python script to replace the virtualFolder string in the QHP
set(py_cmd "
import fileinput
import re
try:
\tfor line in fileinput.input('html/PySide.qhp',inplace=True,backup='.bak'):
\t\tline_copy=line.strip()
\t\tif not line_copy: # check for empty line
\t\t\tcontinue
\t\tmatch=re.match('(^.*virtualFolder.)doc(.*$)',line)
\t\tif match:
\t\t\trepl=''.join([match.group(1),'pyside6',match.group(2)])
\t\t\tprint(line.replace(match.group(0),repl),end='')
\t\telse:
\t\t\tprint(line)
except:
\tpass\n")
file(GENERATE OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/py_script.py CONTENT ${py_cmd})

add_custom_target(apidoc
                  COMMAND ${SHIBOKEN_PYTHON_INTERPRETER} ${SPHINX_BUILD} -b ${DOC_OUTPUT_FORMAT} ${CMAKE_CURRENT_BINARY_DIR}/rst html
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
            VERBATIM)
else()
    if(qhelpgenerator_binary)
        message(STATUS "qhelpgenerator - found")

        file(TO_NATIVE_PATH ${CMAKE_CURRENT_BINARY_DIR}/html/PySide.qhp QHP_FILE)
        add_custom_command(TARGET apidoc POST_BUILD
                COMMAND ${PYTHON_EXECUTABLE} py_script.py
                COMMAND "${qhelpgenerator_binary}" ${QHP_FILE}
                COMMENT "Generating QCH from a QHP file..."
                VERBATIM
        )
    else()
        message(WARNING "qhelpgenerator - not found! qch generation disabled")
    endif()
endif()

# create conf.py based on conf.py.in
configure_file("conf.py.in" "rst/conf.py" @ONLY)

set(CODE_SNIPPET_ROOT "${CMAKE_CURRENT_BINARY_DIR}/rst/codesnippets")

add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/rst/PySide6/QtCore/index.rst"
                   COMMAND Shiboken6::shiboken6 --generator-set=qtdoc ${docHeader}
                           --enable-pyside-extensions
                           --include-paths="${QT_INCLUDE_DIR}${PATH_SEP}${pyside6_SOURCE_DIR}${PATH_SEP}${TS_ROOT}"
                           --api-version=${SUPPORTED_QT_VERSION}
                           --typesystem-paths="${QDOC_TYPESYSTEM_PATH}"
                           --library-source-dir=${QT_SRC_DIR}
                           --documentation-data-dir=${DOC_DATA_DIR}/webxml
                           --output-directory=${CMAKE_CURRENT_BINARY_DIR}/rst
                           --documentation-code-snippets-dir=${CODE_SNIPPET_ROOT}
                           --snippets-path-rewrite=${QT_ROOT_PATH}:${CODE_SNIPPET_ROOT}
                           --documentation-extra-sections-dir=${CMAKE_CURRENT_BINARY_DIR}/rst/extras
                           --additional-documentation=${CMAKE_CURRENT_BINARY_DIR}/rst/additionaldocs.lst
                           ${CMAKE_CURRENT_BINARY_DIR}/typesystem_doc.xml
                   WORKING_DIRECTORY ${${module}_SOURCE_DIR}
                   COMMENT "Running generator to generate documentation...")

add_custom_target("docrsts"
                  DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/rst/PySide6/QtCore/index.rst")

add_custom_target("licensedocrsts"
    COMMAND ${PYTHON_EXECUTABLE}
            ${CMAKE_CURRENT_LIST_DIR}/qtattributionsscannertorst.py
            ${CMAKE_CURRENT_LIST_DIR}/../../..
            ${CMAKE_CURRENT_BINARY_DIR}/rst/licenses.rst
    COMMENT "Creating 3rdparty license documentation..."
)

if (FULLDOCSBUILD)
    add_dependencies(apidoc docrsts licensedocrsts)
    add_dependencies(licensedocrsts docrsts)
endif()

#install files
add_custom_target(apidocinstall
    COMMAND mkdir -p ${CMAKE_INSTALL_PREFIX}/share/doc/PySide6-${BINDING_API_VERSION} && cp -rv ${CMAKE_CURRENT_BINARY_DIR}/html/* ${CMAKE_INSTALL_PREFIX}/share/doc/PySide-${BINDING_API_VERSION}
)

add_dependencies(apidocinstall apidoc)
