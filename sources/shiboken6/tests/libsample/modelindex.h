// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef MODELINDEX_H
#define MODELINDEX_H

class ModelIndex
{
public:
    ModelIndex() = default;

    inline void setValue(int value) { m_value = value; }
    inline int value() const { return m_value; }
    static int getValue(const ModelIndex &index) { return index.value(); }

private:
    int m_value = 0;
};

class ReferentModelIndex
{
public:
    ReferentModelIndex() = default;

    explicit ReferentModelIndex(const ModelIndex &index) : m_index(index) {}

    inline void setValue(int value) { m_index.setValue(value); }
    inline int value() const { return m_index.value(); }
    operator const ModelIndex&() const { return m_index; }

private:
    ModelIndex m_index;
};

class PersistentModelIndex
{
public:
    PersistentModelIndex() = default;

    explicit PersistentModelIndex(const ModelIndex &index) : m_index(index) {}

    inline void setValue(int value) { m_index.setValue(value); }
    inline int value() const { return m_index.value(); }
    operator ModelIndex() const { return m_index; }

private:
    ModelIndex m_index;
};

#endif // MODELINDEX_H
