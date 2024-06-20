# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from functools import partial

from PySide6.QtWebEngineCore import (QWebEngineFindTextResult, QWebEnginePage)
from PySide6.QtWidgets import QLabel, QMenu, QTabBar, QTabWidget
from PySide6.QtGui import QCursor, QIcon, QKeySequence, QPixmap
from PySide6.QtCore import QUrl, Qt, Signal, Slot

from webpage import WebPage
from webview import WebView


class TabWidget(QTabWidget):
    link_hovered = Signal(str)
    load_progress = Signal(int)
    title_changed = Signal(str)
    url_changed = Signal(QUrl)
    fav_icon_changed = Signal(QIcon)
    web_action_enabled_changed = Signal(QWebEnginePage.WebAction, bool)
    dev_tools_requested = Signal(QWebEnginePage)
    find_text_finished = Signal(QWebEngineFindTextResult)

    def __init__(self, profile, parent):
        super().__init__(parent)
        self._profile = profile
        tab_bar = self.tabBar()
        tab_bar.setTabsClosable(True)
        tab_bar.setSelectionBehaviorOnRemove(QTabBar.SelectPreviousTab)
        tab_bar.setMovable(True)
        tab_bar.setContextMenuPolicy(Qt.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self.handle_context_menu_requested)
        tab_bar.tabCloseRequested.connect(self.close_tab)
        tab_bar.tabBarDoubleClicked.connect(self._tabbar_double_clicked)
        self.setDocumentMode(True)
        self.setElideMode(Qt.ElideRight)

        self.currentChanged.connect(self.handle_current_changed)

        if profile.isOffTheRecord():
            icon = QLabel(self)
            pixmap = QPixmap(":ninja.png")
            icon.setPixmap(pixmap.scaledToHeight(tab_bar.height()))
            w = icon.pixmap().width()
            self.setStyleSheet(f"QTabWidget.tab-bar {{ left: {w}px; }}")

    @Slot(int)
    def _tabbar_double_clicked(self, index):
        if index == -1:
            self.create_tab()

    def handle_current_changed(self, index):
        if index != -1:
            view = self.web_view(index)
            if view.url():
                view.setFocus()
            self.title_changed.emit(view.title())
            self.load_progress.emit(view.load_progress())
            self.url_changed.emit(view.url())
            self.fav_icon_changed.emit(view.fav_icon())
            e = view.is_web_action_enabled(QWebEnginePage.Back)
            self.web_action_enabled_changed.emit(QWebEnginePage.Back, e)
            e = view.is_web_action_enabled(QWebEnginePage.Forward)
            self.web_action_enabled_changed.emit(QWebEnginePage.Forward, e)
            e = view.is_web_action_enabled(QWebEnginePage.Stop)
            self.web_action_enabled_changed.emit(QWebEnginePage.Stop, e)
            e = view.is_web_action_enabled(QWebEnginePage.Reload)
            self.web_action_enabled_changed.emit(QWebEnginePage.Reload, e)
        else:
            self.title_changed.emit("")
            self.load_progress.emit(0)
            self.url_changed.emit(QUrl())
            self.fav_icon_changed.emit(QIcon())
            self.web_action_enabled_changed.emit(QWebEnginePage.Back, False)
            self.web_action_enabled_changed.emit(QWebEnginePage.Forward, False)
            self.web_action_enabled_changed.emit(QWebEnginePage.Stop, False)
            self.web_action_enabled_changed.emit(QWebEnginePage.Reload, True)

    def handle_context_menu_requested(self, pos):
        menu = QMenu()
        menu.addAction("New &Tab", QKeySequence.AddTab, self.create_tab)
        index = self.tabBar().tabAt(pos)
        if index != -1:
            action = menu.addAction("Clone Tab")
            action.triggered.connect(partial(self.clone_tab, index))
            menu.addSeparator()
            action = menu.addAction("Close Tab")
            action.setShortcut(QKeySequence.Close)
            action.triggered.connect(partial(self.close_tab, index))
            action = menu.addAction("Close Other Tabs")
            action.triggered.connect(partial(self.close_other_tabs, index))
            menu.addSeparator()
            action = menu.addAction("Reload Tab")
            action.setShortcut(QKeySequence.Refresh)
            action.triggered.connect(partial(self.reload_tab, index))
        else:
            menu.addSeparator()

        menu.addAction("Reload All Tabs", self.reload_all_tabs)
        menu.exec(QCursor.pos())

    def current_web_view(self):
        return self.web_view(self.currentIndex())

    def web_view(self, index):
        return self.widget(index)

    def _title_changed(self, web_view, title):
        index = self.indexOf(web_view)
        if index != -1:
            self.setTabText(index, title)
            self.setTabToolTip(index, title)

        if self.currentIndex() == index:
            self.title_changed.emit(title)

    def _url_changed(self, web_view, url):
        index = self.indexOf(web_view)
        if index != -1:
            self.tabBar().setTabData(index, url)
        if self.currentIndex() == index:
            self.url_changed.emit(url)

    def _load_progress(self, web_view, progress):
        if self.currentIndex() == self.indexOf(web_view):
            self.load_progress.emit(progress)

    def _fav_icon_changed(self, web_view, icon):
        index = self.indexOf(web_view)
        if index != -1:
            self.setTabIcon(index, icon)
        if self.currentIndex() == index:
            self.fav_icon_changed.emit(icon)

    def _link_hovered(self, web_view, url):
        if self.currentIndex() == self.indexOf(web_view):
            self.link_hovered.emit(url)

    def _webaction_enabled_changed(self, webView, action, enabled):
        if self.currentIndex() == self.indexOf(webView):
            self.web_action_enabled_changed.emit(action, enabled)

    def _window_close_requested(self, webView):
        index = self.indexOf(webView)
        if webView.page().inspectedPage():
            self.window().close()
        elif index >= 0:
            self.close_tab(index)

    def _find_text_finished(self, webView, result):
        if self.currentIndex() == self.indexOf(webView):
            self.find_text_finished.emit(result)

    def setup_view(self, webView):
        web_page = webView.page()
        webView.titleChanged.connect(partial(self._title_changed, webView))
        webView.urlChanged.connect(partial(self._url_changed, webView))
        webView.loadProgress.connect(partial(self._load_progress, webView))
        web_page.linkHovered.connect(partial(self._link_hovered, webView))
        webView.fav_icon_changed.connect(partial(self._fav_icon_changed, webView))
        webView.web_action_enabled_changed.connect(partial(self._webaction_enabled_changed,
                                                           webView))
        web_page.windowCloseRequested.connect(partial(self._window_close_requested,
                                                      webView))
        webView.dev_tools_requested.connect(self.dev_tools_requested)
        web_page.findTextFinished.connect(partial(self._find_text_finished,
                                                  webView))

    def create_tab(self):
        web_view = self.create_background_tab()
        self.setCurrentWidget(web_view)
        return web_view

    def create_background_tab(self):
        web_view = WebView()
        web_page = WebPage(self._profile, web_view)
        web_view.set_page(web_page)
        self.setup_view(web_view)
        index = self.addTab(web_view, "(Untitled)")
        self.setTabIcon(index, web_view.fav_icon())
        # Workaround for QTBUG-61770
        web_view.resize(self.currentWidget().size())
        web_view.show()
        return web_view

    def reload_all_tabs(self):
        for i in range(0, self.count()):
            self.web_view(i).reload()

    def close_other_tabs(self, index):
        for i in range(index, self.count() - 1, -1):
            self.close_tab(i)
        for i in range(-1, index - 1, -1):
            self.close_tab(i)

    def close_tab(self, index):
        view = self.web_view(index)
        if view:
            has_focus = view.hasFocus()
            self.removeTab(index)
            if has_focus and self.count() > 0:
                self.current_web_view().setFocus()
            if self.count() == 0:
                self.create_tab()
            view.deleteLater()

    def clone_tab(self, index):
        view = self.web_view(index)
        if view:
            tab = self.create_tab()
            tab.setUrl(view.url())

    def set_url(self, url):
        view = self.current_web_view()
        if view:
            view.setUrl(url)
            view.setFocus()

    def trigger_web_page_action(self, action):
        web_view = self.current_web_view()
        if web_view:
            web_view.triggerPageAction(action)
            web_view.setFocus()

    def next_tab(self):
        next = self.currentIndex() + 1
        if next == self.count():
            next = 0
        self.setCurrentIndex(next)

    def previous_tab(self):
        next = self.currentIndex() - 1
        if next < 0:
            next = self.count() - 1
        self.setCurrentIndex(next)

    def reload_tab(self, index):
        view = self.web_view(index)
        if view:
            view.reload()
