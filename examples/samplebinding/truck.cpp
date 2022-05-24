// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#include <iostream>
#include <random>

#include "truck.h"

Truck::Truck(bool leaveOnDestruction) : m_leaveOnDestruction(leaveOnDestruction) {}

Truck::Truck(const Truck &other)
{
    assign(other);
}

Truck &Truck::operator=(const Truck &other)
{
    if (this != &other) {
        m_flavors.clear();
        assign(other);
    }
    return *this;
}

Truck::Truck(Truck &&other) = default;

Truck& Truck::operator=(Truck &&other) = default;

Truck::~Truck()
{
    if (m_leaveOnDestruction)
        leave();
}

void Truck::addIcecreamFlavor(Icecream *icecream)
{
    m_flavors.push_back(IcecreamPtr(icecream));
}

void Truck::printAvailableFlavors() const
{
    std::cout << "It sells the following flavors: \n";
    for (const auto &flavor : m_flavors)
        std::cout << "  * "  << *flavor << '\n';
    std::cout << '\n';
}

void Truck::arrive() const
{
    std::cout << m_arrivalMessage;
}

void Truck::leave() const
{
    std::cout << "The truck left the neighborhood.\n";
}

void Truck::setLeaveOnDestruction(bool value)
{
    m_leaveOnDestruction = value;
}

void Truck::setArrivalMessage(const std::string &message)
{
    m_arrivalMessage = message;
}

std::string Truck::getArrivalMessage() const
{
    return m_arrivalMessage;
}

void Truck::assign(const Truck &other)
{
    m_flavors.reserve(other.m_flavors.size());
    for (const auto &f : other.m_flavors)
        m_flavors.push_back(IcecreamPtr(f->clone()));
}

bool Truck::deliver() const
{
    std::random_device rd;
    std::mt19937 mt(rd());
    std::uniform_int_distribution<int> dist(1, 2);

    std::cout << "The truck started delivering icecream to all the kids in the neighborhood.\n";
    bool result = false;

    if (dist(mt) == 2)
        result = true;

    return result;
}
