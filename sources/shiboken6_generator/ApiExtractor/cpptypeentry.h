// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef CPPTYPEENTRY_H
#define CPPTYPEENTRY_H

#include "typesystem.h"
#include "typesystem_enums.h"

class CppTypeEntryPrivate;

class CppTypeEntry : public TypeEntry
{
public:
    explicit CppTypeEntry(const QString &entryName, Type t, const QVersionNumber &vr,
                          const TypeEntryCPtr &parent);

    const QString &defaultConstructor() const;
    void setDefaultConstructor(const QString& defaultConstructor);
    bool hasDefaultConstructor() const { return !defaultConstructor().isEmpty(); }

    // View on: Type to use for function argument conversion, fex
    // "std::string_view" -> "std::string" for "foo(std::string_view)".
    // cf AbstractMetaType::viewOn()
    CppTypeEntryCPtr viewOn() const;
    void setViewOn(const CppTypeEntryCPtr &v);

    // Typesystem specification, potentially overriding the code model detection
    bool isDefaultConstructible() const;
    bool isCopyable() const;
    bool isMovable() const;
    bool isMoveOnlyType() const { return !isCopyable() && isMovable(); }

    // Parser/code model interface
    TypeSystem::DefaultConstructibleFlag defaultConstructibleFlag() const;
    void setDefaultConstructibleFlag(TypeSystem::DefaultConstructibleFlag flag);
    void setDefaultConstructibleDetected(bool c); // set value detected by code model

    TypeSystem::CopyableFlag copyableFlag() const;
    void setCopyableFlag(TypeSystem::CopyableFlag flag);
    void setCopyableDetected(bool c); // set value detected by code model

    TypeSystem::MovableFlag movableFlag() const;
    void setMovableFlag(TypeSystem::MovableFlag flag);

    TypeSystem::QtMetaTypeRegistration qtMetaTypeRegistration() const;
    void setQtMetaTypeRegistration(TypeSystem::QtMetaTypeRegistration r);

    TypeEntry *clone() const override;

#ifndef QT_NO_DEBUG_STREAM
    void formatDebug(QDebug &debug) const override;
#endif

protected:
    explicit CppTypeEntry(CppTypeEntryPrivate *d);
};

#endif // CPPTYPEENTRY_H
