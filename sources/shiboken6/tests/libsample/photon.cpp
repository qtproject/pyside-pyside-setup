// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "photon.h"

namespace Photon
{

const ClassType Base::staticType;

int callCalculateForValueDuplicatorPointer(ValueDuplicator *value)
{
    return value->calculate();
}

int callCalculateForValueDuplicatorReference(ValueDuplicator &value)
{
    return value.calculate();
}

int countValueIdentities(const std::list<ValueIdentity> &values)
{
    return values.size();
}

int countValueDuplicators(const std::list<TemplateBase<DuplicatorType> > &values)
{
    return values.size();
}

} // namespace Photon
