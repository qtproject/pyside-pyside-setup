// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "qtxmltosphinxtest.h"
#include "qtxmltosphinx.h"
#include <QtTest/QTest>

#include <QtCore/QBuffer>
#include <QtCore/QDebug>
#include <QtCore/QLoggingCategory>

using namespace Qt::StringLiterals;

Q_LOGGING_CATEGORY(lcQtXmlToSphinxTest, "qt.sphinxtabletest");

// QtXmlToSphinxDocGeneratorInterface
QString QtXmlToSphinxTest::expandFunction(const QString &) const
{
    return {};
}

QString QtXmlToSphinxTest::expandClass(const QString &, const QString &) const
{
    return {};
}

QString QtXmlToSphinxTest::resolveContextForMethod(const QString &, const QString &) const
{
    return {};
}

const QLoggingCategory &QtXmlToSphinxTest::loggingCategory() const
{
    return lcQtXmlToSphinxTest();
}

QtXmlToSphinxLink QtXmlToSphinxTest::resolveLink(const QtXmlToSphinxLink &link) const
{
    return link;
}

QString QtXmlToSphinxTest::transformXml(const QString &xml) const
{
    return QtXmlToSphinx(this, m_parameters, xml).result();
}

void QtXmlToSphinxTest::testTable_data()
{
    QTest::addColumn<QString>("xml");
    QTest::addColumn<QString>("expected");

    QTest::newRow("emptyString") << QString() << QString();

    // testSimpleTable
    const char *xml = R"(<table>
    <header>
        <item>
            <para>Header 1</para>
        </item>
        <item>
            <para>Header 2</para>
        </item>
    </header>
    <row>
        <item>
            <para>1 1</para>
        </item>
        <item>
            <para>1 2</para>
        </item>
    </row>
    <row>
        <item>
            <para>2 1</para>
        </item>
        <item>
            <para>2 2</para>
        </item>
    </row>
</table>)";

    const char *expected = R"(
    +--------+--------+
    |Header 1|Header 2|
    +========+========+
    |1 1     |1 2     |
    +--------+--------+
    |2 1     |2 2     |
    +--------+--------+

)";

    QTest::newRow("testSimpleTable")
        << QString::fromLatin1(xml) << QString::fromLatin1(expected);

    // testRowSpan
    xml = R"(<table>
    <header>
        <item>
            <para>Header 1</para>
        </item>
        <item>
            <para>Header 2</para>
        </item>
    </header>
    <row>
        <item colspan="2">
            <para>I'm a big text!</para>
        </item>
    </row>
    <row>
        <item>
            <para>2 1</para>
        </item>
        <item>
            <para>2 2</para>
        </item>
    </row>
</table>)";

    expected = R"(
    +---------------+--------+
    |Header 1       |Header 2|
    +===============+========+
    |I'm a big text!         |
    +---------------+--------+
    |2 1            |2 2     |
    +---------------+--------+

)";

    QTest::newRow("testColSpan")
        << QString::fromLatin1(xml) << QString::fromLatin1(expected);

    // testRowSpan
    xml = R"(<table>
    <header>
        <item>
            <para>Header 1</para>
        </item>
        <item>
            <para>Header 2</para>
        </item>
    </header>
    <row>
        <item rowspan="2">
            <para>1.1</para>
        </item>
        <item>
            <para>1.2</para>
        </item>
    </row>
    <row>
        <item>
            <para>2 2</para>
        </item>
    </row>
</table>)";

    expected = R"(
    +--------+--------+
    |Header 1|Header 2|
    +========+========+
    |1.1     |1.2     |
    +        +--------+
    |        |2 2     |
    +--------+--------+

)";

    QTest::newRow("testRowSpan")
        << QString::fromLatin1(xml) << QString::fromLatin1(expected);

    // testComplexTable
    xml = R"(<table>
    <header>
        <item>
            <para>Header 1</para>
        </item>
        <item>
            <para>Header 2</para>
        </item>
        <item>
            <para>Header 3</para>
        </item>
    </header>
    <row>
        <item rowspan="2">
            <para>1.1</para>
        </item>
        <item colspan="2">
            <para>1.2</para>
        </item>
    </row>
    <row>
        <item>
            <para>2 2</para>
        </item>
        <item>
            <para>2 3</para>
        </item>
    </row>
</table>)";

    expected = R"(
    +--------+--------+--------+
    |Header 1|Header 2|Header 3|
    +========+========+========+
    |1.1     |1.2              |
    +        +--------+--------+
    |        |2 2     |2 3     |
    +--------+--------+--------+

)";

    QTest::newRow("testComplexTable")
        << QString::fromLatin1(xml) << QString::fromLatin1(expected);

    // testRowSpan2
    xml = R"(<table>
    <header>
        <item><para>h1</para></item>
        <item><para>h2</para></item>
        <item><para>h3</para></item>
        <item><para>h4</para></item>
    </header>
    <row>
        <item rowspan="6"><para>A</para></item>
        <item rowspan="6"><para>B</para></item>
        <item><para>C</para></item>
        <item><para>D</para></item>
    </row>
    <row>
        <item><para>E</para></item>
        <item><para>F</para></item>
    </row>
    <row>
        <item><para>E</para></item>
        <item><para>F</para></item>
    </row>
    <row>
        <item><para>E</para></item>
        <item><para>F</para></item>
    </row>
    <row>
        <item><para>E</para></item>
        <item><para>F</para></item>
    </row>
    <row>
        <item><para>E</para></item>
        <item><para>F</para></item>
    </row>
</table>)";

    expected = R"(
    +--+--+--+--+
    |h1|h2|h3|h4|
    +==+==+==+==+
    |A |B |C |D |
    +  +  +--+--+
    |  |  |E |F |
    +  +  +--+--+
    |  |  |E |F |
    +  +  +--+--+
    |  |  |E |F |
    +  +  +--+--+
    |  |  |E |F |
    +  +  +--+--+
    |  |  |E |F |
    +--+--+--+--+

)";

    QTest::newRow("testRowSpan2")
        << QString::fromLatin1(xml) << QString::fromLatin1(expected);

    // testNestedList
    xml = R"(<table>
    <row>
        <item>
            <list type="bullet">
                <item>
                    <para>I11</para>
                </item>
                <item>
                    <para>I21</para>
                </item>
            </list>
        </item>
        <item>
            <list type="bullet">
                <item>
                    <para>I12</para>
                </item>
                <item>
                    <para>I22</para>
                </item>
            </list>
        </item>
    </row>
</table>)";

    expected = R"(
    +---------+---------+
    |    * I11|    * I12|
    |    * I21|    * I22|
    +---------+---------+

)";

    QTest::newRow("testNestedList")
        << QString::fromLatin1(xml) << QString::fromLatin1(expected);

    // testBrokenTable
    xml = R"(<table>
    <header>
        <item>
            <para>Header 1</para>
        </item>
        <item>
            <para>Header 2</para>
        </item>
    </header>
    <row>
        <item>
            <para>1.1</para>
        </item>
        <item>
            <para>1.2</para>
        </item>
    </row>
    <row>
        <item colspan="2">
            <para>2 2</para>
        </item>
        <item>
            <para>2 3</para>
        </item>
        <item>
            <para>2 4</para>
        </item>
        <item>
            <para>2 5</para>
        </item>
    </row>
    <row>
        <item>
            <para>3 1</para>
        </item>
        <item>
            <para>3 2</para>
        </item>
        <item>
            <para>3 3</para>
        </item>
    </row>
</table>)";

    expected = R"(
    +--------+------------+
    |Header 1|Header 2    |
    +========+============+
    |1.1     |1.2         |
    +--------+------------+
    |2 2       2 3 2 4 2 5|
    +--------+------------+
    |3 1     |3 2 3 3     |
    +--------+------------+

)";

    QTest::newRow("testBrokenTable")
        << QString::fromLatin1(xml) << QString::fromLatin1(expected);
}

void QtXmlToSphinxTest::testTable()
{
    QFETCH(QString, xml);
    QFETCH(QString, expected);

    const QString actual = transformXml(xml);

    QEXPECT_FAIL("testBrokenTable", "testBrokenTable fails", Continue);
    QCOMPARE(actual, expected);
}

using TablePtr = std::shared_ptr<QtXmlToSphinx::Table>;

Q_DECLARE_METATYPE(TablePtr);

void QtXmlToSphinxTest::testTableFormatting_data()
{
    using TableCell = QtXmlToSphinx::TableCell;

    QTest::addColumn<TablePtr>("table");
    QTest::addColumn<QString>("expected");

    TablePtr table(new QtXmlToSphinx::Table);
    table->appendRow({TableCell("item11"), TableCell("item12")});
    table->appendRow({TableCell(""), TableCell("item22")});
    table->normalize();

    const char *expected = R"(+------+------+
|item11|item12|
+------+------+
|      |item22|
+------+------+

)";

    QTest::newRow("normal") << table << QString::fromLatin1(expected);

    table.reset(new QtXmlToSphinx::Table);
    table->appendRow({TableCell("item11"), TableCell("item12\nline2")});
    table->appendRow({TableCell(""), TableCell("item22\nline2\nline3")});
    table->normalize();

    expected = R"(+------+------+
|item11|item12|
|      |line2 |
+------+------+
|      |item22|
|      |line2 |
|      |line3 |
+------+------+

)";

    QTest::newRow("multi-line") << table << QString::fromLatin1(expected);
}

void QtXmlToSphinxTest::testTableFormatting()
{
    QFETCH(TablePtr, table);
    QFETCH(QString, expected);

    StringStream str;
    table->format(str);
    const QString actual = str.toString();

    QCOMPARE(actual, expected);
}

void QtXmlToSphinxTest::testTableFormattingIoDevice_data()
{
    testTableFormatting_data();
}

void QtXmlToSphinxTest::testTableFormattingIoDevice()
{
    QFETCH(TablePtr, table);
    QFETCH(QString, expected);

    QByteArray byteArray;
    {
        TextStream str(&byteArray);
        table->format(str);
    }
    const QString actual = QString::fromUtf8(byteArray);

    QCOMPARE(actual, expected);
}

void QtXmlToSphinxTest::testSnippetExtraction_data()
{
    QTest::addColumn<QByteArray>("file");
    QTest::addColumn<QString>("id");
    QTest::addColumn<QString>("expected");

    const char *fileCpp = R"(bla
// ![snip1]
snip1_line1
// ![snip1] // ![snip2]
snip2_line1
snip2_line2
// ![snip2] // ![snip3]
)";

    const QString id = u"snip2"_s;
    const QString expected  = uR"(snip2_line1
snip2_line2
)"_s;

    const char *filePython = R"(bla
# ![snip1]
snip1_line1
# ![snip1] # ![snip2]
snip2_line1
snip2_line2
# ![snip2] # ![snip3]
)";

    QTest::newRow("c++") << QByteArray(fileCpp) << id << expected;
    QTest::newRow("Python") << QByteArray(filePython) << id << expected;
}

void QtXmlToSphinxTest::testSnippetExtraction()
{
    QFETCH(QByteArray, file);
    QFETCH(QString, id);
    QFETCH(QString, expected);

    QBuffer buffer(&file);
    QVERIFY(buffer.open(QIODevice::ReadOnly));
    QString errorMessage;
    QString actual = QtXmlToSphinx::readSnippet(buffer, id, &errorMessage);
    QVERIFY2(errorMessage.isEmpty(), qPrintable(errorMessage));
    QCOMPARE(actual, expected);
}

QTEST_APPLESS_MAIN( QtXmlToSphinxTest)
