project(QtWebEngineQuick)

set(QtWebEngineQuick_SRC
${QtWebEngineQuick_GEN_DIR}/qquickwebengineprofile_wrapper.cpp
${QtWebEngineQuick_GEN_DIR}/qtwebenginequick_wrapper.cpp
# module is always needed
${QtWebEngineQuick_GEN_DIR}/qtwebenginequick_module_wrapper.cpp
)

set(QtWebEngineQuick_include_dirs
                            ${QtWebEngineQuick_SOURCE_DIR}
                            ${QtWebEngineQuick_BINARY_DIR}
                            ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                            ${Qt${QT_MAJOR_VERSION}Qml_INCLUDE_DIRS}
                            ${libpyside_SOURCE_DIR}
                            ${QtCore_GEN_DIR}
                            ${QtNetwork_GEN_DIR}
                            ${QtQml_GEN_DIR}
                            )

set(QtWebEngineQuick_libraries pyside6
                            ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Network_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}Qml_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}WebEngineQuick_LIBRARIES}
                            )

set(QtWebEngineQuick_deps QtQml QtNetwork QtCore)

create_pyside_module(NAME QtWebEngineQuick
                     INCLUDE_DIRS QtWebEngineQuick_include_dirs
                     LIBRARIES QtWebEngineQuick_libraries
                     DEPS QtWebEngineQuick_deps
                     TYPESYSTEM_PATH QtWebEngineQuick_SOURCE_DIR
                     SOURCES QtWebEngineQuick_SRC)
