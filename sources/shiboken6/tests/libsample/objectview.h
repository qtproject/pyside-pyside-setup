// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OBJECTVIEW_H
#define OBJECTVIEW_H

#include "objecttype.h"
#include "libsamplemacros.h"

class Str;
class ObjectModel;

class LIBSAMPLE_API ObjectView : public ObjectType
{
public:
    explicit ObjectView(ObjectModel *model = nullptr, ObjectType *parent = nullptr)
        : ObjectType(parent), m_model(model) {}

    inline void setModel(ObjectModel *model) { m_model = model; }
    inline ObjectModel *model() const { return m_model; }

    Str displayModelData();
    void modifyModelData(Str &data);

    ObjectType *getRawModelData();

private:
    ObjectModel *m_model;
};

#endif // OBJECTVIEW_H
