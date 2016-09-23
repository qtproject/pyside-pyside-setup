/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of PySide2.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef BASEWRAPPER_P_H
#define BASEWRAPPER_P_H

#include "sbkpython.h"
#include <list>
#include <map>
#include <set>
#include <string>

struct SbkObject;
struct SbkObjectType;
struct SbkConverter;

namespace Shiboken
{
/**
    * This mapping associates a method and argument of an wrapper object with the wrapper of
    * said argument when it needs the binding to help manage its reference count.
    */
typedef std::map<std::string, std::list<PyObject*> > RefCountMap;

/// Linked list of SbkBaseWrapper pointers
typedef std::set<SbkObject*> ChildrenList;

/// Structure used to store information about object parent and children.
struct ParentInfo
{
    /// Default ctor.
    ParentInfo() : parent(0), hasWrapperRef(false) {}
    /// Pointer to parent object.
    SbkObject* parent;
    /// List of object children.
    ChildrenList children;
    /// has internal ref
    bool hasWrapperRef;
};

} // namespace Shiboken

extern "C"
{

/**
 * \internal
 * Private data for SbkBaseWrapper
 */
struct SbkObjectPrivate
{
    /// Pointer to the C++ class.
    void** cptr;
    /// True when Python is responsible for freeing the used memory.
    unsigned int hasOwnership : 1;
    /// This is true when the C++ class of the wrapped object has a virtual destructor AND was created by Python.
    unsigned int containsCppWrapper : 1;
    /// Marked as false when the object is lost to C++ and the binding can not know if it was deleted or not.
    unsigned int validCppObject : 1;
    /// Marked as true when the object constructor was called
    unsigned int cppObjectCreated : 1;
    /// Information about the object parents and children, may be null.
    Shiboken::ParentInfo* parentInfo;
    /// Manage reference count of objects that are referred to but not owned from.
    Shiboken::RefCountMap* referredObjects;

    ~SbkObjectPrivate()
    {
        delete parentInfo;
        parentInfo = 0;
        delete referredObjects;
        referredObjects = 0;
    }
};

// TODO-CONVERTERS: to be deprecated/removed
/// The type behaviour was not defined yet
#define BEHAVIOUR_UNDEFINED 0
/// The type is a value type
#define BEHAVIOUR_VALUETYPE 1
/// The type is an object type
#define BEHAVIOUR_OBJECTTYPE 2

struct SbkObjectTypePrivate
{
    SbkConverter* converter;
    int* mi_offsets;
    MultipleInheritanceInitFunction mi_init;

    /// Special cast function, null if this class doesn't have multiple inheritance.
    SpecialCastFunction mi_specialcast;
    TypeDiscoveryFuncV2 type_discovery;
    /// Pointer to a function responsible for deletion of the C++ instance calling the proper destructor.
    ObjectDestructor cpp_dtor;
    /// True if this type holds two or more C++ instances, e.g.: a Python class which inherits from two C++ classes.
    int is_multicpp : 1;
    /// True if this type was defined by the user.
    int is_user_type : 1;
    /// Tells is the type is a value type or an object-type, see BEHAVIOUR_* constants.
    // TODO-CONVERTERS: to be deprecated/removed
    int type_behaviour : 2;
    /// C++ name
    char* original_name;
    /// Type user data
    void* user_data;
    DeleteUserDataFunc d_func;
    void (*subtype_init)(SbkObjectType*, PyObject*, PyObject*);
};


} // extern "C"

namespace Shiboken
{
/**
 * Utility function used to transform a PyObject that implements sequence protocol into a std::list.
 **/
std::list<SbkObject*> splitPyObject(PyObject* pyObj);

/**
*   Visitor class used by walkOnClassHierarchy function.
*/
class HierarchyVisitor
{
public:
    HierarchyVisitor() : m_wasFinished(false) {}
    virtual ~HierarchyVisitor() {}
    virtual void visit(SbkObjectType* node) = 0;
    virtual void done() {}
    void finish() { m_wasFinished = true; };
    bool wasFinished() const { return m_wasFinished; }
private:
    bool m_wasFinished;
};

class BaseCountVisitor : public HierarchyVisitor
{
public:
    BaseCountVisitor() : m_count(0) {}

    void visit(SbkObjectType*)
    {
        m_count++;
    }

    int count() const { return m_count; }
private:
    int m_count;
};

class BaseAccumulatorVisitor : public HierarchyVisitor
{
public:
    BaseAccumulatorVisitor() {}

    void visit(SbkObjectType* node)
    {
        m_bases.push_back(node);
    }

    std::list<SbkObjectType*> bases() const { return m_bases; }
private:
    std::list<SbkObjectType*> m_bases;
};

class GetIndexVisitor : public HierarchyVisitor
{
public:
    GetIndexVisitor(PyTypeObject* desiredType) : m_index(-1), m_desiredType(desiredType) {}
    virtual void visit(SbkObjectType* node)
    {
        m_index++;
        if (PyType_IsSubtype(reinterpret_cast<PyTypeObject*>(node), m_desiredType))
            finish();
    }
    int index() const { return m_index; }

private:
    int m_index;
    PyTypeObject* m_desiredType;
};

/// Call the destructor of each C++ object held by a Python object
class DtorCallerVisitor : public HierarchyVisitor
{
public:
    DtorCallerVisitor(SbkObject* pyObj) : m_pyObj(pyObj) {}
    void visit(SbkObjectType* node);
    void done();
protected:
    std::list<std::pair<void*, SbkObjectType*> > m_ptrs;
    SbkObject* m_pyObj;
};

/// Dealloc of each C++ object held by a Python object, this implies a call to the C++ object destructor
class DeallocVisitor : public DtorCallerVisitor
{
public:
    DeallocVisitor(SbkObject* pyObj) : DtorCallerVisitor(pyObj) {}
    void done();
};

/// \internal Internal function used to walk on classes inheritance trees.
/**
*   Walk on class hierarchy using a DFS algorithm.
*   For each pure Shiboken type found, HiearchyVisitor::visit is called and the algorithm consider
*   all children of this type as visited.
*/
void walkThroughClassHierarchy(PyTypeObject* currentType, HierarchyVisitor* visitor);

inline int getTypeIndexOnHierarchy(PyTypeObject* baseType, PyTypeObject* desiredType)
{
    GetIndexVisitor visitor(desiredType);
    walkThroughClassHierarchy(baseType, &visitor);
    return visitor.index();
}

inline int getNumberOfCppBaseClasses(PyTypeObject* baseType)
{
    BaseCountVisitor visitor;
    walkThroughClassHierarchy(baseType, &visitor);
    return visitor.count();
}

inline std::list<SbkObjectType*> getCppBaseClasses(PyTypeObject* baseType)
{
    BaseAccumulatorVisitor visitor;
    walkThroughClassHierarchy(baseType, &visitor);
    return visitor.bases();
}

namespace Object
{
/**
*   Decrements the reference counters of every object referred by self.
*   \param self    the wrapper instance that keeps references to other objects.
*/
void clearReferences(SbkObject* self);

/**
 * Destroy internal data
 **/
void deallocData(SbkObject* self, bool doCleanup);

} // namespace Object

} // namespace Shiboken

#endif
