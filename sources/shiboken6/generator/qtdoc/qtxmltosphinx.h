// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef QTXMLTOSPHINX_H
#define QTXMLTOSPHINX_H

#include <textstream.h>

#include <QtCore/QList>
#include <QtCore/QScopedPointer>
#include <QtCore/QStack>

#include <memory>

QT_BEGIN_NAMESPACE
class QDebug;
class QXmlStreamReader;
QT_END_NAMESPACE

class QtXmlToSphinxDocGeneratorInterface;
struct QtXmlToSphinxParameters;
struct QtXmlToSphinxLink;

enum class WebXmlTag;

class QtXmlToSphinx
{
public:
    Q_DISABLE_COPY_MOVE(QtXmlToSphinx)

    struct InlineImage
    {
        QString tag;
        QString href;
    };

    struct TableCell
    {
        short rowSpan = 0;
        short colSpan = 0;
        QString data;

        TableCell(const QString& text = QString()) : data(text) {}
        TableCell(const char* text) : data(QString::fromLatin1(text)) {}
    };

    using TableRow = QList<TableCell>;

    class Table
    {
        public:
            Table() = default;

            bool isEmpty() const { return m_rows.isEmpty(); }

            void setHeaderEnabled(bool enable)
            {
                m_hasHeader = enable;
            }

            bool hasHeader() const
            {
                return m_hasHeader;
            }

            void normalize();

            bool isNormalized() const
            {
                return m_normalized;
            }

            void appendRow(const TableRow &row) { m_rows.append(row); }

            const TableRow &constFirst() const { return m_rows.constFirst(); }
            TableRow &first() { return m_rows.first(); }
            TableRow &last() { return m_rows.last(); }

            void format(TextStream& s) const;
            void formatDebug(QDebug &debug) const;

        private:
            bool hasEmptyLeadingRow() const;
            bool hasEmptyTrailingRow() const;

            QList<TableRow> m_rows;
            bool m_hasHeader = false;
            bool m_normalized = false;
    };

    explicit QtXmlToSphinx(const QtXmlToSphinxDocGeneratorInterface *docGenerator,
                           const QtXmlToSphinxParameters &parameters,
                           const QString& doc,
                           const QString& context = QString());
    ~QtXmlToSphinx();

    QString result() const
    {
        return m_result;
    }

    static void stripPythonQualifiers(QString *s);

    // For testing
    static QString readSnippet(QIODevice &inputFile, const QString &identifier,
                               QString *errorMessage);

private:
    using StringSharedPtr = std::shared_ptr<QString>;

    QString transform(const QString& doc);

    void handleHeadingTag(QXmlStreamReader& reader);
    void handleParaTag(QXmlStreamReader& reader);
    void handleParaTagStart();
    void handleParaTagText(QXmlStreamReader &reader);
    void handleParaTagEnd();
    void handleItalicTag(QXmlStreamReader& reader);
    void handleBoldTag(QXmlStreamReader& reader);
    void handleArgumentTag(QXmlStreamReader& reader);
    void handleSeeAlsoTag(QXmlStreamReader& reader);
    void handleSnippetTag(QXmlStreamReader& reader);
    void handleDotsTag(QXmlStreamReader& reader);
    void handleLinkTag(QXmlStreamReader& reader);
    void handleImageTag(QXmlStreamReader& reader);
    void handleInlineImageTag(QXmlStreamReader& reader);
    void handleListTag(QXmlStreamReader& reader);
    void handleTermTag(QXmlStreamReader& reader);
    void handleSuperScriptTag(QXmlStreamReader& reader);
    void handleQuoteFileTag(QXmlStreamReader& reader);

    // table tagsvoid QtXmlToSphinx::handleValueTag(QXmlStreamReader& reader)

    void handleTableTag(QXmlStreamReader& reader);
    void handleHeaderTag(QXmlStreamReader& reader);
    void handleRowTag(QXmlStreamReader& reader);
    void handleItemTag(QXmlStreamReader& reader);
    void handleRawTag(QXmlStreamReader& reader);
    void handleCodeTag(QXmlStreamReader& reader);
    void handlePageTag(QXmlStreamReader&);
    void handleTargetTag(QXmlStreamReader&);

    void handleIgnoredTag(QXmlStreamReader& reader);
    void handleUnknownTag(QXmlStreamReader& reader);
    void handleUselessTag(QXmlStreamReader& reader);
    void handleAnchorTag(QXmlStreamReader& reader);
    void handleRstPassTroughTag(QXmlStreamReader& reader);

    QtXmlToSphinxLink *handleLinkStart(const QString &type, QString ref) const;
    static void handleLinkText(QtXmlToSphinxLink *linkContext, const QString &linktext) ;
    void handleLinkEnd(QtXmlToSphinxLink *linkContext);
    WebXmlTag parentTag() const;

    void warn(const QString &message) const;
    void debug(const QString &message) const;

    QStack<WebXmlTag> m_tagStack;
    TextStream m_output;
    QString m_result;

    QStack<StringSharedPtr> m_buffers; // Maintain address stability since it used in TextStream

    QStack<Table> m_tables; // Stack of tables, used for <table><list> with nested <item>
    QScopedPointer<QtXmlToSphinxLink> m_linkContext; // for <link>
    QScopedPointer<QtXmlToSphinxLink> m_seeAlsoContext; // for <see-also>foo()</see-also>
    QString m_context;
    const QtXmlToSphinxDocGeneratorInterface *m_generator;
    const QtXmlToSphinxParameters &m_parameters;
    int m_formattingDepth = 0;
    bool m_insideBold = false;
    bool m_insideItalic = false;
    QString m_lastTagName;
    QString m_opened_anchor;
    QList<InlineImage> m_inlineImages;

    bool m_containsAutoTranslations = false;

    struct Snippet
    {
        enum Result {
            Converted, // C++ converted to Python
            Resolved, // Otherwise resolved in snippet paths
            Fallback, // Fallback from  XML
            Error
        };

        QString code;
        Result result;
    };

    void setAutoTranslatedNote(QString *str) const;

    Snippet readSnippetFromLocations(const QString &path,
                                     const QString &identifier,
                                     const QString &fallbackPath,
                                     QString *errorMessage);
    static QString readFromLocation(const QString &location, const QString &identifier,
                             QString *errorMessage);
    void pushOutputBuffer();
    QString popOutputBuffer();
    void writeTable(Table& table);
    bool copyImage(const QString &href) const;
    void callHandler(WebXmlTag t, QXmlStreamReader &);
    void formatCurrentTable();
};

inline TextStream& operator<<(TextStream& s, const QtXmlToSphinx& xmlToSphinx)
{
    return s << xmlToSphinx.result();
}

QDebug operator<<(QDebug d, const QtXmlToSphinxLink &l);
QDebug operator<<(QDebug debug, const QtXmlToSphinx::Table &t);
QDebug operator<<(QDebug debug, const QtXmlToSphinx::TableCell &c);

#endif // QTXMLTOSPHINX_H
