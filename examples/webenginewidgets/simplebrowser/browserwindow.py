# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import (QMainWindow, QFileDialog,
                               QInputDialog, QLineEdit, QMenu, QMessageBox,
                               QProgressBar, QToolBar, QVBoxLayout, QWidget)
from PySide6.QtGui import QAction, QGuiApplication, QIcon, QKeySequence
from PySide6.QtCore import QUrl, Qt, Slot, Signal

from tabwidget import TabWidget


def remove_backspace(keys):
    result = keys.copy()
    # Chromium already handles navigate on backspace when appropriate.
    for i, key in enumerate(result):
        if (key[0].key() & Qt.Key_unknown) == Qt.Key_Backspace:
            del result[i]
            break
    return result


class BrowserWindow(QMainWindow):

    about_to_close = Signal()

    def __init__(self, browser, profile, forDevTools):
        super().__init__()

        self._progress_bar = None
        self._history_back_action = None
        self._history_forward_action = None
        self._stop_action = None
        self._reload_action = None
        self._stop_reload_action = None
        self._url_line_edit = None
        self._fav_action = None
        self._last_search = ""
        self._toolbar = None

        self._browser = browser
        self._profile = profile
        self._tab_widget = TabWidget(profile, self)

        self._stop_icon = QIcon.fromTheme(QIcon.ThemeIcon.ProcessStop,
                                          QIcon(":process-stop.png"))
        self._reload_icon = QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh,
                                            QIcon(":view-refresh.png"))

        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setFocusPolicy(Qt.ClickFocus)

        if not forDevTools:
            self._progress_bar = QProgressBar(self)

            self._toolbar = self.create_tool_bar()
            self.addToolBar(self._toolbar)
            mb = self.menuBar()
            mb.addMenu(self.create_file_menu(self._tab_widget))
            mb.addMenu(self.create_edit_menu())
            mb.addMenu(self.create_view_menu())
            mb.addMenu(self.create_window_menu(self._tab_widget))
            mb.addMenu(self.create_help_menu())

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        if not forDevTools:
            self.addToolBarBreak()

            self._progress_bar.setMaximumHeight(1)
            self._progress_bar.setTextVisible(False)
            s = "QProgressBar {border: 0px} QProgressBar.chunk {background-color: #da4453}"
            self._progress_bar.setStyleSheet(s)

            layout.addWidget(self._progress_bar)

        layout.addWidget(self._tab_widget)
        self.setCentralWidget(central_widget)

        self._tab_widget.title_changed.connect(self.handle_web_view_title_changed)
        if not forDevTools:
            self._tab_widget.link_hovered.connect(self._show_status_message)
            self._tab_widget.load_progress.connect(self.handle_web_view_load_progress)
            self._tab_widget.web_action_enabled_changed.connect(
                self.handle_web_action_enabled_changed)
            self._tab_widget.url_changed.connect(self._url_changed)
            self._tab_widget.fav_icon_changed.connect(self._fav_action.setIcon)
            self._tab_widget.dev_tools_requested.connect(self.handle_dev_tools_requested)
            self._url_line_edit.returnPressed.connect(self._address_return_pressed)
            self._tab_widget.find_text_finished.connect(self.handle_find_text_finished)

            focus_url_line_edit_action = QAction(self)
            self.addAction(focus_url_line_edit_action)
            focus_url_line_edit_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_L))
            focus_url_line_edit_action.triggered.connect(self._focus_url_lineEdit)

        self.handle_web_view_title_changed("")
        self._tab_widget.create_tab()

    @Slot(str)
    def _show_status_message(self, m):
        self.statusBar().showMessage(m)

    @Slot(QUrl)
    def _url_changed(self, url):
        self._url_line_edit.setText(url.toDisplayString())

    @Slot()
    def _address_return_pressed(self):
        url = QUrl.fromUserInput(self._url_line_edit.text())
        self._tab_widget.set_url(url)

    @Slot()
    def _focus_url_lineEdit(self):
        self._url_line_edit.setFocus(Qt.ShortcutFocusReason)

    @Slot()
    def _new_tab(self):
        self._tab_widget.create_tab()
        self._url_line_edit.setFocus()

    @Slot()
    def _close_current_tab(self):
        self._tab_widget.close_tab(self._tab_widget.currentIndex())

    @Slot()
    def _update_close_action_text(self):
        last_win = len(self._browser.windows()) == 1
        self._close_action.setText("Quit" if last_win else "Close Window")

    def sizeHint(self):
        desktop_rect = QGuiApplication.primaryScreen().geometry()
        return desktop_rect.size() * 0.9

    def create_file_menu(self, tabWidget):
        file_menu = QMenu("File")
        file_menu.addAction("&New Window", QKeySequence.New,
                            self.handle_new_window_triggered)
        file_menu.addAction("New &Incognito Window",
                            self.handle_new_incognito_window_triggered)

        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcuts(QKeySequence.AddTab)
        new_tab_action.triggered.connect(self._new_tab)
        file_menu.addAction(new_tab_action)

        file_menu.addAction("&Open File...", QKeySequence.Open,
                            self.handle_file_open_triggered)
        file_menu.addSeparator()

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcuts(QKeySequence.Close)
        close_tab_action.triggered.connect(self._close_current_tab)
        file_menu.addAction(close_tab_action)

        self._close_action = QAction("Quit", self)
        self._close_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_Q))
        self._close_action.triggered.connect(self.close)
        file_menu.addAction(self._close_action)

        file_menu.aboutToShow.connect(self._update_close_action_text)
        return file_menu

    @Slot()
    def _find_next(self):
        tab = self.current_tab()
        if tab and self._last_search:
            tab.findText(self._last_search)

    @Slot()
    def _find_previous(self):
        tab = self.current_tab()
        if tab and self._last_search:
            tab.findText(self._last_search, QWebEnginePage.FindBackward)

    def create_edit_menu(self):
        edit_menu = QMenu("Edit")
        find_action = edit_menu.addAction("Find")
        find_action.setShortcuts(QKeySequence.Find)
        find_action.triggered.connect(self.handle_find_action_triggered)

        find_next_action = edit_menu.addAction("Find Next")
        find_next_action.setShortcut(QKeySequence.FindNext)
        find_next_action.triggered.connect(self._find_next)

        find_previous_action = edit_menu.addAction("Find Previous")
        find_previous_action.setShortcut(QKeySequence.FindPrevious)
        find_previous_action.triggered.connect(self._find_previous)
        return edit_menu

    @Slot()
    def _stop(self):
        self._tab_widget.trigger_web_page_action(QWebEnginePage.Stop)

    @Slot()
    def _reload(self):
        self._tab_widget.trigger_web_page_action(QWebEnginePage.Reload)

    @Slot()
    def _zoom_in(self):
        tab = self.current_tab()
        if tab:
            tab.setZoomFactor(tab.zoomFactor() + 0.1)

    @Slot()
    def _zoom_out(self):
        tab = self.current_tab()
        if tab:
            tab.setZoomFactor(tab.zoomFactor() - 0.1)

    @Slot()
    def _reset_zoom(self):
        tab = self.current_tab()
        if tab:
            tab.setZoomFactor(1)

    @Slot()
    def _toggle_toolbar(self):
        if self._toolbar.isVisible():
            self._view_toolbar_action.setText("Show Toolbar")
            self._toolbar.close()
        else:
            self._view_toolbar_action.setText("Hide Toolbar")
            self._toolbar.show()

    @Slot()
    def _toggle_statusbar(self):
        sb = self.statusBar()
        if sb.isVisible():
            self._view_statusbar_action.setText("Show Status Bar")
            sb.close()
        else:
            self._view_statusbar_action.setText("Hide Status Bar")
            sb.show()

    def create_view_menu(self):
        view_menu = QMenu("View")
        self._stop_action = view_menu.addAction("Stop")
        shortcuts = []
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.Key_Period))
        shortcuts.append(QKeySequence(Qt.Key_Escape))
        self._stop_action.setShortcuts(shortcuts)
        self._stop_action.triggered.connect(self._stop)

        self._reload_action = view_menu.addAction("Reload Page")
        self._reload_action.setShortcuts(QKeySequence.Refresh)
        self._reload_action.triggered.connect(self._reload)

        zoom_in = view_menu.addAction("Zoom In")
        zoom_in.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_Plus))
        zoom_in.triggered.connect(self._zoom_in)

        zoom_out = view_menu.addAction("Zoom Out")
        zoom_out.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_Minus))
        zoom_out.triggered.connect(self._zoom_out)

        reset_zoom = view_menu.addAction("Reset Zoom")
        reset_zoom.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_0))
        reset_zoom.triggered.connect(self._reset_zoom)

        view_menu.addSeparator()
        self._view_toolbar_action = QAction("Hide Toolbar", self)
        self._view_toolbar_action.setShortcut("Ctrl+|")
        self._view_toolbar_action.triggered.connect(self._toggle_toolbar)
        view_menu.addAction(self._view_toolbar_action)

        self._view_statusbar_action = QAction("Hide Status Bar", self)
        self._view_statusbar_action.setShortcut("Ctrl+/")
        self._view_statusbar_action.triggered.connect(self._toggle_statusbar)
        view_menu.addAction(self._view_statusbar_action)
        return view_menu

    @Slot()
    def _emit_dev_tools_requested(self):
        tab = self.current_tab()
        if tab:
            tab.dev_tools_requested.emit(tab.page())

    def create_window_menu(self, tabWidget):
        menu = QMenu("Window")
        self._next_tab_action = QAction("Show Next Tab", self)
        shortcuts = []
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.Key_BraceRight))
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.Key_PageDown))
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.Key_BracketRight))
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.Key_Less))
        self._next_tab_action.setShortcuts(shortcuts)
        self._next_tab_action.triggered.connect(tabWidget.next_tab)

        self._previous_tab_action = QAction("Show Previous Tab", self)
        shortcuts.clear()
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.Key_BraceLeft))
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.Key_PageUp))
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.Key_BracketLeft))
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.Key_Greater))
        self._previous_tab_action.setShortcuts(shortcuts)
        self._previous_tab_action.triggered.connect(tabWidget.previous_tab)

        self._inspector_action = QAction("Open inspector in window", self)
        shortcuts.clear()
        shortcuts.append(QKeySequence(Qt.CTRL | Qt.SHIFT | Qt.Key_I))
        self._inspector_action.setShortcuts(shortcuts)
        self._inspector_action.triggered.connect(self._emit_dev_tools_requested)
        self._window_menu = menu
        menu.aboutToShow.connect(self._populate_window_menu)
        return menu

    def _populate_window_menu(self):
        menu = self._window_menu
        menu.clear()
        menu.addAction(self._next_tab_action)
        menu.addAction(self._previous_tab_action)
        menu.addSeparator()
        menu.addAction(self._inspector_action)
        menu.addSeparator()
        windows = self._browser.windows()
        index = 0
        title = self.window().windowTitle()
        for window in windows:
            action = menu.addAction(title, self.handle_show_window_triggered)
            action.setData(index)
            action.setCheckable(True)
            if window == self:
                action.setChecked(True)
            index += 1

    def create_help_menu(self):
        help_menu = QMenu("Help")
        help_menu.addAction("About Qt", qApp.aboutQt)  # noqa: F821
        return help_menu

    @Slot()
    def _back(self):
        self._tab_widget.trigger_web_page_action(QWebEnginePage.Back)

    @Slot()
    def _forward(self):
        self._tab_widget.trigger_web_page_action(QWebEnginePage.Forward)

    @Slot()
    def _stop_reload(self):
        a = self._stop_reload_action.data()
        self._tab_widget.trigger_web_page_action(QWebEnginePage.WebAction(a))

    def create_tool_bar(self):
        navigation_bar = QToolBar("Navigation")
        navigation_bar.setMovable(False)
        navigation_bar.toggleViewAction().setEnabled(False)

        self._history_back_action = QAction(self)
        back_shortcuts = remove_backspace(QKeySequence.keyBindings(QKeySequence.Back))

        # For some reason Qt doesn't bind the dedicated Back key to Back.
        back_shortcuts.append(QKeySequence(Qt.Key_Back))
        self._history_back_action.setShortcuts(back_shortcuts)
        self._history_back_action.setIconVisibleInMenu(False)
        back_icon = QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious,
                                    QIcon(":go-previous.png"))
        self._history_back_action.setIcon(back_icon)
        self._history_back_action.setToolTip("Go back in history")
        self._history_back_action.triggered.connect(self._back)
        navigation_bar.addAction(self._history_back_action)

        self._history_forward_action = QAction(self)
        fwd_shortcuts = remove_backspace(QKeySequence.keyBindings(QKeySequence.Forward))
        fwd_shortcuts.append(QKeySequence(Qt.Key_Forward))
        self._history_forward_action.setShortcuts(fwd_shortcuts)
        self._history_forward_action.setIconVisibleInMenu(False)
        next_icon = QIcon.fromTheme(QIcon.ThemeIcon.GoNext,
                                    QIcon(":go-next.png"))
        self._history_forward_action.setIcon(next_icon)
        self._history_forward_action.setToolTip("Go forward in history")
        self._history_forward_action.triggered.connect(self._forward)
        navigation_bar.addAction(self._history_forward_action)

        self._stop_reload_action = QAction(self)
        self._stop_reload_action.triggered.connect(self._stop_reload)
        navigation_bar.addAction(self._stop_reload_action)

        self._url_line_edit = QLineEdit(self)
        self._fav_action = QAction(self)
        self._url_line_edit.addAction(self._fav_action, QLineEdit.LeadingPosition)
        self._url_line_edit.setClearButtonEnabled(True)
        navigation_bar.addWidget(self._url_line_edit)

        downloads_action = QAction(self)
        downloads_action.setIcon(QIcon(":go-bottom.png"))
        downloads_action.setToolTip("Show downloads")
        navigation_bar.addAction(downloads_action)
        dw = self._browser.download_manager_widget()
        downloads_action.triggered.connect(dw.show)

        return navigation_bar

    def handle_web_action_enabled_changed(self, action, enabled):
        if action == QWebEnginePage.Back:
            self._history_back_action.setEnabled(enabled)
        elif action == QWebEnginePage.Forward:
            self._history_forward_action.setEnabled(enabled)
        elif action == QWebEnginePage.Reload:
            self._reload_action.setEnabled(enabled)
        elif action == QWebEnginePage.Stop:
            self._stop_action.setEnabled(enabled)
        else:
            print("Unhandled webActionChanged signal", file=sys.stderr)

    def handle_web_view_title_changed(self, title):
        off_the_record = self._profile.isOffTheRecord()
        suffix = ("Qt Simple Browser (Incognito)" if off_the_record
                  else "Qt Simple Browser")
        if title:
            self.setWindowTitle(f"{title} - {suffix}")
        else:
            self.setWindowTitle(suffix)

    def handle_new_window_triggered(self):
        window = self._browser.create_window()
        window._url_line_edit.setFocus()

    def handle_new_incognito_window_triggered(self):
        window = self._browser.create_window(True)
        window._url_line_edit.setFocus()

    def handle_file_open_triggered(self):
        filter = "Web Resources (*.html *.htm *.svg *.png *.gif *.svgz);;All files (*.*)"
        url, _ = QFileDialog.getOpenFileUrl(self, "Open Web Resource", "", filter)
        if url:
            self.current_tab().setUrl(url)

    def handle_find_action_triggered(self):
        if not self.current_tab():
            return
        search, ok = QInputDialog.getText(self, "Find", "Find:",
                                          QLineEdit.Normal, self._last_search)
        if ok and search:
            self._last_search = search
            self.current_tab().findText(self._last_search)

    def closeEvent(self, event):
        count = self._tab_widget.count()
        if count > 1:
            m = f"Are you sure you want to close the window?\nThere are {count} tabs open."
            ret = QMessageBox.warning(self, "Confirm close", m,
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.No)
            if ret == QMessageBox.No:
                event.ignore()
                return

        event.accept()
        self.about_to_close.emit()
        self.deleteLater()

    def tab_widget(self):
        return self._tab_widget

    def current_tab(self):
        return self._tab_widget.current_web_view()

    def handle_web_view_load_progress(self, progress):
        if 0 < progress and progress < 100:
            self._stop_reload_action.setData(QWebEnginePage.Stop)
            self._stop_reload_action.setIcon(self._stop_icon)
            self._stop_reload_action.setToolTip("Stop loading the current page")
            self._progress_bar.setValue(progress)
        else:
            self._stop_reload_action.setData(QWebEnginePage.Reload)
            self._stop_reload_action.setIcon(self._reload_icon)
            self._stop_reload_action.setToolTip("Reload the current page")
            self._progress_bar.setValue(0)

    def handle_show_window_triggered(self):
        action = self.sender()
        if action:
            offset = action.data()
            window = self._browser.windows()[offset]
            window.activateWindow()
            window.current_tab().setFocus()

    def handle_dev_tools_requested(self, source):
        page = self._browser.create_dev_tools_window().current_tab().page()
        source.setDevToolsPage(page)
        source.triggerAction(QWebEnginePage.InspectElement)

    def handle_find_text_finished(self, result):
        sb = self.statusBar()
        if result.numberOfMatches() == 0:
            sb.showMessage(f'"{self._lastSearch}" not found.')
        else:
            active = result.activeMatch()
            number = result.numberOfMatches()
            sb.showMessage(f'"{self._last_search}" found: {active}/{number}')

    def browser(self):
        return self._browser
