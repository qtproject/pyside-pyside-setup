// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DEBUGHELPERS_P_H
#define DEBUGHELPERS_P_H

#include <QtCore/QDebug>
#include <memory>

template <class T>
inline QDebug operator<<(QDebug debug, const std::shared_ptr<T> &ptr)
{
    QDebugStateSaver saver(debug);
    debug.nospace();
    debug << "std::shared_ptr(" << ptr.get() << ")";
    return debug;
}

template <class It>
inline void formatSequence(QDebug &d, It i1, It i2,
                           const char *separator=", ")
{
    for (It i = i1; i != i2; ++i) {
        if (i != i1)
            d << separator;
        d << *i;
    }
}

template <class It>
inline static void formatPtrSequence(QDebug &d, It i1, It i2,
                                     const char *separator=", ")
{
    for (It i = i1; i != i2; ++i) {
        if (i != i1)
            d << separator;
        d << i->get();
    }
}

template <class Container>
static void formatList(QDebug &d, const char *name, const Container &c,
                       const char *separator=", ")
{
    if (const auto size = c.size()) {
        d << ", " << name << '[' << size << "]=(";
        for (qsizetype i = 0; i < size; ++i) {
            if (i)
                d << separator;
             d << c.at(i);
        }
        d << ')';
    }
}

#endif // DEBUGHELPERS_P_H
