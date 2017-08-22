#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib, subprocess, os, zipfile, socket, shutil
from datetime import datetime
from ftplib import FTP
import threading
from mrvl_adb import *
from mrvl_log import *
from mrvl_serial import *
from mrvl_mysql import *
from mrvl_log import *
import serial
import struct

if subprocess.mswindows:
	from win32file import ReadFile, WriteFile
	from win32pipe import PeekNamedPipe
	import errno,msvcrt
else:
	import select
        import fcntl

COMMANDS = {
			'list': ('list', 'Displays a list of all the available files'),
			'get': ('get <remote filename>', 'Downloads a file with a given filename'),
			'put': ('put <local file path> <remote file name>', 'Uploads a file with a given filename'),
			'hb':	('HB owner hostname macaddr duttype dutip swversion status', 'heartbeat with hostname macaddr duttype dutip swversion status'),
			#'hostname': ('hostname $hostname', 'update hosname infomation'),
			#'macaddr': ('macaddr $macaddr', 'update mac address infomation'),
			#'duttype': ('duttype $duttype', 'update dut type infomation'),
			#'swversion': ('swversion $swversion', 'update sw version infomation'),
			'start_testcase': ('start_testcase case_path', 'start a new task(test case)'),
			'stop_testcase': ('stop_testcase', 'stop a running task(stop the running test case)'),
			'put_done': ('put_done', 'finished upload test result'),
			'download': ('download <remote filename>', 'download file from server'),
			'help': ('help', 'Displays a list of all the available commands'),
			'quit': ('quit', 'Disconnects from the server'),
}

def timestamp():
	""" Returns current time stamp. """
	return '[%s]'  % (datetime.strftime(datetime.now(), '%H:%M:%S'))

def display_message(logger, message):
	""" Displays a message with a prepended time stamp. """
	
	#print '%s %s' % (timestamp(), message)
	logger.trace(message)

def validate_file_md5_hash(logger, file, original_hash):
	""" Returns true if file MD5 hash matches with the provided one, false otherwise. """

	if get_file_md5_hash(logger, file) == original_hash:
		return True
		
	return False

def get_file_md5_hash(logger, file):
	""" Returns file MD5 hash"""
	
	md5_hash = hashlib.md5()
	for bytes in read_bytes_from_file(file):
		md5_hash.update(bytes)
	logger.trace("md5:%s"%md5_hash.hexdigest())
	return md5_hash.hexdigest()

def read_bytes_from_file(file, chunk_size = 8100):
	""" Read bytes from a file in chunks. """
	
	with open(file, 'rb') as file:
		while True:
			chunk = file.read(chunk_size)
			
			if chunk:
					yield chunk
			else:
				break

def clean_and_split_input(input):
	""" Removes carriage return and line feed characters and splits input on a single whitespace. """
	
	input = input.strip()
	input = input.split(' ')
		
	return input

def get_os():
	if subprocess.mswindows:
		return "MSWin"
	else:
		return "Linux"
def get_mac_address():
	mac = "unknown"
	if subprocess.mswindows: 
		for line in os.popen("ipconfig /all"): 
			if line.lstrip().startswith('Physical Address'): 
				mac = line.split(':')[1].strip().replace('-',':') 
				break 
	else: 
		# mac = os.popen("/sbin/ifconfig|grep Ether|awk {'print $5'}").read()[:-1] 
		for line in os.popen("/sbin/ifconfig"): 
			if 'Ether' in line: 
				mac = line.split()[4] 
				break 
	return mac
def get_username():
	whoami_cmd = "whoami"
	username = "hzxu"
	if subprocess.mswindows: 
		for line in os.popen(whoami_cmd):
			line = line.strip()
			if line.find("marvell") > -1:
				username = line.split("\\")[-1]
				break 
	else: 
		for line in os.popen(whoami_cmd): 
			line = line.strip()
			if len(line) > 0:
				username = line
	return username
def chk_pingable(ip):
	if subprocess.mswindows: 
		ping_cmd = "ping -n 2 " + ip
		for line in os.popen(ping_cmd):
			line = line.strip()
			if line.find("100% loss") > -1:
				return False
	else:
		ping_cmd = "ping -c 2 " + ip
		for line in os.popen(ping_cmd):
			line = line.strip()
			if line.find("100% packet loss") > -1:
				return False
	return True
def chk_serial_couldopen(port):
	"""
	if subprocess.mswindows:
		print 'Auto-run is started on port [%d]'%(port)
	else:
		print 'Auto-run is started on port [%s]'%(port)
	"""	
	#configure serial port
	l_serial = serial.Serial()
	if platform.system() == 'Windows':
		l_serial.port = port-1
	else:
		l_serial.port = port-1
		l_serial.baudrate = 115200
		l_serial.timeout = None
		l_serial.bytesize = serial.EIGHTBITS
		l_serial.parity = serial.PARITY_NONE
		l_serial.stopbits = serial.STOPBITS_ONE
		l_serial.xonxoff = 0
	try:
		l_serial.open()
	except:
		#print "open serial get exception"
		return False
	if l_serial.isOpen():
		l_serial.close()
		return True
	else:
		return False
def get_serialport_list():
	port_list = []
	for port_idx in range(1, 16):
		if chk_serial_couldopen(port_idx):
			port_list.append(port_idx)
	return port_list
def get_duttype(server_ip):
	mysql_logger = mrvl_logger(os.path.join(os.getcwd(), "mysql.log"))
	dut_type_list = []
	mysql_hdlr = mrvl_mysql(mysql_logger, "Case_Dispatcher", server_ip, "root", "123456")
	res_db = mysql_hdlr.select_table('dut_type')
	for id, name, description, reserved in res_db:
		if description != None:
			dut_type_list.append(name)
	return dut_type_list

def get_ip():
    if subprocess.mswindows:
        return socket.gethostbyname(socket.gethostname())
    else:
        return get_ip_address('eth0')
def get_ip_address(ifname):
        skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pktString = fcntl.ioctl(skt.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
        ipString  = socket.inet_ntoa(pktString[20:24])
        return ipString

	
#
#print "10.37.130.212 could be pingabe: "+str(chk_pingable("10.37.130.212"))
#print "10.37.142.160 could be pingabe: "+str(chk_pingable("10.37.142.160"))
#print get_duttype(logger, "10.37.130.212")
#print get_ip()
if subprocess.mswindows:
	def __recv(logger, conn, maxsize = 1024*512):
		try:
			x = msvcrt.get_osfhandle(conn.fileno())
			(read, nAvail, nMessage) = PeekNamedPipe(x, 0)
			if maxsize < nAvail:
				nAvail = maxsize
			if nAvail > 0:
				(errCode, read) = ReadFile(x, nAvail, None)
				#read = subprocess.Popen._translate_newlines(read)
		except ValueError:
			logger.error( "get one unknow error when receive data" )
			return '', "unknown error"
		except (subprocess.pywintypes.error, Exception), why:
			if why[0] in (109, errno.ESHUTDOWN):
				if why[0] != 109:
					logger.error( "get error when read info from pipe %s, pipe id:%d, reason:%s"%(name, which.pid, str(why)) )
				return '', str(why[-1])
			return '', str(why[-1])
		return read, "sucess"
else:
	def __recv(logger, conn, maxsize = 1024*512):
		data = ''
		err_info = 'sucess'
		flags = fcntl.fcntl(conn, fcntl.F_GETFL)
		if not conn.closed:
			fcntl.fcntl(conn, fcntl.F_SETFL, flags| os.O_NONBLOCK)			
		try:
			if not select.select([conn], [], [], 0)[0]:
				#err_info = 'get error when read info from pipe %s, pipe id:%s, reason:%s'%(name, which.pid, 'select the pipe failed(conn closed)')
				#self.logger.error(err_info)
				err_info = ''
				#return '', err_info		   
			data = conn.read(maxsize)
		except Exception, e:
			error_info =  'get error when read info from pipe, reason:catpture exception %s'%str(e)
		except:
			error_info =  'get error when read info from pipe, reason:catpture unknown exception'
		finally:
			if not conn.closed:
				fcntl.fcntl(conn, fcntl.F_SETFL, flags)
		return data, err_info
def read_pipe(logger, pipe):
	res_stdout, des_stdout = __recv(logger, getattr(pipe, 'stdout'))
	res_stderr, des_stderr = __recv(logger, getattr(pipe, 'stderr'))
	return res_stdout, res_stderr
def zip_dir(logger, dirname, zipfilename):
	try:
		filelist = []
		if os.path.isfile(zipfilename):
			os.remove(zipfilename)
		if os.path.isfile(dirname):
			filelist.append(dirname)
		else :
			for root, dirs, files in os.walk(dirname):
				for name in files:
					#if not name.endswith("wmv"):
						filelist.append(os.path.join(root, name))
		zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED,True)
		for tar in filelist:
			arcname = tar[len(dirname):]
			zf.write(tar,arcname)
		zf.close()
	except Exception,e:
		logger.error("try to zip testresult failed;ERROR: %s"%str(e))
	except:
		logger.error("try to zip testresult failed")

def ftpconnect(ip): 
	ftp_server = ip  
	username = 'sqa'
	password = '123456'
	ftp=FTP()  
	#ftp.set_debuglevel(2) #打开调试级别2，显示详细信æïﾾ? 
	ftp.connect(ftp_server,21) #连接  
	ftp.login(username,password) #登录，如果匿名登录则用空串代替即åïﾾ? 
	return ftp  

def downloadfile(ip, logger, src_file, dst_file, src_path="/home/sqa/CaseDispatcher_v2.0/server/"):
	retry_cnt = 3
        fp=None
        ftp=None
        for attempt in range(retry_cnt):
                try:
                        if fp != None and not fp.closed:
                                try:
                                        fp.close()
                                        os.remove(dst_file)
                                except:
                                        logger.error("Fail to close %s"%dst_file)
                        if ftp!= None:
                                try:
                                        ftp.quit()
                                except:
                                        logger.error("Fail to quit ftp")
			ftp = ftpconnect(ip)  
			#print ftp.getwelcome() #显示ftp服务器欢迎信æïﾾ? 
			bufsize = 1024 #设置缓冲块大åïﾾ
			ftp.cwd(src_path)
			fp = open(dst_file,'wb') #以写模式在本地打开文件  
			ftp.retrbinary('RETR ' + src_file, fp.write, bufsize) #接收服务器上文件并写入本地文äïﾾ? 
			#ftp.set_debuglevel(0) #关闭调试  
			fp.close()  
			ftp.quit() #退出ftp服务åïﾾ
			break
	    	except Exception, e:
			logger.error("get exception:%s when try to download %s from test server for the %d time"%(str(e), src_file,4-retry_cnt))
			#return False
	    	except:
			logger.error("get unknown exception when try to download %s from test server for the %d time"%(src_file,4-retry_cnt))
			#return False
        else:
        	return False
        return True



def mkdir(logger, ftp, remotedir='./'):
	try:
                ftpdir = []
                ftp.dir("",ftpdir.append)
                if remotedir not in str(ftpdir).split(' '):
        		ftp.mkd(remotedir)
		ftp.cwd(remotedir)
	except Exception, e:
		logger.error('get Exception:%s' %str(e))
	except:
		logger.error('Directory Exists %s' %remotedir)

def uploadfile(ip, logger, src_file, dst_file, src_path="/home/sqa/CaseDispatcher_v2.0/server/Log/"):
	if os.path.isfile( src_file ) == False:  
		return False
	retry_cnt = 3
        fp=None
        ftp=None
        for attempt in range(retry_cnt):
                try:
                        if fp != None and not fp.closed:
                                try:
                                        fp.close()
                                        os.remove(dst_file)
                                except:
                                        pass
                        if ftp!= None:
                                try:
                                        ftp.quit()
                                except:
                                        pass
                        ftp = ftpconnect(ip)  
                        #print ftp.getwelcome() #显示ftp服务器欢迎信æïﾾ? 
                        bufsize = 1024 #设置缓冲块大åïﾾ
                        ftp.cwd(src_path)		
                        #ftp.m
                        for folder in dst_file.split("/")[:-1]:
                                mkdir(logger, ftp, folder)
                        ftp.cwd(src_path)
                        file_handler = open( src_file, "rb" )
                        ftp.storbinary( 'STOR %s'%dst_file, file_handler, bufsize )
                        file_handler.close()
                        #ftp.set_debuglevel(0) #关闭调试  
                        ftp.quit() #退出ftp服务åïﾾ
                except Exception, e:
                        logger.error("get exception:%s when try to upload %s from test server"%(str(e), src_file))
                        #return False
                except:
                        logger.error("get unknown exception when try to upload %s from test server"%src_file)
                        #return False
	else:
                return False
	return True


def __uploadfile(ftp, logger, src_file, dst_file, src_path="/home/sqa/CaseDispatcher_v2.0/server/Log/"):
	if os.path.isfile( src_file ) == False:
		return False
	try:
		bufsize = 1024 
		ftp.cwd(src_path)
		
		for folder in dst_file.split("/")[:-1]:
			mkdir(logger, ftp, folder)			
		ftp.cwd(src_path)
		file_handler = open( src_file, "rb" )
		ftp.storbinary( 'STOR %s'%dst_file, file_handler, bufsize )
		file_handler.close()
	except Exception, e:
		logger.error("get exception:%s when try to upload %s to test server: %s"%(str(e), src_file, src_path))
		return False
	except:
		logger.error("get unknown exception when try to upload %s to test server: %s"%src_file, src_path)
		return False
	return True

def __uploadfiles(ftp, logger, src_file, dst_file, src_path="/home/sqa/CaseDispatcher_v2.0/server/Log/"):
	if os.path.isfile( src_file ):
		return __uploadfile(ftp, logger, src_file, dst_file, src_path)
	ftp.cwd(src_path)
	for folder in dst_file.split("/"):
		if len(folder.strip()) > 0:
			mkdir(logger, ftp, folder)
	src_path = src_path + "/" + dst_file
	file_list = os.listdir(src_file)
	res = True
	for file_tmp in file_list:
		if not __uploadfiles(ftp, logger, os.path.join(src_file, file_tmp), file_tmp, src_path):
			res = False
	return res


def uploadfiles(ip, logger, src_file, dst_file, src_path="/home/sqa/CaseDispatcher_v2.0/server/Log/"):
	ftp = ftpconnect(ip)
	res = __uploadfiles(ftp, logger, src_file, dst_file, src_path)
	ftp.quit()
	return res

def __fg_recovery():
    adb_devices=subprocess.Popen("adb devices", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time_start = time.time()
    while time.time() - time_start < 10 and adb_devices.returncode == None:
        time.sleep(1)
        adb_devices.poll()

    stdout, stderr = read_pipe(None, adb_devices)
    if stdout.find('recovery') > -1:
        print "in recovery mode: %s"%stdout
        return True
    return False
def fg_recovery():
    for _ in range(5):
        if __fg_recovery():
            return True
        time.sleep(10)
    return False


def fg_dut_alive(serial_port, dut_ip,dut_type):
    serial_logger = mrvl_logger(os.path.join("serial.txt"))
    serial_hdlr = ComThread(serial_logger, int(serial_port))
    serial_hdlr.start()
    if dut_type == "LinuxSDK":
        serial_hdlr.write(["\x03"])
        time.sleep(2)
        res = serial_hdlr.get_keywords(["Berlin"], 5, AndOr = True, WriteCmd = ["hello", 3], Repeat_cmd = True)
    else:
        if fg_recovery(): 
            res=[True]
        else:
            serial_hdlr.write(["\x03"])
            time.sleep(2)
            res = serial_hdlr.get_keywords(["hello: not found"], 5, AndOr = True, WriteCmd = ["hello", 3], Repeat_cmd = True)
    serial_hdlr.stop()
    del serial_hdlr
    del serial_logger
    return res[0]

__all__ = [
	"timestamp",
	"display_message",
	"validate_file_md5_hash",
	"get_file_md5_hash",
	"read_bytes_from_file",
	"clean_and_split_input",
	"get_os",
	"get_mac_address",
	"read_pipe",
	"zip_dir",
	"downloadfile",
	"uploadfile"
]
