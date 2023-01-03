// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef GENERATOR_H
#define GENERATOR_H

#include <abstractmetalang_typedefs.h>
#include <typedatabase_typedefs.h>
#include <QtCore/QList>

#include <memory>
#include <optional>


class ApiExtractorResult;
class GeneratorContext;
class DefaultValue;
class TextStream;

QString getClassTargetFullName(const AbstractMetaClassCPtr &metaClass,
                               bool includePackageName = true);
QString getClassTargetFullName(const AbstractMetaEnum &metaEnum,
                               bool includePackageName = true);
QString getFilteredCppSignatureString(QString signature);

/**
 *   Base class for all generators. The default implementations does nothing,
 *   you must subclass this to create your own generators.
 */
class Generator
{
public:
    using OptionDescription = QPair<QString, QString>;
    using OptionDescriptions = QList<OptionDescription>;

    /// Optiosn used around the generator code
    enum Option {
        NoOption                 = 0x00000000,
        ExcludeConst             = 0x00000001,
        ExcludeReference         = 0x00000002,

        SkipReturnType           = 0x00000010,
        VirtualCall              = 0x00000040,
        OriginalTypeDescription  = 0x00000080,
        SkipRemovedArguments     = 0x00000100,

        SkipDefaultValues        = 0x00000200,
    };
    Q_DECLARE_FLAGS(Options, Option)

    enum FileNameFlag {
        UnqualifiedName = 0x1,
        KeepCase = 0x2
    };
    Q_DECLARE_FLAGS(FileNameFlags, FileNameFlag)

    Generator();
    virtual ~Generator();

    bool setup(const ApiExtractorResult &api);

    virtual OptionDescriptions options() const;
    virtual bool handleOption(const QString &key, const QString &value);

    /// Returns the top namespace made invisible
    const AbstractMetaClassCList &invisibleTopNamespaces() const;

    /// Returns the output directory
    QString outputDirectory() const;

    /// Set the output directory
    void setOutputDirectory(const QString &outDir);

    /**
     *   Start the code generation, be sure to call setClasses before callign this method.
     *   For each class it creates a QTextStream, call the write method with the current
     *   class and the associated text stream, then write the text stream contents if needed.
     *   \see #write
     */
    bool generate();

    /// Returns the license comment to be prepended to each source file generated.
    QString licenseComment() const;

    /// Sets the license comment to be prepended to each source file generated.
    void setLicenseComment(const QString &licenseComment);

    /// Returns the generator's name. Used for cosmetic purposes.
    virtual const char *name() const = 0;

    /// Returns the API as determined by ApiExtractor
    const ApiExtractorResult &api() const;

    bool hasPrivateClasses() const;

    /// Returns true if the user enabled PySide extensions (command line option)
    bool usePySideExtensions() const;
    /// Returns true if the generated code should not use the
    /// "#define protected public" hack.
    bool avoidProtectedHack() const;

    /**
     *  Retrieves the name of the currently processed module.
     *  While package name is a complete package idetification, e.g. 'PySide.QtCore',
     *  a module name represents the last part of the package, e.g. 'QtCore'.
     *  If the target language separates the modules with characters other than
     *  dots ('.') the generator subclass must overload this method.
     *  \return a string representing the last part of a package name
     */
    static QString moduleName();

    static QString pythonOperatorFunctionName(const QString &cppOpFuncName);

protected:
    /// Helper for determining the file name
    static QString fileNameForContextHelper(const GeneratorContext &context,
                                            const QString &suffix,
                                            FileNameFlags flags = {});

    /// Returns all primitive types found by APIExtractor
    static PrimitiveTypeEntryCList primitiveTypes();

    /// Returns all container types found by APIExtractor
    static ContainerTypeEntryCList containerTypes();

    virtual GeneratorContext contextForClass(const AbstractMetaClassCPtr &c) const;
    static GeneratorContext
        contextForSmartPointer(const AbstractMetaClassCPtr &c, const AbstractMetaType &t,
                           const AbstractMetaClassCPtr &pointeeClass = {});

    /// Generates a file for given AbstractMetaClass or AbstractMetaType (smart pointer case).
    bool generateFileForContext(const GeneratorContext &context);

    /// Returns the file base name for a smart pointer.
    static QString getFileNameBaseForSmartPointer(const AbstractMetaType &smartPointerType);

    /// Returns true if the generator should generate any code for the AbstractMetaClass.
    virtual bool shouldGenerate(const TypeEntryCPtr &t) const;

    /**
    *   Translate metatypes to binding source format.
    *   \param metatype a pointer to metatype
    *   \param context the current meta class
    *   \param option some extra options
    *   \return the metatype translated to binding source format
    */
    QString translateType(AbstractMetaType metatype,
                          const AbstractMetaClassCPtr &context,
                          Options options = NoOption) const;

    /**
     *   Returns the package name.
     */
    static QString packageName();

    // Returns the full name of the type.
    static QString getFullTypeName(TypeEntryCPtr type);
    static QString getFullTypeName(const AbstractMetaType &type);
    static QString getFullTypeName(const AbstractMetaClassCPtr &metaClass);

    /**
     *  Returns the full qualified C++ name for an AbstractMetaType, but removing modifiers
     *  as 'const', '&', and '*' (except if the class is not derived from a template).
     *  This is useful for instantiated templates.
     */
    static QString getFullTypeNameWithoutModifiers(const AbstractMetaType &type);

    /**
     *   Tries to build a minimal constructor for the type.
     *   It will check first for a user defined default constructor.
     *   Returns a null string if it fails.
     */
    static std::optional<DefaultValue>
        minimalConstructor(const ApiExtractorResult &api, const TypeEntryCPtr &type,
                           QString *errorString = nullptr);
    static std::optional<DefaultValue>
        minimalConstructor(const ApiExtractorResult &api, const AbstractMetaType &type,
                           QString *errorString = nullptr);
    static std::optional<DefaultValue>
        minimalConstructor(const ApiExtractorResult &api,
                           const AbstractMetaClassCPtr &metaClass,
                           QString *errorString = nullptr);

    /**
     *   Returns the file name used to write the binding code of an AbstractMetaClass/Type.
     *   \param context the GeneratorContext which contains an AbstractMetaClass or AbstractMetaType
     *   for which the file name must be returned
     *   \return the file name used to write the binding code for the class
     */
    virtual QString fileNameForContext(const GeneratorContext &context) const = 0;


    virtual bool doSetup() = 0;

    /**
     *   Write the bindding code for an AbstractMetaClass.
     *   This is called by generate method.
     *   \param  s   text stream to write the generated output
     *   \param  metaClass  the class that should be generated
     */
    virtual void generateClass(TextStream &s, const GeneratorContext &classContext) = 0;
    virtual bool finishGeneration() = 0;

    /**
    *    Returns the subdirectory path for a given package
    *    (aka module, aka library) name.
    *    If the target language separates the package modules with characters other
    *    than dots ('.') the generator subclass must overload this method.
    *    /param packageName complete package name for which to return the subdirectory path
    *    or nothing the use the name of the currently processed package
    *    /return a string representing the subdirectory path for the given package
    */
    virtual QString subDirectoryForPackage(QString packageName = QString()) const;

private:
    struct GeneratorPrivate;
    GeneratorPrivate *m_d;
};

Q_DECLARE_OPERATORS_FOR_FLAGS(Generator::Options)
Q_DECLARE_OPERATORS_FOR_FLAGS(Generator::FileNameFlags)

using GeneratorPtr = std::shared_ptr<Generator>;
using Generators = QList<GeneratorPtr>;

#endif // GENERATOR_H
