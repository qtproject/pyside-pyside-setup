// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#include "wigglywidget.h"

#include <QtGui/QFontMetrics>
#include <QtGui/QPainter>
#include <QtCore/QTimerEvent>

//! [0]
WigglyWidget::WigglyWidget(QWidget *parent)
    : QWidget(parent)
{
    setBackgroundRole(QPalette::Midlight);
    setAutoFillBackground(true);

    QFont newFont = font();
    newFont.setPointSize(newFont.pointSize() + 20);
    setFont(newFont);
}
//! [0]

//! [1]
void WigglyWidget::paintEvent(QPaintEvent * /* event */)
//! [1] //! [2]
{
    if (m_text.isEmpty())
        return;
    static constexpr int sineTable[16] = {
        0, 38, 71, 92, 100, 92, 71, 38, 0, -38, -71, -92, -100, -92, -71, -38
    };

    QFontMetrics metrics(font());
    int x = (width() - metrics.horizontalAdvance(m_text)) / 2;
    int y = (height() + metrics.ascent() - metrics.descent()) / 2;
    QColor color;
//! [2]

//! [3]
    QPainter painter(this);
//! [3] //! [4]
    for (int i = 0; i < m_text.size(); ++i) {
        int index = (m_step + i) % 16;
        color.setHsv((15 - index) * 16, 255, 191);
        painter.setPen(color);
        const QChar c = m_text.at(i);
        const int dy = (sineTable[index] * metrics.height()) / 400;
        painter.drawText(x, y - dy, c);
        x += metrics.horizontalAdvance(c);
    }
}
//! [4]

//! [5]
void WigglyWidget::timerEvent(QTimerEvent *event)
//! [5] //! [6]
{
    if (event->timerId() == m_timer.timerId()) {
        ++m_step;
        update();
    } else {
        QWidget::timerEvent(event);
    }
//! [6]
}

QString WigglyWidget::text() const
{
    return m_text;
}

void WigglyWidget::setText(const QString &newText)
{
    m_text = newText;
}

bool WigglyWidget::isRunning() const
{
    return m_timer.isActive();
}

void WigglyWidget::setRunning(bool r)
{
    if (r == isRunning())
        return;
    if (r)
        m_timer.start(60, this);
    else
        m_timer.stop();
}
