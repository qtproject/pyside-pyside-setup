#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

from PySide6.QtCore import (Qt, QEvent, QObject, QTimer, Signal, Slot)
from PySide6.QtGui import (QColor, QFont, QPalette)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow, QVBoxLayout, QWidget)

import outcome
import signal
import sys
import traceback
import trio
from random import randint


class MainWindow(QMainWindow):

    set_num = Signal(int, QColor)

    def __init__(self, rows, cols):
        super().__init__()

        self.rows = rows
        self.cols = cols

        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        layout_outer = QVBoxLayout(widget_central)

        self.widget_outer_text = QLabel()
        font = QFont()
        font.setPointSize(14)
        self.widget_outer_text.setFont(font)
        layout_outer.addWidget(self.widget_outer_text, alignment=Qt.AlignmentFlag.AlignCenter)

        widget_inner_grid = QWidget()
        layout_outer.addWidget(widget_inner_grid, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout_inner_grid = QGridLayout(widget_inner_grid)
        k = 1
        for i in range(self.rows):
            for j in range(self.cols):
                box = QLabel(f"{k}")
                self.layout_inner_grid.addWidget(box, i, j, Qt.AlignmentFlag.AlignCenter)
                k += 1

        self.set_num.connect(self.set_num_handler)

    @Slot(int, QColor)
    def set_num_handler(self, i, color):
        row = int((i - 1) / self.cols)
        col = (i - 1) - (row * self.cols)
        widget = self.layout_inner_grid.itemAtPosition(row, col).widget()

        font = QFont()
        font.setWeight(QFont.Bold)
        palette = QPalette()
        palette.setColor(QPalette.WindowText, color)
        widget.setFont(font)
        widget.setPalette(palette)


class Eratosthenes():

    """ This Sieve of Eratosthenes runs on a configurable tick (default
        0.1 seconds). At each tick, a new subroutine will be created
        that will check multiples of the next prime number. Each of
        these subroutines also operates on the same tick. """

    def __init__(self, num, window, tick=0.1):
        self.num = num
        self.sieve = [True] * self.num
        self.base = 0
        self.window = window
        self.tick = tick
        self.coroutines = []
        self.done = False
        self.nursery = None

    async def start(self):
        async with trio.open_nursery() as self.nursery:
            self.nursery.start_soon(self.update_text)
            while self.base <= self.num / 2:
                await trio.sleep(self.tick)
                for i in range(self.base + 1, self.num):
                    if self.sieve[i]:
                        self.base = i
                        break
                self.nursery.start_soon(self.mark_number, self.base + 1)
            while sum(self.coroutines) > 0:
                await trio.sleep(self.tick)
            self.done = True

    async def mark_number(self, base):
        id = len(self.coroutines)
        self.coroutines.append(1)
        color = QColor(randint(64, 192), randint(64, 192), randint(64, 192))
        for i in range(2 * base, self.num + 1, base):
            if self.sieve[i - 1]:
                self.sieve[i - 1] = False
                self.window.set_num.emit(i, color)
            await trio.sleep(self.tick)
        self.coroutines[id] = 0

    async def update_text(self):
        while not self.done:
            await trio.sleep(self.tick)
            if int(trio.lowlevel.current_clock().current_time() + self.tick) % 2:
                text = "⚙️ ...Calculating prime numbers... ⚙️"
            else:
                text = "👩‍💻 ...Hacking the universe... 👩‍💻"
            self.window.widget_outer_text.setText(text)

        self.window.widget_outer_text.setText(
            "🥳 Congratulations! You found all the prime numbers and solved mathematics. 🥳"
        )


class AsyncHelper(QObject):

    trigger_signal = Signal()

    class ReenterQtObject(QObject):
        """ This is a QObject to which an event will be posted, allowing
            Trio to resume when the event is handled. event.fn() is the
            next entry point of the Trio event loop. """
        def event(self, event):
            if event.type() == QEvent.User + 1:
                event.fn()
                return True
            return False

    class ReenterQtEvent(QEvent):
        """ This is the QEvent that will be handled by the ReenterQtObject.
            self.fn is the next entry point of the Trio event loop. """
        def __init__(self, fn):
            super().__init__(QEvent.Type(QEvent.User + 1))
            self.fn = fn

    def __init__(self, entry=None):
        super().__init__()
        self.reenter_qt = self.ReenterQtObject()
        self.entry = entry

    def set_entry(self, entry):
        self.entry = entry

    @Slot()
    def launch_guest_run(self):
        """ To use Trio and Qt together, one must run the Trio event
            loop as a "guest" inside the Qt "host" event loop. """
        if not self.entry:
            raise Exception("No entry point for the Trio guest run was set.")
        trio.lowlevel.start_guest_run(
            self.entry,
            run_sync_soon_threadsafe=self.next_guest_run_schedule,
            done_callback=self.trio_done_callback,
        )

    def next_guest_run_schedule(self, fn):
        """ This function serves to re-schedule the guest (Trio) event
            loop inside the host (Qt) event loop. It is called by Trio
            at the end of an event loop run in order to relinquish back
            to Qt's event loop. By posting an event on the Qt event loop
            that contains Trio's next entry point, it ensures that Trio's
            event loop will be scheduled again by Qt. """
        QApplication.postEvent(self.reenter_qt, self.ReenterQtEvent(fn))

    def trio_done_callback(self, outcome_):
        """ This function is called by Trio when its event loop has
            finished. """
        if isinstance(outcome_, outcome.Error):
            error = outcome_.error
            traceback.print_exception(type(error), error, error.__traceback__)


if __name__ == "__main__":
    rows = 40
    cols = 40
    num = rows * cols

    app = QApplication(sys.argv)
    main_window = MainWindow(rows, cols)
    eratosthenes = Eratosthenes(num, main_window)
    async_helper = AsyncHelper(entry=eratosthenes.start)

    # This establishes the entry point for the Trio guest run. It varies
    # depending on how and when its event loop is to be triggered, e.g.,
    # from the beginning (as here) or rather at a specific moment like
    # a button press.
    QTimer.singleShot(0, async_helper.launch_guest_run)

    main_window.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.exec()
