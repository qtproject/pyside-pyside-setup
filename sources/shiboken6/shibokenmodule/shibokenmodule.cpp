// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

// @snippet isvalid
bool isValid = Shiboken::Object::isValid(%1, false);
%PYARG_0 = %CONVERTTOPYTHON[bool](isValid);
// @snippet isvalid

// @snippet wrapinstance
auto *pyType = reinterpret_cast<PyTypeObject *>(%2);
if (Shiboken::ObjectType::checkType(pyType)) {
    auto *ptr = reinterpret_cast<void *>(%1);
#ifdef Py_GIL_DISABLED
    if (auto wrapper = Shiboken::BindingManager::instance().acquireWrapper(ptr)) {
        %PYARG_0 = reinterpret_cast<PyObject *>(wrapper.release());
    } else {
        %PYARG_0 = Shiboken::Object::newObject(pyType, ptr, false, true);
    }
#else
    if (auto *wrapper = Shiboken::BindingManager::instance().retrieveWrapper(ptr)) {
        %PYARG_0 = reinterpret_cast<PyObject *>(wrapper);
        Py_INCREF(%PYARG_0);
    } else {
        %PYARG_0 = Shiboken::Object::newObject(pyType, ptr, false, true);
    }
#endif // Py_GIL_DISABLED
} else {
    PyErr_SetString(PyExc_TypeError, "You need a shiboken-based type.");
}
// @snippet wrapinstance

// @snippet getcpppointer
if (Shiboken::Object::checkType(%1)) {
    std::vector<void*> ptrs = Shiboken::Object::cppPointers(reinterpret_cast<SbkObject *>(%1));
    %PYARG_0 = PyTuple_New(ptrs.size());
    for (std::size_t i = 0; i < ptrs.size(); ++i)
        PyTuple_SetItem(%PYARG_0, i, PyLong_FromVoidPtr(ptrs[i]));
} else {
    PyErr_SetString(PyExc_TypeError, "You need a shiboken-based type.");
}
// @snippet getcpppointer

// @snippet delete
if (Shiboken::Object::checkType(%1)) {
    Shiboken::Object::callCppDestructors(reinterpret_cast<SbkObject *>(%1));
} else {
    PyErr_SetString(PyExc_TypeError, "You need a shiboken-based type.");
}
// @snippet delete

// @snippet ownedbypython
if (Shiboken::Object::checkType(%1)) {
    bool hasOwnership = Shiboken::Object::hasOwnership(reinterpret_cast<SbkObject *>(%1));
    %PYARG_0 = %CONVERTTOPYTHON[bool](hasOwnership);
} else {
    PyErr_SetString(PyExc_TypeError, "You need a shiboken-based type.");
}
// @snippet ownedbypython

// @snippet createdbypython
if (Shiboken::Object::checkType(%1)) {
    bool wasCreatedByPython = Shiboken::Object::wasCreatedByPython(reinterpret_cast<SbkObject *>(%1));
    %PYARG_0 = %CONVERTTOPYTHON[bool](wasCreatedByPython);
} else {
    PyErr_SetString(PyExc_TypeError, "You need a shiboken-based type.");
}
// @snippet createdbypython

// @snippet disassembleframe
Shiboken::AutoDecRef label(PyObject_Str(%1));
const char *marker = Shiboken::String::toCString(label);
disassembleFrame(marker);
Py_INCREF(Py_None);
%PYARG_0 = Py_None;
// @snippet disassembleframe

// @snippet dump
if (!Shiboken::Object::checkType(%1)) {
    %PYARG_0 = Shiboken::String::fromCString("Ordinary Python type.");
} else {
    std::string str = Shiboken::Object::info(reinterpret_cast<SbkObject *>(%1));
    %PYARG_0 = Shiboken::String::fromCString(str.c_str());
}
// @snippet dump


// @snippet dump-tree
#ifdef Py_GIL_DISABLED
// See "Who may read parentInfo" in the free-threading notes.
PyErr_SetString(PyExc_NotImplementedError,
                "dumpTree() is not available in a free-threaded build");
#else
if (!Shiboken::Object::checkType(%1)) {
    %PYARG_0 = Shiboken::String::fromCString("Ordinary Python type.");
} else {
    std::string str = Shiboken::Object::dumpTree(reinterpret_cast<SbkObject *>(%1));
    %PYARG_0 = Shiboken::String::fromCString(str.c_str());
}
#endif
// @snippet dump-tree

// @snippet replacemoduledict
const bool ok = Shiboken::Module::replaceModuleDict(%1, %2, %3);
%PYARG_0 = %CONVERTTOPYTHON[bool](ok);
// @snippet replacemoduledict

// @snippet getallvalidwrappers
const auto setAll = Shiboken::BindingManager::instance().getAllPyObjects();
PyObject* listAll = PyList_New(0);
if (listAll == nullptr)
    return nullptr;
#ifdef Py_GIL_DISABLED
// PyList_Append() takes its own reference, so the ones held here are dropped
// when the vector goes out of scope.
for (const auto &wrapper : setAll) {
    if (PyList_Append(listAll, wrapper.pyObject()) != 0) {
        Py_DECREF(listAll);
        return nullptr;
    }
}
#else
for (auto *o : setAll) {
    if (o != nullptr) {
        if (PyList_Append(listAll, o) != 0) {
            Py_DECREF(listAll);
            return nullptr;
        }
    }
}
#endif // Py_GIL_DISABLED
return listAll;
// @snippet getallvalidwrappers

// @snippet armfailpoint
#ifdef Py_GIL_DISABLED
// The two kinds have disjoint names: a throwing point is armed as one,
// every other name goes to the parking kind.
const bool ok = Shiboken::armFailpointThrow(%1) || Shiboken::armFailpoint(%1, %2);
#else
const bool ok = Shiboken::armFailpoint(%1, %2);
#endif
%PYARG_0 = %CONVERTTOPYTHON[bool](ok);
// @snippet armfailpoint

// @snippet releasefailpoint
#ifdef Py_GIL_DISABLED
// A throwing point parks nobody: releasing it disarms it, if it is armed.
const bool ok = Shiboken::releaseFailpoint(%1) || Shiboken::disarmFailpointThrow(%1);
#else
const bool ok = Shiboken::releaseFailpoint(%1);
#endif
%PYARG_0 = %CONVERTTOPYTHON[bool](ok);
// @snippet releasefailpoint

// @snippet failpointreached
const bool ok = Shiboken::failpointReached(%1);
%PYARG_0 = %CONVERTTOPYTHON[bool](ok);
// @snippet failpointreached

// @snippet clearfailpoints
Shiboken::clearFailpoints();
// @snippet clearfailpoints

// @snippet failpointnames
const char *names = Shiboken::failpointNames();
%PYARG_0 = %CONVERTTOPYTHON[const char *](names);
// @snippet failpointnames

// @snippet heldrawlocks
const char *held = Shiboken::heldLockNames();
%PYARG_0 = %CONVERTTOPYTHON[const char *](held);
// @snippet heldrawlocks

// @snippet contractexceptions
const char *taken = Shiboken::contractExceptions();
%PYARG_0 = %CONVERTTOPYTHON[const char *](taken);
// @snippet contractexceptions

// @snippet locknestings
const char *nestings = Shiboken::lockNestings();
%PYARG_0 = %CONVERTTOPYTHON[const char *](nestings);
// @snippet locknestings

// @snippet activecalls
size_t count = 0;
if (Shiboken::Object::checkType(%1))
    count = Shiboken::Object::activeCalls(reinterpret_cast<SbkObject *>(%1));
%PYARG_0 = %CONVERTTOPYTHON[size_t](count);
// @snippet activecalls

// @snippet dumptypegraph
const bool ok = Shiboken::BindingManager::instance().dumpTypeGraph(%1);
%PYARG_0 = %CONVERTTOPYTHON[bool](ok);
// @snippet dumptypegraph

// @snippet dumpwrappermap
Shiboken::BindingManager::instance().dumpWrapperMap();
// @snippet dumpwrappermap

// @snippet dumpconverters
Shiboken::Conversions::dumpConverters();
// @snippet dumpconverters

// @snippet init
// Add __version__ and __version_info__ attributes to the module
PyObject* version = PyTuple_New(5);
PyTuple_SetItem(version, 0, PyLong_FromLong(SHIBOKEN_MAJOR_VERSION));
PyTuple_SetItem(version, 1, PyLong_FromLong(SHIBOKEN_MINOR_VERSION));
PyTuple_SetItem(version, 2, PyLong_FromLong(SHIBOKEN_MICRO_VERSION));
PyTuple_SetItem(version, 3, Shiboken::String::fromCString(SHIBOKEN_RELEASE_LEVEL));
PyTuple_SetItem(version, 4, PyLong_FromLong(SHIBOKEN_SERIAL));
PepModule_Add(module, "__version_info__", version);
PyModule_AddStringConstant(module, "__version__", SHIBOKEN_VERSION);
VoidPtr::addVoidPtrToModule(module);
Shiboken::initShibokenSupport(module);
// @snippet init
