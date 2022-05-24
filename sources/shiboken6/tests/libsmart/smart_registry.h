// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SMART_REGISTRY_H
#define SMART_REGISTRY_H

#include <vector>

#include "libsmartmacros.h"

class Obj;
class Integer;

// Used to track which C++ objects are alive.
class LIB_SMART_API Registry {
public:
    static Registry *getInstance();
    ~Registry();

    Registry(const Registry &) = delete;
    Registry &operator=(const Registry &) = delete;
    Registry(Registry &&) = delete;
    Registry &operator=(Registry &&) = delete;

    void add(Obj *p);
    void add(Integer *p);
    void remove(Obj *p);
    void remove(Integer *p);
    int countObjects() const;
    int countIntegers() const;
    bool verbose() const;
    void setVerbose(bool flag);

protected:
    Registry();

private:
    std::vector<Obj *> m_objects;
    std::vector<Integer *> m_integers;
    bool m_verbose = false;
};

#endif // SMART_REGISTRY_H
