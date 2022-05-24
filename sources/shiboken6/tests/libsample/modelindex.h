// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef MODELINDEX_H
#define MODELINDEX_H

#include "libsamplemacros.h"

class ModelIndex
{
public:
    ModelIndex() : m_value(0) {}
    ModelIndex(const ModelIndex& other) { m_value = other.m_value; }
    inline void setValue(int value) { m_value = value; }
    inline int value() const { return m_value; }
    static int getValue(const ModelIndex& index) { return index.value(); }
private:
    int m_value;
};

class ReferentModelIndex
{
public:
    ReferentModelIndex() {}
    ReferentModelIndex(const ModelIndex& index) : m_index(index) {}
    ReferentModelIndex(const ReferentModelIndex& other) { m_index = other.m_index; }
    inline void setValue(int value) { m_index.setValue(value); }
    inline int value() const { return m_index.value(); }
    operator const ModelIndex&() const { return m_index; }
private:
    ModelIndex m_index;
};

class PersistentModelIndex
{
public:
    PersistentModelIndex() {}
    PersistentModelIndex(const ModelIndex& index) : m_index(index) {}
    PersistentModelIndex(const PersistentModelIndex& other) { m_index = other.m_index; }
    inline void setValue(int value) { m_index.setValue(value); }
    inline int value() const { return m_index.value(); }
    operator ModelIndex() const { return m_index; }
private:
    ModelIndex m_index;
};

#endif
