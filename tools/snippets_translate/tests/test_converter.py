# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from converter import snippet_translate as st


def multi_st(lines):
    result = [st(l) for l in lines.split("\n")]
    return "\n".join(result)


def test_comments():
    assert st("// This is a comment") == "# This is a comment"
    assert st("// double slash // inside") == "# double slash // inside"


def test_comments_eol():
    assert st("a = 1; // comment") == "a = 1 # comment"
    assert st("while ( 1 != 1 ) { // comment") == "while 1 != 1: # comment"


def test_qdoc_snippets():
    assert st("//! [0]") == "//! [0]"


def test_arrow():
    assert st("label->setText('something')") == "label.setText('something')"


def test_curly_braces():
    assert st("        {") == ""
    assert st("}") == ""
    assert st("while (true){") == "while True:"
    assert st("while (true)   {  ") == "while True:"


def test_inc_dec():
    assert st("++i;") == "i = i + 1"
    assert st("i--;") == "i = i - 1"


def test_and_or():
    assert st("while (a && b)") == "while a and b:"
    assert st("else if (a || b && c)") == "elif a or b and c:"


def test_while_if_elseif():
    assert st("while(a)") == "while a:"
    assert st("if  (condition){") == "if condition:"
    assert st("    if  (condition){") == "    if condition:"
    assert st("} else if (a) {") == " elif a:"
    assert (
        st("if (!m_vbo.isCreated()) // init() failed,")
        == "if not m_vbo.isCreated(): # init() failed,"
    )
    # Special case, second line from a condition
    assert (
        st("&& event->answerRect().intersects(dropFrame->geometry()))")
        == "and event.answerRect().intersects(dropFrame.geometry()))"
    )


def test_else():
    assert st("else") == "else:"
    assert st("} else {") == "else:"
    assert st("}else") == "else:"
    assert st("else {") == "else:"


def test_new():
    assert st("a = new Something(...);") == "a = Something(...)"
    assert st("a = new Something") == "a = Something()"
    assert st("foo(new X, new Y(b), new Z)") == "foo(X(), Y(b), Z())"
    # Class member initialization list
    assert st("m_mem(new Something(p)),") == "m_mem(Something(p)),"
    assert st("m_mem(new Something),") == "m_mem(Something()),"


def test_semicolon():
    assert st("a = 1;") == "a = 1"
    assert st("};") == ""


def test_include():
    assert st('#include "something.h"') == "from something import *"
    assert st("#include <QtCore>") == "from PySide6 import QtCore"
    assert st("#include <QLabel>") == "from PySide6.QtWidgets import QLabel"
    assert st("#include <NotQt>") == ""
    assert st('#include strange"') == ""


def test_main():
    assert st("int main(int argc, char *argv[])") == 'if __name__ == "__main__":'


def test_cast():
    assert st("a = reinterpret_cast<type>(data);") == "a = type(data)"
    assert st("a = reinterpret_cast<type*>(data) * 9;") == "a = type(data) * 9"
    assert (
        st("elapsed = (elapsed + qobject_cast<QTimer*>(sender())->interval()) % 1000;")
        == "elapsed = (elapsed + QTimer(sender()).interval()) % 1000"
    )
    assert (
         st("a = qobject_cast<type*>(data) * 9 + static_cast<int>(42)")
         == "a = type(data) * 9 + int(42)"
    )


def test_double_colon():
    assert st("Qt::Align") == "Qt.Align"
    assert st('QSound::play("mysounds/bells.wav");') == 'QSound.play("mysounds/bells.wav")'
    assert st("Widget::method") == "Widget.method"

    # multiline statement connect statement
    # eg: connect(reply, &QNetworkReply::errorOccurred,
    #    this, &MyClass::slotError);
    assert st("this, &MyClass::slotError);") == "self.slotError)"


def test_connects():
    assert (
        st("connect(button, &QPushButton::clicked, this, &MyClass::slotClicked);")
        ==  "button.clicked.connect(self.slotClicked)"
    )
    assert (
        st("connect(m_ui->button, &QPushButton::clicked, this, &MyClass::slotClicked);")
        ==  "m_ui.button.clicked.connect(self.slotClicked)"
    )
    assert (
        st("connect(button.get(), &QPushButton::clicked, this, &MyClass::slotClicked);")
        ==  "button.clicked.connect(self.slotClicked)"
    )


def test_cout_endl():
    assert st("cout << 'hello' << 'world' << endl") == "print('hello', 'world')"
    assert st("    cout << 'hallo' << 'welt' << endl") == "    print('hallo', 'welt')"
    assert st("cout << 'hi'") == "print('hi')"
    assert st("'world' << endl") == "print('world')"

    assert st("cout << circ.at(i) << endl;") == "print(circ.at(i))"
    assert (
        st('cout << "Element name: " << qPrintable(e.tagName()) << "\n";')
        == 'print("Element name: ", qPrintable(e.tagName()), "\n")'
    )
    assert (
        st('cout << "First occurrence of Harumi is at position " << i << Qt::endl;')
        == 'print("First occurrence of Harumi is at position ", i)'
    )
    assert st('cout << "Found Jeanette" << endl;') == 'print("Found Jeanette")'
    assert st('cout << "The key: " << it.key() << Qt::endl') == 'print("The key: ", it.key())'
    assert (
        st("cout << (*constIterator).toLocal8Bit().constData() << Qt::endl;")
        == "print((constIterator).toLocal8Bit().constData())"
    )
    assert st("cout << ba[0]; // prints H") == "print(ba[0]) # prints H"
    assert (
        st('cout << "Also the value: " << (*it) << Qt::endl;') == 'print("Also the value: ", (it))'
    )
    assert st('cout << "[" << *data << "]" << Qt::endl;') == 'print("[", data, "]")'

    assert st('out << "Qt rocks!" << Qt::endl;') == 'print(out, "Qt rocks!")'
    assert st('    std::cout << "MyObject::MyObject()\n";') == '    print("MyObject::MyObject()\n")'
    assert st('qDebug() << "Retrieved:" << retrieved;') == 'print("Retrieved:", retrieved)'


def test_variable_declaration():
    assert st("QLabel label;") == "label = QLabel()"
    assert st('QLabel label("Hello");') == 'label = QLabel("Hello")'
    assert st("Widget w;") == "w = Widget()"
    assert st('QLabel *label = new QLabel("Hello");') == 'label = QLabel("Hello")'
    assert st('QLabel label = a_function("Hello");') == 'label = a_function("Hello")'
    assert st('QString a = "something";') == 'a = "something"'
    assert st("int var;") == "var = int()"
    assert st("float v = 0.1;") == "v = 0.1"
    assert st("QSome<thing> var;") == "var = QSome()"
    assert st("QQueue<int> queue;") == "queue = QQueue()"
    assert st("QVBoxLayout *layout = new QVBoxLayout;") == "layout = QVBoxLayout()"
    assert st("QPointer<QLabel> label = new QLabel;") == "label = QLabel()"
    assert st("QMatrix4x4 matrix;") == "matrix = QMatrix4x4()"
    assert st("QList<QImage> collage =") == "collage ="
    assert st("bool b = true;") == "b = True"
    assert st("Q3DBars *m_graph = nullptr;") == "m_graph = None"
    # Do not fall for member function definitions
    assert st("Q3DBars *Graph::bars() const") == "Q3DBars Graph.bars()"
    # Do not fall for member function declarations
    assert st("virtual Q3DBars *bars();") == "virtual Q3DBars bars()"


def test_for():
    assert st("for (int i = 0; i < 10; i++)") == "for i in range(0, 10):"
    assert st("    for (int i = 0; i < 10; i+=2)") == "    for i in range(0, 10, 2):"
    assert st("for (int i = 10; i >= 0; i-=2)") == "for i in range(-1, 10, -2):"
    assert st("for (int i = 0; i < 10; ++i)") == "for i in range(0, 10):"
    assert (
        st("for (int c = 0;" "c < model.columnCount();" "++c) {")
        == "for c in range(0, model.columnCount()):"
    )
    assert (
        st("for (int c = 0;" "c < table->columns();" "++c) {")
        == "for c in range(0, table.columns()):"
    )
    assert st("for (int i = 0; i <= 10; i++)") == "for i in range(0, 11):"
    assert st("for (int i = 10; i >= 0; i--)") == "for i in range(-1, 10, -1):"

    ## if contains "begin()" and "end()", do a 'for it in var'
    assert (
        st(
            "for (QHash<int, QString>::const_iterator it = hash.cbegin(),"
            "end = hash.cend(); it != end; ++it)"
        )
        == "for it in hash:"
    )
    assert (
        st("for (QTextBlock it = doc->begin();" "it != doc->end(); it = it.next())")
        == "for it in doc:"
    )
    assert st("for (auto it = map.begin(); it != map.end(); ++it) {") == "for it in map:"
    assert st("for (i = future.constBegin(); i != future.constEnd(); ++i)") == "for i in future:"
    assert st("for (it = block.begin(); !(it.atEnd()); ++it) {") == "for it in block:"
    assert (
        st("    for (it = snippetPaths.constBegin();" "it != snippetPaths.constEnd(); ++it)")
        == "    for it in snippetPaths:"
    )

    assert st("for (QChar ch : s)") == "for ch in s:"
    assert (
        st("for (const QByteArray &ext : " "qAsConst(extensionList))")
        == "for ext in extensionList:"
    )
    assert st("for (QTreeWidgetItem *item : found) {") == "for item in found:"

    # TODO: Strange cases
    # for ( ; it != end; ++it) {
    # for (; !elt.isNull(); elt = elt.nextSiblingElement("entry")) {
    # for (int i = 0; ids[i]; ++i)
    # for (int i = 0; i < (1>>20); ++i)
    # for(QDomNode n = element.firstChild(); !n.isNull(); n = n.nextSibling())


def test_emit():
    assert st("emit sliderPressed();") == "sliderPressed.emit()"
    assert st("emit actionTriggered(action);") == "actionTriggered.emit(action)"
    assert st("emit activeChanged(d->m_active);") == "activeChanged.emit(d.m_active)"
    assert st("emit dataChanged(index, index);") == "dataChanged.emit(index, index)"
    assert st("emit dataChanged(index, index, {role});") == "dataChanged.emit(index, index, {role})"
    assert (
        st('emit dragResult(tr("The data was copied here."));')
        == 'dragResult.emit(tr("The data was copied here."))'
    )
    assert (
        st("emit mimeTypes(event->mimeData()->formats());")
        == "mimeTypes.emit(event.mimeData().formats())"
    )
    assert (
        st("emit q_ptr->averageFrequencyChanged(m_averageFrequency);")
        == "q_ptr.averageFrequencyChanged.emit(m_averageFrequency)"
    )
    assert st("emit q_ptr->frequencyChanged();") == "q_ptr.frequencyChanged.emit()"
    assert (
        st("emit rangeChanged(d->minimum, d->maximum);")
        == "rangeChanged.emit(d.minimum, d.maximum)"
    )
    assert (
        st("emit sliderMoved((d->position = value));") == "sliderMoved.emit((d.position = value))"
    )
    assert (
        st("emit stateChanged(QContactAction::FinishedState);")
        == "stateChanged.emit(QContactAction.FinishedState)"
    )
    assert st("emit textCompleted(lineEdit->text());") == "textCompleted.emit(lineEdit.text())"
    assert (
        st("emit updateProgress(newstat, m_watcher->progressMaximum());")
        == "updateProgress.emit(newstat, m_watcher.progressMaximum())"
    )


def test_void_functions():
    assert st("void Something::Method(int a, char *b) {") == "def Method(self, a, b):"
    assert (
        st("void MainWindow::updateMenus(QListWidgetItem *current)")
        == "def updateMenus(self, current):"
    )
    assert (
        st("void MyScrollArea::scrollContentsBy(int dx, int dy)")
        == "def scrollContentsBy(self, dx, dy):"
    )
    assert st("void Wrapper::wrapper6() {") == "def wrapper6(self):"
    assert st("void MyClass::setPriority(Priority) {}") == "def setPriority(self, Priority): pass"
    assert st("void MyException::raise() const { throw *this; }") == "def raise(self): raise self"
    assert st("void tst_Skip::test_data()") == "def test_data(self):"
    assert st("void util_function_does_nothing()") == "def util_function_does_nothing():"
    assert st("static inline void cleanup(MyCustomClass *pointer)") == "def cleanup(pointer):"
    # TODO: Which name?
    assert st("void RenderWindow::exposeEvent(QExposeEvent *)") == "def exposeEvent(self, arg__0):"


def test_classes():
    assert st("class MyWidget //: public QWidget") == "class MyWidget(): #: public QWidget"
    assert st("class MyMfcView : public CView") == "class MyMfcView(CView):"
    assert st("class MyGame : public QObject {") == "class MyGame(QObject):"
    assert st("class tst_Skip") == "class tst_Skip():"
    assert st("class A : public B, protected C") == "class A(B, C):"
    assert st("class A : public B, public C") == "class A(B, C):"
    assert st("class SomeTemplate<int> : public QFrame") == "class SomeTemplate(QFrame):"
    # This is a tricky situation because it has a multi line dependency:
    #   class MyMemberSheetExtension : public QObject,
    #          public QDesignerMemberSheetExtension
    #   {
    # we will use the leading comma to trust it's the previously situation.
    assert st("class A : public QObject,") == "class A(QObject,"
    assert st("class B {...};") == "class B(): pass"


def test_constuctors():
    assert st("MyWidget::MyWidget(QWidget *parent)") == "def __init__(self, parent):"
    assert st("Window::Window()") == "def __init__(self):"


def test_inheritance_init():
    assert (
        st(": QClass(fun(re, 1, 2), parent), a(1)")
        == "    super().__init__(fun(re, 1, 2), parent)\n    self.a = 1"
    )
    assert (
        st(":   QQmlNdefRecord(copyFooRecord(record), parent)")
        == "    super().__init__(copyFooRecord(record), parent)"
    )
    assert (
        st("    : QWidget(parent), helper(helper)")
        == "    super().__init__(parent)\n    self.helper = helper"
    )
    assert st("   : QWidget(parent)") == "    super().__init__(parent)"
    assert (
        st(": a(0), bB(99), cC2(1), p_S(10),")
        == "    self.a = 0\n    self.bB = 99\n    self.cC2 = 1\n    self.p_S = 10"
    )
    assert (
        st(": QAbstractFileEngineIterator(nameFilters, filters), index(0) ")
        == "    super().__init__(nameFilters, filters)\n    self.index = 0"
    )
    assert (
        st(": m_document(doc), m_text(text)") == "    self.m_document = doc\n    self.m_text = text"
    )
    assert st(": m_size(size) { }") == "    self.m_size = size"
    assert (
        st(": option->palette.color(QPalette::Mid);")
        == "    self.option.palette.color = QPalette.Mid"
    )
    assert st(": QSqlResult(driver) {}") == "    super().__init__(driver)"


def test_arrays():
    assert st("static const GLfloat vertices[] = {") == "vertices = {"
    assert st("static const char *greeting_strings[] = {") == "greeting_strings = {"
    assert st("uchar arrow_bits[] = {0x3f, 0x1f, 0x0f}") == "arrow_bits = {0x3f, 0x1f, 0x0f}"
    assert st("QList<int> vector { 1, 2, 3, 4 };") == "vector = { 1, 2, 3, 4 }"


def test_functions():
    assert st("int Class::method(a, b, c)") == "def method(self, a, b, c):"
    assert st("QStringView Message::body() const") == "def body(self):"
    assert st("void Ren::exEvent(QExp *)") == "def exEvent(self, arg__0):"
    assert (
        st("QString myDecoderFunc(const QByteArray &localFileName);")
        == "def myDecoderFunc(localFileName):"
    )
    assert st("return QModelIndex();") == "return QModelIndex()"


def test_foreach():
    assert st("foreach (item, selected) {") == "for item in selected:"
    assert st("foreach (const QVariant &v, iterable) {") == "for v in iterable:"
    assert st("foreach (QObject *obj, list)") == "for obj in list:"
    assert (
        st("foreach (const QContactTag& tag, contact.details<QContactTag>()) {")
        == "for tag in contact.details():"
    )


def test_structs():
    assert st("struct ScopedPointerCustomDeleter") == "class ScopedPointerCustomDeleter():"
    assert st("struct Wrapper : public QWidget {") == "class Wrapper(QWidget):"
    assert st("struct Window {") == "class Window():"


def test_ternary_operator():
    assert st("int a = 1 ? b > 0 : 3") == "a = 1 if b > 0 else 3"
    assert (
        st("if (!game.saveGame(json ? Game::Json : Game::Binary))")
        == "if not game.saveGame(json if Game.Json else Game.Binary):"
    )


def test_useless_qt_classes():
    assert st('result += QLatin1String("; ");') == 'result += "; "'
    assert st('result += QString::fromLatin1("; ");') == 'result += "; "'
    assert (
        st('result = QStringLiteral("A") + QStringLiteral("B");')
        == 'result = "A" + "B"')
    assert st("<< QLatin1Char('\0') << endl;") == "print('\0')"
    assert st('result = u"A"_s;') == 'result = "A"'


def test_special_cases():
    assert (
        st('http->setProxy("proxy.example.com", 3128);')
        == 'http.setProxy("proxy.example.com", 3128)'
    )
    assert st("delete something;") == "del something"
    assert (
        st("m_program->setUniformValue(m_matrixUniform, matrix);")
        == "m_program.setUniformValue(m_matrixUniform, matrix)"
    )
    assert (
        st("QObject::connect(&window1, &Window::messageSent,")
        == "window1.messageSent.connect("
    )
    assert st("double num;") == "num = float()"

    # Leave a comment to remember it comes from C++
    assert st("public:") == "# public"
    assert st("private:") == "# private"

    #iterator declaration
    assert st("std::vector<int>::iterator i;") == ""

    # TODO: Handle the existing ones with Python equivalents
    # assert st("std::...")

    # FIXME: Maybe a better interpretation?
    # assert st("QDebug operator<<(QDebug dbg, const Message &message)") == "def __str__(self):"

    # TODO: Maybe play with the format?
    # assert st('m_o.append(tr("version: %1.%2").arg(a).arg(b))') == 'm_o.append(tr("version: {1}.{2}".format(a, b)'


def test_lambdas():
    # QtConcurrent::blockingMap(vector, [](int &x) { x *= 2; });

    # QList<QImage> collage = QtConcurrent::mappedReduced(images,
    #        [&size](const QImage &image) {
    #            return image.scaled(size, size);
    #        },
    #        addToCollage
    #   ).results();
    pass


def test_switch_case():
    source = """switch (v) {
case 1:
    f1();
    break;
case ClassName::EnumValue:
    f2();
    break;
default:
    f3();
    break;
}
"""
    expected = """
if v == 1:
    f1()
    break
elif v == ClassName.EnumValue:
    f2()
    break
else:
    f3()
    break

"""

    assert multi_st(source) == expected


def test_std_function():
    # std::function<QImage(const QImage &)> scale = [](const QImage &img) {
    pass
