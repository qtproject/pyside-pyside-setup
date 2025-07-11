#!/usr/bin/python
# Copyright (C) 2025 Ford Motor Company
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Verify Python <--> C++ interop'''

import os
import sys
import textwrap

import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[2]))  # For init_paths
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QUrl, QProcess, QObject, Signal
from PySide6.QtRemoteObjects import (QRemoteObjectHost, QRemoteObjectNode, QRemoteObjectReplica,
                                     RepFile)
from PySide6.QtTest import QSignalSpy, QTest

sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))  # For wrap_tests_for_cleanup
from test_shared import wrap_tests_for_cleanup
from helper.usesqapplication import UsesQApplication


"""
This test needs to be run from the build directory in
order to locate the harness binary.

The previous tests all verify Remote Objects integration, but only
using Python for both Source and Replica.  We need to make sure there
aren't any surprises in the interplay between Python and C++.

This implements an initial test harness with a C++ app that is
started by the Python unittest.  We leverage the fact that Remote
Objects can
1) Allow remoting any QObject as a Source with enableRemoting
2) Acquire Dynamic Replicas, where the definition needed for the
   Replica is sent from the source.

With these, we can create a working C++ app that doesn't need to be
compiled with any information about the types being used.  We have
a host node in Python that shares a class derived from a RepFile
Source type.  The address of this node is passed to the C++ app via
QProcess, and there a C++ node connects to that address to acquire
(dynamically) a replica of the desired object.

The C++ code also creates a host node and sends the address/port
back to Python via the QProcess interface.  Once the Python code
receives the C++ side address and port, it connects a node to that
URL and acquires the RepFile based type from Python.

Python        C++
Host  ----->  Node (Dynamic acquire)
                |
                |   Once initialized, the dynamic replica is
                |   shared (enable_remoting) from the C++ Host
                |
Node  <-----  Host
"""


def msg_cannot_start(process, executable):
    return ('Cannot start "' + executable + '" in "'
            + os.fspath(Path.cwd()) + '": ' + process.errorString())


def stop_process(process):
    result = process.waitForFinished(2000)
    if not result:
        process.kill()
        result = process.waitForFinished(2000)
    return result


class Controller(QObject):
    ready = Signal()

    def __init__(self, utest: unittest.TestCase):
        super().__init__()
        # Store utest so we can make assertions
        self.utest = utest

        # Set up nodes
        self.host = QRemoteObjectHost()
        self.host.setObjectName("py_host")
        self.host.setHostUrl(QUrl("tcp://127.0.0.1:0"))
        self.cpp_url = None
        self.node = QRemoteObjectNode()
        self.node.setObjectName("py_node")
        self._executable = "cpp_interop.exe" if os.name == "nt" else "./cpp_interop"

    def start(self):
        # Start the C++ application
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.process_harness_output)
        self.process.readyReadStandardError.connect(self.process_harness_stderr_output)
        urls = self.host.hostUrl().toDisplayString()
        print(f'Starting C++ application "{self._executable}" "{urls}"', file=sys.stderr)
        self.process.start(self._executable, [self.host.hostUrl().toDisplayString(), "Simple"])
        self.utest.assertTrue(self.process.waitForStarted(2000),
                              msg_cannot_start(self.process, self._executable))

        # Wait for the C++ application to output the host url
        spy = QSignalSpy(self.ready)
        self.utest.assertTrue(spy.wait(1000))
        self.utest.assertTrue(self.cpp_url.isValid())

        self.utest.assertTrue(self.node.connectToNode(self.cpp_url))
        return True

    def stop(self):
        if self.process.state() == QProcess.ProcessState.Running:
            print(f'Stopping C++ application "{self._executable}" {self.process.processId()}',
                  file=sys.stderr)
            self.process.write("quit\n".encode())
            self.process.closeWriteChannel()
            self.utest.assertTrue(stop_process(self.process))
        self.utest.assertEqual(self.process.exitStatus(), QProcess.ExitStatus.NormalExit)

    def add_source(self, Source, Replica):
        """
        Source and Replica are types.

        Replica is from the rep file
        Source is a class derived from the rep file's Source type
        """
        self.process.write("start\n".encode())
        source = Source()
        self.host.enableRemoting(source)
        replica = self.node.acquire(Replica)
        self.utest.assertTrue(replica.waitForSource(5000))
        self.utest.assertEqual(replica.state(), QRemoteObjectReplica.State.Valid)
        return source, replica

    def process_harness_output(self):
        '''Process stdout from the C++ application, parse for URL'''
        output = self.process.readAllStandardOutput().trimmed()
        lines = output.data().decode().split("\n")
        HOST_LINE = "harness: Host url:"
        for line in lines:
            print("  stdout: ", line, file=sys.stderr)
            if line.startswith(HOST_LINE):
                urls = line[len(HOST_LINE):].strip()
                print(f'url="{urls}"', file=sys.stderr)
                self.cpp_url = QUrl(urls)
                self.ready.emit()

    def process_harness_stderr_output(self):
        '''Print stderr from the C++ application'''
        output = self.process.readAllStandardError().trimmed()
        print("  stderr: ", output.data().decode())


class HarnessTest(UsesQApplication):
    def setUp(self):
        super().setUp()
        self.rep = RepFile(self.__class__.contents)
        self.controller = Controller(self)
        self.assertTrue(self.controller.start())

    def tearDown(self):
        self.controller.stop()
        self.app.processEvents()
        super().tearDown()
        QTest.qWait(100)  # Wait for 100 msec


@wrap_tests_for_cleanup(extra=['rep'])
class TestBasics(HarnessTest):
    contents = textwrap.dedent("""\
        class Simple
        {
            PROP(int i = 2);
            PROP(float f = -1. READWRITE);
        }
        """)

    def compare_properties(self, instance, values):
        '''Compare properties of instance with values'''
        self.assertEqual(instance.i, values[0])
        self.assertAlmostEqual(instance.f, values[1], places=5)

    def testInitialization(self):
        '''Test constructing RepFile from a path string'''
        class Source(self.rep.source["Simple"]):
            pass
        source, replica = self.controller.add_source(Source, self.rep.replica["Simple"])
        self.compare_properties(source, [2, -1])
        self.compare_properties(replica, [2, -1])


if __name__ == '__main__':
    unittest.main()
