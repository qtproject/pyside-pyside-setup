.. _whyqtforpython:

Why Qt for Python?
==================

.. raw:: html

    <div style="float: right; padding-left: 20px; max-width: 30%;
    background-color: #e9eff5; padding-top: 5px;">
      <img src="../../_images/tiobe.png"
          style="width: 90%;"
          alt="TIOBE index for Python" />
      <p style="font-size: 80%;">
      Screenshot from
      <a href="https://www.tiobe.com/tiobe-index/python/">tiobe.com/tiobe-index/python</a>,
      on 2021.09.06
      </p>
    </div>

To answer this question we need to take a step back, and talk a bit about
languages.

Python has been around for almost the same amount of years that Qt has,
and similarly it has been growing, and transforming to become the most used,
loved, and demanded language for many programming areas.

Currently (2021), it's rare to be aware of Machine Learning and Artificial
Intelligence, without having heard of Python. Similarly, when we hear about
Data Science/Analysis/Engineering we know that it is most probably related
to Python.

One can validate this statements by public surveys that have been showing
the evolution and preference of the Python language, like the StackOverflow
Surveys of the lasts years:

+----------------------+-----------+-----------+-----------+
|                      | 2019_     | 2020_     | 2021_     |
+======================+===========+===========+===========+
| Most Loved Language  | 2nd place | 3rd place | 6th place |
+----------------------+-----------+-----------+-----------+
| Most Wanted Language | 1st place | 1st place | 1st place |
+----------------------+-----------+-----------+-----------+

and the `TIOBE index`_ (image on the right).

It's natural to think that this sources might not be enough to judge the
language in general terms, but it certainly highlights a trend among
developers around the world.

Lowering the Qt Barrier
-----------------------

Veteran C++ developers will have no problem with setting up a Qt
application from scratch, or even manage to understand a different
code base written with Qt. In addition, many teams are multidisciplinary,
and other project/company developers might not be fluent in C++.

Python has been luring people into programming, and for the same reason
it's not uncommon that even people with a different background are able
to write code, meaning that different teams are enabled to speak
"the same language".

Creating Qt applications in Python requires only a few lines of code,
and not much configuration is required to execute it. As an /unfair/
example, let's check the code of a simple hello world application:


.. panels::
   :container: container-lg

   :column: col-lg-6 p-2

   .. tabbed:: C++ Header

       .. code-block:: cpp

          #ifndef MAINWINDOW_H
          #define MAINWINDOW_H

          #include <QMainWindow>
          #include <QPushButton>

          class MainWindow : public QMainWindow
          {
              Q_OBJECT
              public:
                  MainWindow(QWidget *parent = nullptr);
              private slots:
                  void handleButton();
              private:
                  QPushButton *m_button;
          };

          #endif // MAINWINDOW_H

   .. tabbed:: C++ Implementation

       .. code-block:: cpp

          #include "mainwindow.h"

          MainWindow::MainWindow(QWidget *parent)
             : QMainWindow(parent)
          {
              m_button = new QPushButton("My Button", this);
              connect(m_button, SIGNAL(clicked()), this,
                      SLOT(handleButton()));
          }

          void MainWindow::handleButton()
          {
              m_button->setText("Ready");
          }

   .. tabbed:: C++ Main

       .. code-block:: cpp

          #include <QApplication>
          #include "mainwindow.h"

          int main(int argc, char *argv[])
          {
              QApplication app(argc, argv);
              MainWindow mainWindow;
              mainWindow.show();
              return app.exec(d);
          }

   ---
   :column: col-lg-6 p-2

   .. tabbed:: Python

      .. code-block:: python

         import sys
         from pyside6.QtWidgets import (QApplication, QMainWindow,
                                        QPushButton)

         class MainWindow(QMainWindow):
             def __init__(self, parent=None):
                 QMainWindow.__init__(self, parent)
                 self.button = QPushButton("My Button", self)
                 self.button.clicked.connect(self.handleButton)

             def handleButton(self):
                 self.button.setText("Ready")

         if __name__ == "__main__":
             app = QApplication([])
             mainWindow = MainWindow()
             mainWindow.show()
             sys.exit(app.exec())

It's fair to say that most of the boilerplate code is provided by many
good IDEs, like QtCreator, but using external tools certainly requires
some practice to use them and get familiarized.

Unity Makes Strength
--------------------

In our mission to enable more developers to enter the Qt World, it's
important to note that this doesn't imply C++ developers are forgotten.

Together with the bindings, Qt for Python provides our binding generator,
Shiboken (Check :ref:`whatisshiboken`), whose functionality has
extensibly been shown by talks on events such as those from our
:ref:`video-gallery` section.

Generating bindings between two languages it nothing new, but it has
always been a non-trivial task, mainly for being as-compatible-as-possible
when using external modules/libraries in your project.

Shiboken's main use case is to extend Qt/C++ project's
functionality, making them **scriptable**.

What does it mean for an application to be scriptable?

* enables a interpreted language to interact directly with the Qt/C++
  application,
* provide the option to modify and create components/elements of the
  application from Python,
* possibility to create a plugins/add-ons system for the application.
* complement a process with external Python functionality.

Check out this `Shiboken Webinar`_ for a hands-on example.

Shiboken excels at Qt-dependent binding generation, meaning that
any Qt/C++ project can be easily exposed to Python.
In addition, Shiboken has proven its support for C++ projects (without Qt),
as shown on event talks and `blog posts`.

Adding Python support to well known solutions/projects is a pattern we keep
seeing in the industry, on a broad range of devices.
This is why we are working every day to improve the Qt for Python offering.

We believe both Qt and Python will benefit from this interaction.

.. _2019: https://insights.stackoverflow.com/survey/2019
.. _2020: https://insights.stackoverflow.com/survey/2020
.. _2021: https://insights.stackoverflow.com/survey/2021
.. _`TIOBE index`: https://www.tiobe.com/tiobe-index/
.. _`blog posts`: https://www.qt.io/blog/tag/qt-for-python
.. _`Shiboken Webinar`: https://www.youtube.com/watch?v=wOMlDutOWXI
