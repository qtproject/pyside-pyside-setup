project(QtCharts)

set(QtCharts_SRC
${QtCharts_GEN_DIR}/qabstractaxis_wrapper.cpp
${QtCharts_GEN_DIR}/qabstractbarseries_wrapper.cpp
${QtCharts_GEN_DIR}/qabstractseries_wrapper.cpp
${QtCharts_GEN_DIR}/qarealegendmarker_wrapper.cpp
${QtCharts_GEN_DIR}/qareaseries_wrapper.cpp
${QtCharts_GEN_DIR}/qbarcategoryaxis_wrapper.cpp
${QtCharts_GEN_DIR}/qbarlegendmarker_wrapper.cpp
${QtCharts_GEN_DIR}/qbarmodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qbarseries_wrapper.cpp
${QtCharts_GEN_DIR}/qbarset_wrapper.cpp
${QtCharts_GEN_DIR}/qboxplotlegendmarker_wrapper.cpp
${QtCharts_GEN_DIR}/qboxplotmodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qboxplotseries_wrapper.cpp
${QtCharts_GEN_DIR}/qboxset_wrapper.cpp
${QtCharts_GEN_DIR}/qcandlesticklegendmarker_wrapper.cpp
${QtCharts_GEN_DIR}/qcandlestickmodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qcandlestickseries_wrapper.cpp
${QtCharts_GEN_DIR}/qcandlestickset_wrapper.cpp
${QtCharts_GEN_DIR}/qcategoryaxis_wrapper.cpp
${QtCharts_GEN_DIR}/qchart_wrapper.cpp
${QtCharts_GEN_DIR}/qchartview_wrapper.cpp
${QtCharts_GEN_DIR}/qdatetimeaxis_wrapper.cpp
${QtCharts_GEN_DIR}/qhbarmodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qhboxplotmodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qhcandlestickmodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qhorizontalbarseries_wrapper.cpp
${QtCharts_GEN_DIR}/qhorizontalpercentbarseries_wrapper.cpp
${QtCharts_GEN_DIR}/qhorizontalstackedbarseries_wrapper.cpp
${QtCharts_GEN_DIR}/qhpiemodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qhxymodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qlegend_wrapper.cpp
${QtCharts_GEN_DIR}/qlegendmarker_wrapper.cpp
${QtCharts_GEN_DIR}/qlineseries_wrapper.cpp
${QtCharts_GEN_DIR}/qlogvalueaxis_wrapper.cpp
${QtCharts_GEN_DIR}/qpercentbarseries_wrapper.cpp
${QtCharts_GEN_DIR}/qpielegendmarker_wrapper.cpp
${QtCharts_GEN_DIR}/qpiemodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qpieseries_wrapper.cpp
${QtCharts_GEN_DIR}/qpieslice_wrapper.cpp
${QtCharts_GEN_DIR}/qpolarchart_wrapper.cpp
${QtCharts_GEN_DIR}/qscatterseries_wrapper.cpp
${QtCharts_GEN_DIR}/qsplineseries_wrapper.cpp
${QtCharts_GEN_DIR}/qstackedbarseries_wrapper.cpp
${QtCharts_GEN_DIR}/qvalueaxis_wrapper.cpp
${QtCharts_GEN_DIR}/qvbarmodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qvboxplotmodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qvcandlestickmodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qvpiemodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qvxymodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qxylegendmarker_wrapper.cpp
${QtCharts_GEN_DIR}/qxymodelmapper_wrapper.cpp
${QtCharts_GEN_DIR}/qxyseries_wrapper.cpp
# module is always needed
${QtCharts_GEN_DIR}/qtcharts_module_wrapper.cpp
)

set(QtCharts_include_dirs ${QtCharts_SOURCE_DIR}
                          ${QtCharts_BINARY_DIR}
                          ${Qt${QT_MAJOR_VERSION}Core_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Gui_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Widgets_INCLUDE_DIRS}
                          ${Qt${QT_MAJOR_VERSION}Charts_INCLUDE_DIRS}
                          ${libpyside_SOURCE_DIR}
                          ${QtCore_GEN_DIR}
                          ${QtGui_GEN_DIR}
                          ${QtWidgets_GEN_DIR})

set(QtCharts_libraries    pyside6
                          ${Qt${QT_MAJOR_VERSION}Charts_LIBRARIES}
                          ${Qt${QT_MAJOR_VERSION}Core_LIBRARIES}
                          ${Qt${QT_MAJOR_VERSION}Gui_LIBRARIES}
                          ${Qt${QT_MAJOR_VERSION}Widgets_LIBRARIES})

set(QtCharts_deps QtCore QtGui QtWidgets)

create_pyside_module(NAME QtCharts
                     INCLUDE_DIRS QtCharts_include_dirs
                     LIBRARIES QtCharts_libraries
                     DEPS QtCharts_deps
                     TYPESYSTEM_PATH QtCharts_SOURCE_DIR
                     SOURCES QtCharts_SRC)
