#!/usr/bin/env python  
#coding=utf-8  
import time
import sys,os,string
import socket
import threading
import select
import zipfile
    
class Server_Listen(threading.Thread):  
    def __init_socket(self):
        try:
            connection_A = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection_A.bind(('', self.PORT_connectionA))
            connection_A.listen(self.MAX_CLIENT)
            self.serv_socket['connection_A'] = connection_A
            return 
        except Exception, e:
            self.main_logger.error("Try to setup socket-server with port:%d get exception:%s"%(self.PORT_connectionA, str(e)))
        except:
            self.main_logger.error("Try to setup socket-server with port:%d get unknown exception"%self.PORT_connectionA)
        self.serv_socket['connection_A'] = None

    def __send_cmd(self, pc_socket, addr, desc, pc_name, port, cmd, bufsize=1024*1000, timeout=30):
        feedback = ''
        ret = False
        if port == 0 or pc_name == None :
            return ret, feedback, pc_socket
        time_start = time.time()
        try:
            if pc_socket == None:
                return False, 'socket is None', None
            self.lock.acquire()
            pc_socket.settimeout(timeout)
            pc_socket.send(cmd+self.end_str)
            if len(cmd) < 50:
                self.main_logger.trace('send command to %s:%s'%(addr[0],cmd))
            while True:
                feedback += pc_socket.recv(bufsize)
                if len(feedback) < 100 and len(feedback) > 0:
                    self.main_logger.trace('get feedback from %s:%s'%(addr[0],feedback[:0-len(self.end_str)]))
                if feedback.endswith(self.end_str):
                    ret = True
                    break
                if time.time() - time_start > timeout:
                    self.main_logger.error("Send cmd %s timeout, feedback:%s"%(cmd, feedback))
                    break
            self.lock.release()
            return ret, feedback[:0-len(self.end_str)], pc_socket
        except Exception, e:
            feedback = "Capture exception:%s when try to write/read socket from %s:%d in (%s); cmd:%s"%(str(e), addr[0], addr[1], desc, cmd)
        except Exception:
            feedback = "Capture unknown exception when try to write/read socket from %s:%d in (%s); ; cmd:%s"%(addr[0], addr[1], desc, cmd)
        self.main_logger.error("%s\r\nWill try to close the connection from (%s,%d)"%(feedback, addr[0], addr[1]))
        try:
            pc_socket.close()
            pc_socket = None
        except:
            pass
        self.lock.release()
        return ret, feedback, pc_socket        
                
    def send_cmd(self, pc_name, cmd, timeout=30):
        ret, feedback, self.pc_info[pc_name]['socket'] = self.__send_cmd(self.pc_info[pc_name]['socket'], self.pc_info[pc_name]['socket_addr'], "Connection A", pc_name, self.PORT_connectionA, cmd, timeout=timeout)
        return ret, feedback
    def __init__(self,logger,pc_info,unknown_pc_info):
        super(Server_Listen, self).__init__()
        self.PORT_connectionA = 9999
        self.MAX_CLIENT = 1000
        self.end_str = '<<EOF'
        self.serv_socket = {}
        self.serv_socket['connection_A'] = None
        self.pc_info = pc_info
        self.unknown_pc_info = unknown_pc_info
        self.main_logger = logger
        self.lock = threading.Lock()
        
    def run(self):
        self.__init_socket()
        if self.serv_socket['connection_A'] == None:
            self.main_logger.error('Connect A listen failed')
            return 
        while True:
            try:
                time.sleep(0.01)
                rs, ws, es = select.select([self.serv_socket['connection_A']], [], [], 1)
                for r in rs:
                    if r == self.serv_socket['connection_A']:
                        conn, addr = self.serv_socket['connection_A'].accept()
                        conn.settimeout(60)
                        ret, feedback, sock = self.__send_cmd(conn, addr,"connection_A", "", self.PORT_connectionA,"get_hostname")
                        pc_name = feedback
                        self.main_logger.trace("Socket(Connection A) from (%s:%d) is connected"%(pc_name, addr[1]))
                        pc_name = string.upper(pc_name)
                        if self.pc_info.has_key(pc_name):
                            if self.pc_info[pc_name]['socket'] != None:
                                self.main_logger.error("Connection A from (%s:%d) will be force close"%(self.pc_info[pc_name]['socket_addr'][0], self.pc_info[pc_name]['socket_addr'][1]))
                                self.pc_info[pc_name]['socket'].close()
                            self.pc_info[pc_name]['socket'] = conn
                            self.pc_info[pc_name]['socket_addr'] = [pc_name, addr[1]]
                        else:
                            self.main_logger.error('unknown!!! :%s connected'%pc_name)
                            if not self.unknown_pc_info.has_key(pc_name):
                                self.unknown_pc_info[pc_name]={}
                            self.unknown_pc_info[pc_name]['socket'] = conn
                            self.unknown_pc_info[pc_name]['socket_addr'] = [pc_name, addr[1]]
                            self.unknown_pc_info[pc_name]['active'] = False
                       
            except KeyboardInterrupt:
                self.main_logger.error( "User Press Ctrl+C,Socket break down.")
                break
            except Exception, e:
                self.main_logger.trace( "Socket captured an exception:%s"%str(e))
                time.sleep(10)
                continue
            except:
                self.main_logger.trace( "Got Unknow error.")
                break
        self.main_logger.error("try to shutdown server listen")
        if self.serv_socket['connection_A'] != None:
            self.serv_socket['connection_A'].close()
