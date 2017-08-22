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

import os,sys,tarfile,shutil,zipfile
import optparse
from twisted.internet import reactor
from client_factory import FileTransferClientFactory
from client_protocol import CommandLineProtocol
import threading,time,string,socket,subprocess
from common import get_os, get_mac_address, read_pipe, zip_dir, downloadfile, uploadfile, uploadfiles, fg_dut_alive, get_duttype, get_username, get_ip, chk_pingable, get_serialport_list
import client_case_maintainer, client_socket_maintainer
from mrvl_log import mrvl_logger
from client_ui import *
import socket
import urllib2

class client_runner(threading.Thread, client_case_maintainer.maintainer, client_socket_maintainer.maintainer):
    
    def __init__(self, dut_ip, ip_address):
        """
        """
        threading.Thread.__init__(self)
        #self.owner = owner
        self.hostname = string.upper(socket.gethostname())#(platform.uname()[1])
        self.ip = socket.gethostbyname(socket.gethostname())
        self.mac_addr = self.get_mac_address()
        self.prv_logger = mrvl_logger(os.path.join(os.getcwd(), "main.log"))
        downloadfile(ip_address, self.prv_logger, "client_info.py", "client_info.py")
        import client_info
        reload(client_info)
        self.dut_type = client_info.client_list[self.hostname]['dut_type']
        self.dut_serial_port = client_info.client_list[self.hostname]['serial_port']
        self.owner = client_info.client_list[self.hostname]['owner']
        
        self.dut_ip = dut_ip
        self.get_OS()
        self.get_sw_version()
        self.prv_logger = mrvl_logger(os.path.join(os.getcwd(), "main.log"))
        downloadfile(ip_address, self.prv_logger, "get_sw_ver.py", "get_sw_ver.py")
        import port_ip_conf
        reload(port_ip_conf)
        self.powerport_ip_map = port_ip_conf.port_ip_map
        ip = socket.gethostname()
        self.pm_type = "Undefined"
        if self.powerport_ip_map.get(ip) == None:
            self.prv_logger.error("invaild ip:%s"%(str(ip)))
        else:
            self.port = self.powerport_ip_map[ip]["port"]
            temp = self.powerport_ip_map[ip]["server_ip"]
            if temp.startswith("apache:"):
                self.pm_server_ip=temp[len("apache:"):]
                self.pm_type = "apache"
                self.prv_logger.trace("pm_server_ip:%s port:%d"%(self.pm_server_ip, self.port))
            else:
                self.pm_server_ip=temp[len("lpt:"):]
                self.pm_type = "lpt"
                self.prv_logger.trace("lpt_server_ip:%s port:%d"%(self.pm_server_ip, self.port))
        
    def download_testcase(self, case_path, config_path):
        downloadfile(ip_address, self.prv_logger, case_path, "testcase.tar.gz")
        downloadfile(ip_address, self.prv_logger, "TestCase/mrvl_lib.tar.gz", "mrvl_lib.tar.gz")
        downloadfile(ip_address, self.prv_logger, config_path, "config.py")
        
        #self.download("download %s testcase.tar.gz"%case_path, 120)
        #self.download("download TestCase/mrvl_lib.tar.gz mrvl_lib.tar.gz", 120)
        #self.download("download %s config.py"%config_path, 120)
    def __search_file(self, fold_dir, dst_file):
        if os.path.basename(fold_dir) == dst_file:
            return fold_dir
        if not os.path.isdir(fold_dir):
            return None
        files = os.listdir(fold_dir)
        for file_name in files:
            if file_name == dst_file:
                return os.path.join(fold_dir, file_name)
        for file_name in files:
            res = self.__search_file(os.path.join(fold_dir, file_name), dst_file)
            if res != None:
                return res

        return None
    def __search_logs(self, fold_dir):
        res = []
        if not os.path.isdir(fold_dir):
            if fold_dir.endswith(".log"):
                res.append(fold_dir)
            return res
        files = os.listdir(fold_dir)
        for file_name in files:
            res.extend(self.__search_logs(os.path.join(fold_dir, file_name)))
        return res
    def upload_testresult(self):
        res_pass = self.find_file(self.last_test_fold, "pass.txt")
        res_fail = self.find_file(self.last_test_fold, "fail.txt")
        if len(res_fail) > 0:
            self.result = 'Failed'
        elif len(res_pass) > 0:
            self.result = 'Pass'
        else:
            self.result = 'Error'
        self.update_status("case_finished %s %s"%(self.cmdid, self.result))
        time_start = time.time()
        os.system("taskkill /F /IM adb.exe")
        try:
            if os.path.exists(self.last_test_fold):
                if self.upload_th != None:
                    self.upload_th.join()

                zip_dir(self.prv_logger, self.last_test_fold, "Test.tar.gz")
                result_fold = None
                if self.result == "Error" and len(self.case_stderr_buf) > 0:
                    fh = file("result.html", "wb")
                    fh.write(self.case_stderr_buf)
                    fh.close()
                    result_html = "result.html"
                else:
                    result_html = self.__search_file(self.last_test_fold, "result.html")
                    result_fold = self.__search_file(self.last_test_fold, "result")
            
                #zip_dir(self.prv_logger, "Sample_log", "Test.tar.gz")
                self.prv_logger.trace( "zip spend %d seconds"%int(time.time() - time_start) )
                #self.upload("upload Test.tar.gz Test.tar.gz %s %s"%(self.cmdid, self.result), 60*60)
                timeStamp = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime())
                if result_fold != None:
                    uploadfiles(ip_address, self.prv_logger, result_fold, "%s/result"%(self.cmdid))
                elif result_html != None:
                    uploadfile(ip_address, self.prv_logger, result_html, "%s/result.html"%(self.cmdid))
                    logs = self.__search_logs(self.last_test_fold)
                    for log_name in logs:
                        uploadfile(ip_address, self.prv_logger, log_name, "%s/%s"%(self.cmdid, os.path.basename(log_name)))
                    self.upload_th = threading.Thread(target = uploadfile, args=(ip_address, self.prv_logger, "Test.tar.gz", "%s/%s_Test.tar.gz"%(self.cmdid, timeStamp)))
                    self.upload_th.setDaemon(True)
                    self.upload_th.start()
            else:
                self.prv_logger.error("test result folder does not exist: %s "%self.last_test_fold)
        except e:
            self.prv_logger.error("Catch Exception when upload testresult: %s"%e)
        self.status_detail = "invalid"
        self.status = "idle"
    def open_url(self, url_str, action):
        try:
            self.prv_logger.trace(url_str)
            res = urllib2.urlopen(url_str, timeout=20)
            self.prv_logger.trace(res.read())
        except Exception, e:
            self.prv_logger.error("try to open url:%s failed"%url_str)
            self.prv_logger.error("-----------------An exception catched when we use power manager to %s: [%s]------------------"%(action, str(e)))
            return False
        except:
            self.prv_logger.error("-----------------unknown exception catched when we use power manager to %s------------------"%action)
            return False
        return True
    def PM_Off(self, powermanager_ip, powermanager_port):    
        action = "off the platform"
        url_str = "http://%s/off%d.php"%(powermanager_ip, powermanager_port)
        return self.open_url(url_str, action)
    def PM_On(self, powermanager_ip, powermanager_port):    
        action = "on the platform"
        url_str = "http://%s/on%d.php"%(powermanager_ip, powermanager_port)
        return self.open_url(url_str, action)
    def hw_power_reset(self):
        if self.pm_type == "apache":
            if self.PM_Off(self.pm_server_ip, self.port) == False:
                return False
            time.sleep(10)
            if self.PM_On(self.pm_server_ip, self.port) == False:
                return False
        elif self.pm_type == "lpt":
            if not self.pek_spi():
                self.prv_logger.error("PEK return to spi failed")
            return False
        else:
            self.prv_logger.error("-----------------unknown reset format:%s------------------"%self.pm_type)
            return False
        return True
    

    def __kill_task_byID(self, pid):
        if subprocess.mswindows:
            os.system("taskkill /F /PID %s >nul 2>&1"%pid)
        else:
            os.system("kill -9 %s >/dev/null 2>&1"%pid)


    #subprocess for kill/conn
    def __subprocess_blocked(self, cmd, timeout = 10):
        fg_timeout = True
        std_out = ''
        std_err = ''
        ret = False
        self.prv_logger.info('try to %s'%cmd)
        try:
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time_start = time.time()
            while (process.returncode == None and time.time() - time_start < timeout):
                #polling process status
                process.poll()
                time.sleep(0.01)
            #if process not end, kill it
            if (process.returncode == None):
                self.prv_logger.info('Call __subprocess_blocked method(%s) timeout; pid:%d'%(cmd, process.pid))
                process.poll()
                process.kill()
                process.wait()        
            else:
                fg_timeout = False
                self.prv_logger.info("Call __supborcess_blocked method(%s) return code:%s"%(cmd, str(process.returncode)))
            std_out, std_err = read_pipe(self.prv_logger, process)
            if fg_timeout:
                self.__kill_task_byID(str(process.pid))
        
            if fg_timeout or process.returncode != 0:
                ret = False
            else:
                ret = True
            del process
        except Exception, e:
            self.prv_logger.error("get exception:%s in __subprocess_blocked(%s)"%(str(e), str(cmd)))
        except:
            self.prv_logger.error("get unknown exception in __subprocess_blocked(%s)"%(str(cmd)))
        return ret, std_out, std_err
    def _pek_command(self, cmd):
        ret, std_out, std_err = self.__subprocess_blocked(cmd, 5)
        return ret
        
    def _pek_clear(self):
        return self._pek_command("./lpt -c")
    def _pek_spi(self):
        return self._pek_command("./lpt -s")
    def _pek_emmc(self):
        return self._pek_command("./lpt -e")
    def _pek_reset(self):
        return self._pek_command("./lpt -r")

    def pek_emmc(self):
        if not self._pek_clear():
            self.prv_logger.error("PEK clear failed")
            return False
        if not self._pek_emmc():
            self.prv_logger.error("PEK set emmc mode failed")
            return False
        if not self._pek_reset():
            self.prv_logger.error("PEK reset(reboot) failed")
            return False
        return True
    def pek_spi(self):
        if not self._pek_clear():
            self.prv_logger.error("PEK clear failed")
            return False
        if not self._pek_spi():
            self.prv_logger.error("PEK set spi mode failed")
            return False
        if not self._pek_reset():
            self.prv_logger.error("PEK reset(reboot) failed")
            return False
        return True
    def pek_reset(self):
        if not self._pek_reset():
            self.prv_logger.error("PEK reset(reboot) failed")
            return False
        return True
    
    def run(self):
        #"""
        time_last_updatest = time.time()
        while True:
            try:
                if self.status == "busy" and (self.status_detail == "running" or self.status_detail == "cancel" or self.status_detail == "stopped"):
                    if not self.case_talk():
                        if self.status_detail != "cancel":
                            self.status_detail = "uploading"
                            self.upload_testresult()
                        else:
                            self.status = 'idle'
                            self.status_detail = 'invalid'
                
                
                #self.prv_logger.trace( "self.status :%s; self.status_detail:%s"%(self.status, self.status_detail) )
                #self.update_status("HB %s %s %s %s %s %s %s %s"%(self.owner, self.hostname, self.mac_addr, self.dut_type, self.dut_ip, self.sw_version, self.status, self.cmdid))
                
                if time.time() - time_last_updatest > 5:
                    time_last_updatest = time.time()
                    if self.status != 'busy':
                        self.serial_lock.acquire()
                        if not fg_dut_alive(self.dut_serial_port, self.dut_ip, self.dut_type):
                            self.status = "dead"
                            if self.dut_type == "LinuxSDK":
                                self.pek_spi()
                                self.status = "idle"
                            else:
                                self.hw_power_reset()
                                #self.status = "idle"
                            time.sleep(20)
                        else:
                            if self.status == "dead":
                                self.status = "idle"
                            #self.download("download get_sw_ver.py get_sw_ver.py", 12)
                            #downloadfile(options.ip_address, self.prv_logger, "get_sw_ver.py", "get_sw_ver.py")
                            self.get_sw_version()
                        self.serial_lock.release()
                    self.prv_logger.trace( "self.status :%s; self.status_detail:%s"%(self.status, self.status_detail) )
                    self.update_status("HB %s %s %s %s %s %s %s %s"%(self.owner, self.hostname, self.mac_addr, self.dut_type, self.dut_ip, self.sw_version, self.status, self.cmdid))

            except KeyboardInterrupt:
                self.prv_logger.trace( "User Press Ctrl+C,Socket break down.")
                break
            except Exception, e:
                self.prv_logger.error( str(e) )
                break
            except:
                self.prv_logger.trace( "get a unknown exception" )
                break
            time.sleep(0.01)
        #"""

if __name__ == '__main__':
    
    print 'Client started, incoming files will be saved to %s' % (os.getcwd())
    print sys.argv[0]
    os.chdir(os.path.dirname(sys.argv[0])) 
    ip_address = sys.argv[1]
    cr = client_runner(None, ip_address)
    cmdlineProtocol = CommandLineProtocol(os.getcwd())
    factory = FileTransferClientFactory(cr.prv_logger, os.getcwd(), cmdlineProtocol, cr.start_testcase, cr.stop_testcase, cr.cancel_testcase)
    cr.set_cmdlineProtocol(cmdlineProtocol)
    cr.set_factory(factory)
    connection = reactor.connectTCP(ip_address, 1234, factory)
    #stdio.StandardIO(cmdProtocol)
    cr.setDaemon(True)  
    cr.start()
    reactor.run()
