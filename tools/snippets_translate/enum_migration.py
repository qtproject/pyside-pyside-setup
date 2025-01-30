# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

MOUSE_BUTTONS = ("NoButton", "AllButtons", "LeftButton", "RightButton", "MiddleButton",
                 "BackButton", "XButton", "ExtraButton", "ForwardButton", "ExtraButton",
                 "TaskButton")

MODIFIERS = ("NoModifier", "ShiftModifier", "ControlModifier", "AltModifier",
             "MetaModifier", "KeypadModifier", "GroupSwitchModifier")

GLOBAL_COLORS = ("white", "black", "red", "darkRed", "green", "darkGreen", "blue",
                 "darkBlue", "cyan", "darkCyan", "magenta", "darkMagenta", "yellow",
                 "darkYellow", "gray", "darkGray", "lightGray", "transparent")

ALIGN_VALUES = ("AlignHCenter", "AlignLeft", "AlignCenter", "AlignRight", "AlignVCenter",
                "AlignTop", "AlignBotton", "AlignJustify", "AlignBaseline", "AlignAbsolute",
                "AlignLeading", "Trailing")


def _get_replacements():
    result = [
        ("Qt::Key_", "Qt.Key.Key_"),
        ("Qt::CTRL", "Qt.Modifier.CTRL"),
        ("Qt::ALT", "Qt.Modifier.ALT"),
        ("Qt::CaseInsensitive", "Qt.CaseSensitivity.CaseInsensitive"),
        ("Qt::CaseSensitive", "Qt.CaseSensitivity.CaseSensitive"),
        ("QImage::Format_", "QImage.Format.Format_"),
        ("Qt::WA_DeleteOnClose", "Qt.WidgetAttribute.WA_DeleteOnClose"),
        ("QQuickView::Ready", "QQuickView.Status.Ready"),
        ("QQuickView::Error", "QQuickView.Status.Error"),
        ("QQuickView::Loading", "QQuickView.Status.Loading"),
        ("QPainter::Antialiasing", "QPainter.RenderHint.Antialiasing"),
        ("QQuickView::SizeRootObjectToView", "QQuickView.ResizeMode.SizeRootObjectToView"),
        ("QQuickView::SizeViewToRootObject", "QQuickView.ResizeMode.SizeViewToRootObject"),
        ("QKeySequence::", "QKeySequence.StandardKey."),
        ("QEvent::", "QEvent.Type.")
    ]
    for c in GLOBAL_COLORS:
        result.append((f"Qt::{c}", f"Qt.GlobalColor.{c}"))
    for b in ("Close", "Ok", "Cancel", "Yes", "No"):
        result.append((f"QDialogButtonBox::{b}", f"QDialogButtonBox.StandardButton.{b}"))
        result.append((f"QMessageBox::{b}", f"QMessageBox.StandardButton.{b}"))
    for b in MOUSE_BUTTONS:
        result.append((f"Qt::{b}", f"Qt.MouseButton.{b}"))
    for a in ALIGN_VALUES:
        result.append((f"Qt::{a}", f"Qt.AlignmentFlag.{a}"))
    for m in MODIFIERS:
        result.append((f"Qt::{m}", f"Qt.KeyboardModifier.{m}"))
    for m in ("ReadOnly", "WriteOnly", "Text"):
        result.append((f"QIODevice::{m}", f"QIODevice.OpenModeFlag.{m}"))
        result.append((f"QFile::{m}", f"QFile.OpenModeFlag.{m}"))
    for p in ("Preferred", "Ignored", "Fixed", "Maximum", "Minimum", "Expanding"):
        result.append((f"QSizePolicy::{p}", f"QSizePolicy.Policy.{p}"))
    for r in ("DisplayRole", "EditRole"):
        result.append((f"Qt::{r}", f"Qt.ItemDataRole.{r}"))
    for f in ("Box", "StyledPanel", "Panel", "WinPanel", "NoFrame"):
        result.append((f"QFrame::{f}", "QFrame.Shape.{f}"))
    for f in ("Raised", "Sunken"):
        result.append((f"QFrame::{f}", "QFrame.Shadow.{f}"))
    return result


REPLACEMENTS = _get_replacements()


def qualify_enums(s):
    for replacement in REPLACEMENTS:
        s = s.replace(replacement[0], replacement[1])
    return s
