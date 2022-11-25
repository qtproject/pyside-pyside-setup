// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
#ifndef TYPESYSTEMPARSER_H
#define TYPESYSTEMPARSER_H

#include "typesystem.h"
#include "containertypeentry.h"
#include "typedatabase.h"
#include "typedatabase_p.h"
#include "typesystem_typedefs.h"
#include "codesnip.h"

#include <QtCore/QStack>
#include <QtCore/QHash>
#include <QtCore/QScopedPointer>

#include <memory>

QT_FORWARD_DECLARE_CLASS(QVersionNumber)
QT_FORWARD_DECLARE_CLASS(QXmlStreamAttributes)
QT_FORWARD_DECLARE_CLASS(QXmlStreamReader)

class ConditionalStreamReader;

class TypeSystemEntityResolver;
class TypeDatabase;

class FlagsTypeEntry;
class TypeSystemTypeEntry;
class ValueTypeEntry;
class EnumTypeEntry;

enum class ParserState;

enum class StackElement {
            None,

            // Type tags
            ObjectTypeEntry,
            FirstTypeEntry = ObjectTypeEntry,
            ValueTypeEntry,
            InterfaceTypeEntry,
            NamespaceTypeEntry,
            LastComplexTypeEntry = NamespaceTypeEntry,

            // Non-complex type tags
            PrimitiveTypeEntry,
            EnumTypeEntry,
            ContainerTypeEntry,
            FunctionTypeEntry,
            CustomTypeEntry,
            SmartPointerTypeEntry,
            TypedefTypeEntry,
            LastTypeEntry = TypedefTypeEntry,

            // Documentation tags
            InjectDocumentation,
            FirstDocumentation = InjectDocumentation,
            ModifyDocumentation,
            LastDocumentation = ModifyDocumentation,

            // Simple tags
            ExtraIncludes,
            Include,
            ModifyFunction,
            ModifyField,
            Root,
            SuppressedWarning,
            Rejection,
            LoadTypesystem,
            RejectEnumValue,
            Template,
            InsertTemplate,
            Replace,
            AddFunction,
            AddPyMethodDef,
            DeclareFunction,
            NativeToTarget,
            TargetToNative,
            AddConversion,
            SystemInclude,
            Property,

            // Code snip tags
            InjectCode,

            // Function modifier tags
            Rename, // (modify-argument)
            ModifyArgument,
            Thread,

            // Argument modifier tags
            ConversionRule,
            ReplaceType,
            ReplaceDefaultExpression,
            RemoveArgument,
            DefineOwnership,
            RemoveDefaultExpression,
            NoNullPointers,
            ReferenceCount,
            ParentOwner,
            Array,
            ArgumentModifiers,

            ImportFile,
            OpaqueContainer,
            Configuration,
            Unimplemented
};

inline uint64_t operator&(StackElement s1, StackElement s2)
{
    return uint64_t(s1) & uint64_t(s2);
}

inline StackElement operator|(StackElement s1, StackElement s2)
{
    return StackElement(uint64_t(s1) | uint64_t(s2));
}

struct StackElementContext
{
    CodeSnipList conversionCodeSnips;
    AddedFunctionList addedFunctions;
    FunctionModificationList functionMods;
    FieldModificationList fieldMods;
    DocModificationList docModifications;
    TypeEntryPtr entry;
    int addedFunctionModificationIndex = -1;
};

class TypeSystemParser
{
public:
    Q_DISABLE_COPY(TypeSystemParser)

    using StackElementContextPtr = std::shared_ptr<StackElementContext>;
    using ContextStack = QStack<StackElementContextPtr>;

    explicit TypeSystemParser(const std::shared_ptr<TypeDatabaseParserContext> &context,
                              bool generate);
    ~TypeSystemParser();

    bool parse(ConditionalStreamReader &reader);

    QString errorString() const { return m_error; }

private:
    bool parseXml(ConditionalStreamReader &reader);
    bool setupSmartPointerInstantiations();
    bool startElement(const ConditionalStreamReader &reader, StackElement element);
    SmartPointerTypeEntryPtr parseSmartPointerEntry(const ConditionalStreamReader &,
                                                  const QString &name,
                                                  const QVersionNumber &since,
                                                  QXmlStreamAttributes *attributes);
    bool endElement(StackElement element);
    template <class String> // QString/QStringRef
    bool characters(const String &ch);

    bool importFileElement(const QXmlStreamAttributes &atts);

    TypeEntryCPtr currentParentTypeEntry() const;
    bool checkRootElement();
    bool applyCommonAttributes(const ConditionalStreamReader &reader,
                               const TypeEntryPtr &type,
                               QXmlStreamAttributes *attributes);
    PrimitiveTypeEntryPtr
        parsePrimitiveTypeEntry(const ConditionalStreamReader &, const QString &name,
                                const QVersionNumber &since, QXmlStreamAttributes *);
    CustomTypeEntryPtr
        parseCustomTypeEntry(const ConditionalStreamReader &, const QString &name,
                             const QVersionNumber &since, QXmlStreamAttributes *);
    bool parseOpaqueContainers(QStringView s, OpaqueContainers *result);
    ContainerTypeEntryPtr
        parseContainerTypeEntry(const ConditionalStreamReader &, const QString &name,
                                 const QVersionNumber &since, QXmlStreamAttributes *);
    bool parseOpaqueContainerElement(QXmlStreamAttributes *attributes);
    EnumTypeEntryPtr
        parseEnumTypeEntry(const ConditionalStreamReader &, const QString &name,
                           const QVersionNumber &since, QXmlStreamAttributes *);
    FlagsTypeEntryPtr
        parseFlagsEntry(const ConditionalStreamReader &, const EnumTypeEntryPtr &enumEntry,
                        QString flagName, const QVersionNumber &since,
                        QXmlStreamAttributes *);

    NamespaceTypeEntryPtr
        parseNamespaceTypeEntry(const ConditionalStreamReader &,
                                const QString &name, const QVersionNumber &since,
                                QXmlStreamAttributes *attributes);

    ValueTypeEntryPtr
        parseValueTypeEntry(const ConditionalStreamReader &, const QString &name,
                            const QVersionNumber &since, QXmlStreamAttributes *);
    FunctionTypeEntryPtr
        parseFunctionTypeEntry(const ConditionalStreamReader &, const QString &name,
                               const QVersionNumber &since, QXmlStreamAttributes *);
    TypedefEntryPtr
        parseTypedefEntry(const ConditionalStreamReader &, const QString &name,
                          StackElement topElement,
                          const QVersionNumber &since, QXmlStreamAttributes *);
    void applyComplexTypeAttributes(const ConditionalStreamReader &, const ComplexTypeEntryPtr &ctype,
                                    QXmlStreamAttributes *) const;
    bool parseConfiguration(StackElement topElement,
                            QXmlStreamAttributes *attributes);
    bool parseRenameFunction(const ConditionalStreamReader &, QString *name,
                             QXmlStreamAttributes *);
    bool parseInjectDocumentation(const ConditionalStreamReader &, StackElement topElement,
                                  QXmlStreamAttributes *);
    bool parseModifyDocumentation(const ConditionalStreamReader &, StackElement topElement,
                                  QXmlStreamAttributes *);
    TypeSystemTypeEntryPtr
        parseRootElement(const ConditionalStreamReader &, const QVersionNumber &since,
                         QXmlStreamAttributes *);
    bool loadTypesystem(const ConditionalStreamReader &, QXmlStreamAttributes *);
    bool parseRejectEnumValue(const ConditionalStreamReader &, QXmlStreamAttributes *);
    bool parseReplaceArgumentType(const ConditionalStreamReader &, StackElement topElement,
                                  QXmlStreamAttributes *);
    bool parseCustomConversion(const ConditionalStreamReader &, StackElement topElement,
                               QXmlStreamAttributes *);
    bool parseAddConversion(const ConditionalStreamReader &, StackElement topElement,
                            QXmlStreamAttributes *);
    bool parseNativeToTarget(const ConditionalStreamReader &, StackElement topElement,
                             QXmlStreamAttributes *attributes);
    bool parseModifyArgument(const ConditionalStreamReader &, StackElement topElement,
                             QXmlStreamAttributes *attributes);
    bool parseNoNullPointer(const ConditionalStreamReader &, StackElement topElement,
                            QXmlStreamAttributes *attributes);
    bool parseDefineOwnership(const ConditionalStreamReader &, StackElement topElement,
                              QXmlStreamAttributes *);
    bool parseRename(const ConditionalStreamReader &, StackElement topElement,
                     QXmlStreamAttributes *);
    bool parseModifyField(const ConditionalStreamReader &, QXmlStreamAttributes *);
    bool parseAddFunction(const ConditionalStreamReader &, StackElement topElement,
                          StackElement t, QXmlStreamAttributes *);
    bool parseAddPyMethodDef(const ConditionalStreamReader &,
                             StackElement topElement, QXmlStreamAttributes *attributes);
    bool parseProperty(const ConditionalStreamReader &, StackElement topElement,
                       QXmlStreamAttributes *);
    bool parseModifyFunction(const ConditionalStreamReader &, StackElement topElement,
                             QXmlStreamAttributes *);
    bool parseReplaceDefaultExpression(const ConditionalStreamReader &,
                                       StackElement topElement, QXmlStreamAttributes *);
     bool parseReferenceCount(const ConditionalStreamReader &, StackElement topElement,
                              QXmlStreamAttributes *);
     bool parseParentOwner(const ConditionalStreamReader &, StackElement topElement,
                           QXmlStreamAttributes *);
     bool readFileSnippet(QXmlStreamAttributes *attributes, CodeSnip *snip);
     bool parseInjectCode(const ConditionalStreamReader &, StackElement topElement, QXmlStreamAttributes *);
     bool parseInclude(const ConditionalStreamReader &, StackElement topElement,
                       const TypeEntryPtr &entry, QXmlStreamAttributes *);
     bool parseSystemInclude(const ConditionalStreamReader &, QXmlStreamAttributes *);
     TemplateInstance
         *parseInsertTemplate(const ConditionalStreamReader &, StackElement topElement,
                              QXmlStreamAttributes *);
     bool parseReplace(const ConditionalStreamReader &, StackElement topElement,
                       QXmlStreamAttributes *);
     bool checkDuplicatedTypeEntry(const ConditionalStreamReader &reader,
                                   StackElement t, const QString &name) const;
     ParserState parserState(qsizetype offset = 0) const;
     CodeSnipAbstract *injectCodeTarget(qsizetype offset = 0) const;

    std::shared_ptr<TypeDatabaseParserContext> m_context;
    QStack<StackElement> m_stack;
    int m_currentDroppedEntryDepth = 0;
    int m_ignoreDepth = 0;
    QString m_defaultPackage;
    QString m_defaultSuperclass;
    TypeSystem::ExceptionHandling m_exceptionHandling = TypeSystem::ExceptionHandling::Unspecified;
    TypeSystem::AllowThread m_allowThread = TypeSystem::AllowThread::Unspecified;
    QString m_error;
    const TypeEntry::CodeGeneration m_generate;

    EnumTypeEntryPtr m_currentEnum;
    TemplateInstancePtr m_templateInstance;
    TemplateEntryPtr m_templateEntry;
    ContextStack m_contextStack;

    QString m_currentSignature;
    QString m_currentPath;
    QString m_currentFile;
    QScopedPointer<TypeSystemEntityResolver> m_entityResolver;
};

#endif // TYPESYSTEMPARSER_H
