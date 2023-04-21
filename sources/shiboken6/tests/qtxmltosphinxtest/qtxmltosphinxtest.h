// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef QTXMLTOSPHINXTEST_H
#define QTXMLTOSPHINXTEST_H

#include "qtxmltosphinxinterface.h"

#include <QtCore/QObject>

class QtXmlToSphinxTest : public QObject, public QtXmlToSphinxDocGeneratorInterface
{
    Q_OBJECT
public:
    // QtXmlToSphinxDocGeneratorInterface
    QString expandFunction(const QString &) const override;
    QString expandClass(const QString &, const QString &) const override;
    QString resolveContextForMethod(const QString &,
                                    const QString &) const override;
    const QLoggingCategory &loggingCategory() const override;
    QtXmlToSphinxLink resolveLink(const QtXmlToSphinxLink &link) const override;

private slots:
    void testTable_data();
    void testTable();
    void testTableFormatting_data();
    void testTableFormatting();
    void testTableFormattingIoDevice_data();
    void testTableFormattingIoDevice();
    void testSnippetExtraction_data();
    void testSnippetExtraction();

private:
    QString transformXml(const QString &xml) const;

    QtXmlToSphinxParameters m_parameters;
};

#endif // QTXMLTOSPHINXTEST_H
