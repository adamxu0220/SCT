#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time,string

def offline_all_conn(mysql_hdlr):
    if mysql_hdlr.select_table('conn_info', {'status':'idle'} ):
        mysql_hdlr.update('conn_info', {'status':'offline'}, {'status':'idle'})
    if mysql_hdlr.select_table('conn_info', {'status':'busy'} ):
        mysql_hdlr.update('conn_info', {'status':'offline'}, {'status':'busy'})
    print "333333333"
def get_1stinfo_from_cmd_pool(db_data):
    if db_data == None: return None
    for id, cmd_owner, case_id, case_parametar, dut_type, client_id, exc_client_id, sw_version, create_time, deadline, start_time, end_time, status, result, bugid, reserved,group_id in db_data[:1]:
        return {'id':id, 
                'cmd_owner':cmd_owner,
                'case_id':case_id, 
                'case_parametar':case_parametar, 
                'dut_type':dut_type, 
                'client_id':client_id,
                'exc_client_id':exc_client_id,
                'sw_version':sw_version,
                'create_time':create_time,
                'deadline':deadline,
                'start_time':start_time,
                'end_time':end_time,
                'status':status,
                'result':result,
                'bugid':bugid,
                'reserved':reserved}
    return None
def get_1stinfo_from_conn_info(db_data):
    if db_data == None: return None
    for id, client_id, mac_addr, owner, dut_type, dut_ip, client_ip, client_conn_port, sw_version, start_time, end_time, status, lastupdate_time, client_pcname in db_data[:1]:
        return {'id':id,
                'client_id':client_id,
                'mac_addr':mac_addr,
                'owner':owner,
                'dut_type':dut_type,
                'dut_ip':dut_ip,
                'client_ip':client_ip,
                'client_conn_port':client_conn_port,
                'sw_version':sw_version,
                'start_time':start_time,
                'end_time':end_time,
                'status':status,
                'lastupdate_time':lastupdate_time,
                'client_pcname': client_pcname}
    return None

def get_1stinfo_from_case_info(db_data):
    if db_data == None: return None
    for id, name, path, dut_type, description, reserved, create_time, case_type in db_data[:1]:
        return {'id':id,
                'name':name,
                'path':path,
                'dut_type':dut_type,
                'create_time':create_time,
                'description':description,
                'reserved':reserved,
                'case_type':case_type}
    return None


def get_private_cmds(mysql_hdlr, owner, duttype, clientid, swversion):
    if clientid != 0:
        args_where = {'cmd_owner':owner, 'status':'not run', 'dut_type':duttype}
        res_db = mysql_hdlr.select_table('case_cmd_pool', args_where, orderby='id', where_str_addtional="deadline>Now() and (client_id = %s or client_id like '%%;%s;%%' or client_id like '%s;%%' or client_id like '%%;%s')"%(clientid, clientid, clientid, clientid))
        return res_db
    args_where = {'cmd_owner':owner, 'status':'not run', 'dut_type':duttype}
    res_db = mysql_hdlr.select_table('case_cmd_pool', args_where, orderby='id', where_str_addtional="deadline>Now()")
    #to be continue
    return res_db

def get_neighbour_cmds(mysql_hdlr, owner, duttype, clientid, swversion):
    if clientid != 0:
        args_where = {'status':'not run', 'dut_type':duttype}
        res_db = mysql_hdlr.select_table('case_cmd_pool', args_where, orderby='id', where_str_addtional="deadline>Now() and cmd_owner != '%s' and (client_id = %s or client_id like '%%;%s;%%' or client_id like '%s;%%' or client_id like '%%;%s')"%(owner, clientid, clientid, clientid, clientid))
        return res_db
    args_where = {'status':'not run', 'dut_type':duttype}
    res_db = mysql_hdlr.select_table('case_cmd_pool', args_where, orderby='id', where_str_addtional="deadline>Now() and cmd_owner != '%s'"%(owner))
    return res_db

def get_private_cmd(mysql_hdlr, owner, duttype, clientid, swversion):
    res = get_private_cmds(mysql_hdlr, owner, duttype, clientid, swversion)
    return get_1stinfo_from_cmd_pool(res)
def get_neighbour_cmd(mysql_hdlr, owner, duttype, clientid, swversion):
    res = get_neighbour_cmds(mysql_hdlr, owner, duttype, clientid, swversion)
    return get_1stinfo_from_cmd_pool(res)
def get_special_cmd(mysql_hdlr, id):
    args_where = {'id':id}
    return get_1stinfo_from_cmd_pool( mysql_hdlr.select_table('case_cmd_pool', args_where))


def update_special_cmd(mysql_hdlr, id, cond):
    return mysql_hdlr.update('case_cmd_pool', cond, {'id':id})   
def insert_connection_cmd(mysql_hdlr, cond):
    return mysql_hdlr.insert('conn_info', cond) 
def update_connection_cmd(mysql_hdlr, update_cond, search_cond, where_str_addtional=None):
    return mysql_hdlr.update('conn_info', update_cond, search_cond, where_str_addtional=None)
def update_connection_id(mysql_hdlr, search_cond):
    conn_info = get_connection_info(mysql_hdlr, search_cond)
    if conn_info == None:
        return False
    client_id = conn_info['client_id']
    if client_id == 0 or client_id == 16777215:
        client_id = conn_info['id']
    return mysql_hdlr.update('conn_info', {'client_id':client_id}, search_cond)
    

def get_connection_info(mysql_hdlr, cond):
    res_db = mysql_hdlr.select_table('conn_info', cond, orderby='id')
    if res_db != None and len(res_db) > 0:
        return get_1stinfo_from_conn_info(res_db)
    return None


def get_case_info(mysql_hdlr, cond):
    res_db = mysql_hdlr.select_table('case_info', cond, orderby='id')
    if res_db != None and len(res_db) > 0:
        return get_1stinfo_from_case_info(res_db)
    return None

def talk(mysql_hdlr):
    res_db = mysql_hdlr.select_table('dut_type')

__all__ = ["offline_all_conn",
           "get_private_cmd", 
           "get_neighbour_cmd", 
           "get_special_cmd", 
           "update_special_cmd", 
           "insert_connection_cmd", 
           "update_connection_cmd", 
           "get_connection_info",
           "get_case_info"]
