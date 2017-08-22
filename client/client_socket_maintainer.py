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

import os,tarfile,shutil,zipfile
import optparse
from twisted.internet import reactor
from client_factory import FileTransferClientFactory
from client_protocol import CommandLineProtocol, FileTransferProtocol
import threading,time,string,socket,subprocess
from common import read_pipe


class maintainer():
	cmdlineProtocol = None
	factory = None
	
	#lock = threading.Lock()
	
	def set_cmdlineProtocol(self, cmdlineProtocol):
		self.cmdlineProtocol = cmdlineProtocol
	def set_factory(self, factory):
		self.factory = factory
		
	def update_status(self, cmd, timeout = 30):
		#self.lock.acquire()
		self.cmdlineProtocol.update_status(cmd)
		time_start = time.time()
		while time.time() - time_start < timeout:
			if not self.cmdlineProtocol.fgBusy():
				self.prv_logger.trace( "%s done;takes %d seconds"%(cmd, int(time.time() - time_start)))
				break
			time.sleep(0.01)
		else:
			self.prv_logger.trace("%s timeout(%d)"%(cmd, int(time.time() - time_start)))
		#self.lock.release()
		
	
	def download(self, download_cmd, timeout = 10):
		#self.lock.acquire()
		self.cmdlineProtocol.download_file(download_cmd)
		time_start = time.time()
		while time.time() - time_start < timeout:
			if not self.cmdlineProtocol.fgBusy():				
				self.prv_logger.trace( "%s done;takes %d seconds"%(download_cmd, int(time.time() - time_start)))
				break
			time.sleep(1)
		else:
			self.prv_logger.trace("%s done;takes %d seconds!!!"%(download_cmd, int(time.time() - time_start)))
		#self.lock.release()
	
	def upload(self, download_cmd, timeout = 10):
		#self.lock.acquire()
		self.cmdlineProtocol.upload_file(download_cmd)
		time_start = time.time()
		while time.time() - time_start < timeout:
			if not self.cmdlineProtocol.fgBusy():				
				self.prv_logger.trace("%s done;takes %d seconds"%(download_cmd, int(time.time() - time_start)))
				break
			time.sleep(1)
		else:
			self.prv_logger.trace("%s done;takes %d seconds!!!"%(download_cmd, int(time.time() - time_start)))
		#self.lock.release()
	
	
