/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef QPYTEXTOBJECT
#define QPYTEXTOBJECT

#include <QtCore/QObject>
#include <QtGui/QTextObjectInterface>

// Qt5: no idea why this definition is not found automatically! It should come
// from <QTextObjectInterface> which resolves to qabstracttextdocumentlayout.h
#ifdef Q_MOC_RUN
Q_DECLARE_INTERFACE(QTextObjectInterface, "org.qt-project.Qt.QTextObjectInterface")
#endif

class QPyTextObject : public QObject, public QTextObjectInterface
{
    Q_OBJECT
    Q_INTERFACES(QTextObjectInterface)
public:
    QPyTextObject(QObject *parent = nullptr) : QObject(parent) {}
    void drawObject(QPainter *painter, const QRectF &rect, QTextDocument *doc,
                    int posInDocument, const QTextFormat &format) = 0;
    QSizeF intrinsicSize(QTextDocument *doc, int posInDocument, const QTextFormat &format) = 0;
};
#endif


