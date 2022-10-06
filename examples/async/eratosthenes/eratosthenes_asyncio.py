# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import (Qt, QEvent, QObject, QTimer, Signal, Slot)
from PySide6.QtGui import (QColor, QFont, QPalette)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow, QVBoxLayout, QWidget)

import asyncio
import outcome
import signal
import sys
import traceback
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
        self.loop = None

    def get_tick(self):
        return self.loop.time() + self.tick

    async def start(self):
        self.loop = asyncio.get_event_loop()
        asyncio.create_task(self.update_text())
        while self.base <= self.num / 2:
            await asyncio.sleep(self.tick)
            for i in range(self.base + 1, self.num):
                if self.sieve[i]:
                    self.base = i
                    break
            asyncio.create_task(self.mark_number(self.base + 1))
        while sum(self.coroutines) > 0:
            await asyncio.sleep(self.tick)
        self.done = True

    async def mark_number(self, base):
        id = len(self.coroutines)
        self.coroutines.append(1)
        color = QColor(randint(64, 192), randint(64, 192), randint(64, 192))
        for i in range(2 * base, self.num + 1, base):
            if self.sieve[i - 1]:
                self.sieve[i - 1] = False
                self.window.set_num.emit(i, color)
            await asyncio.sleep(self.tick)
        self.coroutines[id] = 0

    async def update_text(self):
        while not self.done:
            await asyncio.sleep(self.tick)
            if int(self.loop.time() + self.tick) % 2:
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
        self.loop = asyncio.new_event_loop()

    def set_entry(self, entry):
        self.entry = entry

    @Slot()
    def launch_guest_run(self):
        """ To use asyncio and Qt together, one must run the asyncio
            event loop as a "guest" inside the Qt "host" event loop. """
        if not self.entry:
            raise Exception("No entry point for the asyncio event loop was set.")
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.entry())
        self.loop.call_soon(self.next_guest_run_schedule)
        self.loop.run_forever()

    def continue_loop(self):
        """ This function is called by an event posted to the Qt event
            loop to restart the asyncio event loop. """
        self.loop.call_soon(self.next_guest_run_schedule)
        self.loop.run_forever()

    def next_guest_run_schedule(self):
        """ This function serves to pause and re-schedule the guest
            (asyncio) event loop inside the host (Qt) event loop. It is
            registered in asyncio as a callback to be called at the next
            iteration of the event loop. When this function runs, it
            first stops the asyncio event loop, then by posting an event
            on the Qt event loop, it both relinquishes to Qt's event
            loop and also schedules the asyncio event loop to run again.
            Upon handling this event, a function will be called that
            resumes the asyncio event loop. """
        self.loop.stop()
        QApplication.postEvent(self.reenter_qt, self.ReenterQtEvent(self.continue_loop))


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
