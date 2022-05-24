// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTDROPTYPEENTRIES_H
#define TESTDROPTYPEENTRIES_H

#include <QtCore/QObject>

class TestDropTypeEntries : public QObject
{
    Q_OBJECT
    private slots:
        void testDropEntries();
        void testDontDropEntries();
        void testDropEntryWithChildTags();
        void testDontDropEntryWithChildTags();
        void testConditionalParsing_data();
        void testConditionalParsing();
        void testEntityParsing();
};

#endif
