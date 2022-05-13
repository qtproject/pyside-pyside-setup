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

#ifndef TYPESYSTEM_H
#define TYPESYSTEM_H

#include "typesystem_enums.h"
#include "typesystem_typedefs.h"
#include "include.h"

#include <QtCore/QString>
#include <QtCore/QScopedPointer>

class AbstractMetaType;
class CustomConversion;
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
                       const TypeEntry *parent);
    virtual ~TypeEntry();

    Type type() const;

    const TypeEntry *parent() const;
    void setParent(const TypeEntry *p);
    bool isChildOf(const TypeEntry *p) const;
    const TypeSystemTypeEntry *typeSystemTypeEntry() const;
    // cf AbstractMetaClass::targetLangEnclosingClass()
    const TypeEntry *targetLangEnclosingEntry() const;

    bool isPrimitive() const;
    bool isEnum() const;
    bool isFlags() const;
    bool isObject() const;
    bool isNamespace() const;
    bool isContainer() const;
    bool isSmartPointer() const;
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
    const CustomTypeEntry *targetLangApiType() const;
    bool hasTargetLangApiType() const;
    void setTargetLangApiType(CustomTypeEntry *cte);
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

    const CodeSnipList &codeSnips() const;
    CodeSnipList &codeSnips();
    void setCodeSnips(const CodeSnipList &codeSnips);
    void addCodeSnip(const CodeSnip &codeSnip);

    void setDocModification(const DocModificationList& docMods);
    DocModificationList docModifications() const;

    const IncludeList &extraIncludes() const;
    void setExtraIncludes(const IncludeList &includes);
    void addExtraInclude(const Include &newInclude);

    /// Extra includes for function arguments determined by the meta builder.
    const IncludeList &argumentIncludes() const;
    void addArgumentInclude(const Include &newInclude);

    Include include() const;
    void setInclude(const Include &inc);

    // FIXME PYSIDE7: Remove
    /// Set the target type conversion rule
    void setTargetConversionRule(const QString& conversionRule);

    /// Returns the target type conversion rule
    QString targetConversionRule() const;

    QVersionNumber version() const;

    /// TODO-CONVERTER: mark as deprecated
    bool hasTargetConversionRule() const;

    bool isCppPrimitive() const;

    bool hasCustomConversion() const;
    void setCustomConversion(CustomConversion* customConversion);
    CustomConversion* customConversion() const;

    // View on: Type to use for function argument conversion, fex
    // std::string_view -> std::string for foo(std::string_view).
    // cf AbstractMetaType::viewOn()
    TypeEntry *viewOn() const;
    void setViewOn(TypeEntry *v);

    virtual TypeEntry *clone() const;

    void useAsTypedef(const TypeEntry *source);

    SourceLocation sourceLocation() const;
    void setSourceLocation(const SourceLocation &sourceLocation);

    const PrimitiveTypeEntry *asPrimitive() const;

    // Query functions for generators
    /// Returns true if the type is a primitive but not a C++ primitive.
    bool isUserPrimitive() const;
    /// Returns true if the type passed has a Python wrapper for it.
    /// Although namespace has a Python wrapper, it's not considered a type.
    bool isWrapperType() const;
    /// Returns true if the type is a C++ integral primitive,
    /// i.e. bool, char, int, long, and their unsigned counterparts.
    bool isCppIntegralPrimitive() const;
    /// Returns true if the type is an extended C++ primitive, a void*,
    /// a const char*, or a std::string (cf isCppPrimitive()).
    bool isExtendedCppPrimitive() const;

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

#endif // TYPESYSTEM_H
