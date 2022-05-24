// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#ifndef WIGGLYWIDGET_H
#define WIGGLYWIDGET_H

#include "macros.h"

#include <QtWidgets/QWidget>
#include <QtCore/QBasicTimer>

//! [0]
class BINDINGS_API WigglyWidget : public QWidget
{
    Q_OBJECT
    Q_PROPERTY(bool running READ isRunning WRITE setRunning)
    Q_PROPERTY(QString text READ text WRITE setText)

public:
    WigglyWidget(QWidget *parent = nullptr);

    QString text() const;
    bool isRunning() const;

public slots:
    void setText(const QString &newText);
    void setRunning(bool r);

protected:
    void paintEvent(QPaintEvent *event) override;
    void timerEvent(QTimerEvent *event) override;

private:
    QBasicTimer m_timer;
    QString m_text;
    int m_step = 0;
};
//! [0]

#endif
