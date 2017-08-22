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

import os,tarfile,shutil,zipfile,re
import threading,time,string,socket,subprocess
from common import get_os, get_mac_address, read_pipe, zip_dir
if not subprocess.mswindows:
        import pexpect

class maintainer():
	owner = "unknown"
	OS = "unknown"
	hostname = "unknown"
	ip = "unknown"
	dut_serial_port = None
	mac_addr = "unknown"
	dut_type = "unknown"
	dut_ip = ""
	sw_version = "unknown"	
	status = 'idle'
	status_detail = 'invalid'
	result = 'error'
	cmdid = "NULL"
	
	
	case_process = None	
	case_stdout_buf = ""
	case_stderr_buf = ""
	
	last_test_fold = None
	
	pythondiff_list = []
	upload_th = None
	serial_lock = threading.Lock()
	def __get_pid(self, app_name_win, app_name_linux):
		if subprocess.mswindows:
			PID_pro = subprocess.Popen('tasklist /FI "IMAGENAME eq %s"'%app_name_win,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			app_name = app_name_win
		else:
			PID_pro = subprocess.Popen('pidof %s'%app_name_linux,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			app_name = app_name_linux

		time_start = time.time()
		while PID_pro != None and PID_pro.returncode == None and time.time() - time_start < 10:
			PID_pro.poll()
			time.sleep(0.1)
		if time.time() - time_start > 10:
			self.prv_logger.error('Get %s PID timeout'%app_name)
			return False, ''

		if PID_pro != None:
			pid_out, pid_err = read_pipe(self.prv_logger, PID_pro)
			if subprocess.mswindows:
				PID_re = "%s.*?(\d+).*?"%app_name_win
				pid_list = []
				lines = pid_out.split("\r\n")
				for line in lines:
					f = re.match(PID_re, line)
					if f != None:
						pid = f.group(1)
						pid_list.append(pid)
			else:
				pid_list = pid_out.replace("\n", "").split(" ")						
			self.prv_logger.trace('Get %s PID list:%s'%(app_name, pid_list))
			return True, pid_list 
		else:
			self.prv_logger.error('Get %s PID subprocess failed.'%app_name)
			return False, ''		

	def __get_python_pid(self):
		return self.__get_pid("python.exe", "python")
	def __get_adb_pid(self):
		return self.__get_pid("adb.exe", "adb")
	def __taskkill_cmd(self,cmd):
		if not subprocess.mswindows:
			stc = pexpect.spawn('sudo kill -9 %s >/dev/null 2>&1'%cmd)
			stc.expect(':',timeout=30)
			stc.sendline('sqa')
			time.sleep(1)
			stc.terminate(True)
		else:
			os.system('taskkill /F /PID %s > nul 2>&1'%cmd)
	def runcase_teardown(self):
                if len(self.pythondiff_list) > 0:
                        self.prv_logger.trace("Will kill these pid: %s"%str(self.pythondiff_list))
		while len(self.pythondiff_list) > 0:
			self.__taskkill_cmd(self.pythondiff_list.pop())
		if self.upload_th != None:
			self.upload_th.join()
		try:
			self.serial_lock.release()
		except:
			pass
		
	
	def download_testcase(self, case_path):
		raise NotImplementedError()
	def upload_testresult(self):
		raise NotImplementedError()
		
			
	def find_file(self, dirname, filename):
		res = []
		if os.path.isdir(dirname):
			files = os.listdir(dirname)
			for file in files:
				filepath = os.path.join(dirname, file)
				res.extend(self.find_file(filepath, filename))
		else:
			if os.path.basename(dirname) == filename:
				res.append(dirname)
		return res
	def	get_diff_list(self, current_list, prv_list):
		tmp_list = []
		for current_pid in current_list:
			if prv_list.count(current_pid) > 0:
				continue
			tmp_list.append(current_pid)
		return tmp_list 
		
	def	start_testcase(self, case_path, config_path, cmdid, parameter=None):
		"""
		used to start a new test case
		"""
		self.prv_logger.trace("in start_testcase")
		self.status = 'busy'
		self.cmdid = cmdid
		self.result = 'error'
		self.status_detail = 'downloading_testcase'
		self.case_stdout_buf = ""
		self.case_stderr_buf = ""
		self.runcase_teardown()
		self.serial_lock.acquire()
		try:
			#hard code
			os.system("taskkill /F /IM adb.exe")
			if os.path.isfile("Test.tar.gz"):
				os.remove("Test.tar.gz")
			if os.path.isfile("testcase.tar.gz"):
				os.remove("testcase.tar.gz")
			if os.path.isfile("mrvl_lib.tar.gz"):
				os.remove("mrvl_lib.tar.gz")
			if self.last_test_fold != None and os.path.isdir(self.last_test_fold):
				shutil.rmtree(self.last_test_fold, ignore_errors=True)
		except Exception, e:
			self.prv_logger.error( "capture exception:%s when delete testcase.tar.gz, mrvl_lib.tar.gz and Test"%str(e))
		except:
			self.prv_logger.error( "capture unknown error when delete testcase.tar.gz, mrvl_lib.tar.gz and Test")
		
		self.download_testcase(case_path, config_path)
		self.status_detail = "starting"
		
		
		pythonpid_list_prv = self.__get_python_pid()
		self.run_testcase(parameter)		
		self.status_detail = "running"

		pythonpid_list_now = self.__get_python_pid()
		adbpid_list_now = self.__get_adb_pid()
		self.pythondiff_list = self.get_diff_list(pythonpid_list_now, pythonpid_list_prv)#list(set(pythonpid_list_now) - set(pythonpid_list_prv))
		
	def stop_testcase(self):
		"""
		used to stop a running test case
		subprocess stop
		"""
		self.status_detail = 'stopped'
		self.runcase_teardown()
	def cancel_testcase(self):
		"""
		used to cancel a running test case
		subprocess stop
		"""
		self.status_detail = 'cancel'
		self.runcase_teardown()
	def run_testcase(self, parameter):
		"""
		"""
		self.prv_logger.trace("try to run testcase")
		try:	
			timeStamp = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime())
			self.last_test_fold = "%s_Test"%timeStamp		
			tar = tarfile.open("mrvl_lib.tar.gz")
			tar.extractall(path = self.last_test_fold)
			tar.close()
			
			tar = tarfile.open("testcase.tar.gz")
			tar.extractall(path = self.last_test_fold)
			casename = tar.members[0].name
			self.prv_logger.trace( "try to run testcase:%s"%casename)
			tar.close()
			if os.path.getsize("config.py") > 0:
       				shutil.copy("config.py", os.path.join(self.last_test_fold, casename))
                        if parameter != None:
                            para_str = "--parameter %s"%parameter
                        else:
                            para_str = ""
			if self.dut_ip != None:
				cmd = "python -u %s --ip %s -p %s %s"%(os.path.join(self.last_test_fold, casename, "main.py"), self.dut_ip, self.dut_serial_port, para_str)
			else:
				cmd = "python -u %s -p %s %s"%(os.path.join(self.last_test_fold, casename, "main.py"), self.dut_serial_port, para_str)
			self.prv_logger.trace( cmd)
			self.case_process = subprocess.Popen(cmd, shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		except Exception, e:
			self.prv_logger.error( "capture exception:%s when extract testcase.tar.gz, mrvl_lib.tar.gz "%str(e))
		except:
			self.prv_logger.error( "capture unknown error when extract testcase.tar.gz, mrvl_lib.tar.gz ")
		
	
	#########################################################################################################
	#this function used to get current client's OS
	#########################################################################################################	
	def get_OS(self):
		self.OS = get_os()
	#########################################################################################################
	#this function used to get mac address from test client
	#########################################################################################################
	def get_mac_address(self):
		return get_mac_address()
	def get_sw_version(self):
		import get_sw_ver
		reload(get_sw_ver)
		self.sw_version = get_sw_ver.get_version(self.dut_type, self.dut_serial_port, self.dut_ip)
	
	
	def case_talk(self):
		if self.case_process != None:
			self.case_process.poll()
			stdout_str, stderr_str = read_pipe(self.prv_logger, self.case_process)
			self.case_stdout_buf += stdout_str
			self.case_stderr_buf += stderr_str

			#if len(self.case_stderr_buf) > 0 and self.case_stderr_buf.find('VIDIOC_QUERYMENU:') == -1:
			#	#get error info; logger.err
			#	self.prv_logger.error("get error info from subprocess; error info:\"%s\" length of error info:%d"%(self.case_stderr_buf, len(self.case_stderr_buf)))
			#	return False
			if self.case_process.returncode != None:
				self.prv_logger.error("return code:%s"%str(self.case_process.returncode))
				self.prv_logger.error("stdout:%s"%str(self.case_stdout_buf))
				self.prv_logger.error("stderr:%s"%str(self.case_stderr_buf))
				self.runcase_teardown()
				return False
			if len(stdout_str) > 0:
				self.prv_logger.trace(stdout_str)
			return True
		self.runcase_teardown()
		return False
__all__ = ["maintainer"]
