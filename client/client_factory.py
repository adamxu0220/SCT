# -*- coding: utf-8 -*-
#
# Name: Pyton Twisted binary file transfer demo (client)
# Description: Simple demo which shows how you can transfer binary files using
# the Twisted framework.
#
# Keep in mind that this is only a demo and there are many possible scenarios
# where program can break.
#
# Author: Tomaž Muraus (http://www.tomaz-muraus.info)
# License: GPL

# Requirements:
# - Python >= 2.5
# - Twisted (http://twistedmatrix.com/)

from twisted.internet.protocol import ReconnectingClientFactory
from client_protocol import CommandLineProtocol, FileTransferProtocol

class FileTransferClientFactory(ReconnectingClientFactory):
    protocol = FileTransferProtocol
    CmdLineProtocol = None
    startcase_func = None
    stopcase_func = None
    cancelcase_func = None
    prv_logger = None
    def __init__(self, logger, files_path, cmdlineProtocol, startcase_func, stopcase_func, cancelcase_func):
        self.files_path = files_path
        self.CmdLineProtocol = cmdlineProtocol
        self.startcase_func = startcase_func
        self.stopcase_func = stopcase_func
        self.cancelcase_func = cancelcase_func
        self.prv_logger = logger

    """
    update CommandLineProtocol to FileTransferProtocol
    """
    def buildProtocol(self, addr):
        self.prv_logger.trace("in buildProtocol")
        p = self.protocol()
        p.setCmdLineProtocol(self.CmdLineProtocol)
        p.setLogger(self.prv_logger)
        p.set_startcase_func(self.startcase_func)
        p.set_stopcase_func(self.stopcase_func)
        p.set_cancelcase_func(self.cancelcase_func)
        p.factory = self
        return p
__all__ = ["FileTransferClientFactory"]    