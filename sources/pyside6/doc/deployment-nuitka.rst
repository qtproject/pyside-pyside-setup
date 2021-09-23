|project| & Nuitka
##################

`Nuitka <https://nuitka.net/>`_ lets you compile your python application into a
stand-alone executable. Besides being a Python compiler which provides a fair
acceleration, it has the side-effect of acting as an installer as well.
Nuitka supports Linux, macOS and Windows.

For more details, see the `official documentation <https://nuitka.net/pages/overview.html>`_.

Preparation
===========

Install `Nuitka` via **pip** with the following command::

    pip3 install nuitka

After installation, the `nuitka3` binary is located in your virtual environment's `bin/`
directory, or where your Python executable is located.
Alternatively, you can also run::

    python3 -m nuitka

to achieve the same effect.

Freeze an application
=====================

`Nuitka` has many options that you can use. To list them all, run `nuitka3 -h`.

To simply compile a project, you can run::

    nuitka3 <programname>

There are two main features:

 * the option to place it in a directory containing the libraries
   (`--standalone)
 * the option to package the whole project (including shared libraries) into one executable file
   (`--onefile`)

If you use these options, you need to specify `--plugin-enable=pyside6`.

Run an example
--------------

Now, consider the following script, named `hello.py`::

    import sys
    import random
    from PySide6.QtWidgets import (QApplication, QLabel, QPushButton,
                                   QVBoxLayout, QWidget)
    from PySide6.QtCore import Slot, Qt

    class MyWidget(QWidget):
        def __init__(self):
            QWidget.__init__(self)

            self.hello = ["Hallo Welt", "你好，世界", "Hei maailma",
                "Hola Mundo", "Привет мир"]

            self.button = QPushButton("Click me!")
            self.text = QLabel("Hello World")
            self.text.setAlignment(Qt.AlignCenter)

            self.layout = QVBoxLayout()
            self.layout.addWidget(self.text)
            self.layout.addWidget(self.button)
            self.setLayout(self.layout)

            # Connecting the signal
            self.button.clicked.connect(self.magic)

        @Slot()
        def magic(self):
            self.text.setText(random.choice(self.hello))

    if __name__ == "__main__":
        app = QApplication(sys.argv)

        widget = MyWidget()
        widget.resize(800, 600)
        widget.show()

        sys.exit(app.exec())

You don't have to copy this script. You find it as `examples/installer_test/hello.py`.

The command line to proceed looks like this::

    nuitka3 examples/installer_test/hello.py

This process creates an executable `hello.bin` and a directory hello.build that you
don't need. You can execute the binary directly.

In order to create a bundle which can be copied onto a machine without any pre-existing
installation, run::

    nuitka3 --standalone --plugin-enable=pyside6 examples/installer_test/hello.py

This creates an application `hello.dist/hello` that contains everything needed to run.

To run the application, go to `hello.dist/` and run the program::

    cd hello.dist
    ./hello

Use the `--onefile` option if you prefer to have everything bundled into one executable, without
the shared libraries next to it. First you need to install::

    pip3 install zstandard

for data compression. Then you can run

    nuitka3 --onefile --plugin-enable=pyside6 examples/installer_test/hello.py

This process takes a bit longer, but in the end you have one executable `hello.bin`::

    ./hello.bin


Some Caveats
============


Nuitka issue on macOS
---------------------

Nuitka currently has a problem with the macOS bundle files on current macOS versions.
That has the effect that `--standalone` and `--onefile` create a crashing application.
Older versions which don't have the recent macOS API changes from 2020 will work.
We are currently trying to fix that problem.
