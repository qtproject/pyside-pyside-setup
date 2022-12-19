// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef MAPUSER_H
#define MAPUSER_H

#include "libsamplemacros.h"

#include "complex.h"
#include "bytearray.h"

#include <map>
#include <list>
#include <utility>
#include <string>

class LIBSAMPLE_API MapUser
{
public:
    MapUser() {}
    virtual ~MapUser() {}

    virtual std::map<std::string, std::pair<Complex, int> > createMap();
    std::map<std::string, std::pair<Complex, int> > callCreateMap();

    void showMap(std::map<std::string, int> mapping);

    inline void setMap(std::map<std::string, std::list<int> > map) { m_map = map; }
    inline std::map<std::string, std::list<int> > getMap() { return m_map; }

    // Compile test
    static void pointerToMap(std::map<std::string, std::string> *arg);
    static void referenceToMap(std::map<std::string, std::string> &arg);

    inline const std::map<int, ByteArray> &passMapIntValueType(const std::map<int, ByteArray>& arg) { return arg; }

    std::map<int, std::list<std::list<double> > > foo() const;

private:
    std::map<std::string, std::list<int> > m_map;
};

#endif // MAPUSER_H
