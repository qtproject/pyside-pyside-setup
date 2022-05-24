# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc


class BasicPySlotCase(object):
    '''Base class that tests python slots and signal emissions.

    Python slots are defined as any callable passed to QObject.connect().
    '''
    def setUp(self):
        self.called = False

    def tearDown(self):
        try:
            del self.args
        except:
            pass
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def cb(self, *args):
        '''Simple callback with arbitrary arguments.

        The test function must setup the 'args' attribute with a sequence
        containing the arguments expected to be received by this slot.
        Currently only a single connection is supported.
        '''
        if tuple(self.args) == args:
            self.called = True
        else:
            raise ValueError('Invalid arguments for callback')
