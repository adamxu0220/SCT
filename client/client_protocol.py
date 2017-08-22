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
from twisted.internet import reactor, protocol, stdio, defer
from twisted.protocols import basic
from twisted.internet.protocol import ClientFactory, Protocol, ReconnectingClientFactory
from common import COMMANDS, display_message, validate_file_md5_hash, get_file_md5_hash, read_bytes_from_file, clean_and_split_input
import os, threading

"""
this protocol used to communicate with server
"""
class CommandLineProtocol(basic.LineReceiver):
	delimiter = '\n'
	filetransferProtocol = None
	transport = None
	fg_ready = False
	fg_busy = False
	prv_logger = None
	def __init__(self, files_path):
		self.files_path = files_path
		
		
	def update(self, filetransferProtocol, factory, transport, fg_ready):
		self.filetransferProtocol = filetransferProtocol
		self.factory = factory
		self.transport = transport
		self.files_path = self.factory.files_path
		self.fg_ready = fg_ready
		self.prv_logger.trace("CommandLineProtocol ready:%s"%self.fg_ready)
		
	
	def lineReceived(self, line):
		""" If a line is received, call sendCommand(), else prompt user for input. """
		
	def __upload_file(self, line):
		""" Download a file from the server. """		
		data = clean_and_split_input(line) 
		if len(data) == 0 or data == '' or self.transport == None:
			return False
		command = data[0].lower()
		if command == 'upload':			
			try:
				file_path = data[1]
				filename = data[2]
				cmdid = data[3]
				result = data[4]
			except IndexError:
				self._display_message('Missing local file path or remote file name')
				return False
			
			if not os.path.isfile(file_path):
				self._display_message('This file does not exist')
				return False

			file_size = os.path.getsize(file_path) / 1024			
			self.prv_logger.trace('Uploading file: %s (%d KB)' % (filename, file_size)			)
			self.transport.write('upload %s %s %s %s\n' % (filename, get_file_md5_hash(self.prv_logger, file_path), cmdid, result))
			self.setRawMode()
			
			for bytes in read_bytes_from_file(file_path):
				self.transport.write(bytes)
			
			self.transport.write('\r\r\r\r\n')   
			
			# When the transfer is finished, we go back to the line mode 
			self.setLineMode()
			return True
		else:
			self.prv_logger.error("invalid cmd:%s"%command)
			return False
	def upload_file(self, line):
		if self.__upload_file(line):
			self.fg_busy = True
			return True
		return False
	def __download_file(self, line):
		""" Download a file from the server. """		
		data = clean_and_split_input(line) 
		if len(data) == 0 or data == '' or self.transport == None:
			return False
		command = data[0].lower()
		if command == 'download':			
			try:
				src_filename = data[1]
				dst_filename = data[2]
			except IndexError:
				self._display_message('Missing filename')
				return False
			self.transport.write('%s %s %s\n' % ("get", src_filename, dst_filename))
			return True
		else:
			self.prv_logger.error("invalid cmd:%s"%command)
			return False
	def download_file(self, line):
		if self.__download_file(line):
			self.fg_busy = True
			return True
		return False
	

	def __update_status(self, line):	
		""" Download a file from the server. """		
		data = clean_and_split_input(line) 
		if len(data) == 0 or data == '' or self.transport == None:
			return False
		command = data[0].lower()
		if command == 'hb':
			self.transport.write('%s %s\n' % (command, ' '.join(data[1:])))
			return True
		elif command == 'case_finished':
			self.transport.write('%s %s\n' % (command, ' '.join(data[1:])))
			return True
		else:
			self.prv_logger.error("invalid cmd:%s"%command)
			return False
	def update_status(self, line):
		if self.__update_status(line):
			self.fg_busy = True
			return True
		return False
	
	def fgBusy(self):
		return self.fg_busy
	def set_idle(self):
		self.fg_busy = False
		
	
		
	def _sendCommand(self, line):
		""" Sends a command to the server. """
		
		data = clean_and_split_input(line) 
		if len(data) == 0 or data == '' or self.transport == None:
			return 

		command = data[0].lower()
		if not command in COMMANDS:
			self._display_message('Invalid command:%s'%command)
			return
		
		if command == 'list' or command == 'help' or command == 'quit':
			self.transport.write('%s\n' % (command))
		elif command == 'get':
			try:
				src_filename = data[1]
				dst_filename = data[2]
			except IndexError:
				self._display_message('Missing filename')
				return
			
			self.transport.write('%s %s %s\n' % (command, src_filename, dst_filename))
		elif command == 'put':
			try:
				file_path = data[1]
				filename = data[2]
			except IndexError:
				self._display_message('Missing local file path or remote file name')
				return
			
			if not os.path.isfile(file_path):
				self._display_message('This file does not exist')
				return

			file_size = os.path.getsize(file_path) / 1024
			
			self.prv_logger.trace('Uploading file: %s (%d KB)' % (filename, file_size))
			
			self.transport.write('PUT %s %s\n' % (filename, get_file_md5_hash(self.prv_logger, file_path)))
			self.setRawMode()
			
			for bytes in read_bytes_from_file(file_path):
				self.transport.write(bytes)
			
			self.transport.write('\r\r\r\r\n')   
			
			# When the transfer is finished, we go back to the line mode 
			self.setLineMode()
		elif command == 'download':			
			try:
				src_filename = data[1]
				dst_filename = data[2]
			except IndexError:
				self._display_message('Missing filename')
				return
			self.prv_logger.trace('%s %s %s\n' % ("get", src_filename, dst_filename))
			self.transport.write('%s %s %s\n' % ("get", src_filename, dst_filename))
			self.prv_logger.trace('%s %s %s done\n' % ("get", src_filename, dst_filename))
		elif command == 'hb':
			self.transport.write('%s %s\n' % (command, ' '.join(data[1:])))
		else:
			self.transport.write('%s %s\n' % (command, data[1]))
			
	def _display_message(self, message):
		""" Helper function which prints a message and prompts user for input. """
		
		self.prv_logger.trace(message)



class FileTransferProtocol(basic.LineReceiver):
	delimiter = '\n'
	CmdLineProtocol = None
	fg_ready = False
	startcase_func = None
	stopcase_func = None
	cancelcase_func = None
	prv_logger = None
	
	def setCmdLineProtocol(self, CmdLineProtocol):
		self.CmdLineProtocol = CmdLineProtocol
	def setLogger(self, logger):
		self.prv_logger = logger
		self.CmdLineProtocol.prv_logger = logger
	def connectionMade(self):
		self.buffer = []
		self.file_handler = None
		self.file_data = ()
		self.fg_ready = True
		if self.CmdLineProtocol != None:
			self.CmdLineProtocol.update(self, self.factory, self.transport, self.fg_ready)
		self.prv_logger.trace('Connected to the server')		
	def connectionLost(self, reason):
		self.file_handler = None
		self.file_data = ()
		self.fg_ready = False
		if self.CmdLineProtocol != None:
			self.CmdLineProtocol.update(self, self.factory, self.transport, self.fg_ready)		
		self.prv_logger.trace('Connection to the server has been lost')
		#reactor.stop()
	def set_startcase_func(self, startcase_func):
		self.startcase_func = startcase_func
	def set_stopcase_func(self, stopcase_func):
		self.stopcase_func = stopcase_func
	def set_cancelcase_func(self, cancelcase_func):
		self.cancelcase_func = cancelcase_func	
		
	def _process_response(self, line = None):
		"""
		handle start/stop test case
		handle download test case
		handle upload test result
		handle update get-dut-sw-version method
		"""
		data = clean_and_split_input(line) 
		if len(data) == 0 or data == '':
			return 
		command = data[0].lower()
		if command == "stop_testcase":
			self.prv_logger.trace("try to stop running task")
			if self.stopcase_func != None:
				self.prv_logger.trace("call self.stopcase_func")
				self.stopcase_func()
		elif command == "start_testcase":
			self.prv_logger.trace("try to start new task")
			if self.startcase_func != None:
				self.prv_logger.trace("call self.startcase_func")
                                if len(data) == 4:
                                    th = threading.Thread(target = self.startcase_func, args = (data[1], data[2], data[3]))
                                
                                elif len(data) >= 5:
				    th = threading.Thread(target = self.startcase_func, args = (data[1], data[2], data[3], " ".join(data[4:])))
                                
                                else:
                                    self.prv_logger.error("error, invalid len(data):%d; data:%s"%(len(data), line));
                                
				th.setDaemon(True)
				th.start()
		elif command == "cancel_testcase":
			self.prv_logger.trace("try to cancel new task")
			if self.cancelcase_func != None:
				self.prv_logger.trace("call self.cancelcase_func")
				self.cancelcase_func()
		else:
			self.prv_logger.trace("unhandle command:%s"%command)
		
	def process_response(self, lines = None):
		""" Displays a server response. """		
		if lines:
			for line in lines:
				self.prv_logger.trace('%s' % (line))
				self._process_response(line)
	
	def lineReceived(self, line):
		if not vars(self).has_key("factory") or self.factory == None or not self.fg_ready: return
		if line == 'ENDMSG':
			self.prv_logger.trace(self.buffer)
			self.process_response(self.buffer)
			self.buffer = []
			self.CmdLineProtocol.set_idle()
		elif line.startswith('HASH'):
			# Received a file name and hash, server is sending us a file
			data = clean_and_split_input(line)

			filename = data[1]
			file_hash = data[2]
			
			self.file_data = (filename, file_hash)
			self.setRawMode()
		else:
			self.buffer.append(line)
			
	def rawDataReceived(self, data):
		if not vars(self).has_key("factory") or self.factory == None: return
		filename = self.file_data[0]
		file_path = os.path.join(self.factory.files_path, os.path.basename(filename))
		
		self.prv_logger.trace('Receiving file chunk (%d KB)' % (len(data)))
		
		if not self.file_handler:
			self.file_handler = open(file_path, 'wb')
			
		if data.endswith('\r\r\r\r\n'):
			# Last chunk
			data = data[:-2]
			self.file_handler.write(data)
			self.setLineMode()
			
			self.file_handler.close()
			self.file_handler = None
			
			if validate_file_md5_hash(self.prv_logger, file_path, self.file_data[1]):
				self.prv_logger.trace('File %s has been successfully transfered and saved' % (filename))
			else:
				#os.unlink(file_path)
				self.prv_logger.trace('File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename))
			self.CmdLineProtocol.set_idle()
		else:
			self.file_handler.write(data)
			
__all__ = ["CommandLineProtocol", "FileTransferProtocol"]
