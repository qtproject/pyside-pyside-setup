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

std::string info(SbkObject *self)
{
    std::ostringstream s;

    s << "id................ " << self << '\n';
    if (self->d && self->d->cptr) {
        const std::vector<PyTypeObject *> bases = getBases(self);

        s << "C++ address....... ";
        for (size_t i = 0, size = bases.size(); i < size; ++i)
            s << bases[i]->tp_name << '/' << self->d->cptr[i] << ' ';
        s << "\n";
    }
    else {
        s << "C++ address....... <<Deleted>>\n";
    }

    s << "hasOwnership...... " << bool(self->d->hasOwnership) << "\n"
         "containsCppWrapper " << self->d->containsCppWrapper << "\n"
         "validCppObject.... " << self->d->validCppObject << "\n"
         "wasCreatedByPython " << self->d->cppObjectCreated << "\n"
         "value......        " << isValueType(self) << "\n"
         "reference count... " << Py_REFCNT(reinterpret_cast<PyObject *>(self)) << '\n';

    if (self->d->parentInfo && self->d->parentInfo->parent) {
        auto *obParent = reinterpret_cast<PyObject *>(self->d->parentInfo->parent);
        s << "parent............ <" << Py_TYPE(obParent)->tp_name << " at " << obParent << ">\n";
    }

    if (self->d->parentInfo && !self->d->parentInfo->children.empty()) {
        const auto &children = self->d->parentInfo->children;
        s << "children.......... [" << children.size() << "] ";
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

    if (self->d->referredObjects && !self->d->referredObjects->empty()) {
        const Shiboken::RefCountMap &map = *self->d->referredObjects;
        s << "referred objects.. ";
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
    return s.str();
}

} // namespace Shiboken::Object
