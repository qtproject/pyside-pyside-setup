// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "simplefile.h"

#include <cstdlib>
#include <cstdio>
#include <string>
#include <filesystem>

class SimpleFilePrivate
{
public:
    LIBMINIMAL_DISABLE_COPY_MOVE(SimpleFilePrivate)

    SimpleFilePrivate(const char *filename) : m_filename(filename) {}
    ~SimpleFilePrivate() = default;

    std::string m_filename;
    FILE *m_descriptor = nullptr;
    long m_size = 0;
};

SimpleFile::SimpleFile(const char *filename) :
    p(std::make_unique<SimpleFilePrivate>(filename))
{
}

SimpleFile::~SimpleFile()
{
    close();
}

const char *SimpleFile::filename()
{
    return p->m_filename.c_str();
}

long SimpleFile::size() const
{
    return p->m_size;
}

bool SimpleFile::open()
{
    auto *descriptor = std::fopen(p->m_filename.c_str(), "rb");
    if (descriptor == nullptr)
        return false;

    p->m_descriptor = descriptor;
    const auto size = std::filesystem::file_size(std::filesystem::path(p->m_filename));
    p->m_size = long(size);

    return true;
}

void SimpleFile::close()
{
    if (p->m_descriptor != nullptr) {
        std::fclose(p->m_descriptor);
        p->m_descriptor = nullptr;
    }
}

bool SimpleFile::exists() const
{
    return std::filesystem::exists(std::filesystem::path(p->m_filename));
}

bool SimpleFile::exists(const char *filename)
{
    return std::filesystem::exists(std::filesystem::path(filename));
}
