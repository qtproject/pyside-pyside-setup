// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

// Converted from basic_test.py
#include <QtCore/Qt>
#include <QtGui/QColor>
#include <QtGui/QPainter>
#include <QtGui/QPaintEvent>
#include <QtGui/QShortcut>
#include <QtWidgets/QApplication>
#include <QtWidgets/QWidget>

class Window : public QWidget
{
public:

    Window(QWidget * parent = nullptr)
    {
        super()->__init__(parent);
    }

    void paintEvent(QPaintEvent * e)
    {
        paint("bla");
    }

    void paint(const QString & what, color = Qt::blue)
    {
        { // Converted from context manager
            p = QPainter();
            p->setPen(QColor(color));
            rect = rect();
            w = rect->width();
            h = rect->height();
            p->drawLine(0, 0, w, h);
            p->drawLine(0, h, w, 0);
            p->drawText(rect->center(), what);
        }
    }

    void sum()
    {
        values = {1, 2, 3};
        result = 0;
        for (v: values) {
            result += v
        }
        return result;
    }
};

int main(int argc, char *argv[])
{
    QApplication app(sys->argv);
    window = Window();
    auto *sc = new QShortcut((Qt::CTRL | Qt::Key_Q), window);
    sc->activated->connect(window->close);
    window->setWindowTitle("Test");
    window->show();
    sys->exit(app.exec());
    return 0;
}
