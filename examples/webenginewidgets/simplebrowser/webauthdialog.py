# Converted from webauthdialog.cpp

# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from ui_webauthdialog import Ui_WebAuthDialog

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QButtonGroup,
                               QScrollArea, QWidget, QDialogButtonBox,
                               QSizePolicy, QRadioButton)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineCore import QWebEngineWebAuthUxRequest


class WebAuthDialog(QDialog):

    def __init__(self, request, parent=None):
        super().__init__(parent)

        self.uxRequest = request
        self.uiWebAuthDialog = Ui_WebAuthDialog()
        self.uiWebAuthDialog.setupUi(self)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.scroll_area = QScrollArea(self)
        self.select_account_widget = QWidget(self)
        self.scroll_area.setWidget(self.select_account_widget)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.select_account_widget.resize(400, 150)

        self.select_account_layout = QVBoxLayout(self.select_account_widget)
        self.uiWebAuthDialog.m_mainVerticalLayout.addWidget(self.scroll_area)
        self.select_account_layout.setAlignment(Qt.AlignTop)

        self.update_display()

        self.uiWebAuthDialog.buttonBox.rejected.connect(self.onCancelRequest)
        self.uiWebAuthDialog.buttonBox.accepted.connect(self.onAcceptRequest)

        button = self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Retry)
        button.clicked.connect(self.onRetry)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def __del__(self):
        for button in self.button_group.buttons():
            button.deleteLater()

        if self.button_group:
            self.button_group.deleteLater()
            self.button_group = None

        if self.uiWebAuthDialog:
            del self.uiWebAuthDialog
            self.uiWebAuthDialog = None

        if self.scroll_area:
            self.scroll_area.deleteLater()
            self.scroll_area = None

    def update_display(self):
        state = self.uxRequest.state()
        if state == QWebEngineWebAuthUxRequest.WebAuthUxState.SelectAccount:
            self.setupSelectAccountUI()
        elif state == QWebEngineWebAuthUxRequest.WebAuthUxState.CollectPin:
            self.setupCollectPinUI()
        elif state == QWebEngineWebAuthUxRequest.WebAuthUxState.FinishTokenCollection:
            self.setupFinishCollectTokenUI()
        elif state == QWebEngineWebAuthUxRequest.WebAuthUxState.RequestFailed:
            self.setupErrorUI()

        self.adjustSize()

    def setupSelectAccountUI(self):
        self.uiWebAuthDialog.m_headingLabel.setText(self.tr("Choose a Passkey"))
        self.uiWebAuthDialog.m_description.setText(self.tr("Which passkey do you want to use for ")
                                                   + self.uxRequest.relyingPartyId()
                                                   + self.tr("? "))
        self.uiWebAuthDialog.m_pinGroupBox.setVisible(False)
        self.uiWebAuthDialog.m_mainVerticalLayout.removeWidget(self.uiWebAuthDialog.m_pinGroupBox)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Retry).setVisible(False)

        self.clearSelectAccountButtons()
        self.scroll_area.setVisible(True)
        self.select_account_widget.resize(self.width(), self.height())
        userNames = self.uxRequest.userNames()
        # Create radio buttons for each name
        for name in userNames:
            radioButton = QRadioButton(name)
            self.select_account_layout.addWidget(radioButton)
            self.button_group.addButton(radioButton)

        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("Ok"))
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Ok).setVisible(True)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Cancel).setVisible(True)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Retry).setVisible(False)

    def setupFinishCollectTokenUI(self):

        self.clearSelectAccountButtons()
        self.uiWebAuthDialog.m_headingLabel.setText(self.tr("Use your security key with")
                                                    + self.uxRequest.relyingPartyId())
        self.uiWebAuthDialog.m_description.setText(
            self.tr("Touch your security key again to complete the request."))
        self.uiWebAuthDialog.m_pinGroupBox.setVisible(False)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Ok).setVisible(False)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Retry).setVisible(False)
        self.scroll_area.setVisible(False)

    def setupCollectPinUI(self):

        self.clearSelectAccountButtons()
        self.uiWebAuthDialog.m_mainVerticalLayout.addWidget(self.uiWebAuthDialog.m_pinGroupBox)
        self.uiWebAuthDialog.m_pinGroupBox.setVisible(True)
        self.uiWebAuthDialog.m_confirmPinLabel.setVisible(False)
        self.uiWebAuthDialog.m_confirmPinLineEdit.setVisible(False)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("Next"))
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Ok).setVisible(True)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Cancel).setVisible(True)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Retry).setVisible(False)
        self.scroll_area.setVisible(False)

        pinRequestInfo = self.uxRequest.pinRequest()

        if pinRequestInfo.reason == QWebEngineWebAuthUxRequest.PinEntryReason.Challenge:
            self.uiWebAuthDialog.m_headingLabel.setText(self.tr("PIN Required"))
            self.uiWebAuthDialog.m_description.setText(
                self.tr("Enter the PIN for your security key"))
            self.uiWebAuthDialog.m_confirmPinLabel.setVisible(False)
            self.uiWebAuthDialog.m_confirmPinLineEdit.setVisible(False)
        else:
            if pinRequestInfo.reason == QWebEngineWebAuthUxRequest.PinEntryReason.Set:
                self.uiWebAuthDialog.m_headingLabel.setText(self.tr("New PIN Required"))
                self.uiWebAuthDialog.m_description.setText(
                    self.tr("Set new PIN for your security key"))
            else:
                self.uiWebAuthDialog.m_headingLabel.setText(self.tr("Change PIN Required"))
                self.uiWebAuthDialog.m_description.setText(
                    self.tr("Change PIN for your security key"))

            self.uiWebAuthDialog.m_confirmPinLabel.setVisible(True)
            self.uiWebAuthDialog.m_confirmPinLineEdit.setVisible(True)

        errorDetails = ""

        if pinRequestInfo.error == QWebEngineWebAuthUxRequest.PinEntryError.InternalUvLocked:
            errorDetails = self.tr("Internal User Verification Locked ")
        elif pinRequestInfo.error == QWebEngineWebAuthUxRequest.PinEntryError.WrongPin:
            errorDetails = self.tr("Wrong PIN")
        elif pinRequestInfo.error == QWebEngineWebAuthUxRequest.PinEntryError.TooShort:
            errorDetails = self.tr("Too Short")
        elif pinRequestInfo.error == QWebEngineWebAuthUxRequest.PinEntryError.InvalidCharacters:
            errorDetails = self.tr("Invalid Characters")
        elif pinRequestInfo.error == QWebEngineWebAuthUxRequest.PinEntryError.SameAsCurrentPin:
            errorDetails = self.tr("Same as current PIN")

        if errorDetails:
            errorDetails += f" {pinRequestInfo.remainingAttempts} attempts remaining"

        self.uiWebAuthDialog.m_pinEntryErrorLabel.setText(errorDetails)

    def onCancelRequest(self):

        self.uxRequest.cancel()

    def onAcceptRequest(self):

        state = self.uxRequest.state()
        if state == QWebEngineWebAuthUxRequest.WebAuthUxState.SelectAccount:
            if self.button_group.checkedButton():
                self.uxRequest.setSelectedAccount(self.button_group.checkedButton().text())
        elif state == QWebEngineWebAuthUxRequest.WebAuthUxState.CollectPin:
            self.uxRequest.setPin(self.uiWebAuthDialog.m_pinLineEdit.text())

    def setupErrorUI(self):

        self.clearSelectAccountButtons()
        error_description = ""
        error_heading = self.tr("Something went wrong")
        isVisibleRetry = False

        state = self.uxRequest.requestFailureReason()
        failure_reason = QWebEngineWebAuthUxRequest.RequestFailureReason

        if state == failure_reason.Timeout:
            error_description = self.tr("Request Timeout")
        elif state == failure_reason.KeyNotRegistered:
            error_description = self.tr("Key not registered")
        elif state == failure_reason.KeyAlreadyRegistered:
            error_description = self.tr("You already registered self device."
                                        "Try again with device")
            isVisibleRetry = True
        elif state == failure_reason.SoftPinBlock:
            error_description = self.tr(
                "The security key is locked because the wrong PIN was entered too many times."
                "To unlock it, remove and reinsert it.")
            isVisibleRetry = True
        elif state == failure_reason.HardPinBlock:
            error_description = self.tr(
                "The security key is locked because the wrong PIN was entered too many times."
                " Yo'll need to reset the security key.")
        elif state == failure_reason.AuthenticatorRemovedDuringPinEntry:
            error_description = self.tr(
                "Authenticator removed during verification. Please reinsert and try again")
        elif state == failure_reason.AuthenticatorMissingResidentKeys:
            error_description = self.tr("Authenticator doesn't have resident key support")
        elif state == failure_reason.AuthenticatorMissingUserVerification:
            error_description = self.tr("Authenticator missing user verification")
        elif state == failure_reason.AuthenticatorMissingLargeBlob:
            error_description = self.tr("Authenticator missing Large Blob support")
        elif state == failure_reason.NoCommonAlgorithms:
            error_description = self.tr("Authenticator missing Large Blob support")
        elif state == failure_reason.StorageFull:
            error_description = self.tr("Storage Full")
        elif state == failure_reason.UserConsentDenied:
            error_description = self.tr("User consent denied")
        elif state == failure_reason.WinUserCancelled:
            error_description = self.tr("User Cancelled Request")

        self.uiWebAuthDialog.m_headingLabel.setText(error_heading)
        self.uiWebAuthDialog.m_description.setText(error_description)
        self.uiWebAuthDialog.m_description.adjustSize()
        self.uiWebAuthDialog.m_pinGroupBox.setVisible(False)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Ok).setVisible(False)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Retry).setVisible(isVisibleRetry)
        if isVisibleRetry:
            self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Retry).setFocus()
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Cancel).setVisible(True)
        self.uiWebAuthDialog.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Close"))
        self.scroll_area.setVisible(False)

    def onRetry(self):
        self.uxRequest.retry()

    def clearSelectAccountButtons(self):
        buttons = self.button_group.buttons()

        for radio_button in buttons:
            self.select_account_layout.removeWidget(radio_button)
            self.button_group.removeButton(radio_button)
            radio_button.deleteLater()
