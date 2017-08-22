import time
import string
import os
import logging
import logging.handlers
import traceback

"""
Define the private exception
"""
class MyEx(Exception):
    __data = ""
    def __init__(self,data):
        self.__data = data
    def __str__(self):  # ... str(#)
        return self.__data


class mrvl_logger:  
    """
    The constructor
    """
    def __init__(self, test_case_log_target_file, format="%(asctime)s  %(levelname)s:  %(message)s"):
        self.Trace_lvl = 60
        logging.addLevelName(self.Trace_lvl, "TRACE") 
        self.Serial_lvl = 70
        logging.addLevelName(self.Serial_lvl, "SERIAL") 
        self.logger = logging.getLogger(os.path.basename(test_case_log_target_file))
        formatter = logging.Formatter(format)
        self.test_case_log_hdlr = logging.handlers.TimedRotatingFileHandler(test_case_log_target_file,when='D',interval=7,backupCount=100)#logging.FileHandler(test_case_log_target_file, 'wb+')
        self.test_case_log_hdlr.setFormatter(formatter)
        self.logger.addHandler(self.test_case_log_hdlr)
        self.logger.setLevel(logging.DEBUG)
        self.add_cc = None


    """
    The destructor
    """
    def __del__(self):
        self.logger.removeHandler(self.test_case_log_hdlr)
        del self.logger
        self.add_cc = None
    """
    Logs a message with level DEBUG on the root logger.
    The msg is the message format string, and the args are the arguments which are merged into msg using the string formatting operator.
    (Note that this means that you can use keywords in the format string, together with a single dictionary argument.)

    There are two keyword arguments in kwargs which are inspected: exc_info which, if it does not evaluate as false, causes exception information to be added to the logging message. If an exception tuple (in the format returned by sys.exc_info()) is provided, it is used; otherwise, sys.exc_info() is called to get the exception information.

    The other optional keyword argument is extra which can be used to pass a dictionary which is used to populate the __dict__ of the LogRecord created for the logging event with user-defined attributes. These custom attributes can then be used as you like. For example, they could be incorporated into logged messages. For example:
    """
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs) 

    def set_add_cc(self,func):
        
        self.add_cc = func

    """
    This function used to Logs a message with level INFO on the root logger. The arguments are interpreted as for debug().    
    """
    def info(self, msg, *args, **kwargs):
        #print msg
        self.logger.info(msg, *args, **kwargs)
    
    """
    This function used to Logs a message with level ERROR on the root logger. The arguments are interpreted as for debug().
    """
    def error(self, msg, *args, **kwargs):
        print msg
        try:
            timeStamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            self.add_cc.writeTrace("%s ERROR: %s"%(timeStamp,msg))
        except:
            pass
        self.logger.error(msg, *args, **kwargs)
        
    
    """
    This function used to rasie out a user defined exception
    """
    def prv_raise(self, msg, *args):
        self.exception(msg, args)
    """
    This function used to Logs a message with level raise on the root logger. The arguments are interpreted as for debug().
    """
    def exception(self, msg, *args):
        str_cstack = traceback.format_exc()
        if len(str_cstack) > 4 and  not (str_cstack[0:4] == "None" and ord(str_cstack[4]) == 10):
            self.info(traceback.format_exc())        
        self.logger.exception(msg, *args)
        raise MyEx(msg)

    """
    This function used to Logs a message with level TRACE on the root logger. The arguments are interpreted as for debug().
    """
    def trace(self, msg, *args, **kwargs):
        print msg
        try:
            timeStamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            self.add_cc.writeTrace("%s TRACE: %s"%(timeStamp,msg))
        except:
            pass
        self.logger.log(self.Trace_lvl, msg, *args, **kwargs)
    """
    This function used to Logs a message with level TRACE on the root logger. The arguments are interpreted as for debug().
    """
    def serial(self, msg, *args, **kwargs):
        self.logger.log(self.Serial_lvl, msg, *args, **kwargs)
    
    """
    This function used to Logs a message with level ERROR on the root logger. The arguments are interpreted as for debug().
    Exception info is added to the logging message. This function should only be called from an exception handler.
    """
    def	__exception(self, msg, *args):
        self.logger.exception(msg, *args)
        
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
        

        

