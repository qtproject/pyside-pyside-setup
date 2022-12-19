// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SIMPLEFILE_H
#define SIMPLEFILE_H

#include "libsamplemacros.h"

class SimpleFile_p;

class LIBSAMPLE_API SimpleFile
{
public:
    explicit SimpleFile(const char *filename);
    ~SimpleFile();

    const char *filename();
    long size();
    bool open();
    void close();

    bool exists() const;
    static bool exists(const char *filename);

private:
    SimpleFile_p *p;
};

#endif // SIMPLEFILE_H
