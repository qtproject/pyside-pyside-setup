// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SIMPLEFILE_H
#define SIMPLEFILE_H

#include "libsamplemacros.h"

#include <memory>

class SimpleFilePrivate;

class LIBSAMPLE_API SimpleFile
{
public:
    LIBMINIMAL_DISABLE_COPY(SimpleFile)
    LIBMINIMAL_DEFAULT_MOVE(SimpleFile)

    explicit SimpleFile(const char *filename);
    ~SimpleFile();

    const char *filename();
    long size() const;
    bool open();
    void close();

    bool exists() const;
    static bool exists(const char *filename);

private:
    std::unique_ptr<SimpleFilePrivate> p;
};

#endif // SIMPLEFILE_H
