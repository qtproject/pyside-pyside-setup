// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "basewrapper.h"
#include "basewrapper_p.h"
#include "pep384impl.h"

#include <iostream>
#include <sstream>

namespace Shiboken::Object {

static std::vector<PyTypeObject *> getBases(SbkObject *self)
{
    auto *type = Shiboken::pyType(self);
    return ObjectType::isUserType(type)
        ? getCppBaseClasses(type)
        : std::vector<PyTypeObject *>(1, type);
}

static bool isValueType(SbkObject *self)
{
    return PepType_SOTP(Shiboken::pyType(self))->type_behaviour == BEHAVIOUR_VALUETYPE;
}

void _debugFormat(std::ostream &s, SbkObject *self)
{
    assert(self);
    auto *d = self->d;
    if (!d) {
        s  << "[Invalid]";
        return;
    }
    if (d->cptr) {
        const std::vector<PyTypeObject *> bases = getBases(self);
        for (size_t i = 0, size = bases.size(); i < size; ++i)
            s << ", C++: " << bases[i]->tp_name << '/' << self->d->cptr[i];
    } else {
         s << " [Deleted]";
    }
    if (d->hasOwnership)
        s << " [hasOwnership]";
    if (d->containsCppWrapper)
        s << " [containsCppWrapper]";
    if (d->validCppObject)
        s << " [validCppObject]";
    if (d->cppObjectCreated)
        s << " [wasCreatedByPython]";
    s << (isValueType(self) ? " [value]" : " [object]");

#ifdef Py_GIL_DISABLED
    // The graph and the referred objects are published under the state lock;
    // read them there, to the end. Not callable while holding it.
    // See "Who may read parentInfo" in the free-threading notes.
    StateLockGuard guard;
#endif
    if (d->parentInfo) {
        if (auto *parent = d->parentInfo->parent)
            s << ", parent=" << reinterpret_cast<PyObject *>(parent)->ob_type->tp_name
                << '/' << parent;
        if (!d->parentInfo->children.empty())
            s << ", " << d->parentInfo->children.size() << " child(ren)";
    }
    if (d->referredObjects && !d->referredObjects->empty())
        s << ", " << d->referredObjects->size() << " referred object(s)";
}

static void info_format_preamble(std::ostream &s, SbkObject *self, const std::string &indent)
{
    s << indent << "id................ " << self << '\n';
    if (self->d && self->d->cptr) {
        const std::vector<PyTypeObject *> bases = getBases(self);

        s << indent << "C++ address....... ";
        for (size_t i = 0, size = bases.size(); i < size; ++i)
            s << bases[i]->tp_name << '/' << self->d->cptr[i] << ' ';
        s << "\n";
    }
    else {
        s << indent << "C++ address....... <<Deleted>>\n";
    }

    s << indent << "hasOwnership...... " << bool(self->d->hasOwnership) << '\n'
        << indent << "containsCppWrapper " << self->d->containsCppWrapper << '\n'
        << indent << "validCppObject.... " << self->d->validCppObject << '\n'
        << indent << "wasCreatedByPython " << self->d->cppObjectCreated << '\n'
        << indent << "value......        " << isValueType(self) << '\n'
        << indent << "reference count... " << Py_REFCNT(reinterpret_cast<PyObject *>(self)) << '\n';
}

static void info_format_parent(std::ostream &s, SbkObject *self, const std::string &indent)
{
    if (self->d->parentInfo && self->d->parentInfo->parent) {
        auto *obParent = reinterpret_cast<PyObject *>(self->d->parentInfo->parent);
        s << indent << "parent............ <" << Py_TYPE(obParent)->tp_name << " at " << obParent << ">\n";
    }
}

static void info_format_children(std::ostream &s, SbkObject *self, const std::string &indent)
{
    if (self->d->parentInfo && !self->d->parentInfo->children.empty()) {
        const auto &children = self->d->parentInfo->children;
        s << indent << "children.......... [" << children.size() << "] ";
        int n = 0;
        for (SbkObject *sbkChild : children) {
            auto *obChild = reinterpret_cast<PyObject *>(sbkChild);
            if (n++ > 5) {
                s << "...";
                break;
            }
            s << '<' << Py_TYPE(obChild)->tp_name << " at " << obChild << "> ";
        }
        s << '\n';
    }
}

static void info_format_referredObjects(std::ostream &s, SbkObject *self, const std::string &indent)
{
    if (self->d->referredObjects && !self->d->referredObjects->empty()) {
        const Shiboken::RefCountMap &map = *self->d->referredObjects;
        s << indent << "referred objects.. ";
        std::string lastKey;
        for (const auto &p : map) {
            if (p.first != lastKey) {
                if (!lastKey.empty())
                    s << "                   ";
                s << '"' << p.first << "\" => ";
                lastKey = p.first;
            }
            s << '<' << Py_TYPE(p.second)->tp_name << " at " << p.second << "> ";
        }
        s << '\n';
    }
}

#ifndef Py_GIL_DISABLED
static void dumpTreeRecursion(std::ostream &s, SbkObject *self, unsigned depth = 0)
{
    const std::string indent(4 * depth, ' ');
    info_format_preamble(s, self, indent);
    info_format_referredObjects(s, self, indent);
    if (self->d->parentInfo && !self->d->parentInfo->children.empty()) {
        s << indent << "Children:\n";
        for (SbkObject *sbkChild : self->d->parentInfo->children) {
            dumpTreeRecursion(s, sbkChild, depth + 1);
            s << '\n';
        }
    }
}
#endif // !Py_GIL_DISABLED

std::string dumpTree(SbkObject *self)
{
#ifdef Py_GIL_DISABLED
    // The walk reads the children with no lock, and the preamble it runs per
    // child may not hold one.
    // See "Who may read parentInfo" in the free-threading notes.
    static_cast<void>(self);
    return "dumpTree() is not available in a free-threaded build";
#else
    std::ostringstream s;
    dumpTreeRecursion(s, self, 0);
    return s.str();
#endif
}

std::string info(SbkObject *self)
{
    std::ostringstream s;
    const std::string indent;
    info_format_preamble(s, self, indent);
#ifdef Py_GIL_DISABLED
    // As in _debugFormat(): the rest reads what the state lock publishes.
    StateLockGuard guard;
#endif
    info_format_parent(s, self, indent);
    info_format_children(s, self, indent);
    info_format_referredObjects(s, self, indent);
    return s.str();
}

} // namespace Shiboken::Object
