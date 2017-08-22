#Filename:adb_api.py

import sys
import time
import threading
import subprocess
import logging
import errno
import os
import inspect
import re

if subprocess.mswindows:
    from win32file import ReadFile, WriteFile
    from win32pipe import PeekNamedPipe
    import msvcrt
else:
    import select
    import fcntl

DEBUG = False

class ADB_Interface_init():
    def __get_script_fold(self):
        caller_file = inspect.stack()[1][1]         # caller's filename
        return os.path.abspath(os.path.dirname(caller_file))# path
    #used to init/delete logger for mrvl_adb debug
    def __initlog(self, logname):
        new_logger = logging.getLogger(logname)
        formatter = logging.Formatter("%(asctime)s  %(levelname)s:		[%(filename)s][%(funcName)s][%(lineno)d]		%(message)s")
        new_logger_hdlr = logging.FileHandler(logname, 'wb+')
        new_logger_hdlr.setFormatter(formatter)
        new_logger.addHandler(new_logger_hdlr)
        new_logger.setLevel(logging.DEBUG)
        return new_logger, new_logger_hdlr
    def __dellog(self, logger, logger_hdlr):
        logger.removeHandler(logger_hdlr)
        del logger

    def __init__(self, ip, logpath):
        self.adb_lock = threading.Lock()
        self.fg_adb_exist = False
        platform = os.path.join(self.__get_script_fold(), "platform-tools")
        if subprocess.mswindows:
            self.__adb = os.path.join(platform, 'adb.exe')
        else:
            self.__adb = 'adb'
        self.__process_buf = []
        self.__dict_offline = {}
        self.logcat_process = None
        
        #init logger
        self.logname = os.path.join(logpath, 'adb.log')
        self.logger, self.hdlr = self.__initlog(self.logname)   

       
        if subprocess.mswindows: 
            #check self.__adb exist
            if not os.path.isfile(self.__adb):
                self.logger.error('ADB exe not exits!!!!!!!!!!')
            else:
                self.fg_adb_exist = True
        else:
            #error handle miss
            self.fg_adb_exist = True

        #start adb server
        if self.fg_adb_exist == True:
            self.kill_server()
            self.start_server()
    def __del__(self):
        self.kill_server()        
        self.__dellog(self.logger, self.hdlr)
        del self.adb_lock
        return True


    def kill_task_byID(self, pid):
        self.__kill_task_byID(pid)
    def kill_task_byName(self, name):
        self.__kill_task_byName(name)
    def __kill_task_byID(self, pid):
        self.logger.info("try to kill pid:%s"%pid)
        if subprocess.mswindows:
            os.system("taskkill /F /PID %s >nul 2>&1"%pid)
        else:
            os.system("kill -9 %s >/dev/null 2>&1"%pid)
    def __kill_task_byName(self, name):
        if subprocess.mswindows:
            os.system("taskkill /F /IM %s >nul 2>&1"%name)
        else:
            os.system("kill -9 $(pidof %s) >/dev/null 2>&1"%name)

    
    def __set_offline(self, ip):
        if self.__dict_offline.has_key(ip):
            self.__dict_offline[ip] = False
        else:
            self.__dict_offline.update({ip:False})
    def __set_online(self, ip):
        if self.__dict_offline.has_key(ip):
            self.__dict_offline[ip] = True
        else:
            self.__dict_offline.update({ip:True})
    def fg_device_online(self, ip):    
        if self.__dict_offline.has_key(ip):
            return self.__dict_offline[ip]
        return False
        

    #adb start-server
    #used to start adb server
    def start_server(self):
        #self.cmds_blocked(None, sys._getframe().f_code.co_name, None, 10)
        res, cmd = self.__get_cmds(None, sys._getframe().f_code.co_name, None)
        fg_timeout, stdout, stderr = self.__subprocess_blocked(cmd, 10)
        return (not fg_timeout) 
    #adb kill-server
    #used to kill adb server
    #adb kill-server and taskkill /F /IM adb.exe or kill -9 pidof(adb)
    def kill_server(self):
        print "kill_server"
        if subprocess.mswindows:
            self.__kill_task_byName("dwwin.exe")
            self.__kill_task_byName("vsjitdebugger.exe")
            self.__kill_task_byName("adb.exe")
        else:
            self.__kill_task_byName("adb")
    #used to recv data from pipe
    #return "read data", "sucess or fail reason"
    if subprocess.mswindows:
        def __recv(self, which, name, maxsize = 1024):
            conn = getattr(which, name)
            try:
             
                x = msvcrt.get_osfhandle(conn.fileno())
                (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
                if maxsize < nAvail:
                    nAvail = maxsize
                if nAvail > 0:
                    (errCode, read) = ReadFile(x, nAvail, None)
                    #read = subprocess.Popen._translate_newlines(read)
            except ValueError:
                self.logger.error("get one unknow error when receive data")
                return '', "unknown error"
            except (subprocess.pywintypes.error, Exception), why:
                if why[0] in (109, errno.ESHUTDOWN):
                    if why[0] != 109:
                        self.logger.error( "get error when read info from pipe %s, pipe id:%d, reason:%s"%(name, which.pid, str(why)) )
                    return '', str(why[-1])
                return '', str(why[-1])
            return read, "sucess"
    else:
        def _close(self, which):
            which.close()
            setattr(which, None)
        def __recv(self, which, name, maxsize = 1024):
            data = ''
            err_info = 'sucess'
            conn = getattr(which, name)
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
                error_info =  'get error when read info from pipe %s, pipe id:%s, reason:catpture exception %s'%(name, which.pid, str(e))
            except:
                error_info =  'get error when read info from pipe %s, pipe id:%s, reason:catpture unknown exception'%(name, which.pid)
            finally:
                if not conn.closed:
                    fcntl.fcntl(conn, fcntl.F_SETFL, flags)
            return data, err_info
    #used to write data into pipe
    #return "written data"
    """
    def __send(self, which, name, input):
        if DEBUG == True:
            self.logger.info("read stdout and stderr from pid:%d"%pipe.pid)
        
        stdout_data, ret_stdout = self.__recv(pipe, "stdout", maxsize)
        stderr_data, ret_stderr = self.__recv(pipe, "stderr", maxsize)
        if ret_stdout == "The pipe has been ended." or ret_stderr == "The pipe has been ended.":
            return stdout_data, stderr_data, False
        
        if DEBUG == True:
            if ret_stdout != "sucess":
                self.logger.error(ret_stdout)
            elif ret_stderr != "sucess":
                self.logger.error(ret_stderr)
        return stdout_data, stderr_data, True    #used to call subprocess popen
    """
    #subprocess for kill/conn
    def __subprocess_blocked(self, cmd, timeout = 10):
        fg_timeout = True
        std_out = ''
        std_err = ''
        self.logger.info('try to %s'%cmd)
        try:
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time_start = time.time()
            while (process.returncode == None and time.time() - time_start < timeout):
                #polling process status
                process.poll()
                time.sleep(0.01)  
                std_out_tmp, std_err_tmp, res = self.read_pipe(process)
                std_out += std_out_tmp
                std_err += std_err_tmp
            #if process not end, kill it
            if (process.returncode == None):
                self.logger.info('Call __subprocess_blocked method timeout; pid:%d'%process.pid)
                process.poll()
                process.kill()
                process.wait()
            else:
                fg_timeout = False
            std_out_tmp, std_err_tmp, res = self.read_pipe(process)
            std_out += std_out_tmp
            std_err += std_err_tmp

            if fg_timeout:
                self.__kill_task_byID(str(process.pid))
            del process
        except Exception, e:
            self.logger.error("get exception:%s in __subprocess_blocked(%s)"%(str(e), str(cmd)))
        except:
            self.logger.error("get unknown exception in __subprocess_blocked(%s)"%(str(cmd)))
        return fg_timeout, std_out, std_err
        
    def __subprocess_unblocked(self, cmd):
        process = None
        try:
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)                
        except Exception, e:
            self.logger.error("get exception:%s in __subprocess_unblocked(%s)"%(str(e), str(cmd)))
        except:
            self.logger.error("get unknown exception in __subprocess_unblocked(%s)"%(str(cmd)))
        return process
    
    def __subprocess_blocked_specialBG(self, ip, cmd, timeout = 10):
        fg_timeout = True
        std_out = ''
        std_err = ''

        try:
            process = subprocess.Popen('%s -s %s:5555 shell'%(self.__adb, ip), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #create task thread
            process.stdin.write(cmd+"\n")
            time.sleep(1)
            process.stdin.write("exit\n")
            process.stdin.close()
            time_start = time.time()
            while (process.returncode == None and time.time() - time_start < timeout):
                #polling process status
                process.poll()
                time.sleep(0.01)  
            #if process not end, kill it
            if (process.returncode == None):
                self.logger.info('Call __subprocess_blocked method timeout; pid:%d'%process.pid)
                process.poll()
                process.kill()
                process.wait()
            else:
                fg_timeout = False
            std_out, std_err, res = self.read_pipe(process)
            del process
        except Exception, e:
            self.logger.error("get exception:%s in __subprocess_blocked(%s)"%(str(e), str(cmd)))
        except:
            self.logger.error("get unknown exception in __subprocess_blocked(%s)"%(str(cmd)))
        return fg_timeout, std_out, std_err

    if subprocess.mswindows:    
        def __get_adb_pid(self):
            cmd = "tasklist /FI \"IMAGENAME eq adb.exe\""
            if DEBUG:
                self.logger.info('in __get_adb_pid function; \r\ncmd:%s'%cmd)
            ret = False;res_reason = '';res_out = '';res_err = '';pid_list = []
            fg_timeout, res_out, res_err = self.__subprocess_blocked(cmd, 20)
        
            if fg_timeout == False and len(res_err) == 0:
                ret = True
                lines = res_out.split("\r\n")
                res_reason = res_out
                for line in lines:
                    if line.find("adb.exe") > -1: 
                        #pid = line[(line.find("adb.exe")+ len("adb.exe")) : line.find("Console")].strip()
                        pattern_str = 'adb.exe\s+\d{1,6}\s+'
                        pid = re.compile(pattern_str).search(line).group()[7:].strip()
                        pid_list.append(pid)
            if DEBUG:
                self.logger.info('out __get_adb_pid function; \r\ncmd:%s \r\nresult:%s \r\ndescription:%s'%(cmd, ret, res_reason))
            return ret, res_reason, res_out, res_err, pid_list
    else:
        def __get_adb_pid(self):
            ret = False;res_reason = '';res_out = '';res_err = '';pid_list = []
            fg_timeout, res_out, res_err = self.__subprocess_blocked('pidof adb', 20)
            if fg_timeout == False and len(res_err) == 0:
                ret = True
                lines = res_out.strip().split(" ")
                res_reason = res_out
                for pid in lines:
                    pid_list.append(pid)
            return ret, res_reason, res_out, res_err, pid_list


    
    
    #record the process and pid of the child-porcess(adb)
    def __subprocess_blocked_adb(self, ip, cmd, timeout):
        fg_timeout = True;stdout = '';stderr = ''
        self.adb_lock.acquire()
        try:
            pid_list_prv = self.__get_adb_pid()
            fg_timeout, stdout, stderr = self.__subprocess_blocked(cmd, timeout) 
            pid_list_now = self.__get_adb_pid()
            diff_list = b3 = [val for val in pid_list_now[-1] if val not in pid_list_prv[-1]]
            if fg_timeout and len(diff_list) > 0:
                self.logger.info("Pid list:%s before run :%s"%(str(pid_list_prv), cmd))
                self.logger.info("Pid list:%s after run :%s"%(str(pid_list_now), cmd))
                for temp in diff_list:
                    self.__kill_task_byID(str(temp))
        except Exception, e:
            self.logger.error("get exception:%s in __subprocess_blocked_adb(%s)"%(str(e), str(cmd)))
        except:
            self.logger.error("get unknown exception in __subprocess_blocked_adb(%s)"%(str(cmd)))
        self.adb_lock.release()
        return fg_timeout, stdout, stderr
    
    
    #record the process and pid of the child-porcess(adb)
    def __subprocess_unblocked_adb(self, ip, cmd):
        process = None
        diff_list = []
        self.adb_lock.acquire()
        try:
            pid_list_prv = self.__get_adb_pid()
            process = self.__subprocess_unblocked(cmd)
            time.sleep(1)
            pid_list_now = self.__get_adb_pid()
            diff_list = b3 = [val for val in pid_list_now[-1] if val not in pid_list_prv[-1]]
            #if len(diff_list) > 0:
            self.__process_buf.append([ip, process, diff_list, cmd])
        except Exception, e:
            self.logger.error("get exception:%s in __subprocess_unblocked_adb(%s)"%(str(e), str(cmd)))
        except:
            self.logger.error("get unknown exception in __subprocess_unblocked_adb(%s)"%(str(cmd)))
        self.adb_lock.release()
        return process, diff_list


    #return path of adb.exe/adb
    def get_adb(self):
        return self.__adb
    #return data of stdout stderr from subprocess
    #return "stdout_data", "stderr_data", "True/False, pipe open or close"
    def read_pipe(self, pipe, maxsize = 1024*1024):
        if DEBUG == True:
            self.logger.info("read stdout and stderr from pid:%d"%pipe.pid)            
        
        stdout_data, ret_stdout = self.__recv(pipe, "stdout", maxsize)
        stderr_data, ret_stderr = self.__recv(pipe, "stderr", maxsize)
        if ret_stdout == "The pipe has been ended." or ret_stderr == "The pipe has been ended.":
            return stdout_data, stderr_data, False
        
        if DEBUG == True:
            if ret_stdout != "sucess":
                self.logger.error(ret_stdout)
            elif ret_stderr != "sucess":
                self.logger.error(ret_stderr)
        return stdout_data, stderr_data, True
    
    """
    #send data into stdin of the subprocess
    def send(self, process, cmds):
        self.process.poll()
        res = self.__send(self.process, "stdin", cmds)
    """
    #recv data from stdout or stderr of the subprocess
    def recv(self, process, name, maxlen = 1024*16):
        res_out = ""
        while True:
            process.poll()
            data, ret = self.__recv(process, name)
            data = data.strip()
            if data == '':
                return data
            res_out += data
            if maxlen != None and len(res_out) >= maxlen:
                break
        return res_out

    #when subprocess closed, the child-process(adb) could not be auto-closed in Unix since the close_fds could not be set ture
    #If close_fds is true, all file descriptors except 0, 1 and 2 will be closed before the child process is executed. (Unix only). Or, on Windows, if close_fds is true then no handles will be inherited by the child process. Note that on Windows, you cannot set close_fds to true and also redirect the standard handles by setting stdin, stdout or stderr.
    def update_adbbg(self, ip):
        self.adb_lock.acquire()
        try:
            self.logger.info("in update_adbbg %s"%str(self.__process_buf))        
            while True:
                for process_attr in self.__process_buf:
                    if process_attr[0] != ip:
                        continue
                    process_attr[1].poll()
                    self.logger.info("%s\r\nadb proess: %s should exit"%(str(process_attr), str(process_attr[1])))
                    for temp in process_attr[2]:
                        self.logger.info("taskkill /F /PID %s"%str(temp))
                        self.__kill_task_byID(str(temp))
                    self.__kill_task_byID(str(process_attr[1].pid))
                    self.__process_buf.remove(process_attr)
                    break
                else:
                    break
        except Exception, e:
            self.logger.error("get exception:%s in update_adbbg(%s)"%(str(e), str(ip)))
        except:
            self.logger.error("get unknown exception in update_adbbg(%s)"%(str(ip)))
        self.adb_lock.release()
        
    def __get_cmds(self, ip, method, param):
        if method == "connect" or method == "disconnect":
            cmd = "%s %s %s:5555"%(self.__adb, method, ip)
        elif method == "devices" or method == "kill_server" or method == "start_server":
            cmd = "%s %s"%(self.__adb, method.replace("_", "-"))
        elif method == "root":
            if ip == "usb":
                cmd = "%s -d %s"%(self.__adb, method)
            else:
                cmd = "%s -s %s:5555 %s"%(self.__adb, ip, method)
            param = ""
        elif method == 'shell_specialBG':
            cmd = param
        elif param != None:
            cmd = "%s -s %s:5555 %s %s"%(self.__adb, ip, method, param)
        else:
            cmd = "%s -s %s:5555 %s"%(self.__adb, ip, method)
            
        if ip == 'usb':
            if method == 'shell' or method == 'pull' or method == 'push' or method == 'logcat' or method == 'forward' or method == 'root':
                cmd = "%s -d  %s %s"%(self.__adb, method, param)
            else:
                self.logger.error("currently only support adb -d shell/pull/push/logcat/forward/root cmds; your cmd:%s"%method)
                return False, "currently only support adb -d shell/pull/push/logcat/forward/root cmds; your cmd:%"%method
        return True, cmd
            

    #run some cmds about adb; unblocked; return the subprocess if sucess
    #e.g. adb -s 192.168.1.1:5555 logcat -v time;
    #the subprocess of cmds and adb maynot auto-destroy, that means you need: 1. store the pid of cmds and adb; 2. clean up them when they were closed.
    #should return the subprocess
    def cmds_unblocked(self, ip, method, param=None):       
        if ip != None and ip != "usb" and self.fg_device_online(ip) == False and method != "root":
            self.reconnect(ip)
            
        res, cmd = self.__get_cmds(ip, method, param)
        if res == False:
            return False, cmd, None, ['-1']
            
            
        self.logger.info('cmd:%s'%(cmd))
        res_reason = ''
        ret = False
        try:
            process, subp_pid = self.__subprocess_unblocked_adb(ip, cmd)
            self.logger.info("pid : %d ; subprocess id: %s"%(process.pid, str(subp_pid)))
            ret = True
        except Exception, e:
            res_reason = 'Exception (%s) captured in cmds_unblocked in mrvl_adb.py;'%str(e)
        except:
            res_reason = 'Unkown error captured in cmds_unblocked in mrvl_adb.py;'
        if len(res_reason) > 1024:
            res_reason_print = res_reason[:1023]
        else:
            res_reason_print = res_reason
        self.logger.info('cmd:%s \r\nresult:%s \r\ndescription:%s'%(cmd, ret, res_reason_print))
        if ret == False and res_reason.find("error: device not found") > -1:
            #device offline
            self.logger.error("try to offline :%s"%ip)
            #self.kill_server()
            self.__set_offline(ip)
        else:
            self.__set_online(ip)
        return ret, res_reason, process, subp_pid
    
    #run some cmds about adb; blocked untill timeout or subprocess terminated
    #e.g. adb -s 192.168.1.1 shell ls -la; adb -s 192.168.1.1 shell date;
    #the subprocess of cmds and adb maynot auto-destroy, that means you need: 1. store the pid of cmds and adb; 2. clean up them when they were closed.
    #should return succeed or failed
    def cmds_blocked(self, ip, method, param=None, timeout = 10, fg_specialBG=False):
        if ip != None and self.fg_device_online(ip) == False and method != "root":
            self.reconnect(ip)

        fg_timeout = False
        if method == None:
            self.logger.info('adb.cmds_blocked can not be called directly;')
            return False, 'adb.cmds_blocked can not be called directly', "", ""
        if timeout == None:
            self.logger.info('adb.cmds_blocked should have timeout')
            return False, "timeout should not be None", "", ""
        
        res, cmd = self.__get_cmds(ip, method, param)
        if res == False:
            return False, cmd, "", ""

        self.logger.info('in cmds_blocked function; \r\ncmd:%s \r\ntimeout:%s'%(cmd, str(timeout)))
        res_reason = ''
        ret = False
        res_out = ""
        res_err = ""
        process = None
        try:
            if not fg_specialBG:
                fg_timeout, res_out, res_err = self.__subprocess_blocked_adb(ip, cmd, timeout)
            else:
                fg_timeout, res_out, res_err = self.__subprocess_blocked_specialBG(ip, cmd, timeout)
                
            if fg_timeout == True:
                res_reason = "Call '%s' timeout, could not return in %d seconds;\r\nstdout:%s\r\nstderr:%s\r\n"%(cmd, timeout, res_out, res_err)
            elif method == "pull" or method == "push":
                res_reason = res_err
                if res_err.find("bytes in") > -1 or res_err.find("0 files skipped.") > -1:
                    ret = True
                else:
                    ret = False
            elif len(res_err) > 0 and (method != "connect" and method != "disconnect" and method != "devices"):                
                res_reason = "Call '%s'; get error data from stderr;\r\nstdout:%s;\r\nstderr:%s\r\n"%(cmd, res_out, res_err)
            elif method == "connect" or method == "disconnect" or method == "devices":
                res_reason = res_out
                ret = True
            else:
                #pass
                res_reason = res_out
                ret = True
            
        except Exception, e:
            res_reason = 'Exception (%s) captured in cmds_blocked in adb_api_init.py;'%str(e)
        except:
            res_reason = 'Unkown error captured in cmds_blocked in adb_api_init.py;'
        if len(res_reason) > 1024:
            res_reason_print = res_reason[:1023]
        else:
            res_reason_print = res_reason
        self.logger.info('out cmds_blocked function; \r\ncmd:%s; \r\nresult:%s \r\ndescription:%s'%(cmd, ret, res_reason_print))
        if ret == False and res_err.find("ADB server didn't ACK") > -1:
            #device offline
            self.logger.error("ADB server didn't ACK;taskkill /F /IM adb.exe;vsjitdebugger.exe;dwwin.exe and try to offline :%s"%ip)
            self.kill_server()
            self.__set_offline(ip)
        elif ret == False and (res_err.find("error: device") > -1 or res_err.find("cannot connect") > -1 or res_err.find('protocol fault') > -1 ):
            #device offline
            self.logger.error("try to offline :%s"%ip)
            #self.kill_server()
            self.__set_offline(ip)
        elif ret == True and (res_out.find("No such device ") > -1 or res_out.find("unable to connect") > -1):
            ret = False
            ret_reason = res_out
        elif ret == False and fg_timeout == True:
            #device offline
            self.logger.error("try to offline :%s"%ip)
            #self.kill_server()
            self.__set_offline(ip)            
        elif self.fg_device_online(ip) == False:
            self.__set_online(ip)
        
        return ret, res_reason, res_out, res_err
    

    #similar with cmds_unblocked; special cmds: logcat 
    def logcat(self, ip, redirection=None):
        try:
            if self.logcat_process != None:
                    
                if (self.logcat_process.returncode == None):
                    self.logger.info('retry to close logcat-process')
                    self.logcat_process.poll()
                    self.logcat_process.kill()
                    self.logcat_process.wait()
                    self.update_adbbg(ip)
        except Exception, e:
            self.logger.error("try to close logcat process get an exception:%s"%str(e))
        except:
            self.logger.error("try to close logcat process get an unknown exception")
        if redirection == None:
            cmds = " -v threadtime"
        else:
            cmds = " -v threadtime > %s"%(redirection)
        ret = self.cmds_unblocked(ip, sys._getframe().f_code.co_name, cmds)
        if ret[0]:
            self.logcat_process = ret[2]
        return ret
    #similar with cmds_blocked; special cmds: bugreport
    def bugreport(self, ip, redirection):
        cmds = " > %s"%(redirection)
        ret = self.cmds_blocked(ip, sys._getframe().f_code.co_name, cmds, 150)
        return ret
    
    #use adb push file; if timeout=None, blocked untill push finished
    #call cmds_blocked; return succeed or failed
    def push(self, ip, srcfile, dstfile, timeout=60):
        return self.cmds_blocked(ip, sys._getframe().f_code.co_name, "%s %s"%(srcfile, dstfile), timeout)
    #use adb pull file; if timeout=None, blocked untill pull finished
    #call cmds_blocked; return succeed or failed
    def pull(self, ip, srcfile, dstfile, timeout=2):
        return self.cmds_blocked(ip, sys._getframe().f_code.co_name, "%s %s"%(srcfile, dstfile), timeout)    
    #adb connect ip:5555
    #call cmds_blocked; return succeed or failed    
    def connect(self, ip, timeout=15):
        self.cmds_blocked(ip, sys._getframe().f_code.co_name, None, timeout)
        self.root(ip)
        return self.cmds_blocked(ip, sys._getframe().f_code.co_name, None, timeout)
    #adb disconnect ip:5555
    #call cmds_blocked; return succeed or failed
    def disconnect(self, ip, timeout=15):
        return self.cmds_blocked(ip, sys._getframe().f_code.co_name, None, timeout)
    
    #adb reboot ip:5555
    #call cmds_blocked; return succeed or failed
    def reboot(self, ip, timeout=15):
        return self.cmds_blocked(ip, sys._getframe().f_code.co_name, None, 5)
    #adb devices    
    #call cmds_blocked; return succeed or failed
    def devices(self):
        return self.cmds_blocked(None, sys._getframe().f_code.co_name, None, timeout=15)
    #adb root; - restarts the adbd daemon with root permissions
    #call cmds_blocked; return succeed or failed
    def root(self, ip):
        return self.cmds_blocked(ip, sys._getframe().f_code.co_name, None, timeout=15)

    #call shell date to update devices
    #call devices to check wether the device connected
    def fg_connectted(self, ip):
        self.shell(ip, "date", timeout=2)
        ret = self.devices()
        if ret[0] == True:
            if ret[1].find("%s:5555"%ip) > -1:
                return True
        return False
    
    #
    def reconnect(self, ip):
        self.update_adbbg(ip)
        if ip != "usb":
            #fg_timeout, std_out, std_err = self.__subprocess_blocked("%s disconnect %s:5555"%(self.__adb, ip), 1)
            self.logger.info ("try to online :%s; %s connect %s:5555"%(ip, self.__adb, ip))
            fg_timeout, std_out, std_err = self.__subprocess_blocked("%s connect %s:5555"%(self.__adb, ip), 1)
        else:
            self.logger.info ("try to online adb(by '%s devices')"%self.__adb)
            fg_timeout, std_out, std_err = self.__subprocess_blocked("%s devices"%(self.__adb), 1)
        if fg_timeout == True or len(std_err) > 0:
            return False
        
        self.root(ip)
        if ip != "usb":
            #fg_timeout, std_out, std_err = self.__subprocess_blocked("%s disconnect %s:5555"%(self.__adb, ip), 1)
            fg_timeout, std_out, std_err = self.__subprocess_blocked("%s connect %s:5555"%(self.__adb, ip), 1)
        else:
            fg_timeout, std_out, std_err = self.__subprocess_blocked("%s devices"%(self.__adb), 1)

        self.__set_online(ip)
        return True
        
    #adb -s ip:5555 shell cmd
    #call cmds_blocked; return succeed or failed
    def shell(self, ip, cmd, timeout=2, retry_cnt=1):
        for _ in range(retry_cnt):
            ret = self.cmds_blocked(ip, sys._getframe().f_code.co_name, cmd, timeout)
            if ret[0]:
                break
        return ret
    def forward(self, ip, cmd, timeout=2):
        return self.cmds_blocked(ip, sys._getframe().f_code.co_name, cmd, timeout)
    def shell_specialBG(self, ip, cmd, timeout=2):
        return self.cmds_blocked(ip, sys._getframe().f_code.co_name, cmd, timeout, True)
    
        
        
    def chk_pingable(self, ip, timeout=3):
        if subprocess.mswindows:
            cmds = "ping -n 1 %s"%ip
        else:
            cmds = "ping -c 1000 %s"%ip
        fg_timeout, std_out, std_err = self.__subprocess_blocked(cmds, timeout)
        if std_out.find('Request timed out') == -1 and (std_out.find('0% packet loss') > -1 or std_out.find("0% loss") > -1):
            return True, std_out, std_err
        return False, std_out, std_err

    def popen(self, cmd):
        return self.__subprocess_unblocked(cmd)
    
    def sendevent(self, ip, cmd):
        self.logger.info ("try to sendevent :%s"%(cmd))
        return self.shell(ip, cmd)
        #fg_timeout, std_out, std_err = self.__subprocess_blocked("%s shell %s:5555 %s"%(self.__adb, ip, cmds))
        #if fg_timeout == True or len(std_err) > 0:
        #    self.logger.info("try to sendevent :%s failed\r\nstdout:%s\r\nstderr:%s\r\nfg_timeout:%s"%(cmds, std_out, std_err, str(fg_timeout)))
        #    return False
        
        #    self.logger.info("try to sendevent :%s succeed\r\nstdout:%s\r\nstderr:%s\r\nfg_timeout:%s"%(cmds, std_out, std_err, str(fg_timeout)))
        #return True
    
    
    
    

    def file_exist(self, ip, file_name):
        res = self.shell(ip, 'ls -la '+file_name)
        if res[0] == True and res[1].find('No such')== -1:
            return True,''
        else:
            return False,res[1]

    def file_remove(self, ip, file_name):
        for _ in range(10):
            res = self.shell(ip, 'rm -rf '+file_name, 10)
            if res[1].find('Read-only')== -1:
                return True,''
        else:
                return False,res[1]
    
    def get_anr(self, ip, dst_fold, fg_del_afterget=True):
        res = self.__get_anr(dst_fold, ip)
        if fg_del_afterget == True:
            self.file_remove(ip, '/data/anr/*')
            self.file_remove(ip, '/data/anr')
        return res

    def __get_anr(self, dst_fold, ip):
        self.file_remove(ip, '/data/anr/traces.txt.bugreport')
        res = self.file_exist(ip, '/data/anr/*')
        if res[0] == False:
            self.logger.info("Get anr folder fail for  %s"%res[1])
            return False,res[1]
        #time_tag = int(time.time())
        time_tag = time.strftime('%Y_%m_%d_%H_%M_%S_', time.localtime(time.time()))
        anr_filename = "%sanr"%time_tag
        
        self.logger.info("save anr file folder as %s"%anr_filename)
        self.pull(ip, '/data/anr', "%s/%s"%(dst_fold, anr_filename), 5)
        self.logger.info("get anr files and saved in %s"%anr_filename)
        return True, anr_filename
    
    
