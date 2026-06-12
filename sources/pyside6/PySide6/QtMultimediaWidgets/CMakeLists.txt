# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: BSD-3-Clause

set(QtMultimediaWidgets_SRC
${QtMultimediaWidgets_GEN_DIR}/qgraphicsvideoitem_wrapper.cpp
${QtMultimediaWidgets_GEN_DIR}/qvideowidget_wrapper.cpp
# module is always needed
${QtMultimediaWidgets_GEN_DIR}/qtmultimediawidgets_module_wrapper.cpp
)

set(QtMultimediaWidgets_include_dirs
    ${QtCore_GEN_DIR}
    ${QtGui_GEN_DIR}
    ${QtNetwork_GEN_DIR}
    ${QtWidgets_GEN_DIR}
    ${QtMultimedia_GEN_DIR}
)

set(QtMultimediaWidgets_deps
    QtCore
    QtGui
    QtNetwork
    QtWidgets
    QtMultimedia
)

set(QtMultimediaWidgets_libraries
    Qt::MultimediaWidgets
)

create_pyside_module(NAME QtMultimediaWidgets
                     INCLUDE_DIRS QtMultimediaWidgets_include_dirs
                     LIBRARIES QtMultimediaWidgets_libraries
                     DEPS QtMultimediaWidgets_deps
                     TYPESYSTEM_PATH CMAKE_CURRENT_SOURCE_DIR
                     SOURCES QtMultimediaWidgets_SRC)
