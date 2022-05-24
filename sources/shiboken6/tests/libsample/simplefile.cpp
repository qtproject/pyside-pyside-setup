// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include <stdlib.h>
#include <string.h>
#include <fstream>
#include "simplefile.h"

class SimpleFile_p
{
public:
    SimpleFile_p(const char* filename) : m_descriptor(nullptr), m_size(0)
    {
        m_filename = strdup(filename);
    }

    ~SimpleFile_p()
    {
        free(m_filename);
    }

    char* m_filename;
    FILE* m_descriptor;
    long m_size;
};

SimpleFile::SimpleFile(const char* filename)
{
    p = new SimpleFile_p(filename);
}

SimpleFile::~SimpleFile()
{
    close();
    delete p;
}

const char* SimpleFile::filename()
{
    return p->m_filename;
}

long SimpleFile::size()
{
    return p->m_size;
}

bool
SimpleFile::open()
{
    if ((p->m_descriptor = fopen(p->m_filename, "rb")) == nullptr)
        return false;

    fseek(p->m_descriptor, 0, SEEK_END);
    p->m_size = ftell(p->m_descriptor);
    rewind(p->m_descriptor);

    return true;
}

void
SimpleFile::close()
{
    if (p->m_descriptor) {
        fclose(p->m_descriptor);
        p->m_descriptor = nullptr;
    }
}

bool
SimpleFile::exists() const
{
    std::ifstream ifile(p->m_filename);
    return !ifile.fail();
}

bool
SimpleFile::exists(const char* filename)
{
    std::ifstream ifile(filename);
    return !ifile.fail();
}

