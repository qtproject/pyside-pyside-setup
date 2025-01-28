# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from functools import partial

from PySide6.QtWebEngineCore import (QWebEngineFileSystemAccessRequest,
                                     QWebEnginePage,
                                     QWebEngineWebAuthUxRequest)
from PySide6.QtWebEngineWidgets import QWebEngineView

from PySide6.QtWidgets import QDialog, QMessageBox, QStyle
from PySide6.QtGui import QIcon
from PySide6.QtNetwork import QAuthenticator
from PySide6.QtCore import QTimer, Signal, Slot, Qt

from webpage import WebPage
from webpopupwindow import WebPopupWindow
from ui_passworddialog import Ui_PasswordDialog
from ui_certificateerrordialog import Ui_CertificateErrorDialog
from webauthdialog import WebAuthDialog


def question_for_feature(feature):

    if feature == QWebEnginePage.Geolocation:
        return "Allow %1 to access your location information?"
    if feature == QWebEnginePage.MediaAudioCapture:
        return "Allow %1 to access your microphone?"
    if feature == QWebEnginePage.MediaVideoCapture:
        return "Allow %1 to access your webcam?"
    if feature == QWebEnginePage.MediaAudioVideoCapture:
        return "Allow %1 to access your microphone and webcam?"
    if feature == QWebEnginePage.MouseLock:
        return "Allow %1 to lock your mouse cursor?"
    if feature == QWebEnginePage.DesktopVideoCapture:
        return "Allow %1 to capture video of your desktop?"
    if feature == QWebEnginePage.DesktopAudioVideoCapture:
        return "Allow %1 to capture audio and video of your desktop?"
    if feature == QWebEnginePage.Notifications:
        return "Allow %1 to show notification on your desktop?"
    return ""


class WebView(QWebEngineView):

    web_action_enabled_changed = Signal(QWebEnginePage.WebAction, bool)
    fav_icon_changed = Signal(QIcon)
    dev_tools_requested = Signal(QWebEnginePage)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._load_progress = 100
        self.loadStarted.connect(self._load_started)
        self.loadProgress.connect(self._slot_load_progress)
        self.loadFinished.connect(self._load_finished)
        self.iconChanged.connect(self._emit_faviconchanged)
        self.renderProcessTerminated.connect(self._render_process_terminated)

        self._error_icon = QIcon(":dialog-error.png")
        self._loading_icon = QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh,
                                             QIcon(":view-refresh.png"))
        self._default_icon = QIcon(":text-html.png")
        self.auth_dialog = None

    @Slot()
    def _load_started(self):
        self._load_progress = 0
        self.fav_icon_changed.emit(self.fav_icon())

    @Slot(int)
    def _slot_load_progress(self, progress):
        self._load_progress = progress

    @Slot()
    def _emit_faviconchanged(self):
        self.fav_icon_changed.emit(self.fav_icon())

    @Slot(bool)
    def _load_finished(self, success):
        self._load_progress = 100 if success else -1
        self._emit_faviconchanged()

    @Slot(QWebEnginePage.RenderProcessTerminationStatus, int)
    def _render_process_terminated(self, termStatus, statusCode):
        status = ""
        if termStatus == QWebEnginePage.NormalTerminationStatus:
            status = "Render process normal exit"
        elif termStatus == QWebEnginePage.AbnormalTerminationStatus:
            status = "Render process abnormal exit"
        elif termStatus == QWebEnginePage.CrashedTerminationStatus:
            status = "Render process crashed"
        elif termStatus == QWebEnginePage.KilledTerminationStatus:
            status = "Render process killed"

        m = f"Render process exited with code: {statusCode:#x}\nDo you want to reload the page?"
        btn = QMessageBox.question(self.window(), status, m)
        if btn == QMessageBox.Yes:
            QTimer.singleShot(0, self.reload)

    def set_page(self, page):
        old_page = self.page()
        if old_page and isinstance(old_page, WebPage):
            old_page.createCertificateErrorDialog.disconnect(self.handle_certificate_error)
            old_page.authenticationRequired.disconnect(self.handle_authentication_required)
            old_page.featurePermissionRequested.disconnect(self.handle_feature_permission_requested)
            old_page.proxyAuthenticationRequired.disconnect(
                self.handle_proxy_authentication_required)
            old_page.registerProtocolHandlerRequested.disconnect(
                self.handle_register_protocol_handler_requested)
            old_page.webAuthUxRequested.disconnect(self.handle_web_auth_ux_requested)
            old_page.fileSystemAccessRequested.disconnect(self.handle_file_system_access_requested)

        self.create_web_action_trigger(page, QWebEnginePage.WebAction.Forward)
        self.create_web_action_trigger(page, QWebEnginePage.WebAction.Back)
        self.create_web_action_trigger(page, QWebEnginePage.WebAction.Reload)
        self.create_web_action_trigger(page, QWebEnginePage.WebAction.Stop)
        super().setPage(page)
        page.create_certificate_error_dialog.connect(self.handle_certificate_error)
        page.authenticationRequired.connect(self.handle_authentication_required)
        page.featurePermissionRequested.connect(self.handle_feature_permission_requested)
        page.proxyAuthenticationRequired.connect(self.handle_proxy_authentication_required)
        page.registerProtocolHandlerRequested.connect(
            self.handle_register_protocol_handler_requested)
        page.webAuthUxRequested.connect(self.handle_web_auth_ux_requested)
        page.fileSystemAccessRequested.connect(self.handle_file_system_access_requested)

    def load_progress(self):
        return self._load_progress

    def _emit_webactionenabledchanged(self, action, webAction):
        self.web_action_enabled_changed.emit(webAction, action.isEnabled())

    def create_web_action_trigger(self, page, webAction):
        action = page.action(webAction)
        action.changed.connect(partial(self._emit_webactionenabledchanged, action, webAction))

    def is_web_action_enabled(self, webAction):
        return self.page().action(webAction).isEnabled()

    def fav_icon(self):
        fav_icon = self.icon()
        if not fav_icon.isNull():
            return fav_icon
        if self._load_progress < 0:
            return self._error_icon
        if self._load_progress < 100:
            return self._loading_icon
        return self._default_icon

    def createWindow(self, type):
        main_window = self.window()
        if not main_window:
            return None

        if type == QWebEnginePage.WebBrowserTab:
            return main_window.tab_widget().create_tab()

        if type == QWebEnginePage.WebBrowserBackgroundTab:
            return main_window.tab_widget().create_background_tab()

        if type == QWebEnginePage.WebBrowserWindow:
            return main_window.browser().createWindow().current_tab()

        if type == QWebEnginePage.WebDialog:
            view = WebView()
            WebPopupWindow(view, self.page().profile(), self.window())
            view.dev_tools_requested.connect(self.dev_tools_requested)
            return view

        return None

    @Slot()
    def _emit_devtools_requested(self):
        self.dev_tools_requested.emit(self.page())

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        actions = menu.actions()
        inspect_action = self.page().action(QWebEnginePage.InspectElement)
        if inspect_action in actions:
            inspect_action.setText("Inspect element")
        else:
            vs = self.page().action(QWebEnginePage.ViewSource)
            if vs not in actions:
                menu.addSeparator()

            action = menu.addAction("Open inspector in new window")
            action.triggered.connect(self._emit_devtools_requested)

        menu.popup(event.globalPos())

    def handle_certificate_error(self, error):
        w = self.window()
        dialog = QDialog(w)
        dialog.setModal(True)

        certificate_dialog = Ui_CertificateErrorDialog()
        certificate_dialog.setupUi(dialog)
        certificate_dialog.m_iconLabel.setText("")
        icon = QIcon(w.style().standardIcon(QStyle.SP_MessageBoxWarning, 0, w))
        certificate_dialog.m_iconLabel.setPixmap(icon.pixmap(32, 32))
        certificate_dialog.m_errorLabel.setText(error.description())
        dialog.setWindowTitle("Certificate Error")

        if dialog.exec() == QDialog.Accepted:
            error.acceptCertificate()
        else:
            error.rejectCertificate()

    def handle_authentication_required(self, requestUrl, auth):
        w = self.window()
        dialog = QDialog(w)
        dialog.setModal(True)

        password_dialog = Ui_PasswordDialog()
        password_dialog.setupUi(dialog)

        password_dialog.m_iconLabel.setText("")
        icon = QIcon(w.style().standardIcon(QStyle.SP_MessageBoxQuestion, 0, w))
        password_dialog.m_iconLabel.setPixmap(icon.pixmap(32, 32))

        url_str = requestUrl.toString().toHtmlEscaped()
        realm = auth.realm()
        m = f'Enter username and password for "{realm}" at {url_str}'
        password_dialog.m_infoLabel.setText(m)
        password_dialog.m_infoLabel.setWordWrap(True)

        if dialog.exec() == QDialog.Accepted:
            auth.setUser(password_dialog.m_userNameLineEdit.text())
            auth.setPassword(password_dialog.m_passwordLineEdit.text())
        else:
            # Set authenticator null if dialog is cancelled
            auth = QAuthenticator()

    def handle_feature_permission_requested(self, securityOrigin, feature):
        title = "Permission Request"
        host = securityOrigin.host()
        question = question_for_feature(feature).replace("%1", host)
        w = self.window()
        page = self.page()
        if question and QMessageBox.question(w, title, question) == QMessageBox.Yes:
            page.setFeaturePermission(securityOrigin, feature,
                                      QWebEnginePage.PermissionGrantedByUser)
        else:
            page.setFeaturePermission(securityOrigin, feature,
                                      QWebEnginePage.PermissionDeniedByUser)

    def handle_proxy_authentication_required(self, url, auth, proxyHost):
        w = self.window()
        dialog = QDialog(w)
        dialog.setModal(True)

        password_dialog = Ui_PasswordDialog()
        password_dialog.setupUi(dialog)

        password_dialog.m_iconLabel.setText("")

        icon = QIcon(w.style().standardIcon(QStyle.SP_MessageBoxQuestion, 0, w))
        password_dialog.m_iconLabel.setPixmap(icon.pixmap(32, 32))

        proxy = proxyHost.toHtmlEscaped()
        password_dialog.m_infoLabel.setText(f'Connect to proxy "{proxy}" using:')
        password_dialog.m_infoLabel.setWordWrap(True)

        if dialog.exec() == QDialog.Accepted:
            auth.setUser(password_dialog.m_userNameLineEdit.text())
            auth.setPassword(password_dialog.m_passwordLineEdit.text())
        else:
            # Set authenticator null if dialog is cancelled
            auth = QAuthenticator()

    def handle_web_auth_ux_requested(self, request):
        if self.auth_dialog:
            self.auth_dialog.deleteLater()

        self.auth_dialog = WebAuthDialog(request, self.window())
        self.auth_dialog.setModal(False)
        self.auth_dialog.setWindowFlags(self.auth_dialog.windowFlags()
                                        & ~Qt.WindowContextHelpButtonHint)

        request.stateChanged.connect(self.on_state_changed)
        self.auth_dialog.show()

    def on_state_changed(self, state):
        if state in (QWebEngineWebAuthUxRequest.WebAuthUxState.Completed,
                     QWebEngineWebAuthUxRequest.WebAuthUxState.Cancelled):
            if self.auth_dialog:
                self.auth_dialog.deleteLater()
                self.auth_dialog = None
        else:
            if self.auth_dialog:
                self.auth_dialog.update_display()

    def handle_register_protocol_handler_requested(self, request):
        host = request.origin().host()
        m = f"Allow {host} to open all {request.scheme()} links?"
        answer = QMessageBox.question(self.window(), "Permission Request", m)
        if answer == QMessageBox.Yes:
            request.accept()
        else:
            request.reject()

    def handle_file_system_access_requested(self, request):
        access_type = ""
        type = request.accessFlags()
        if type == QWebEngineFileSystemAccessRequest.Read:
            access_type = "read"
        elif type == QWebEngineFileSystemAccessRequest.Write:
            access_type = "write"
        elif type == (QWebEngineFileSystemAccessRequest.Read
                      | QWebEngineFileSystemAccessRequest.Write):
            access_type = "read and write"
        host = request.origin().host()
        path = request.filePath().toString()
        t = "File system access request"
        m = f"Give {host} {access_type} access to {path}?"
        answer = QMessageBox.question(self.window(), t, m)
        if answer == QMessageBox.Yes:
            request.accept()
        else:
            request.reject()
