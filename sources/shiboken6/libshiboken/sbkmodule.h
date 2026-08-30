// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBK_MODULE_H
#define SBK_MODULE_H

#include "sbkpython.h"
#include "shibokenmacros.h"

#include <atomic>

extern "C"
{
struct SbkConverter;
}

namespace Shiboken::Module {

#ifdef Py_GIL_DISABLED
/// A one-way flag: false until something is finished, true from then on. The
/// store is a release and the load an acquire, so whoever sees it set also
/// sees everything that was stored before it.
///
/// Not copyable, and that is what keeps TypeInitStruct out of a by-value
/// parameter: a copy of a registry entry carries a flag that nothing will
/// ever set, and a copied atomic changes how the struct is passed.
class ReadyFlag
{
public:
    ReadyFlag() noexcept = default;
    ReadyFlag(const ReadyFlag &) = delete;
    ReadyFlag &operator=(const ReadyFlag &) = delete;

    bool isSet() const noexcept { return m_value.load(std::memory_order_acquire); }
    void set() noexcept { m_value.store(true, std::memory_order_release); }

private:
    std::atomic<bool> m_value;
};
#endif // Py_GIL_DISABLED

struct TypeInitStruct
{
    PyTypeObject *type;
    const char *fullName;
#ifdef Py_GIL_DISABLED
    /// Set at the end of the generated type initialization, once the
    /// converter is registered. `type` is published earlier than that on
    /// purpose - it is the re-entrancy guard for an initialization that
    /// nests on the same thread - so the pointer alone does not mean the
    /// type can be converted. get() hands the type out from its unlocked
    /// fast path only once this is set.
    ///
    /// It does not cover what the module does with the type afterwards:
    /// incarnateType() adds it to its module and creates its subtypes, and
    /// the static fields of a class are filled from exec_<module>(). A
    /// caller that needs those has to go through the attribute, as it
    /// always had to.
    ///
    /// Braced, because the generated type array initializes the first two
    /// members only.
    ReadyFlag ready{};
#endif // Py_GIL_DISABLED
};

/// PYSIDE-2404: Replacing the arguments in cpythonTypeNameExt by a function.
LIBSHIBOKEN_API PyTypeObject *get(TypeInitStruct &typeStruct);

#ifdef Py_GIL_DISABLED
/// End of the generated type initialization: everything stored before this
/// is visible to whoever sees the type through get().
LIBSHIBOKEN_API void setReady(TypeInitStruct &typeStruct);
#endif

/// PYSIDE-2404: Make sure that mentioned classes really exist.
LIBSHIBOKEN_API void loadLazyClassesWithName(const char *name);

/// PYSIDE-2404: incarnate all classes for star imports.
LIBSHIBOKEN_API void resolveLazyClasses(PyObject *module);

/**
 *  Imports and returns the module named \p moduleName, or a NULL pointer in case of failure.
 *  If the module is already imported, it increments its reference count before returning it.
 *  \returns the module specified in \p moduleName or NULL if an error occurs.
 */
LIBSHIBOKEN_API PyObject *import(const char *moduleName);

/**
 *  Creates a new Python module named \p moduleName using the information passed in \p moduleData
 *  and calls exec() on it.
 *  \returns a newly created module.
 */
[[deprecated]] LIBSHIBOKEN_API PyObject *create(const char *moduleName, PyModuleDef *moduleData);

/// Creates a new Python module named \p moduleName using the information passed in \p moduleData.
/// exec() is not called (Support for Nuitka).
/// \returns a newly created module.
LIBSHIBOKEN_API PyObject *createOnly(const char *moduleName, PyModuleDef *moduleData);

/// Executes a module (multi-phase initialization helper)
LIBSHIBOKEN_API void exec(PyObject *module);

using TypeCreationFunction = PyTypeObject *(*)(PyObject *module);

/// Adds a type creation function to the module.
LIBSHIBOKEN_API void AddTypeCreationFunction(PyObject *module,
                                             const char *name,
                                             TypeCreationFunction func);

LIBSHIBOKEN_API void AddTypeCreationFunction(PyObject *module,
                                             const char *enclosingName,
                                             TypeCreationFunction func,
                                             const char *subTypeNamePath);

/**
 *  Registers the list of types created by \p module.
 *  \param module   Module where the types were created.
 *  \param types    Array of PyTypeObject *objects representing the types created on \p module.
 */
LIBSHIBOKEN_API void registerTypes(PyObject *module, TypeInitStruct *types);

/**
 *  Retrieves the array of types.
 *  \param module   Module where the types were created.
 *  \returns        A pointer to the PyTypeObject *array of types.
 */
LIBSHIBOKEN_API TypeInitStruct *getTypes(PyObject *module);

/**
 *  Registers the list of converters created by \p module for non-wrapper types.
 *  \param module       Module where the converters were created.
 *  \param converters   Array of SbkConverter *objects representing the converters created on \p module.
 */
LIBSHIBOKEN_API void registerTypeConverters(PyObject *module, SbkConverter **converters);

/**
 *  Retrieves the array of converters.
 *  \param module   Module where the converters were created.
 *  \returns        A pointer to the SbkConverter *array of converters.
 */
LIBSHIBOKEN_API SbkConverter **getTypeConverters(PyObject *module);

/**
 *  Replace the dictionary of a module. This allows to use `__missing__`.
 */
LIBSHIBOKEN_API bool replaceModuleDict(PyObject *module, PyObject *modClass, PyObject *dict);

} // namespace Shiboken::Module

#endif // SBK_MODULE_H
