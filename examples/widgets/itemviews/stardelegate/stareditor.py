# Copyright (C) 2010 Hans-Peter Jansen <hpj@urpla.net>
# Copyright (C) 2011 Arun Srinivasan <rulfzid@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtWidgets import (QWidget)
from PySide6.QtGui import (QPainter)
from PySide6.QtCore import Signal

from starrating import StarRating


class StarEditor(QWidget):
    """ The custom editor for editing StarRatings. """

    # A signal to tell the delegate when we've finished editing.
    editing_finished = Signal()

    def __init__(self, parent=None):
        """ Initialize the editor object, making sure we can watch mouse
            events.
        """
        super().__init__(parent)

        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        self.star_rating = StarRating()

    def sizeHint(self):
        """ Tell the caller how big we are. """
        return self.star_rating.sizeHint()

    def paintEvent(self, event):
        """ Paint the editor, offloading the work to the StarRating class. """
        with QPainter(self) as painter:
            self.star_rating.paint(painter, self.rect(), self.palette(), isEditable=True)

    def mouseMoveEvent(self, event):
        """ As the mouse moves inside the editor, track the position and
            update the editor to display as many stars as necessary.
        """
        star = self.star_at_position(event.x())

        if (star != self.star_rating.star_count) and (star != -1):
            self.star_rating.star_count = star
            self.update()

    def mouseReleaseEvent(self, event):
        """ Once the user has clicked his/her chosen star rating, tell the
            delegate we're done editing.
        """
        self.editing_finished.emit()

    def star_at_position(self, x):
        """ Calculate which star the user's mouse cursor is currently
            hovering over.
        """
        star = (x / (self.star_rating.sizeHint().width() / self.star_rating.MAX_STAR_COUNT)) + 1
        if (star <= 0) or (star > self.star_rating.MAX_STAR_COUNT):
            return -1

        return star
