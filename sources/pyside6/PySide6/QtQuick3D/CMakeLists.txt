project(QtQuick3D)

set(QtQuick3D_SRC
${QtQuick3D_GEN_DIR}/qquick3d_wrapper.cpp
${QtQuick3D_GEN_DIR}/qquick3dobject_wrapper.cpp
${QtQuick3D_GEN_DIR}/qquick3dgeometry_wrapper.cpp
${QtQuick3D_GEN_DIR}/qquick3dgeometry_attribute_wrapper.cpp
${QtQuick3D_GEN_DIR}/qquick3dinstancing_wrapper.cpp
${QtQuick3D_GEN_DIR}/qquick3dinstancing_instancetableentry_wrapper.cpp
${QtQuick3D_GEN_DIR}/qquick3dtexturedata_wrapper.cpp
# module is always needed
${QtQuick3D_GEN_DIR}/qtquick3d_module_wrapper.cpp
)

set(QtQuick3D_include_dirs  ${QtQuick3D_SOURCE_DIR}
                          ${QtQml_SOURCE_DIR}
                          ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Core_PRIVATE_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}OpenGL_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Network_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Qml_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Qml_PRIVATE_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Quick_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Quick3D_INCLUDE_DIRS}
                          ${libpyside_SOURCE_DIR}
                          ${QtGui_GEN_DIR}
                          ${QtOpenGL_GEN_DIR}
                          ${QtCore_GEN_DIR}
                          ${QtNetwork_GEN_DIR}
                          ${QtQml_GEN_DIR}
                          ${QtQuick_GEN_DIR}
                          ${QtQuick3D_GEN_DIR})

set(QtQuick3D_libraries pyside6
                      ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                      ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES}
                      ${Qt${QT_MAJOR_VERSION}OpenGL_LIBRARIES}
                      ${Qt${QT_MAJOR_VERSION}Network_LIBRARIES}
                      ${Qt${QT_MAJOR_VERSION}Qml_LIBRARIES}
                      ${Qt${QT_MAJOR_VERSION}Quick_LIBRARIES}
                      ${Qt${QT_MAJOR_VERSION}Quick3D_LIBRARIES})

set(QtQuick3D_deps QtGui QtOpenGL QtNetwork QtQml)

create_pyside_module(NAME QtQuick3D
    INCLUDE_DIRS QtQuick3D_include_dirs
    LIBRARIES QtQuick3D_libraries
    DEPS QtQuick3D_deps
    TYPESYSTEM_PATH QtQuick3D_SOURCE_DIR
    SOURCES QtQuick3D_SRC)
