// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#ifndef TRUCK_H
#define TRUCK_H

#include "icecream.h"
#include "macros.h"

#include <memory>
#include <vector>

class BINDINGS_API Truck
{
public:
    explicit Truck(bool leaveOnDestruction = false);
    Truck(const Truck &other);
    Truck& operator=(const Truck &other);
    Truck(Truck &&other);
    Truck& operator=(Truck &&other);

    ~Truck();

    void addIcecreamFlavor(Icecream *icecream);
    void printAvailableFlavors() const;

    bool deliver() const;
    void arrive() const;
    void leave() const;

    void setLeaveOnDestruction(bool value);

    void setArrivalMessage(const std::string &message);
    std::string getArrivalMessage() const;

private:
    using IcecreamPtr = std::shared_ptr<Icecream>;

    void assign(const Truck &other);

    bool m_leaveOnDestruction = false;
    std::string m_arrivalMessage = "A new icecream truck has arrived!\n";
    std::vector<IcecreamPtr> m_flavors;
};

#endif // TRUCK_H
