// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TYPESYSTEM_H
#define TYPESYSTEM_H

#include "include.h"
#include "typesystem_typedefs.h"

#include <QtCore/qobjectdefs.h>
#include <QtCore/QString>
#include <QtCore/QScopedPointer>

class AbstractMetaType;
class CustomTypeEntry;
class PrimitiveTypeEntry;
class SourceLocation;
class TypeSystemTypeEntry;

class TypeEntryPrivate;

QT_BEGIN_NAMESPACE
class QDebug;
class QVersionNumber;
QT_END_NAMESPACE

class TypeEntry
{
    Q_GADGET
public:
    Q_DISABLE_COPY_MOVE(TypeEntry)

    enum Type {
        PrimitiveType,
        VoidType,
        VarargsType,
        FlagsType,
        EnumType,
        EnumValue,
        ConstantValueType,
        TemplateArgumentType,
        BasicValueType,
        ContainerType,
        ObjectType,
        NamespaceType,
        ArrayType,
        TypeSystemType,
        CustomType,
        PythonType,
        FunctionType,
        SmartPointerType,
        TypedefType
    };
    Q_ENUM(Type)

    enum CodeGeneration {
        GenerateNothing,     // Rejection, private type, ConstantValueTypeEntry or similar
        GenerationDisabled,  // generate='no' in type system
        GenerateCode,        // Generate code
        GenerateForSubclass, // Inherited from a loaded dependent type system.
    };
    Q_ENUM(CodeGeneration)

    explicit TypeEntry(const QString &entryName, Type t, const QVersionNumber &vr,
                       const TypeEntryCPtr &parent);
    virtual ~TypeEntry();

    Type type() const;

    TypeEntryCPtr parent() const;
    void setParent(const TypeEntryCPtr &);
    bool isChildOf(const TypeEntryCPtr &p) const;

    bool isPrimitive() const;
    bool isEnum() const;
    bool isFlags() const;
    bool isObject() const;
    bool isNamespace() const;
    bool isContainer() const;
    bool isSmartPointer() const;
    bool isUniquePointer() const;
    bool isArray() const;
    bool isTemplateArgument() const;
    bool isVoid() const;
    bool isVarargs() const;
    bool isCustom() const;
    bool isTypeSystem() const;
    bool isFunction() const;
    bool isEnumValue() const;

    bool stream() const;
    void setStream(bool b);

    bool isBuiltIn() const;
    void setBuiltIn(bool b);

    bool isPrivate() const;
    void setPrivate(bool b);

    // The type's name in C++, fully qualified
    QString name() const;
    // C++ excluding inline namespaces
    QString shortName() const;
    // Name as specified in XML
    QString entryName() const;

    CodeGeneration codeGeneration() const;
    void setCodeGeneration(CodeGeneration cg);

    // Returns true if code must be generated for this entry,
    // it will return false in case of types coming from typesystems
    // included for reference only.
    // NOTE: 'GenerateForSubclass' means 'generate="no"'
    //       on 'load-typesystem' tag
    bool generateCode() const;

    /// Returns whether the C++ generators should generate this entry
    bool shouldGenerate() const;

    int revision() const;
    void setRevision(int r); // see typedatabase.cpp
    int sbkIndex() const; // see typedatabase.cpp
    void setSbkIndex(int i);

    virtual QString qualifiedCppName() const;

    /// Its type's name in target language API.
    /// The target language API name represents how this type is referred on
    /// low level code for the target language. Examples: for Java this would
    /// be a JNI name, for Python it should represent the CPython type name.
    /// \return string representing the target language API name
    /// Currently used only for PrimitiveTypeEntry (attribute "target").
    CustomTypeEntryCPtr targetLangApiType() const;
    bool hasTargetLangApiType() const;
    void setTargetLangApiType(const CustomTypeEntryPtr &cte);
    QString targetLangApiName() const;

    // The type's name in TargetLang
    QString targetLangName() const; // "Foo.Bar"
    void setTargetLangName(const QString &n);
    QString targetLangEntryName() const; // "Bar"

    // The package
    QString targetLangPackage() const;
    void setTargetLangPackage(const QString &p);

    QString qualifiedTargetLangName() const;

    virtual bool isValue() const;
    virtual bool isComplex() const;

    const IncludeList &extraIncludes() const;
    void setExtraIncludes(const IncludeList &includes);
    void addExtraInclude(const Include &newInclude);

    Include include() const;
    void setInclude(const Include &inc);

    QVersionNumber version() const;

    // View on: Type to use for function argument conversion, fex
    // std::string_view -> std::string for foo(std::string_view).
    // cf AbstractMetaType::viewOn()
    TypeEntryPtr viewOn() const;
    void setViewOn(const TypeEntryPtr &v);

    virtual TypeEntry *clone() const;

    void useAsTypedef(const TypeEntryCPtr &source);

    SourceLocation sourceLocation() const;
    void setSourceLocation(const SourceLocation &sourceLocation);

    // Query functions for generators
    /// Returns true if the type passed has a Python wrapper for it.
    /// Although namespace has a Python wrapper, it's not considered a type.
    bool isWrapperType() const;

#ifndef QT_NO_DEBUG_STREAM
    virtual void formatDebug(QDebug &d) const;
#endif

protected:
    explicit TypeEntry(TypeEntryPrivate *d);

    const TypeEntryPrivate *d_func() const;
    TypeEntryPrivate *d_func();

    virtual QString buildTargetLangName() const;

private:
    bool setRevisionHelper(int r);
    int sbkIndexHelper() const;
    QScopedPointer<TypeEntryPrivate> m_d;
};

TypeSystemTypeEntryCPtr typeSystemTypeEntry(TypeEntryCPtr e);

// cf AbstractMetaClass::targetLangEnclosingClass()
TypeEntryCPtr targetLangEnclosingEntry(const TypeEntryCPtr &e);

bool isCppPrimitive(const TypeEntryCPtr &e);

/// Returns true if the type is a primitive but not a C++ primitive.
bool isUserPrimitive(const TypeEntryCPtr &e);

/// Returns true if the type is a C++ integral primitive,
/// i.e. bool, char, int, long, and their unsigned counterparts.
bool isCppIntegralPrimitive(const TypeEntryCPtr &e);

/// Returns true if the type is an extended C++ primitive, a void*,
/// a const char*, or a std::string (cf isCppPrimitive()).
bool isExtendedCppPrimitive(const TypeEntryCPtr &e);

#endif // TYPESYSTEM_H
