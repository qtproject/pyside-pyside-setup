// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <iostream>
#include <list>
#include "abstract.h"
#include "derived.h"
#include "kindergarten.h"
#include "complex.h"
#include "point.h"
#include "size.h"
#include "listuser.h"
#include "samplenamespace.h"

int
main(int argv, char **argc)
{
    std::cout << std::endl;

    Derived derived;

    std::cout << std::endl;

    derived.unpureVirtual();
    derived.pureVirtual();
    derived.callPureVirtual();

    std::cout << std::endl;
    auto *abs = Abstract::createObject();
    std::cout << "Abstract::createObject(): " << abs << std::endl << std::endl;
    delete abs;

    abs = Derived::createObject();
    std::cout << "Derived::createObject() : ";
    abs->show();
    std::cout << std::endl;
    delete abs;
    std::cout << std::endl;

    abs = Derived::createObject();
    std::cout << "Derived::createObject() : ";
    abs->show();
    std::cout << std::endl;
    delete abs;
    std::cout << std::endl;

    std::cout << "\n-----------------------------------------\n";

    KinderGarten kg;
    Derived *d[] = { 0, 0, 0 };

    for (int i = 0; i < 3; i++) {
        d[i] = new Derived(i);
        d[i]->show();
        std::cout << std::endl;
        kg.addChild(d[i]);
    }

    kg.show();
    std::cout << std::endl;

    std::cout << "\n* kill child ";
    d[2]->show();
    std::cout << " ----------------\n";
    kg.killChild(d[2]);
    kg.show();
    std::cout << std::endl;

    std::cout << "\n* release child ";
    d[1]->show();
    std::cout << " -------------\n";
    Abstract *released = kg.releaseChild(d[1]);
    std::cout << "released: ";
    released->show();
    std::cout << std::endl;
    kg.show();
    std::cout << "\n\n* kill children ------------------------------------\n";
    kg.killChildren();
    kg.show();
    std::cout << "\n\n-----------------------------------------\n";
    ListUser lu;
    std::cout << "ListUser::createList()\n";
    std::list<int> intlist = lu.createList();
    for (std::list<int>::iterator it = intlist.begin(); it != intlist.end(); it++)
        std::cout << "* " << *it << std::endl;

    std::cout << "ListUser::createComplexList\n";
    std::list<Complex> cpxlist = ListUser::createComplexList(Complex(1.1, 2.2), Complex(3.3, 4.4));
    for (std::list<Complex>::iterator it = cpxlist.begin(); it != cpxlist.end(); it++) {
        std::cout << "* ";
        (*it).show();
        std::cout << std::endl;
    }
    std::cout << "\n-----------------------------------------\n"
        << "SampleNamespace\n";

    std::cout << "SampleNamespace::RandomNumber: ";
    std::cout << SampleNamespace::getNumber(SampleNamespace::RandomNumber);
    std::cout << std::endl;
    std::cout << "SampleNamespace::UnixTime: ";
    std::cout << SampleNamespace::getNumber(SampleNamespace::UnixTime);
    std::cout << std::endl;
    double val_d = 1.3;
    std::cout << "SampleNamespace::powerOfTwo(" << val_d << "): ";
    std::cout << SampleNamespace::powerOfTwo(val_d) << std::endl;
    int val_i = 7;
    std::cout << "SampleNamespace::powerOfTwo(" << val_i << "): ";
    std::cout << SampleNamespace::powerOfTwo(val_i) << std::endl;
    std::cout << std::endl;

    std::cout << "-----------------------------------------" << std::endl;
    std::cout << "Point" << std::endl;

    Point p1(1.1, 2.2);
    std::cout << "p1: ";
    p1.show();
    std::cout << std::endl;

    Point p2(3.4, 5.6);
    std::cout << "p2: ";
    p2.show();
    std::cout << std::endl;

    std::cout << "p1 + p2 == ";
    (p1 + p2).show();
    std::cout << std::endl;

    std::cout << "p1 * 2.0 == ";
    (p1 * 2.0).show();
    std::cout << std::endl;

    std::cout << "1.5 * p2 == ";
    (1.5 * p2).show();
    std::cout << std::endl;

    std::cout << "p1: ";
    p1.show();
    std::cout << std::endl << "p2: ";
    p2.show();
    std::cout << std::endl << "p1 += p2" << std::endl;
    p1 += p2;
    std::cout << "p1: ";
    p1.show();
    std::cout << std::endl;

    std::cout << "p1 == p2 ? " << ((p1 == p2) ? "true" : "false") << std::endl;
    std::cout << "p1 == p1 ? " << ((p1 == p1) ? "true" : "false") << std::endl;
    std::cout << "p2 == p2 ? " << ((p2 == p2) ? "true" : "false") << std::endl;

    std::cout << "-----------------------------------------" << std::endl;
    std::cout << "Size" << std::endl;

    Size s1(2, 2);
    std::cout << "s1: ";
    s1.show();
    std::cout << ", area: " << s1.calculateArea();
    std::cout << std::endl;

    Size s2(3, 5);
    std::cout << "s2: ";
    s2.show();
    std::cout << ", area: " << s2.calculateArea();
    std::cout << std::endl;

    std::cout << std::endl;

    std::cout << "s1 == s2 ? " << ((s1 == s2) ? "true" : "false") << std::endl;
    std::cout << "s1 != s2 ? " << ((s1 != s2) ? "true" : "false") << std::endl;

    std::cout << "s1 <  s2 ? " << ((s1 <  s2) ? "true" : "false") << std::endl;
    std::cout << "s1 <= s2 ? " << ((s1 <= s2) ? "true" : "false") << std::endl;
    std::cout << "s1 >  s2 ? " << ((s1 >  s2) ? "true" : "false") << std::endl;
    std::cout << "s1 >= s2 ? " << ((s1 >= s2) ? "true" : "false") << std::endl;

    std::cout << "s1 <  10 ? " << ((s1 <  10) ? "true" : "false") << std::endl;
    std::cout << "s1 <= 10 ? " << ((s1 <= 10) ? "true" : "false") << std::endl;
    std::cout << "s1 >  10 ? " << ((s1 >  10) ? "true" : "false") << std::endl;
    std::cout << "s1 >= 10 ? " << ((s1 >= 10) ? "true" : "false") << std::endl;
    std::cout << "s2 <  10 ? " << ((s2 <  10) ? "true" : "false") << std::endl;
    std::cout << "s2 <= 10 ? " << ((s2 <= 10) ? "true" : "false") << std::endl;
    std::cout << "s2 >  10 ? " << ((s2 >  10) ? "true" : "false") << std::endl;
    std::cout << "s2 >= 10 ? " << ((s2 >= 10) ? "true" : "false") << std::endl;
    std::cout << std::endl;

    std::cout << "s1: ";
    s1.show();
    std::cout << std::endl << "s2: ";
    s2.show();
    std::cout << std::endl << "s1 += s2" << std::endl;
    s1 += s2;
    std::cout << "s1: ";
    s1.show();
    std::cout << std::endl;

    std::cout << std::endl;

    std::cout << "s1: ";
    s1.show();
    std::cout << std::endl << "s1 *= 2.0" << std::endl;
    s1 *= 2.0;
    std::cout << "s1: ";
    s1.show();
    std::cout << std::endl;

    std::cout << std::endl;

    return 0;
}

