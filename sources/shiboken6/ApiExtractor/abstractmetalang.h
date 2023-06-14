// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef ABSTRACTMETALANG_H
#define ABSTRACTMETALANG_H

#include "abstractmetalang_enums.h"
#include "abstractmetalang_typedefs.h"
#include "enclosingclassmixin.h"
#include "typesystem_typedefs.h"

#include <QtCore/qobjectdefs.h>
#include <QtCore/QScopedPointer>
#include <QtCore/QStringList>

QT_FORWARD_DECLARE_CLASS(QDebug)

enum class Access;
class AbstractMetaClassPrivate;
class ComplexTypeEntry;
class Documentation;
class EnumTypeEntry;
class QPropertySpec;
class SourceLocation;
struct UsingMember;

class AbstractMetaClass : public EnclosingClassMixin
{
    Q_GADGET
public:
    Q_DISABLE_COPY_MOVE(AbstractMetaClass)

    enum CppWrapperFlag {
        NoCppWrapper = 0x0,
        CppProtectedHackWrapper = 0x1,// Make protected functions accessible
        CppVirtualMethodWrapper = 0x2 // Need C++ wrapper for calling Python overrides
    };
    Q_DECLARE_FLAGS(CppWrapper, CppWrapperFlag)

    enum Attribute {
        None                          = 0x00000000,

        Abstract                      = 0x00000001,
        FinalInTargetLang             = 0x00000002,

        HasRejectedConstructor        = 0x00000010,
        HasRejectedDefaultConstructor = 0x00000020,

        FinalCppClass                 = 0x00000100,
        Deprecated                    = 0x00000200,
        Struct                        = 0x00000400
    };
    Q_DECLARE_FLAGS(Attributes, Attribute)
    Q_FLAG(Attribute)

    Attributes attributes() const;
    void setAttributes(Attributes attributes);

    void operator+=(Attribute attribute);
    void operator-=(Attribute attribute);

    bool isFinalInTargetLang() const;
    bool isAbstract() const;

    AbstractMetaClass();
    ~AbstractMetaClass();

    const AbstractMetaFunctionCList &functions() const;
    void setFunctions(const AbstractMetaFunctionCList &functions);
    static void addFunction(const AbstractMetaClassPtr &klass,
                            const AbstractMetaFunctionCPtr &function);
    bool hasFunction(const QString &str) const;
    AbstractMetaFunctionCPtr findFunction(QStringView functionName) const;
    AbstractMetaFunctionCList findFunctions(QStringView functionName) const;
    AbstractMetaFunctionCPtr findOperatorBool() const;
    // Find a Qt-style isNull() method suitable for nb_bool
    AbstractMetaFunctionCPtr findQtIsNullMethod() const;
    bool hasSignal(const AbstractMetaFunction *f) const;

    bool hasConstructors() const;
    AbstractMetaFunctionCPtr copyConstructor() const;
    bool hasCopyConstructor() const;
    bool hasPrivateCopyConstructor() const;

    static void addDefaultConstructor(const AbstractMetaClassPtr &klass);
    static void addDefaultCopyConstructor(const AbstractMetaClassPtr &klass);

    bool hasNonPrivateConstructor() const;
    void setHasNonPrivateConstructor(bool value);

    bool hasPrivateConstructor() const;
    void setHasPrivateConstructor(bool value);

    bool hasDeletedDefaultConstructor() const;
    void setHasDeletedDefaultConstructor(bool value);

    bool hasDeletedCopyConstructor() const;
    void setHasDeletedCopyConstructor(bool value);

    bool hasPrivateDestructor() const;
    void setHasPrivateDestructor(bool value);

    bool hasProtectedDestructor() const;
    void setHasProtectedDestructor(bool value);

    bool hasVirtualDestructor() const;
    void setHasVirtualDestructor(bool value);

    bool isDefaultConstructible() const;
    bool isImplicitlyDefaultConstructible() const;
    bool canAddDefaultConstructor() const;

    bool isCopyConstructible() const;
    bool isImplicitlyCopyConstructible() const;
    bool canAddDefaultCopyConstructor() const;

    static void addSynthesizedComparisonOperators(const AbstractMetaClassPtr &c);

    bool generateExceptionHandling() const;

    CppWrapper cppWrapper() const;

    const UsingMembers &usingMembers() const;
    void addUsingMember(const UsingMember &um);
    bool isUsingMember(const AbstractMetaClassCPtr &c, const QString &memberName,
                       Access minimumAccess) const;
    bool hasUsingMemberFor(const QString &memberName) const;

    AbstractMetaFunctionCList queryFunctionsByName(const QString &name) const;
    static bool queryFunction(const AbstractMetaFunction *f, FunctionQueryOptions query);
    static AbstractMetaFunctionCList queryFunctionList(const AbstractMetaFunctionCList &list,
                                                      FunctionQueryOptions query);
    static AbstractMetaFunctionCPtr queryFirstFunction(const AbstractMetaFunctionCList &list,
                                                       FunctionQueryOptions query);

    AbstractMetaFunctionCList queryFunctions(FunctionQueryOptions query) const;
    AbstractMetaFunctionCList functionsInTargetLang() const;
    AbstractMetaFunctionCList cppSignalFunctions() const;
    AbstractMetaFunctionCList implicitConversions() const;

    /**
     *   Retrieves all class' operator overloads that meet
     *   query criteria defined with the OperatorQueryOption
     *   enum.
     *   /param query composition of OperatorQueryOption enum values
     *   /return list of operator overload methods that meet the
     *   query criteria
     */
    AbstractMetaFunctionCList operatorOverloads(OperatorQueryOptions query) const;

    bool hasArithmeticOperatorOverload() const;
    bool hasIncDecrementOperatorOverload() const;
    bool hasBitwiseOperatorOverload() const;
    bool hasComparisonOperatorOverload() const;
    bool hasLogicalOperatorOverload() const;

    const AbstractMetaFieldList &fields() const;
    AbstractMetaFieldList &fields();
    void setFields(const AbstractMetaFieldList &fields);
    void addField(const AbstractMetaField &field);
    bool hasStaticFields() const;

    std::optional<AbstractMetaField> findField(QStringView name) const;

    const AbstractMetaEnumList &enums() const;
    AbstractMetaEnumList &enums();
    void setEnums(const AbstractMetaEnumList &enums);
    void addEnum(const AbstractMetaEnum &e);

    std::optional<AbstractMetaEnum> findEnum(const QString &enumName) const;
    std::optional<AbstractMetaEnumValue> findEnumValue(const QString &enumName) const;
    void getEnumsToBeGenerated(AbstractMetaEnumList *enumList) const;
    void getEnumsFromInvisibleNamespacesToBeGenerated(AbstractMetaEnumList *enumList) const;

    void getFunctionsFromInvisibleNamespacesToBeGenerated(AbstractMetaFunctionCList *funcList) const;

    QString fullName() const;

    /**
     *   Retrieves the class name without any namespace/scope information.
     *   /return the class name without scope information
     */
    QString name() const;

    const Documentation &documentation() const;
    void setDocumentation(const Documentation& doc);

    QString baseClassName() const;

    AbstractMetaClassCPtr defaultSuperclass() const; // Attribute "default-superclass"
    void setDefaultSuperclass(const AbstractMetaClassPtr &s);

    AbstractMetaClassCPtr baseClass() const;
    const AbstractMetaClassCList &baseClasses() const;
    // base classes including defaultSuperclass
    AbstractMetaClassCList typeSystemBaseClasses() const;
    // Recursive list of all base classes including defaultSuperclass
    AbstractMetaClassCList allTypeSystemAncestors() const;

    void addBaseClass(const AbstractMetaClassCPtr &base_class);
    void setBaseClass(const AbstractMetaClassCPtr &base_class);

    /**
     *   \return the namespace from another package which this namespace extends.
     */
    AbstractMetaClassCPtr extendedNamespace() const;
    void setExtendedNamespace(const AbstractMetaClassCPtr &e);

    const AbstractMetaClassCList &innerClasses() const;
    void addInnerClass(const AbstractMetaClassPtr &cl);
    void setInnerClasses(const AbstractMetaClassCList &innerClasses);

    QString package() const;

    bool isNamespace() const;
    bool isInvisibleNamespace() const;
    bool isInlineNamespace() const;

    bool isQtNamespace() const;

    QString qualifiedCppName() const;

    bool hasSignals() const;

    /**
    *   Says if the class that declares or inherits a virtual function.
    *   \return true if the class implements or inherits any virtual methods
    */
    bool isPolymorphic() const;

    /**
     * Tells if this class has one or more fields (member variables) that are protected.
     * \return true if the class has protected fields.
     */
    bool hasProtectedFields() const;


    const TypeEntryCList &templateArguments() const;
    void setTemplateArguments(const TypeEntryCList &);

    // only valid during metabuilder's run
    const QStringList &baseClassNames() const;
    void setBaseClassNames(const QStringList &names);

    ComplexTypeEntryCPtr typeEntry() const;
    ComplexTypeEntryPtr typeEntry();
    void setTypeEntry(const ComplexTypeEntryPtr &type);

    /// Returns the global hash function as found by the code parser
    QString hashFunction() const;
    void setHashFunction(const QString &);

    /// Returns whether the class has a qHash() overload. Currently unused,
    /// specified in type system.
    bool hasHashFunction() const;

    const QList<QPropertySpec> &propertySpecs() const;
    void addPropertySpec(const QPropertySpec &spec);
    void setPropertyDocumentation(const QString &name, const Documentation &doc);

    // Helpers to search whether a functions is a property setter/getter/reset
    enum class PropertyFunction
    {
        Read,
        Write,
        Reset,
        Notify
    };
    struct PropertyFunctionSearchResult
    {
        qsizetype index;
        PropertyFunction function;
    };

    PropertyFunctionSearchResult searchPropertyFunction(const QString &name) const;

    std::optional<QPropertySpec> propertySpecByName(const QString &name) const;

    /// Returns a list of conversion operators for this class. The conversion
    /// operators are defined in other classes of the same module.
    const AbstractMetaFunctionCList &externalConversionOperators() const;
    /// Adds a converter operator for this class.
    void addExternalConversionOperator(const AbstractMetaFunctionCPtr &conversionOp);
    /// Returns true if this class has any converter operators defined elsewhere.
    bool hasExternalConversionOperators() const;

    void sortFunctions();

    AbstractMetaClassCPtr templateBaseClass() const;
    void setTemplateBaseClass(const AbstractMetaClassCPtr &cls);

    bool hasTemplateBaseClassInstantiations() const;
    const AbstractMetaTypeList &templateBaseClassInstantiations() const;
    void setTemplateBaseClassInstantiations(const AbstractMetaTypeList& instantiations);

    void setTypeDef(bool typeDef);
    bool isTypeDef() const;

    bool isStream() const;
    void setStream(bool stream);

    bool hasToStringCapability() const;
    void setToStringCapability(bool value, uint indirections = 0);

    uint toStringCapabilityIndirections() const;

    bool deleteInMainThread() const;

    // Query functions for generators
    bool isObjectType() const;
    bool isCopyable() const;
    bool isValueTypeWithCopyConstructorOnly() const;
    void setValueTypeWithCopyConstructorOnly(bool v);
    static bool determineValueTypeWithCopyConstructorOnly(const AbstractMetaClassCPtr &c,
                                                          bool avoidProtectedHack);

    static AbstractMetaClassPtr findClass(const AbstractMetaClassList &classes,
                                        QStringView name);
    static AbstractMetaClassCPtr findClass(const AbstractMetaClassCList &classes,
                                              QStringView name);
    static AbstractMetaClassPtr findClass(const AbstractMetaClassList &classes,
                                        const TypeEntryCPtr &typeEntry);
    static AbstractMetaClassCPtr findClass(const AbstractMetaClassCList &classes,
                                              const TypeEntryCPtr &typeEntry);
    AbstractMetaClassCPtr findBaseClass(const QString &qualifiedName) const;

    static std::optional<AbstractMetaEnumValue> findEnumValue(const AbstractMetaClassList &classes,
                                                              const QString &string);

    SourceLocation sourceLocation() const;
    void setSourceLocation(const SourceLocation &sourceLocation);

    // For AbstractMetaBuilder
    static void fixFunctions(const AbstractMetaClassPtr &klass);
    bool needsInheritanceSetup() const;
    void setInheritanceDone(bool b);
    bool inheritanceDone() const;

    template <class Function>
    void invisibleNamespaceRecursion(Function f) const;

private:
#ifndef QT_NO_DEBUG_STREAM
    void format(QDebug &d) const;
    void formatMembers(QDebug &d) const;
    friend QDebug operator<<(QDebug d, const AbstractMetaClassCPtr &ac);
#endif

    QScopedPointer<AbstractMetaClassPrivate> d;
};

inline bool AbstractMetaClass::isFinalInTargetLang() const
{
    return attributes().testFlag(FinalInTargetLang);
}

inline bool AbstractMetaClass::isAbstract() const
{
    return attributes().testFlag(Abstract);
}

template <class Function>
void AbstractMetaClass::invisibleNamespaceRecursion(Function f) const
{
    for (const auto &ic : innerClasses()) {
        if (ic->isInvisibleNamespace()) {
            f(ic);
            ic->invisibleNamespaceRecursion(f);
        }
    }
}

bool inheritsFrom(const AbstractMetaClassCPtr &c, const AbstractMetaClassCPtr &other);
bool inheritsFrom(const AbstractMetaClassCPtr &c, const QString &name);
inline bool isQObject(const AbstractMetaClassCPtr &c)
{
    return inheritsFrom(c, QStringLiteral("QObject"));
}

AbstractMetaClassCPtr findBaseClass(const AbstractMetaClassCPtr &c,
                                    const QString &qualifiedName);

/// Return type entry of the base class that declares the parent management
TypeEntryCPtr parentManagementEntry(const AbstractMetaClassCPtr &klass);
inline bool hasParentManagement(const AbstractMetaClassCPtr &c)
{ return bool(parentManagementEntry(c)); }

AbstractMetaClassCList allBaseClasses(const AbstractMetaClassCPtr metaClass);

Q_DECLARE_OPERATORS_FOR_FLAGS(AbstractMetaClass::CppWrapper);

Q_DECLARE_OPERATORS_FOR_FLAGS(AbstractMetaClass::Attributes);

#endif // ABSTRACTMETALANG_H
