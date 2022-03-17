/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the test suite of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "qtxmltosphinxinterface.h"
#include "qtxmltosphinx.h"

#include <QtCore/QCommandLineParser>
#include <QtCore/QCoreApplication>
#include <QtCore/QDebug>
#include <QtCore/QFile>
#include <QtCore/QLoggingCategory>

#include <exception>
#include <iostream>

static const char help[] = R"(QtXmlToSphinx WebXML to rst converter

A manual test for converting WebXML files to rst files for checking
formatting.
)";

Q_LOGGING_CATEGORY(lcQtXmlToSphinx, "qt.xmltosphinx");

static std::ostream &operator<<(std::ostream &str, const QString &s)
{
    str << s.toUtf8().constData();
    return str;
}

class QtXmlToSphinxDocGenerator : public QtXmlToSphinxDocGeneratorInterface
{
public:
    QtXmlToSphinxDocGenerator() = default;

    QString expandFunction(const QString &) const override;
    QString expandClass(const QString &, const QString &) const override;
    QString resolveContextForMethod(const QString &,
                                    const QString &) const override;
    const QLoggingCategory &loggingCategory() const override;
    QtXmlToSphinxLink resolveLink(const QtXmlToSphinxLink &link) const override;
};

// QtXmlToSphinxDocGeneratorInterface
QString QtXmlToSphinxDocGenerator::expandFunction(const QString &) const
{
    return {};
}

QString QtXmlToSphinxDocGenerator::expandClass(const QString &, const QString &) const
{
    return {};
}

QString QtXmlToSphinxDocGenerator::resolveContextForMethod(const QString &, const QString &) const
{
    return {};
}

const QLoggingCategory &QtXmlToSphinxDocGenerator::loggingCategory() const
{
    return lcQtXmlToSphinx();
}

QtXmlToSphinxLink QtXmlToSphinxDocGenerator::resolveLink(const QtXmlToSphinxLink &link) const
{
    return link;
}

static bool run(const QString &fileName)
{
    QtXmlToSphinxDocGenerator generator;
    QtXmlToSphinxParameters parameters;

    QFile file(fileName);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        std::cerr << "Cannot open " << fileName << ": " << file.errorString() << '\n';
        return false;
    }
    const QString xml = QString::fromUtf8(file.readAll());
    file.close();
    std::cout << QtXmlToSphinx(&generator, parameters, xml).result();
    return true;
}

int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);

    QCommandLineParser commandLineParser;
    commandLineParser.setApplicationDescription(QString::fromLatin1(help));
    commandLineParser.addHelpOption();
    commandLineParser.addPositionalArgument(u"[file]"_qs, u"WebXML file to process."_qs);
    commandLineParser.process(QCoreApplication::arguments());
    if (commandLineParser.positionalArguments().isEmpty())
        commandLineParser.showHelp(0); // quits

    int exitCode = 1;
    try {
        if (run(commandLineParser.positionalArguments().constFirst()))
            exitCode = 0;
    } catch (const std::exception &e) {
        std::cerr << "An exception occurred: " << e.what() << '\n';
    }
    return exitCode;
}
