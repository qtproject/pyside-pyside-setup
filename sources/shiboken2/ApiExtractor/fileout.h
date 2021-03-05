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

#ifndef FILEOUT_H
#define FILEOUT_H

#include <QtCore/QObject>
#include <QtCore/QTextStream>

QT_FORWARD_DECLARE_CLASS(QFile)

class FileOut : public QObject
{
private:
    QByteArray tmp;
    QString name;

public:
    Q_DISABLE_COPY(FileOut)

    enum State { Failure, Unchanged, Success };

    explicit FileOut(QString name);
    ~FileOut();

    QString filePath() const { return name; }

    State done();
    State done(QString *errorMessage);

    void touch() { touchFile(name); }

    static void touchFile(const QString &filePath);

    QTextStream stream;

    static bool dummy;
    static bool diff;

private:
    bool isDone;
};

#endif // FILEOUT_H
