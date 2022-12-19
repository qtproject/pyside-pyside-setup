// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "simplefile.h"

#include <cstdlib>
#include <cstring>
#include <fstream>

class SimpleFile_p
{
public:
    SimpleFile_p(const char *filename) :
        m_filename(strdup(filename)) {}

    ~SimpleFile_p()
    {
        std::free(m_filename);
    }

    char *m_filename;
    FILE *m_descriptor = nullptr;
    long m_size = 0;
};

SimpleFile::SimpleFile(const char *filename)
{
    p = new SimpleFile_p(filename);
}

SimpleFile::~SimpleFile()
{
    close();
    delete p;
}

const char *SimpleFile::filename()
{
    return p->m_filename;
}

long SimpleFile::size()
{
    return p->m_size;
}

bool SimpleFile::open()
{
    auto *descriptor = fopen(p->m_filename, "rb");
    if (descriptor == nullptr)
        return false;

    p->m_descriptor = descriptor;
    std::fseek(p->m_descriptor, 0, SEEK_END);
    p->m_size = ftell(p->m_descriptor);
    std::rewind(p->m_descriptor);

    return true;
}

void SimpleFile::close()
{
    if (p->m_descriptor) {
        std::fclose(p->m_descriptor);
        p->m_descriptor = nullptr;
    }
}

bool SimpleFile::exists() const
{
    std::ifstream ifile(p->m_filename);
    return !ifile.fail();
}

bool SimpleFile::exists(const char *filename)
{
    std::ifstream ifile(filename);
    return !ifile.fail();
}
