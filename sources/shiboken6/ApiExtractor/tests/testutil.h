// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTUTIL_H
#define TESTUTIL_H
#include <QtCore/QBuffer>
#include <QtCore/QDebug>
#include <QtCore/QDir>
#include <QtCore/QTemporaryFile>
#include "abstractmetabuilder.h"
#include "reporthandler.h"
#include "typedatabase.h"

#include <exception>
#include <memory>

namespace TestUtil
{
    static AbstractMetaBuilder *parse(const char *cppCode, const char *xmlCode,
                                      bool silent = true,
                                      const QString &apiVersion = {},
                                      const QStringList &dropTypeEntries = {},
                                      LanguageLevel languageLevel = LanguageLevel::Default)
    {
        ReportHandler::setSilent(silent);
        ReportHandler::startTimer();
        auto *td = TypeDatabase::instance(true);
        if (apiVersion.isEmpty())
            TypeDatabase::clearApiVersions();
        else if (!TypeDatabase::setApiVersion(QStringLiteral("*"), apiVersion))
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
        // parse C++ code
        QTemporaryFile tempSource(QDir::tempPath() + QStringLiteral("/st_XXXXXX_main.cpp"));
        if (!tempSource.open()) {
            qWarning().noquote().nospace() << "Creation of temporary file failed: "
                << tempSource.errorString();
            return nullptr;
        }
        QByteArrayList arguments;
        arguments.append(QFile::encodeName(tempSource.fileName()));
        tempSource.write(cppCode, qint64(strlen(cppCode)));
        tempSource.close();

        auto builder = std::make_unique<AbstractMetaBuilder>();
        try {
            if (!builder->build(arguments, {}, true, languageLevel))
                return nullptr;
        } catch (const std::exception &e) {
            qWarning("%s", e.what());
            return nullptr;
        }
        return builder.release();
    }
} // namespace TestUtil

#endif
