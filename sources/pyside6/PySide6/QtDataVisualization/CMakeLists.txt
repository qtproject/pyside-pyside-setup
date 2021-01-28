project(QtDataVisualization)

set(QtDataVisualization_SRC
${QtDataVisualization_GEN_DIR}/qabstract3daxis_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qcategory3daxis_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qlogvalue3daxisformatter_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qvalue3daxis_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qvalue3daxisformatter_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qabstract3dseries_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qabstractdataproxy_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qbar3dseries_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qbardataitem_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qbardataproxy_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qcustom3ditem_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qcustom3dlabel_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qcustom3dvolume_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qheightmapsurfacedataproxy_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qitemmodelbardataproxy_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qitemmodelscatterdataproxy_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qitemmodelsurfacedataproxy_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qscatter3dseries_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qscatterdataitem_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qscatterdataproxy_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qsurface3dseries_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qsurfacedataitem_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qsurfacedataproxy_wrapper.cpp
${QtDataVisualization_GEN_DIR}/q3dbars_wrapper.cpp
${QtDataVisualization_GEN_DIR}/q3dcamera_wrapper.cpp
${QtDataVisualization_GEN_DIR}/q3dlight_wrapper.cpp
${QtDataVisualization_GEN_DIR}/q3dobject_wrapper.cpp
${QtDataVisualization_GEN_DIR}/q3dscatter_wrapper.cpp
${QtDataVisualization_GEN_DIR}/q3dscene_wrapper.cpp
${QtDataVisualization_GEN_DIR}/q3dsurface_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qabstract3dgraph_wrapper.cpp
${QtDataVisualization_GEN_DIR}/q3dinputhandler_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qabstract3dinputhandler_wrapper.cpp
${QtDataVisualization_GEN_DIR}/qtouch3dinputhandler_wrapper.cpp
${QtDataVisualization_GEN_DIR}/q3dtheme_wrapper.cpp
# module is always needed
${QtDataVisualization_GEN_DIR}/qtdatavisualization_module_wrapper.cpp
)

set(QtDataVisualization_include_dirs ${QtDataVisualization_SOURCE_DIR}
                          ${QtDataVisualization_BINARY_DIR}
                          ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}DataVisualization_INCLUDE_DIRS}
                          ${libpyside_SOURCE_DIR}
                          ${QtCore_GEN_DIR}
                          ${QtGui_GEN_DIR})

set(QtDataVisualization_libraries    pyside6
                          ${Qt${QT_MAJOR_VERSION}DataVisualization_LIBRARIES}
                          ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                          ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES})

set(QtDataVisualization_deps QtCore QtGui)

create_pyside_module(NAME QtDataVisualization
                     INCLUDE_DIRS QtDataVisualization_include_dirs
                     LIBRARIES QtDataVisualization_libraries
                     DEPS QtDataVisualization_deps
                     TYPESYSTEM_PATH QtDataVisualization_SOURCE_DIR
                     SOURCES QtDataVisualization_SRC)
