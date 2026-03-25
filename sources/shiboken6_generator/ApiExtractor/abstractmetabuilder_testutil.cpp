// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "abstractmetabuilder_testutil.h"
#include "abstractmetabuilder.h"
#include "abstractmetabuilder_p.h"
#include "reporthandler.h"
#include "typedatabase.h"

#include <QtCore/qbuffer.h>
#include <QtCore/qdebug.h>
#include <QtCore/qdir.h>
#include <QtCore/qtemporaryfile.h>

#include <exception>

static std::unique_ptr<QTemporaryFile> writeCppCode(const char *cppCode)
{
    const QString pattern = QDir::tempPath() + QLatin1StringView("/st_XXXXXX_main.cpp");
    auto result = std::make_unique<QTemporaryFile>(pattern);
    if (!result->open()) {
        qWarning("Creation of temporary file failed: %s", qPrintable(result->errorString()));
        return {};
    }
    result->write(cppCode, qint64(qstrlen(cppCode)));
    result->close();
    return result;
}

namespace TestUtil
{
std::shared_ptr<_FileModelItem>
    buildDom(const char *cppCode, bool silent, LanguageLevel languageLevel)
{
    ReportHandler::setSilent(silent);
    ReportHandler::startTimer();
    auto tempSource = writeCppCode(cppCode);
    if (!tempSource)
        return {};
    return AbstractMetaBuilderPrivate::buildDom({QFile::encodeName(tempSource->fileName())},
                                                true, languageLevel, 0);
}

std::unique_ptr<AbstractMetaBuilder>
    parse(const char *cppCode, const char *xmlCode, bool silent, const QString &apiVersion,
          const QStringList &dropTypeEntries, LanguageLevel languageLevel)
{
    ReportHandler::setSilent(silent);
    ReportHandler::startTimer();
    auto *td = TypeDatabase::instance(true);
    if (apiVersion.isEmpty())
        TypeDatabase::clearApiVersions();
    else if (!TypeDatabase::setApiVersion(QLatin1StringView("*"), apiVersion))
        return nullptr;
    td->setDropTypeEntries(dropTypeEntries);
    QBuffer buffer;
    // parse typesystem
    buffer.setData(xmlCode);
    if (!buffer.open(QIODevice::ReadOnly))
        return nullptr;
    if (!td->parseFile(&buffer))
        return nullptr;
    buffer.close();
    auto tempSource = writeCppCode(cppCode);
    if (!tempSource)
        return nullptr;
    auto builder = std::make_unique<AbstractMetaBuilder>();
    try {
        QByteArrayList arguments{QFile::encodeName(tempSource->fileName())};
        if (!builder->build(arguments, {}, true, languageLevel))
            builder.reset();
    } catch (const std::exception &e) {
        qWarning("%s", e.what());
        builder.reset();
    }
    return builder;
}
} // namespace TestUtil
