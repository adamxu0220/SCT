#!/usr/bin/python
import threading
import time
import sys
import serial
import string
import re
import types
import platform

class ComThread:
    def __init__(self, logger, serial_port):
        self.main_lock = threading.Lock()        
        self.trace_lock = threading.Lock()
        self.buff_lock = threading.Lock()
        self.l_serial = None
        self.alive = False
        self.port = serial_port
        self.logger = logger
        self.trace_list = []
        self.serial_cmd_queue = []
        self.buff_data = ''
        
    def __del__(self):
        del self.main_lock
        del self.trace_lock
        del self.buff_lock

    def add_buff(self, data):
        self.buff_lock.acquire()
        self.buff_data += data
        self.buff_lock.release()
    def clear_buff(self):
        self.buff_lock.acquire()
        self.buff_data = ''
        self.buff_lock.release()
    def get_and_clear_buff(self):
        self.buff_lock.acquire()
        data = self.buff_data
        self.buff_data = ''
        self.buff_lock.release()
        return data


    def chg_logger(self, logger):
        self.main_lock.acquire()
        self.logger = logger
        self.main_lock.release()
        
        
    def add_logger(self, logname, logger, buff_size=1024*1024):
        logname = "%s%s"%(logname, str(time.time()))
        self.trace_lock.acquire()
        self.trace_list.append([logname, logger, "", buff_size])
        self.trace_lock.release()
        return logname
        
    def get_logger_buff(self, logname):
        self.trace_lock.acquire()
        for _ in self.trace_list:
            if _[0] == logname:
                self.trace_lock.release()
                return _[2]
        else:
            self.trace_lock.release()
            return ""
    
    def del_logger(self, logname):
        self.trace_lock.acquire()
        for _ in self.trace_list:
            if _[0] == logname:                
                break
        else:
            self.trace_lock.release()
            return
        self.trace_list.remove(_)
        self.trace_lock.release()

    def su(self):
        ret = self.get_keywords([re.compile("(uid=\d{1,5}\(root\) gid=\d{1,5}\(root\))")], 2, False, ["id", 1])
        print ret
        if not ret[0]:
            print "write su"
            self.write("su")
            time.sleep(1)

        
    
    #keywords   -- define a keywod list
    #AndOr      -- True: find all of the keywords
    #           -- False: find any of the keywords
    #return value:  ret[0] got or not
    #               ret[1] return the keyword it found when AndOr == False; Otherwise return ""
    #WriteCmd:  define the write cammond and the sleep time when repeate write
    def get_keywords(self, keywords, timeout, AndOr = False, WriteCmd = None, Repeat_cmd = True):
        time_start = time.time()
        logger_name = self.add_logger("temp", None)
        keywords_found = []
        while time.time() - time_start < timeout:
            if WriteCmd != None:
                #self.write('\x03')
                #time.sleep(1)
                self.write(WriteCmd[0])
                time.sleep(WriteCmd[1])
                if not Repeat_cmd:
                    WriteCmd = None
            data = self.get_logger_buff(logger_name)
            data_raw = data
            while data.find("\r") > -1:
                data = data.replace("\r", "")
            while data.find("\n") > -1:
                data = data.replace("\n", "")
            keywords_found = []
            if AndOr == True:                
                for keyword in keywords:
                    if type(keyword) == types.StringType:
                        if data.find(keyword) == -1:
                            break
                        else:
                            keywords_found.append(keyword)
                    else:
                        if keyword.search(data) == None:
                            break
                        else:
                            keywords_found.append(keyword.search(data).group())
                else:
                    self.del_logger(logger_name)
                    return True, keywords_found, data_raw
                #return False, keywords_found, data_raw
            else:
                for keyword in keywords:
                    if type(keyword) == types.StringType:
                        if data.find(keyword) > -1:
                            self.del_logger(logger_name)
                            return True, keyword, data_raw
                    elif keyword.search(data) != None:
                        return True, keyword.search(data).group(), data_raw
            time.sleep(1)
        else:
            self.del_logger(logger_name)
            return False, keywords_found, data_raw
        
    #get ip    
    def get_ip(self, timeout=30, ip=["10.","192."]):
        #self.write("su")
        #time.sleep(1)
        pattern_list = []
        for _ in ip:
            dot_count = _.count('.')
            pattern_str = _.replace('.', '\.')
            if _.endswith('.'):
                pattern_str = '%s\d{1,3}'%(pattern_str)
            while dot_count < 3:
                pattern_str = '%s\.\d{1,3}'%pattern_str
                dot_count += 1
            pattern_list.append(re.compile(pattern_str))    
        
        res = self.get_keywords(pattern_list, timeout, AndOr=False, WriteCmd = ["ifconfig eth0;ifconfig mlan0;netcfg", 2])
        if res[0] == True:
            return True, res[1]
        else:
            return False, "Do not get the ip address"

    def get_ESSID(self, timeout=10):
        #self.write("su")
        #time.sleep(1)
        
        res = self.get_keywords(["ESSID"], timeout, AndOr=False, WriteCmd = ["iwconfig wlan0", 2])
        if res[0] == True:
            pos1 = res[2].find("ESSID")
            pos2 = res[2].find("\"", pos1)+1
            pos3 = res[2].find("\"", pos2)
            if pos1> -1 and pos2 > pos1 and pos3 > pos2:
                ESSID = res[2][pos2:pos3]
                ESSID = ESSID.strip()
                return True, ESSID
        
        return False, "Do not get the ESSID"
    
    def __get_event_id(self, data):
        pos1 = 0
        event_id_list = []
        while True:
            pos1 = data.find('/dev/input/event', pos1)
            pos2 = data.find(' ', pos1)
            if pos1 > -1 and pos2 > pos1:
                event_id_list.append(data[pos1:pos2].strip())
                pos1 = pos2                
            else:
                break
        return event_id_list
    def __get_event_name(self, data):
        pos1 = 0
        event_name_list = []
        while True:
            pos1 = data.find('name:', pos1)
            if pos1 > -1:
                pos1 = data.find('"', pos1) + 1
                pos2 = data.find('"', pos1)                
                if pos1 > -1 and pos2 > pos1:
                    event_name_list.append(data[pos1:pos2].strip())
                    pos1 = pos2
                else:
                    break
            else:
                break
        return event_name_list
    
    
    def __get_event_key0001(self, data):
        pos1 = 0
        event_name_list = []
        while True:
            pos1 = data.find('KEY (0001):', pos1) + len('KEY (0001):')
            pos2 = data.find(':', pos1)
            if pos1 > len('KEY (0001):') and pos2 > pos1:
                data_buf = data[pos1:pos2].strip()
                data_buf = data_buf.replace('  ', ' ')
                event_name_list.append(data_buf.split(' '))
                pos1 = pos2
            else:
                break
        return event_name_list
    
    def get_devices(self, timeout=10):
        res = self.get_keywords(["@android:"], timeout, AndOr=False, WriteCmd = ["getevent -p", timeout])
        if res[0] == True:
            return True, [self.__get_event_id(res[2]), self.__get_event_name(res[2]), self.__get_event_key0001(res[2])], res[2]
        
        return False, [None, None, None], "Do not get any device"
    
    def get_special_devices(self, device_name_found = 'Logitech Unifying Device', min_events = 100):
        res, [device_list, device_name_list, device_key0001_list], res_reason = self.get_devices()
        if res == True:
            for _ in range(len(device_list)):
                device = device_list[_]
                device_name = device_name_list[_]
                device_key0001 = device_key0001_list[_]
                print device
                print device_name
                if device_name.find(device_name_found) > -1:
                    if len(device_key0001) > min_events:
                        return True, device
        return False, ""
        
        
        
    def FirstReader(self):
        try:
            data = ""
            data_temp = ""
            while True:
                self.main_lock.acquire()
                if self.alive == False:
                    self.main_lock.release()
                    break
                self.main_lock.release()  
                #time.sleep(0.1)
                try:
                    n = self.l_serial.inWaiting()
                    if n:
                        data = data_temp + self.l_serial.read(n)
                        data = data.replace('\r','').replace("[35;1m", "").replace("[0m", "").replace("[0;32m", "").replace("[0;35m", "").replace("[0;39m", "")
                        
                        #data = data.replace('\n', "[%s]\n"%str(time.time()))
                        if data.count('\n') > 0:
                            pos = data.rfind('\n')
                            data_temp = data[pos+1:]
                            data = data[:pos]
                            #time_str = str(time.time())
                            #data = "[%s]%s"%(time_str, data)
                            #data = data.replace('\n', "\n[%s]"%str(time.time()))
                        else:
                            data_temp = data
                            time.sleep(0.01)
                            continue
                        
                        self.main_lock.acquire()
                        self.logger.info(data)
                        self.main_lock.release()
                        self.add_buff(data)
                        self.trace_lock.acquire()
                        for _ in self.trace_list:
                            if _[1] != None:
                                time_str = "%.2f"%(time.time())
                                _[1].info("[%s]%s"%(time_str, data.replace('\n', '\n[%s]'%time_str)))
                                #_[1].info(data)
                            if _[3] > 0:
                                length = len(_[2]) + len(data)
                                if length > _[3]:
                                    _[2] = _[2][(length - _[3]):] + data
                                else:
                                    _[2] += data
                        self.trace_lock.release()
                            
                    
                    time.sleep(0.01)
                        
                    if True:
                        self.main_lock.acquire()
                        if len(self.serial_cmd_queue) > 0:
                            cmd = self.serial_cmd_queue.pop()
                            self.logger.info( "!!!!!!!write command:%s"%cmd)
                            if type(cmd) == type(""):
                                self.l_serial.write(cmd+'\n')
                            elif type(cmd) == type([]):
                                for cmd_tmp in cmd:
                                    self.l_serial.write(cmd_tmp)
                            #self.l_serial.write(cmd+'\n')
                        self.main_lock.release()
                except Exception, ex:
                    #import traceback
                    #traceback.print_exc()
                    self.logger.error('Serial port read error! The error msg is :\r\n' + str(ex))
                except:
                    self.logger.error('Serial port get and unknow error!')
        except Exception,e:
            self.logger.error('FirstReader thread captured an exception:%s'%str(e))
        self.alive = False

    def set_serialport(self, port):
        self.port = port

    def start(self):
        #user prompt
        if platform.system() == 'Windows':
            print 'Auto-run is started on port [%d]'%(self.port)
        else:
            print 'Auto-run is started on port [%s]'%(self.port)
        #configure serial port
        self.l_serial = serial.Serial()
        if platform.system() == 'Windows':
            self.l_serial.port = int(self.port)-1
        else:
            self.l_serial.port = int(self.port)-1
        self.l_serial.baudrate = 115200
        self.l_serial.timeout = None
        self.l_serial.bytesize = serial.EIGHTBITS
        self.l_serial.parity = serial.PARITY_NONE
        self.l_serial.stopbits = serial.STOPBITS_ONE
        self.l_serial.xonxoff = 0
        try:
            self.l_serial.open()
        except:
            print "open serial get exception"
        self.thread_read = None
        if self.l_serial.isOpen():
            self.waitEnd = threading.Event()
            self.alive = True
            self.thread_read = None
            self.thread_read = threading.Thread(target=self.FirstReader)
            self.thread_read.setName("FIRST_READER")
            self.thread_read.setDaemon(True)
            self.thread_read.start()
            return True
        else:
            return False
        
    def write(self, cmds):
        self.main_lock.acquire()
        self.serial_cmd_queue.insert(0,cmds)
        self.main_lock.release()

    def stop(self):
        if self.alive:
            self.alive = False
            self.thread_read.join()
        #end thread read
        if self.thread_read != None:
            del self.thread_read
        #close serial port
        try:
            if self.l_serial.isOpen():
                self.l_serial.close()
        except Exception,e:
            self.logger.error('Captured an exception when try to close serial port:%s'%str(e))
        except:
            self.logger.error('Captured an exception when try to close serial port,Unknow error!')



