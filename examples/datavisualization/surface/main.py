# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtDataVisualization import Q3DSurface
from PySide6.QtGui import QBrush, QIcon, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QHBoxLayout,
                               QLabel, QMessageBox, QPushButton, QRadioButton,
                               QSizePolicy, QSlider, QVBoxLayout, QWidget)

from surfacegraph import SurfaceGraph

THEMES = ["Qt", "Primary Colors", "Digia", "Stone Moss", "Army Blue", "Retro",
          "Ebony", "Isabelle"]


class Window(QWidget):
    def __init__(self, graph, parent=None):
        super().__init__(parent)
        self._graph = graph
        self._container = QWidget.createWindowContainer(self._graph, self,
                                                        Qt.Widget)

        screen_size = self._graph.screen().size()
        self._container.setMinimumSize(QSize(screen_size.width() / 2,
                                       screen_size.height() / 1.6))
        self._container.setMaximumSize(screen_size)
        self._container.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Expanding)
        self._container.setFocusPolicy(Qt.StrongFocus)

        h_layout = QHBoxLayout(self)
        v_layout = QVBoxLayout()
        h_layout.addWidget(self._container, 1)
        h_layout.addLayout(v_layout)
        v_layout.setAlignment(Qt.AlignTop)

        model_group_box = QGroupBox("Model")

        sqrt_sin_model_rb = QRadioButton(self)
        sqrt_sin_model_rb.setText("Sqrt& Sin")
        sqrt_sin_model_rb.setChecked(False)

        height_map_model_rb = QRadioButton(self)
        height_map_model_rb.setText("Height Map")
        height_map_model_rb.setChecked(False)

        model_vbox = QVBoxLayout()
        model_vbox.addWidget(sqrt_sin_model_rb)
        model_vbox.addWidget(height_map_model_rb)
        model_group_box.setLayout(model_vbox)

        selection_group_box = QGroupBox("Selection Mode")

        mode_none_rb = QRadioButton(self)
        mode_none_rb.setText("No selection")
        mode_none_rb.setChecked(False)

        mode_item_rb = QRadioButton(self)
        mode_item_rb.setText("Item")
        mode_item_rb.setChecked(False)

        mode_slice_row_rb = QRadioButton(self)
        mode_slice_row_rb.setText("Row Slice")
        mode_slice_row_rb.setChecked(False)

        mode_slice_column_rb = QRadioButton(self)
        mode_slice_column_rb.setText("Column Slice")
        mode_slice_column_rb.setChecked(False)

        selection_vbox = QVBoxLayout()
        selection_vbox.addWidget(mode_none_rb)
        selection_vbox.addWidget(mode_item_rb)
        selection_vbox.addWidget(mode_slice_row_rb)
        selection_vbox.addWidget(mode_slice_column_rb)
        selection_group_box.setLayout(selection_vbox)

        axis_min_slider_x = QSlider(Qt.Orientation.Horizontal, self)
        axis_min_slider_x.setMinimum(0)
        axis_min_slider_x.setTickInterval(1)
        axis_min_slider_x.setEnabled(True)
        axis_max_slider_x = QSlider(Qt.Orientation.Horizontal, self)
        axis_max_slider_x.setMinimum(1)
        axis_max_slider_x.setTickInterval(1)
        axis_max_slider_x.setEnabled(True)
        axis_min_slider_z = QSlider(Qt.Orientation.Horizontal, self)
        axis_min_slider_z.setMinimum(0)
        axis_min_slider_z.setTickInterval(1)
        axis_min_slider_z.setEnabled(True)
        axis_max_slider_z = QSlider(Qt.Orientation.Horizontal, self)
        axis_max_slider_z.setMinimum(1)
        axis_max_slider_z.setTickInterval(1)
        axis_max_slider_z.setEnabled(True)

        theme_list = QComboBox(self)
        theme_list.addItems(THEMES)

        color_group_box = QGroupBox("Custom gradient")

        gr_bto_y = QLinearGradient(0, 0, 1, 100)
        gr_bto_y.setColorAt(1.0, Qt.black)
        gr_bto_y.setColorAt(0.67, Qt.blue)
        gr_bto_y.setColorAt(0.33, Qt.red)
        gr_bto_y.setColorAt(0.0, Qt.yellow)

        pm = QPixmap(24, 100)
        pmp = QPainter(pm)
        pmp.setBrush(QBrush(gr_bto_y))
        pmp.setPen(Qt.NoPen)
        pmp.drawRect(0, 0, 24, 100)
        pmp.end()

        gradient_bto_ypb = QPushButton(self)
        gradient_bto_ypb.setIcon(QIcon(pm))
        gradient_bto_ypb.setIconSize(QSize(24, 100))

        gr_gto_r = QLinearGradient(0, 0, 1, 100)
        gr_gto_r.setColorAt(1.0, Qt.darkGreen)
        gr_gto_r.setColorAt(0.5, Qt.yellow)
        gr_gto_r.setColorAt(0.2, Qt.red)
        gr_gto_r.setColorAt(0.0, Qt.darkRed)
        pmp.begin(pm)
        pmp.setBrush(QBrush(gr_gto_r))
        pmp.drawRect(0, 0, 24, 100)
        pmp.end()

        gradient_gto_rpb = QPushButton(self)
        gradient_gto_rpb.setIcon(QIcon(pm))
        gradient_gto_rpb.setIconSize(QSize(24, 100))

        color_hbox = QHBoxLayout()
        color_hbox.addWidget(gradient_bto_ypb)
        color_hbox.addWidget(gradient_gto_rpb)
        color_group_box.setLayout(color_hbox)

        v_layout.addWidget(model_group_box)
        v_layout.addWidget(selection_group_box)
        v_layout.addWidget(QLabel("Column range"))
        v_layout.addWidget(axis_min_slider_x)
        v_layout.addWidget(axis_max_slider_x)
        v_layout.addWidget(QLabel("Row range"))
        v_layout.addWidget(axis_min_slider_z)
        v_layout.addWidget(axis_max_slider_z)
        v_layout.addWidget(QLabel("Theme"))
        v_layout.addWidget(theme_list)
        v_layout.addWidget(color_group_box)

        self._modifier = SurfaceGraph(self._graph)

        height_map_model_rb.toggled.connect(self._modifier.enable_height_map_model)
        sqrt_sin_model_rb.toggled.connect(self._modifier.enable_sqrt_sin_model)
        mode_none_rb.toggled.connect(self._modifier.toggle_mode_none)
        mode_item_rb.toggled.connect(self._modifier.toggle_mode_item)
        mode_slice_row_rb.toggled.connect(self._modifier.toggle_mode_slice_row)
        mode_slice_column_rb.toggled.connect(self._modifier.toggle_mode_slice_column)
        axis_min_slider_x.valueChanged.connect(self._modifier.adjust_xmin)
        axis_max_slider_x.valueChanged.connect(self._modifier.adjust_xmax)
        axis_min_slider_z.valueChanged.connect(self._modifier.adjust_zmin)
        axis_max_slider_z.valueChanged.connect(self._modifier.adjust_zmax)
        theme_list.currentIndexChanged[int].connect(self._modifier.change_theme)
        gradient_bto_ypb.pressed.connect(self._modifier.set_black_to_yellow_gradient)
        gradient_gto_rpb.pressed.connect(self._modifier.set_green_to_red_gradient)

        self._modifier.set_axis_min_slider_x(axis_min_slider_x)
        self._modifier.set_axis_max_slider_x(axis_max_slider_x)
        self._modifier.set_axis_min_slider_z(axis_min_slider_z)
        self._modifier.set_axis_max_slider_z(axis_max_slider_z)

        sqrt_sin_model_rb.setChecked(True)
        mode_item_rb.setChecked(True)
        theme_list.setCurrentIndex(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    graph = Q3DSurface()
    if not graph.hasContext():
        msg_box = QMessageBox()
        msg_box.setText("Couldn't initialize the OpenGL context.")
        msg_box.exec()
        sys.exit(-1)

    window = Window(graph)
    window.setWindowTitle("Surface example")
    window.show()

    sys.exit(app.exec())
