/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
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

#ifndef APIEXTRACTOR_H
#define APIEXTRACTOR_H

#include "abstractmetalang_typedefs.h"
#include "abstractmetatype.h"
#include "apiextractorflags.h"
#include "header_paths.h"
#include "clangparser/compilersupport.h"

#include <QtCore/QFileInfoList>
#include <QtCore/QStringList>

#include <optional>

class ApiExtractorResult;
class AbstractMetaClass;
class AbstractMetaEnum;
class AbstractMetaFunction;

QT_BEGIN_NAMESPACE
class QDebug;
class QIODevice;
QT_END_NAMESPACE

struct ApiExtractorPrivate;

class ApiExtractor
{
public:
    Q_DISABLE_COPY_MOVE(ApiExtractor)

    ApiExtractor();
    ~ApiExtractor();

    void setTypeSystem(const QString& typeSystemFileName);
    QString typeSystem() const;
    void setCppFileNames(const QFileInfoList &cppFileNames);
    QFileInfoList cppFileNames() const;
    void setSkipDeprecated(bool value);
    static void setSuppressWarnings(bool value);
    static void setSilent(bool value);
    static void addTypesystemSearchPath(const QString &path);
    static void addTypesystemSearchPath(const QStringList& paths);
    static void setTypesystemKeywords(const QStringList& keywords);
    void addIncludePath(const HeaderPath& path);
    void addIncludePath(const HeaderPaths& paths);
    HeaderPaths includePaths() const;
    void setLogDirectory(const QString& logDir);
    static bool setApiVersion(const QString &package, const QString &version);
    static void setDropTypeEntries(const QStringList &dropEntries);
    LanguageLevel languageLevel() const;
    void setLanguageLevel(LanguageLevel languageLevel);
    QStringList clangOptions() const;
    void setClangOptions(const QStringList &co);
    static void setUseGlobalHeader(bool h);

    const AbstractMetaEnumList &globalEnums() const;
    const AbstractMetaFunctionCList &globalFunctions() const;
    const AbstractMetaClassList &classes() const;
    const AbstractMetaClassList &smartPointers() const;

    std::optional<ApiExtractorResult> run(ApiExtractorFlags flags);

    /// Forwards to AbstractMetaBuilder::inheritTemplateFunction()
    static AbstractMetaFunctionPtr
        inheritTemplateFunction(const AbstractMetaFunctionCPtr &function,
                                const AbstractMetaTypeList &templateTypes);

    /// Forwards to AbstractMetaBuilder::inheritTemplateMember()
    static AbstractMetaFunctionPtr
        inheritTemplateMember(const AbstractMetaFunctionCPtr &function,
                              const AbstractMetaTypeList &templateTypes,
                              const AbstractMetaClass *templateClass,
                              AbstractMetaClass *subclass);

private:
    ApiExtractorPrivate *d;

#ifndef QT_NO_DEBUG_STREAM
    friend QDebug operator<<(QDebug d, const ApiExtractor &ae);
#endif
};

#endif // APIEXTRACTOR_H

