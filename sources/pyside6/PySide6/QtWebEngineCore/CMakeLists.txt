project(QtWebEngineCore)

set(QtWebEngineCore_SRC
${QtWebEngineCore_GEN_DIR}/qwebenginecertificateerror_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginecontextmenurequest_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginecookiestore_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginedownloadrequest_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginefullscreenrequest_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginehistory_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginehistoryitem_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginehistorymodel_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginehttprequest_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginepage_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebengineprofile_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginescript_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginescriptcollection_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebenginesettings_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebengineurlrequestinfo_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebengineurlrequestinterceptor_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebengineurlrequestjob_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebengineurlscheme_wrapper.cpp
${QtWebEngineCore_GEN_DIR}/qwebengineurlschemehandler_wrapper.cpp
# module is always needed
${QtWebEngineCore_GEN_DIR}/qtwebenginecore_module_wrapper.cpp
)

set(QtWebEngineCore_include_dirs
                            ${QtWebEngineCore_SOURCE_DIR}
                            ${QtWebEngineCore_BINARY_DIR}
                            ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Widgets_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}PrintSupport_INCLUDE_DIRS}
                            ${libpyside_SOURCE_DIR}
                            ${QtCore_GEN_DIR}
                            ${QtGui_GEN_DIR}
                            ${QtWidgets_GEN_DIR}
                            ${QtNetwork_GEN_DIR}
                            ${QtPrintSupport_GEN_DIR}
                            )
set(QtWebEngineCore_libraries pyside6
                            ${Qt${QT_MAJOR_VERSION}WebEngineCore_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Widgets_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Network_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}PrintSupport_LIBRARIES}
                            )
set(QtWebEngineCore_deps QtCore QtGui QtNetwork QtPrintSupport)
create_pyside_module(NAME QtWebEngineCore
                     INCLUDE_DIRS QtWebEngineCore_include_dirs
                     LIBRARIES QtWebEngineCore_libraries
                     DEPS QtWebEngineCore_deps
                     TYPESYSTEM_PATH QtWebEngineCore_SOURCE_DIR
                     SOURCES QtWebEngineCore_SRC)

