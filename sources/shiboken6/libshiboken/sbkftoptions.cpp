// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "sbkftoptions.h"

#ifdef Py_GIL_DISABLED

#include <cstdlib>
#include <string_view>

namespace Shiboken::FreeThreading {

// Parsed the way PYSIDE6_OPTION_PYTHON_ENUM is parsed: the words on/off, and
// numbers in any of the usual bases. "0b111" is the readable spelling for
// flags and the reason this is not a plain atoi().
static int parseOption(const char *e)
{
    // All bits, not just the ones named below: unset has to mean "every lock
    // there is", including any added later, without touching this line.
    if (e == nullptr || *e == '\0')
        return ~0;

    const std::string_view v{e};
    if (v == "yes" || v == "on" || v == "true")
        return ~0;
    if (v == "no" || v == "off" || v == "false")
        return 0;

    int base = 10;
    std::size_t offset = 0;
    if (v.size() > 2 && v[0] == '0') {
        if (v[1] == 'b' || v[1] == 'B') {
            base = 2;
            offset = 2;
        } else if (v[1] == 'x' || v[1] == 'X') {
            base = 16;
            offset = 2;
        }
    }
    return static_cast<int>(std::strtol(e + offset, nullptr, base));
}

bool optionEnabled(Option opt)
{
    static const int flags = parseOption(std::getenv("PYSIDE6_OPTION_FT"));
    return (flags & opt) != 0;
}

} // namespace Shiboken::FreeThreading

#endif // Py_GIL_DISABLED
