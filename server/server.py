#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Name: Pyton Twisted binary file transfer demo (server)
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

import os,time
import optparse
import threading
from twisted.internet import reactor, protocol
from twisted.protocols import basic

from common import COMMANDS, display_message, validate_file_md5_hash, get_file_md5_hash, read_bytes_from_file, clean_and_split_input, get_case_name
from mysql_cmds import offline_all_conn, get_neighbour_cmd, get_private_cmd, get_special_cmd, update_special_cmd, update_connection_cmd, insert_connection_cmd, get_connection_info, update_connection_id, get_case_info, talk
import sys
sys.path.append("TestCase")
from mrvl_lib import *

class FileTransferProtocol(basic.LineReceiver):
	delimiter = '\n'
        busy_cnt = 0
        mysql_hdlr = None
        prv_logger = None
        file_data = {}
        def set_mysql_hdlr(self, mysql_hdlr):
            self.mysql_hdlr = mysql_hdlr
        def set_logger(self, logger):
            self.prv_logger = logger
	def connectionMade(self):
		self.factory.clients.append(self)
		self.file_data = {}
		
		self.transport.write('Welcome\n')
		self.transport.write('Type help for list of all the available commands\n')
		self.transport.write('ENDMSG\n')
                timeStamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                update_connection_cmd(self.mysql_hdlr,
                                     {'end_time':timeStamp, 'status':'offline'},
                                     {'client_ip':str(self.transport.getPeer().host)})
		insert_connection_cmd(self.mysql_hdlr, {'start_time':timeStamp, 'client_conn_port':str(self.transport.getPeer().port), 'client_ip':str(self.transport.getPeer().host)})
		display_message(self.prv_logger, 'Connection from: %s (%d clients total)' % (str(self.transport.getPeer().port), len(self.factory.clients)))
		
	def connectionLost(self, reason):
		self.factory.clients.remove(self)
		self.file_data = {}
                timeStamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                update_connection_cmd(self.mysql_hdlr,
                                     {'end_time':timeStamp, 'status':'offline'},
                                     {'client_conn_port':str(self.transport.getPeer().port), 'client_ip':str(self.transport.getPeer().host)})
		
		display_message(self.prv_logger, 'Connection from %s lost (%d clients left)' % (self.transport.getPeer().host, len(self.factory.clients)))

	def lineReceived(self, line):
		display_message(self.prv_logger, 'Received the following line from the client [%s]: %s' % (self.transport.getPeer().host, line))
		
		data = self._cleanAndSplitInput(line)
		if len(data) == 0 or data == '':
			return 
		
		command = data[0].lower()
		if not command in COMMANDS:
			self.transport.write('Invalid command:%s\n'%command)
			self.transport.write('ENDMSG\n')
			return
		if command == 'list':
			self._send_list_of_files()
		elif command == 'get':
			try:
				src_filename = data[1]
                                dst_filename = data[2]
			except IndexError:
				self.transport.write('Missing filename\n')
				self.transport.write('ENDMSG\n')
				return
		        abs_file_path = os.path.join(self.factory.files_path, src_filename)	
			if not os.path.isfile(abs_file_path):
				self.transport.write('File with filename %s does not exist\n' % (src_filename))
				self.transport.write('ENDMSG\n')
				return
                        file_size = os.path.getsize(abs_file_path)
                        md5_hash = get_file_md5_hash(abs_file_path)
			
			display_message(self.prv_logger, 'Sending file to (%s:%s): %s (%d KB)' % (str(self.transport.getPeer().host), str(self.transport.getPeer().port), src_filename, file_size / 1024))
			
			self.transport.write('HASH %s %s\n' % (dst_filename, md5_hash))
			self.setRawMode()
			
			for bytes in read_bytes_from_file(abs_file_path):
				self.transport.write(bytes)
			
			self.transport.write('\r\r\r\r\n')	
			self.setLineMode()
		elif command == 'put' or command == 'upload':
			try:
				filename = data[1]
				file_hash = data[2]
			except IndexError:
				self.transport.write('Missing filename or file MD5 hash\n')
				self.transport.write('ENDMSG\n')
				return
                        if command == 'upload':
                            try:
                                id = data[3]
                                result = data[4]
                            except IndexError:
                                self.transport.write('Missing id or result when upload\n')
                                self.transport.write('ENDMSG\n')
                                return
                            timeStamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                            if not update_special_cmd(self.mysql_hdlr, id, {'status':'finished', 'end_time':timeStamp, 'result':result}):
                                self.prv_logger.error("update mysql failed; status: running->finished")
                            self.file_data["%s:%s"%(str(self.transport.getPeer().host), str(self.transport.getPeer().port))] = {'filename':filename, 'file_hash':file_hash, 'id':id}
                        else:
      			    self.file_data["%s:%s"%(str(self.transport.getPeer().host), str(self.transport.getPeer().port))] = {'filename':filename, 'file_hash':file_hash}
			
			# Switch to the raw mode (for receiving binary data)
			print 'Receiving file: %s' % (filename)
			self.setRawMode()
                elif command == 'case_finished':
                        id = data[1]
                        result = data[2]
                        timeStamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                        self.prv_logger.trace("update mysql, case id:%s, result:%s"%(id, result))
                        if len(data) > 3:
                                if not update_special_cmd(self.mysql_hdlr, id, {'status':'finished', 'end_time':timeStamp, 'result':result, 'reserved': ' '.join(data[3:])}):
                                    self.prv_logger.error("update mysql failed; status: running->finished")
                        elif not update_special_cmd(self.mysql_hdlr, id, {'status':'finished', 'end_time':timeStamp, 'result':result}):
                                self.prv_logger.error("update mysql failed; status: running->finished")
                        self.transport.write('ENDMSG\n')
		elif command == 'help':
			self.transport.write('Available commands:\n\n')
			
			for key, value in COMMANDS.iteritems():
				self.transport.write('%s - %s\n' % (value[0], value[1]))
			
			self.transport.write('ENDMSG\n')
		elif command == 'hb':
			try:
                                owner = data[1]
				hostname = data[2].lower()
				macaddr = data[3].lower()
				duttype = data[4]
                                dutip = data[5]
				swversion = data[6]
                                status = data[7]
                                taskid = data[8]
                                timeStamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                                update_connection_cmd(self.mysql_hdlr,
                                     {'end_time':timeStamp, 'status':'offline', 'client_pcname':hostname},
                                     {'mac_addr':macaddr},
                                     where_str_addtional='client_conn_port != %s'%str(self.transport.getPeer().port))
                                update_connection_cmd(self.mysql_hdlr, 
                                                      {'mac_addr':macaddr, 'owner':owner, 'dut_type':duttype, 'dut_ip':dutip, 'sw_version':swversion, 'status':status, 'client_pcname':hostname},
                                                      {'client_conn_port':str(self.transport.getPeer().port), 'client_ip':str(self.transport.getPeer().host)},
                                                      where_str_addtional='order by id desc limit 1')
                                update_connection_id(self.mysql_hdlr, {'mac_addr':macaddr})
                                conn_info = get_connection_info(self.mysql_hdlr,
                                                      {'client_conn_port':str(self.transport.getPeer().port), 'client_ip':str(self.transport.getPeer().host)})
                                if conn_info != None:
                                    client_id = conn_info['client_id']
                                else:
                                    client_id = 0
                                #hardcode
                                self.prv_logger.trace("current connection id:%d"%client_id)
                                private_cmd = get_private_cmd(self.mysql_hdlr, owner, duttype, client_id, swversion)
                                neighbour_cmd = get_neighbour_cmd(self.mysql_hdlr, owner, duttype, client_id, swversion)
                                if status == 'idle':
                                    self.busy_cnt = 0
                                    #self.transport.write('start_testcase %s\n'%os.path.join("BG2CDP", "Chromecast_HBOGO.tar.gz"))
                                    if private_cmd != None: cmd_list = private_cmd
                                    elif neighbour_cmd != None: cmd_list = neighbour_cmd
                                    else:
                                        self.prv_logger.trace( "could not get any command from mysql")
                                        cmd_list = None

                                    if cmd_list != None: 
                                        case_info = get_case_info(self.mysql_hdlr, {'id':cmd_list['case_id']})
                                        if case_info != None:
                                            start_case_cmd = case_info['path']
                                        else:
                                            start_case_cmd
                                    else: start_case_cmd = None
                                    if start_case_cmd != None:
                                        self.transport.write('start_testcase %s %s %s %s\n'%(start_case_cmd, os.path.join("TestCase", "Config", str(cmd_list['id']), 'config.py'), cmd_list['id'], cmd_list['case_parametar']))
                                        timeStamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                                        if not update_special_cmd(self.mysql_hdlr, cmd_list['id'], {'status':'running', 'exc_client_id':client_id, 'start_time':timeStamp, 'sw_version':swversion}): self.prv_logger.error("update mysql failed;status:not run->running")    
                                    #self.transport.write('ENDMSG\n')
                                elif status == 'busy':
                                    #update_special_cmd(self.mysql_hdlr, taskid, {'status':'running', 'sw_version':swversion})
                                    self.prv_logger.trace( "dut is busy(id:%s)"%taskid)
                                    res = get_special_cmd(self.mysql_hdlr, taskid)
                                    if res != None:
                                        if res['status'] == 'running':
                                            self.prv_logger.trace('got it(id:%s)'%taskid)
                                            if res['cmd_owner'] != owner and private_cmd != None:
                                                self.prv_logger.trace('case(id:%s; case_id:%s; owner:%s) will be canceled;'%(res['id'], res['case_id'], res['cmd_owner']))
                                                self.prv_logger.trace('case(id:%s; case_id:%s; owner:%s) will be run;'%(private_cmd['id'], private_cmd['case_id'], private_cmd['cmd_owner']))
                                                if not update_special_cmd(self.mysql_hdlr, taskid, {'status':'not run'}): self.prv_logger.error("update mysql failed;status:not running->not run")
                                                self.transport.write('cancel_testcase\n')
                                                update_special_cmd(self.mysql_hdlr, taskid, {'status':'not run', 'sw_version':swversion})
                                        elif res['status'] == 'stopped':
                                            self.transport.write('stop_testcase\n')
                                            update_special_cmd(self.mysql_hdlr, taskid, {'status':'finished', 'result':'stopped', 'reserved':'manually stopped', 'sw_version':swversion})
                                        elif res['status'] == 'restart':
                                            self.transport.write('cancel_testcase\n')
                                            update_special_cmd(self.mysql_hdlr, taskid, {'status':'not run', 'reserved':'manually canceled', 'sw_version':swversion})
                                        else:
                                            update_special_cmd(self.mysql_hdlr, taskid, {'status':'running', 'sw_version':swversion})
                                            self.prv_logger.trace('invalid status:%s (id:%s)'%(res['status'], taskid))
                                    else:
                                        self.prv_logger.error('could not get(id:%s) in db'%taskid)

                                else:
                                    """
                                    should be hang or other unhandle status,
                                    need notify administrator and client owner
                                    """
                                self.transport.write('ENDMSG\n')
                                print "owner:%s hostname:%s macaddr:%s duttype:%s dutip:%s swversion:%s status:%s"%(owner, hostname, macaddr, duttype, dutip, swversion, status)
			except IndexError:
				self.transport.write('Missing hostname, macaddr, duttype or swversion\n')
				self.transport.write('ENDMSG\n')
                                self.prv_logger.trace('Missing hostname, macaddr, duttype or swversion\n')
				return
                        #except Exception, e:
                        #        self.prv_logger.trace('Capture exception:%s'%str(e))
                        #except:
                        #        self.prv_logger.trace('Capture unknown exception')
		elif command == 'quit':
			self.transport.loseConnection()
			
	def rawDataReceived(self, data):
                key = "%s:%s"%(str(self.transport.getPeer().host), str(self.transport.getPeer().port))
                if not self.file_data.has_key(key):
                    return
		filename = self.file_data[key]['filename']
                timeStamp = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime())
                if not self.file_data[key].has_key('id'):
                    file_path = os.path.join(self.factory.files_path, "%s_%s"%(timeStamp, filename))
                else:
                    path_tmp = os.path.join(self.factory.files_path, "Log", str(self.file_data[key]['id']))
                    if not os.path.isdir(path_tmp):
                        os.mkdir(path_tmp)
                    file_path = os.path.join(path_tmp, "%s_%s"%(timeStamp, filename))
		
		display_message(self.prv_logger, 'Receiving file chunk (%d KB) from (%s)' % (len(data)/1024, key))
		
		if not self.file_data[key].has_key('file_handler') and not self.file_data[key].has_key('file_path'):
			self.file_data[key]['file_handler'] = open(file_path, 'wb')
                        self.file_data[key]['file_path'] = file_path
		
		if data.endswith('\r\r\r\r\n'):
			# Last chunk
			data = data[:-2]
			self.file_data[key]['file_handler'].write(data)
			self.setLineMode()
			
			self.file_data[key]['file_handler'].close()
			#self.file_data[key]['file_handler'] = None
		        file_path = self.file_data[key]['file_path']	
                        file_hash = self.file_data[key]['file_hash']
                        del self.file_data[key]
                        #self.file_data[key]['file_path'] = None
			if validate_file_md5_hash(file_path, file_hash):
				self.transport.write('File was successfully transfered and saved\n')
                                self.transport.write('put_done\n')
				self.transport.write('ENDMSG\n')
				
				display_message(self.prv_logger, 'File %s has been successfully transfered' % (filename))
			else:
				#os.unlink(file_path)
				self.transport.write('File was successfully transfered but not saved, due to invalid MD5 hash\n')
                                self.transport.write('put_done\n')
				self.transport.write('ENDMSG\n')
			
				display_message(self.prv_logger, 'File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename))
		else:
			self.file_data[key]['file_handler'].write(data)
		
	def _send_list_of_files(self):
		files = self._get_file_list()
		self.factory.files = files
		
		self.transport.write('Files (%d): \n\n' % len(files))	
		for key, value in files.iteritems():
			self.transport.write('- %s (%d.2 KB)\n' % (key, (value[1] / 1024.0)))
			
		self.transport.write('ENDMSG\n')
			
	def _get_file_list(self):
		""" Returns a list of the files in the specified directory as a dictionary:
		
		dict['file name'] = (file path, file size, file md5 hash)
		"""
		
		file_list = {}
		for filename in os.listdir(self.factory.files_path):
			file_path = os.path.join(self.factory.files_path, filename)
			
			if os.path.isdir(file_path):
				continue
			
			file_size = os.path.getsize(file_path)
			md5_hash = get_file_md5_hash(file_path)

			file_list[filename] = (file_path, file_size, md5_hash)

		return file_list
			
	def _cleanAndSplitInput(self, input):
		input = input.strip()
		input = input.split(' ')
		
		return input

class FileTransferServerFactory(protocol.ServerFactory):
	
	protocol = FileTransferProtocol
	mysql_hdlr = None
        prv_logger = None
	def __init__(self, files_path, logger, mysql_hdlr):
		self.files_path = files_path
		
		self.clients = []
		self.files = None
                self.mysql_hdlr = mysql_hdlr
                self.prv_logger = logger
        def buildProtocol(self, addr):
            p = self.protocol()
            p.factory = self
            p.set_mysql_hdlr(self.mysql_hdlr)
            p.set_logger(self.prv_logger)
            return p

class mysql_talk(threading.Thread):
	def __init__(self, mysql_hdlr):
		super(mysql_talk, self).__init__()
	        self.mysql_hdlr = mysql_hdlr

	def run(self):
		while True:
			time.sleep(60*60)
			talk(self.mysql_hdlr)
	
if __name__ == '__main__':
	parser = optparse.OptionParser()
	parser.add_option('-p', '--port', action = 'store', type = 'int', dest = 'port', default = 1234, help = 'server listening port')
	parser.add_option('--path', action = 'store', type = 'string', dest = 'path', help = 'directory where the incoming files are saved')
	(options, args) = parser.parse_args()

	main_logger = mrvl_common.mrvl_logger(os.path.join(os.getcwd(), "main.log"))
	display_message(main_logger, 'Listening on port %d, serving files from directory: %s' % (options.port, options.path))


        mysql_logger = mrvl_common.mrvl_logger(os.path.join(os.getcwd(),"mysql.log"))
        mysql_hdlr = mrvl_common.mrvl_mysql(mysql_logger, 'Case_Dispatcher')
        offline_all_conn(mysql_hdlr)
	mysql_talk_thread = mysql_talk(mysql_hdlr)
	mysql_talk_thread.start()
	reactor.listenTCP(options.port, FileTransferServerFactory(options.path, main_logger, mysql_hdlr))
	reactor.run()
