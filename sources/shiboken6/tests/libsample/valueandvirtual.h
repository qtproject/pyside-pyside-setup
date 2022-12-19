// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef VALUEANDVIRTUAL_H
#define VALUEANDVIRTUAL_H

class ValueAndVirtual
{
public:
    explicit ValueAndVirtual(int id) : m_id(id) {}
    virtual ~ValueAndVirtual() = default;

    bool operator()(int id, int id2) { return id == id2; }

    inline int id() const { return m_id; }

private:
    int m_id;
};

#endif // VALUEANDVIRTUAL_H
