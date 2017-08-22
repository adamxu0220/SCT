#from mrvl_serial import *
from mrvl_adb import *
from mrvl_log import *
from mrvl_serial import *
import re

def get_bg2cdp_version(serial_port, dut_ip):
    serial_logger = mrvl_logger(os.path.join("serial.txt"))
    serial_hdlr = ComThread(serial_logger, int(serial_port))
    serial_hdlr.start()
    
    keywords = "ro.build.display.id"
    res = "Unknown"
    ret = serial_hdlr.get_keywords([keywords], 5, AndOr = True, WriteCmd = ["grep %s /system/build.prop"%keywords, 3], Repeat_cmd = True)
    if ret[0] and ret[2].find(keywords+"=") > -1:
        res = ret[2][ret[2].find(keywords+"=") + 1 + len(keywords):]
    serial_hdlr.stop()
    del serial_hdlr
    del serial_logger
    return res.replace(" ", "0x20")

def get_bg2q4k_version(serial_port, dut_ip):
    serial_logger = mrvl_logger(os.path.join("serial.txt"))
    serial_hdlr = ComThread(serial_logger, int(serial_port))
    serial_hdlr.start()

    keywords = "ro.build.version.incremental"
    res = "Unknown"
    ret = serial_hdlr.get_keywords([keywords], 5, AndOr = True, WriteCmd = ["grep %s /system/build.prop"%keywords, 3], Repeat_cmd = True)
    if ret[0] and ret[2].find(keywords+"=") > -1:
        res = ret[2][ret[2].find(keywords+"=") +1+ len(keywords):].strip()
    if res.find(' ') > -1:
        res = res[:res.find(' ')]
    if res.find('root') > -1:
        res = res[:res.find('root')]
    serial_hdlr.stop()
    del serial_hdlr
    del serial_logger
    return res.replace(" ", "0x20")

def get_midastv_version(serial_port, dut_ip):
    serial_logger = mrvl_logger(os.path.join("serial.txt"))
    serial_hdlr = ComThread(serial_logger, int(serial_port))
    serial_hdlr.start()
    keywords = re.compile(r"\[ro\.build\.version\.incremental\]: \[(.*?)\]")
    res = "Unknown"
    ret = serial_hdlr.get_keywords([keywords], 5, AndOr = True, WriteCmd = ["getprop", 0.2], Repeat_cmd = True)
    if ret[0]:
        res = keywords.search(ret[-1]).group(1)
    serial_hdlr.stop()
    del serial_hdlr
    del serial_logger
    return res.replace(" ", "0x20") 


def get_version(dut_type, serial_port, dut_ip):
    if dut_type == 'bg2cdp' or dut_type == "ANCHOVY2_BG2CDP":
        return get_bg2cdp_version(serial_port, dut_ip)
    if dut_type == 'bg2q4k' or dut_type == 'ANDROIDTV_SPRUCE_BG2Q4K' or dut_type == 'TPV2K15_BG2Q4K' or dut_type == 'ANDROIDTV_SPRINT_BG4CT':
        return get_bg2q4k_version(serial_port, dut_ip)
    if dut_type == 'MIDAS_TV':
        return get_midastv_version(serial_port, dut_ip)
    return "unknown"

