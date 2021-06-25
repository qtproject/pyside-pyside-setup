project(QtWebEngineWidgets)

set(QtWebEngineWidgets_SRC
${QtWebEngineWidgets_GEN_DIR}/qwebengineview_wrapper.cpp
# module is always needed
${QtWebEngineWidgets_GEN_DIR}/qtwebenginewidgets_module_wrapper.cpp
)

set(QtWebEngineWidgets_include_dirs
                            ${QtWebEngineWidgets_SOURCE_DIR}
                            ${QtWebEngineWidgets_BINARY_DIR}
                            ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Widgets_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}PrintSupport_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}WebEngineWidgets_INCLUDE_DIRS}
                            ${libpyside_SOURCE_DIR}
                            ${QtCore_GEN_DIR}
                            ${QtGui_GEN_DIR}
                            ${QtWidgets_GEN_DIR}
                            ${QtWebEngineWidgets_GEN_DIR}
                            ${QtNetwork_GEN_DIR}
                            ${QtWebEngineCore_GEN_DIR}
                            ${QtPrintSupport_GEN_DIR}
                            )
set(QtWebEngineWidgets_libraries      pyside6
                            ${Qt${QT_MAJOR_VERSION}WebEngineWidgets_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Network_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Widgets_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}PrintSupport_LIBRARIES}
                            )
set(QtWebEngineWidgets_deps QtGui QtWidgets QtNetwork QtPrintSupport QtWebEngineCore)
create_pyside_module(NAME QtWebEngineWidgets
                     INCLUDE_DIRS QtWebEngineWidgets_include_dirs
                     LIBRARIES QtWebEngineWidgets_libraries
                     DEPS QtWebEngineWidgets_deps
                     TYPESYSTEM_PATH QtWebEngineWidgets_SOURCE_DIR
                     SOURCES QtWebEngineWidgets_SRC)

