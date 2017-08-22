#!/usr/bin/env python  
#coding=utf-8  
import time
import sys,os
import threading
import subprocess
import select
import traceback
#this threading used to monitor those online-client
#HB == check status 
class Server_Monitor(threading.Thread):
    def get_client_status(self, pc_name):
        ret, feedback = self.send_cmd(pc_name, 'chk_status')
        if ret:
            return ret, feedback.split(";")[0], feedback.split(";")[1]
        else:
            return ret, None, None
        
    def update_client(self, pc_name):
       
        if self.pc_info[pc_name]['status'] == 'idle':
            return
               
        ret, status = self.CaseDispatcher.fg_case_running(pc_name)      
        print '##get status :%s'%status
        
        if status == "idle" and self.pc_info[pc_name]['status'] == 'running':
            #update test result
            ret_gettestres, test_result = self.CaseDispatcher.get_test_result(pc_name)
            if ret_gettestres:
                self.__update_teststatus_in_db(pc_name,test_result)
        else:
            self.__update_teststatus_in_db(pc_name,status)
        if not ret:
            #platform lost connect; end the case
            self.main_logger.trace('platform(%s) lost connect; case:%s will be stopped'%(self.pc_info[pc_name]['ip'], self.pc_info[pc_name]['running_case']))
            self.offline_pc(pc_name, 'DUT controller lost connection')
            return
        if self.pc_info[pc_name]['running_case'].find('CTS') != -1:
            if status.find('Passed') != -1 or status.find('Failed') != -1:
                self.main_logger.trace('case:%s is end'%self.pc_info[pc_name]['running_case'])
                self.offline_pc(pc_name, status)
                time.sleep(60)
        else:   
            if status.find('running') == -1 and status.find('stopping') == -1 and status.find('loading') == -1 and self.pc_info[pc_name]['status'] == 'running':
        ##            status = self.CaseDispatcher.run_case_getlog(pc_name, self.pc_info[pc_name]['test_dirname'])
                self.main_logger.trace('case:%s is end'%self.pc_info[pc_name]['running_case'])
                self.offline_pc(pc_name, status)
                time.sleep(60)
    
    def __init__(self, lock, mysql_hdlr, adb_hdlr, logger, pc_info, unknown_pc_info, case_info, send_cmd, CaseDispatcher, update_cfg):  
        super(Server_Monitor, self).__init__()
        self.mysql_hdlr = mysql_hdlr
        self.adb_hdlr = adb_hdlr
        self.main_logger = logger
        self.pc_info = pc_info
        self.unknown_pc_info = unknown_pc_info
        self.case_info = case_info
        self.send_cmd = send_cmd
        self.CaseDispatcher = CaseDispatcher
##        self.hdlr_monitor_conn = threading.Thread(target = self.func_monitor_conn)
##        self.hdlr_monitor_conn.start()
        self.update_cfg = update_cfg
##        self.valid_status = ['running','timeout','pass','get_anr and get_tombstones','get_anr','get_tombstones','DUT lost connection']
        self.lock = lock

        self.BUFSIZE = 1024
        self.__end_str = '<<EOF'
        
    def __offline_pc(self, pc_name, status):
        if status != None:
            self.__update_testresult_in_db(pc_name, self.pc_info[pc_name]['start_time'], time.time(), status)
        self.pc_info[pc_name]['status'] = 'idle'
        self.pc_info[pc_name]['running_case'] = None
        self.pc_info[pc_name]['timeout'] = 0
        self.pc_info[pc_name]['start_time'] = time.time()            
        self.pc_info[pc_name]['test_dirname'] = ''
    def offline_pc(self, pc_name, status=None):
        self.main_logger.trace('offline pc:%s; case:%s'%(pc_name, str(self.pc_info[pc_name]['running_case'])))
        self.CaseDispatcher.stop_case(pc_name)
##        self.CaseDispatcher.run_case_getlog(pc_name, self.pc_info[pc_name]['test_dirname'])

        self.__offline_pc(pc_name, status)
    
    def func_monitor_conn(self):
        while True:
            time.sleep(2)
            for pc_name in self.pc_info.keys():
##                if self.pc_info[pc_name]['socket_serial'] != None:
##                    ret, feedback = self.send_cmd_serial(pc_name, 'HB')
##                    #handle send cmd failed case'
##                    #update serial console
##                print self.pc_info[pc_name]['socket']
                if self.pc_info[pc_name]['socket'] != None:
                    ret, feedback = self.send_cmd(pc_name, 'HB')
                    #handle send cmd failed case'
                    #do nothing except update socket handler; DUT status will be updated by update client
                    if not ret and self.pc_info[pc_name]['status'] == 'running':
                        self.main_logger.trace('socket conn lost; case:%s is stopped; '%self.pc_info[pc_name]['running_case'])
                        self.offline_pc(pc_name, 'DUT controler lost connection')

    def __insert_testresult_in_db(self, pc_name, timestamp):
        casename = self.pc_info[pc_name]['running_case']
        testfold = self.pc_info[pc_name]['test_dirname']
        sbt_version = self.pc_info[pc_name]['sbt_version']
        self.mysql_hdlr.insert('test_result', {'case_name':casename,
                                               'case_id':self.case_info[casename]['id'],
                                               'DUT_DUTCtl':pc_name,
                                               'start_time':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
                                               'end_time':'0000-00-00 00:00:00',
                                               'status':'running',
                                               'result_path':testfold,
                                               'sbt_version':sbt_version})
    def __update_testresult_in_db(self, pc_name, timestamp_start, timestamp_end, status):
        casename = self.pc_info[pc_name]['running_case']
        sbt_version = self.pc_info[pc_name]['sbt_version']
        self.mysql_hdlr.update('test_result', {'start_time':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_start)), 
                                               'end_time':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_end)), 
                                               'status':status,
                                               'sbt_version':sbt_version},
                                              {'case_name':casename, 
                                               'DUT_DUTCtl':pc_name, 
                                               'start_time':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_start))})
    def __update_teststatus_in_db(self, pc_name, status):
        casename = self.pc_info[pc_name]['running_case']
        sbt_version = self.pc_info[pc_name]['sbt_version']
        self.mysql_hdlr.update('test_result', {'status':status,
                                               'sbt_version':sbt_version},
                                              {'case_name':casename, 
                                               'DUT_DUTCtl':pc_name, 
                                               'start_time':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.pc_info[pc_name]['start_time']))})
 
    def __get_valid_conn(self):
        conn_list = []
        for pc_name in self.pc_info.keys():
            if self.pc_info[pc_name]['active'] and self.pc_info[pc_name]['type']=='PC' and self.pc_info[pc_name]['socket'] != None:
                conn_list.append(self.pc_info[pc_name]['socket'])
        #self.main_logger.trace("get %d conn"%len(conn_list))
        return conn_list
    def __get_pcname_byconn(self, conn):
        for pc_name in self.pc_info.keys():
            if self.pc_info[pc_name]['socket'] is conn:
                return True, pc_name
        return False, ''
    def __process_cmd(self, pc_name, cmd):
        self.main_logger.info("Get command:\"%s\" from %s"%(cmd, pc_name))
        if cmd.startswith("update_status:"):
            #update status
            self.__update_teststatus_in_db(pc_name, cmd[len("update_status:"):])
            self.pc_info[pc_name]['socket'].sendall(self.__end_str)
        elif cmd.startswith("update_testresult:"):
            #update testresult
            self.__update_testresult_in_db(pc_name, self.pc_info[pc_name]['start_time'], time.time(), cmd[len("update_testresult:"):])
            self.pc_info[pc_name]['socket'].sendall(self.__end_str)
            case_name = self.pc_info[pc_name]['running_case']
            self.case_info[case_name]['have_run'] += 1
        elif cmd.startswith("sbt_version:"):
            self.pc_info[pc_name]['sbt_version'] = cmd[len("sbt_version:"):]
        elif cmd == "PM_reset":
            #PM reset
            if self.pc_info[pc_name]['PM_link'].startswith('http'):
                self.pc_info[pc_name]['socket'].sendall(self.pc_info[pc_name]['PM_link'] + self.__end_str)
        elif cmd == "Req_testcase":
            #request a testcase cmd
            ret, casename, test_dirname = self.CaseDispatcher.request_case(pc_name)
            if ret:
                self.main_logger.trace("dispatch case:%s to pc:%s"%(casename, pc_name))
                self.pc_info[pc_name]['status'] = 'running'
                self.pc_info[pc_name]['running_case'] = casename
                self.pc_info[pc_name]['test_dirname'] = test_dirname
                self.pc_info[pc_name]['timeout'] = self.case_info[casename]['timeout']
                self.pc_info[pc_name]['start_time'] = time.time()
                self.pc_info[pc_name]['sbt_version'] = 'unknown'

                self.__insert_testresult_in_db(pc_name, self.pc_info[pc_name]['start_time'])
                self.pc_info[pc_name]['socket'].sendall("python -u case_main.py \"%s\":%s:%s"%(
                                                        self.case_info[casename]['cmd'], 
                                                        str(self.case_info[casename]['timeout']),
                                                        test_dirname) + self.__end_str)
            else:
                self.main_logger.error("testlist of pc:%s is null"%pc_name)
                self.pc_info[pc_name]['socket'].sendall('no_testcase' + self.__end_str)

    def __monitor_dut_controller(self, conn_list):
        if len(conn_list) == 0:
            return
        try:
            rs, ws, es = select.select(conn_list, [], conn_list, 1)
            for e in es:
                ret, pc_name = self.__get_pcname_byconn(e)
                self.main_logger.error("connection from pc:%s get exception"%pc_name)
                if ret:
                    try:
                        self.pc_info[pc_name]['socket'].close()
                        self.main_logger.error("PC:%s connection get exception; try to close"%pc_name)
                    except:
                        self.main_logger.error("Get exception when close connection from PC:%s"%pc_name)
                    self.pc_info[pc_name]['socket'] = None

            for r in rs:
                ret, pc_name = self.__get_pcname_byconn(r)
                self.main_logger.trace("connection from pc:%s ready to read"%pc_name)
                if ret:
                    self.pc_info[pc_name]['rcv_buf'] += r.recv(self.BUFSIZE)
                    if self.pc_info[pc_name]['rcv_buf'].find(self.__end_str):
                        cmds = self.pc_info[pc_name]['rcv_buf'].split(self.__end_str)
                        for cmd in cmds[:-1]:
                            #process cmd
                            self.__process_cmd(pc_name, cmd)
                        self.pc_info[pc_name]['rcv_buf'] = cmds[-1]
        except KeyboardInterrupt:
            self.main_logger.error( "User Press Ctrl+C,Socket break down." )
	except Exception, e:
            self.main_logger.error( "Socket captured an exception:%s"%str(e) )
            self.main_logger.error(traceback.format_exc())
        except:
            self.main_logger.error( "Got Unknow error." )
            self.main_logger.error(traceback.format_exc())
            


    def run(self):
        while True:
            time.sleep(1)
            self.lock.acquire()
            self.update_cfg(self.adb_hdlr, self.mysql_hdlr, self.main_logger, self.pc_info, self.case_info, self.unknown_pc_info)
            self.__monitor_dut_controller(self.__get_valid_conn()) 
            """
            for pc_name in self.pc_info.keys():
                if self.pc_info[pc_name]['active']:
                    self.main_logger.trace("pc_name:%s status:%s active:%s DUT type:%s ip:%s"%(pc_name, self.pc_info[pc_name]['status'], self.pc_info[pc_name]['active'], self.pc_info[pc_name]['type'], self.pc_info[pc_name]['ip']))
                if self.pc_info[pc_name]['socket'] != None and self.pc_info[pc_name]['type']=='PC':
                    self.main_logger.info("do nothing")
                    if self.pc_info[pc_name]['status'] == 'idle' and self.pc_info[pc_name]['active']:
                        socket_addr_old = self.pc_info[pc_name]['socket_addr']
                        ret, casename, test_dirname, timeout = self.CaseDispatcher.dispatch_case(pc_name)
                        if ret:
                            if socket_addr_old == self.pc_info[pc_name]['socket_addr']:
                                self.pc_info[pc_name]['status'] = 'running'
                                self.pc_info[pc_name]['running_case'] = casename
                                self.pc_info[pc_name]['test_dirname'] = test_dirname
                                self.pc_info[pc_name]['timeout'] = timeout
                                self.pc_info[pc_name]['start_time'] = time.time()
                                self.__insert_testresult_in_db(pc_name, self.pc_info[pc_name]['start_time'])
                            else:
                                self.pc_info[pc_name]['running_case'] = casename
                                self.pc_info[pc_name]['test_dirname'] = test_dirname
                                self.offline_pc(pc_name)
                    elif self.pc_info[pc_name]['status'] == 'running' and self.pc_info[pc_name]['active']:
                        self.update_client(pc_name)
                    elif self.pc_info[pc_name]['status'] == 'running' and not self.pc_info[pc_name]['active']:
                        self.offline_pc(pc_name, 'deactive')
                elif self.pc_info[pc_name]['type'] == 'DUT' and self.pc_info[pc_name]['ip'] != '':
                    if self.pc_info[pc_name]['status'] == 'idle' and self.pc_info[pc_name]['active']:
                        self.main_logger.trace("pc_name:%s status:%s active:%s DUT type:%s ip:%s"%(pc_name, self.pc_info[pc_name]['status'], self.pc_info[pc_name]['active'], self.pc_info[pc_name]['type'], self.pc_info[pc_name]['ip']))
                        ret, casename, test_dirname, timeout = self.CaseDispatcher.dispatch_case(pc_name)
                        if ret:
                            self.pc_info[pc_name]['status'] = 'running'
                            self.pc_info[pc_name]['running_case'] = casename
                            self.pc_info[pc_name]['test_dirname'] = test_dirname
                            self.pc_info[pc_name]['timeout'] = timeout
                            self.pc_info[pc_name]['start_time'] = time.time()
                            self.__insert_testresult_in_db(pc_name, self.pc_info[pc_name]['start_time'])
                    elif self.pc_info[pc_name]['status'] == 'running' and self.pc_info[pc_name]['active']:
                        self.update_client(pc_name)
                    elif self.pc_info[pc_name]['status'] == 'running' and not self.pc_info[pc_name]['active']:
                        self.offline_pc(pc_name, 'deactive')
            """
            self.lock.release()
                    #handle send cmd failed case
                    #update status
