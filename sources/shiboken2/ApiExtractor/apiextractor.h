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

#ifndef APIEXTRACTOR_H
#define APIEXTRACTOR_H

#include "dependency.h"
#include "abstractmetalang_typedefs.h"
#include "apiextractormacros.h"
#include "header_paths.h"
#include "typedatabase_typedefs.h"
#include "typesystem_typedefs.h"
#include "clangparser/compilersupport.h"
#include <QFileInfoList>
#include <QStringList>

class AbstractMetaBuilder;
class AbstractMetaClass;
class AbstractMetaEnum;
class AbstractMetaFunction;
class AbstractMetaType;
class ContainerTypeEntry;
class EnumTypeEntry;
class FlagsTypeEntry;
class PrimitiveTypeEntry;
class TypeEntry;

QT_BEGIN_NAMESPACE
class QDebug;
class QIODevice;
QT_END_NAMESPACE

class ApiExtractor
{
public:
    Q_DISABLE_COPY(ApiExtractor)

    ApiExtractor();
    ~ApiExtractor();

    void setTypeSystem(const QString& typeSystemFileName);
    QString typeSystem() const { return m_typeSystemFileName; }
    void setCppFileNames(const QFileInfoList &cppFileNames);
    QFileInfoList cppFileNames() const { return m_cppFileNames; }
    void setSkipDeprecated(bool value);
    void setSuppressWarnings(bool value);
    void setSilent(bool value);
    void addTypesystemSearchPath(const QString& path);
    void addTypesystemSearchPath(const QStringList& paths);
    void addIncludePath(const HeaderPath& path);
    void addIncludePath(const HeaderPaths& paths);
    HeaderPaths includePaths() const { return m_includePaths; }
    void setLogDirectory(const QString& logDir);
    bool setApiVersion(const QString& package, const QString& version);
    void setDropTypeEntries(QString dropEntries);
    LanguageLevel languageLevel() const;
    void setLanguageLevel(LanguageLevel languageLevel);

    const AbstractMetaEnumList &globalEnums() const;
    const AbstractMetaFunctionList &globalFunctions() const;
    const AbstractMetaClassList &classes() const;
    const AbstractMetaClassList &smartPointers() const;
    AbstractMetaClassList classesTopologicalSorted(const Dependencies &additionalDependencies = Dependencies()) const;
    PrimitiveTypeEntryList primitiveTypes() const;
    ContainerTypeEntryList containerTypes() const;

    const AbstractMetaEnum* findAbstractMetaEnum(const TypeEntry* typeEntry) const;

    int classCount() const;

    bool run(bool usePySideExtensions);
private:
    QString m_typeSystemFileName;
    QFileInfoList m_cppFileNames;
    HeaderPaths m_includePaths;
    AbstractMetaBuilder* m_builder = nullptr;
    QString m_logDirectory;
    LanguageLevel m_languageLevel = LanguageLevel::Default;
    bool m_skipDeprecated = false;

#ifndef QT_NO_DEBUG_STREAM
    friend QDebug operator<<(QDebug d, const ApiExtractor &ae);
#endif
};

#endif // APIEXTRACTOR_H

