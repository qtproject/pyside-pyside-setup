// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <iostream>
#include "mapuser.h"

std::map<std::string, std::pair<Complex, int> >
MapUser::callCreateMap()
{
    return createMap();
}


std::map<std::string, std::pair<Complex, int> >
MapUser::createMap()
{
    std::map<std::string, std::pair<Complex, int> > retval;

    std::pair<std::string, std::pair<Complex, int> >
            item0("zero", std::pair<Complex, int>(Complex(1.2, 3.4), 2));
    retval.insert(item0);

    std::pair<std::string, std::pair<Complex, int> >
            item1("one", std::pair<Complex, int>(Complex(5.6, 7.8), 3));
    retval.insert(item1);

    std::pair<std::string, std::pair<Complex, int> >
            item2("two", std::pair<Complex, int>(Complex(9.1, 2.3), 5));
    retval.insert(item2);

    return retval;
}

void
MapUser::showMap(std::map<std::string, int> mapping)
{
    std::cout << __FUNCTION__ << std::endl;
    for (auto it = mapping.begin(), end = mapping.end(); it != end; ++it)
        std::cout << (*it).first << " => " << (*it).second << std::endl;
}

void MapUser::pointerToMap(std::map<std::string, std::string> *)
{
}

void MapUser::referenceToMap(std::map<std::string, std::string> &)
{
}

std::map<int, std::list<std::list<double> > > MapUser::foo() const
{
    std::map<int, std::list<std::list<double> > > result;
    return result;
}
