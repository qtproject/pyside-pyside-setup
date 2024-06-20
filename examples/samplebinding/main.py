# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""An example showcasing how to use bindings for a custom non-Qt C++ library"""

from Universe import Icecream, Truck


class VanillaChocolateIcecream(Icecream):
    def __init__(self, flavor=""):
        super().__init__(flavor)

    def clone(self):
        return VanillaChocolateIcecream(self.getFlavor())

    def getFlavor(self):
        return "vanilla sprinked with chocolate"


class VanillaChocolateCherryIcecream(VanillaChocolateIcecream):
    def __init__(self, flavor=""):
        super().__init__(flavor)

    def clone(self):
        return VanillaChocolateCherryIcecream(self.getFlavor())

    def getFlavor(self):
        base_flavor = super(VanillaChocolateCherryIcecream, self).getFlavor()
        return f"{base_flavor} and a cherry"


if __name__ == '__main__':
    leave_on_destruction = True
    truck = Truck(leave_on_destruction)

    flavors = ["vanilla", "chocolate", "strawberry"]
    for f in flavors:
        icecream = Icecream(f)
        truck.addIcecreamFlavor(icecream)

    truck.addIcecreamFlavor(VanillaChocolateIcecream())
    truck.addIcecreamFlavor(VanillaChocolateCherryIcecream())

    truck.arrive()
    truck.printAvailableFlavors()
    result = truck.deliver()

    if result:
        print("All the kids got some icecream!")
    else:
        print("Aww, someone didn't get the flavor they wanted...")

    if not result:
        special_truck = Truck(truck)
        del truck

        print("")
        special_truck.arrivalMessage = "A new SPECIAL icecream truck has arrived!\n"
        special_truck.arrive()
        special_truck.addIcecreamFlavor(Icecream("SPECIAL *magical* icecream"))
        special_truck.printAvailableFlavors()
        special_truck.deliver()
        print("Now everyone got the flavor they wanted!")
        special_truck.leave()
