# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the networkauth redditclient example from Qt v6.x"""

from argparse import ArgumentParser, RawTextHelpFormatter
import sys

from PySide6.QtWidgets import QApplication, QListView

from redditmodel import RedditModel


if __name__ == '__main__':
    parser = ArgumentParser(description='Qt Reddit client example',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('--client', '-i', type=str, help='Client id')
    options = parser.parse_args()
    if not options.client:
        print('Specify a client id', file=sys.stderr)
        sys.exit(-1)

    app = QApplication(sys.argv)
    view = QListView()
    model = RedditModel(options.client)
    view.setModel(model)
    view.show()
    sys.exit(app.exec())
