// Copyright (C) 2025 Ford Motor Company
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

#include <QtCore/qcoreapplication.h>
#include <QtCore/qsocketnotifier.h>
#include <QtCore/qtimer.h>

#include <QtRemoteObjects/qremoteobjectreplica.h>
#include <QtRemoteObjects/qremoteobjectnode.h>

#ifdef Q_OS_WIN
#  include <QtCore/qt_windows.h>
#  include <QtCore/qwineventnotifier.h>
#endif // Q_OS_WIN

#include <iostream>

using namespace Qt::StringLiterals;

class CommandReader : public QObject
{
    Q_OBJECT
public:
    explicit CommandReader(QObject *parent = nullptr) : QObject(parent)
    {
#ifndef Q_OS_WIN
        auto *notifier = new QSocketNotifier(fileno(stdin), QSocketNotifier::Read, this);
        connect(notifier, &QSocketNotifier::activated, this, &CommandReader::handleInput);
#else
        // FIXME: Does not work, signals triggers too often, the app is stuck in getline()
        auto notifier = new QWinEventNotifier(GetStdHandle(STD_INPUT_HANDLE), this);
        connect(notifier, &QWinEventNotifier::activated, this, &CommandReader::handleInput);
#endif
    }

signals:
    void started();

private slots:
    void handleInput()
    {
        std::string line;
        if (!std::getline(std::cin, line))
            return;

        if (line == "quit") {
            std::cerr << "harness: Received quit. Stopping harness event loop.\n";
            QCoreApplication::quit();
        } else if (line == "start") {
            std::cerr << "harness: Received start. Initializing harness nodes.\n";
            emit started();
        } else {
            std::cerr << "harness: Unknown command \"" << line << "\"\n";
        }
    }
};

class Runner : public QObject
{
    Q_OBJECT
public:
    Runner(const QUrl &url, const QString &repName, QObject *parent = nullptr)
        : QObject(parent)
        , m_url(url)
        , m_repName(repName)
    {
        m_host.setObjectName("cpp_host");
        if (!m_host.setHostUrl(QUrl("tcp://127.0.0.1:0"_L1))) {
            qWarning() << "harness: setHostUrl failed: " << m_host.lastError() << m_host.hostUrl();
            std::cerr << "harness: Fatal harness error.\n";
            QCoreApplication::exit(-2);
        }

        m_node.setObjectName("cpp_node");
        std::cout << "harness: Host url:" << m_host.hostUrl().toEncoded().constData() << '\n';
        std::cout.flush();
    }

public slots:
    void onStart()
    {
        m_node.connectToNode(m_url);
        m_replica.reset(m_node.acquireDynamic(m_repName));
        if (!m_replica->waitForSource(1000)) {
            std::cerr << "harness: Failed to acquire replica.\n";
            QCoreApplication::exit(-1);
        }

        m_host.enableRemoting(m_replica.get());
    }

private:
    QUrl m_url;
    QString m_repName;
    QRemoteObjectHost m_host;
    QRemoteObjectNode m_node;
    std::unique_ptr<QRemoteObjectDynamicReplica> m_replica;
};

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <url> <name of type>\n";
        return -1;
    }
    QUrl url = QUrl::fromUserInput(QString::fromUtf8(argv[1]));
    QString repName = QString::fromUtf8(argv[2]);

    if (!url.isValid()) {
        std::cerr << "Invalid URL: " << argv[1] << '\n';
        return -1;
    }

    CommandReader reader;
    Runner runner(url, repName);


    QRemoteObjectNode node;
    node.setObjectName("cpp_node");
    std::unique_ptr<QRemoteObjectDynamicReplica> replica;

    QObject::connect(&reader, &CommandReader::started, &runner, &Runner::onStart);

    return QCoreApplication::exec();
}

#include "cpp_interop.moc"
