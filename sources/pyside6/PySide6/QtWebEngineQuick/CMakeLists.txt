project(QtWebEngineQuick)

set(QtWebEngineQuick_SRC
${QtWebEngineQuick_GEN_DIR}/qtwebenginequick_wrapper.cpp
# module is always needed
${QtWebEngineQuick_GEN_DIR}/qtwebenginequick_module_wrapper.cpp
)

set(QtWebEngineQuick_include_dirs
                            ${QtWebEngineQuick_SOURCE_DIR}
                            ${QtWebEngineQuick_BINARY_DIR}
                            ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                            ${libpyside_SOURCE_DIR}
                            ${QtCore_GEN_DIR}
                            )

set(QtWebEngineQuick_libraries pyside6
                            ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                            ${Qt${QT_MAJOR_VERSION}WebEngineQuick_LIBRARIES}
                            )

set(QtWebEngineQuick_deps QtCore)

create_pyside_module(NAME QtWebEngineQuick
                     INCLUDE_DIRS QtWebEngineQuick_include_dirs
                     LIBRARIES QtWebEngineQuick_libraries
                     DEPS QtWebEngineQuick_deps
                     TYPESYSTEM_PATH QtWebEngineQuick_SOURCE_DIR
                     SOURCES QtWebEngineQuick_SRC)
