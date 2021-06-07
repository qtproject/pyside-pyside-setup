project(QtDesigner)

qt_wrap_cpp(QtDesigner_static_src "${pyside6_SOURCE_DIR}/qpydesignerextensions.h")
list(APPEND QtDesigner_static_src "${QtDesigner_SOURCE_DIR}/qpydesignercustomwidgetcollection.cpp")

set(QtDesigner_SRC
${QtDesigner_GEN_DIR}/qabstractextensionfactory_wrapper.cpp
${QtDesigner_GEN_DIR}/qabstractextensionmanager_wrapper.cpp
${QtDesigner_GEN_DIR}/qabstractformbuilder_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesigneractioneditorinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignercontainerextension_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignercustomwidgetcollectioninterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignercustomwidgetinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerdnditeminterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerdynamicpropertysheetextension_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerformeditorinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerformwindowcursorinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerformwindowinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerformwindowmanagerinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerformwindowtoolinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignermembersheetextension_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerobjectinspectorinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerpropertyeditorinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerpropertysheetextension_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignertaskmenuextension_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerwidgetboxinterface_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerwidgetboxinterface_category_wrapper.cpp
${QtDesigner_GEN_DIR}/qdesignerwidgetboxinterface_widget_wrapper.cpp
${QtDesigner_GEN_DIR}/qextensionmanager_wrapper.cpp
${QtDesigner_GEN_DIR}/qextensionfactory_wrapper.cpp
${QtDesigner_GEN_DIR}/qformbuilder_wrapper.cpp
${QtDesigner_GEN_DIR}/qpydesignercustomwidgetcollection_wrapper.cpp
${QtDesigner_GEN_DIR}/qpydesignercontainerextension_wrapper.cpp
${QtDesigner_GEN_DIR}/qpydesignermembersheetextension_wrapper.cpp
${QtDesigner_GEN_DIR}/qpydesignerpropertysheetextension_wrapper.cpp
${QtDesigner_GEN_DIR}/qpydesignertaskmenuextension_wrapper.cpp

# module is always needed
${QtDesigner_GEN_DIR}/qtdesigner_module_wrapper.cpp
)

configure_file("${QtDesigner_SOURCE_DIR}/QtDesigner_global.pre.h.in"
               "${QtDesigner_BINARY_DIR}/QtDesigner_global.pre.h" @ONLY)
configure_file("${QtDesigner_SOURCE_DIR}/QtDesigner_global.post.h.in"
               "${QtDesigner_BINARY_DIR}/QtDesigner_global.post.h" @ONLY)

set(QtDesigner_include_dirs ${QtDesigner_SOURCE_DIR}
                            ${QtDesigner_BINARY_DIR}
                            ${QtCore_GEN_DIR}
                            ${QtGui_GEN_DIR}
                            ${QtWidgets_GEN_DIR}
                            )
set(QtDesigner_libraries pyside6
                         ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                         ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES}
                         ${Qt${QT_MAJOR_VERSION}Widgets_LIBRARIES}
                         ${Qt${QT_MAJOR_VERSION}Designer_LIBRARIES}
                         )
set(QtDesigner_deps QtWidgets)

create_pyside_module(NAME QtDesigner
                     INCLUDE_DIRS QtDesigner_include_dirs
                     LIBRARIES QtDesigner_libraries
                     DEPS QtDesigner_deps
                     TYPESYSTEM_PATH QtDesigner_SOURCE_DIR
                     SOURCES QtDesigner_SRC
                     STATIC_SOURCES QtDesigner_static_src
                     TYPESYSTEM_NAME ${QtDesigner_BINARY_DIR}/typesystem_designer.xml)

install(FILES ${pyside6_SOURCE_DIR}/qpydesignerextensions.h DESTINATION include/PySide6/QtDesigner)
